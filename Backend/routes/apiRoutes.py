from fastapi import APIRouter,Depends,Request,status
from authentication.auth import verify_jwt
from db.db import  get_database
from schemas.query import ResearchRequest
from components.orchestrator import orchestrator
from components.task_splitter import task_splitter
from components.research_planner import research_planner
from schemas.document import reports
from datetime import datetime,timezone
from fastapi.responses import StreamingResponse
from pymongo.errors import PyMongoError
from utils.limiter import limiter
from utils.index_pipeline import check_pipeline,insert_pipeline
from components.report_merger import merger
from db.redis import get_redis
from db.get_documents import get_documents
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

router=APIRouter()
redis_cache=get_redis()
db=get_database()

@router.get("/api/documents")
async def returnDocuments(
    page_num:int=1,
    user=Depends(verify_jwt)
):
    user_id=user["sub"]
    page_number=page_num
    # Fetch the documents from the database for this user and return to the frontend.
    response={}
    try:
        if(redis_cache):
            response=redis_cache.get(f'{user_id}:{page_num}')
            if(response):
                return response
    except Exception as e:
        logger.error(f'redis error: {e}')
        return response
    
    try:
        if(db!=None):
            response=await get_documents(db_connection=db,user_id=user_id,page_num=page_number)
            if(response["total_pages"]):
                if(redis_cache):
                    redis_cache.set(f'{user_id}:{page_number}',f'{response}',ex=3600)
        return response
    except Exception as e:
        logger.error(f'Database/redis error, {e}')
        return response
    
@router.post(
    '/api/research',
)
@limiter.limit("1/hour")
async def deepResearch(
    request:Request,
    body:ResearchRequest,
    user=Depends(verify_jwt)
):
    
    user_id=user["sub"] # handeled by verify_jwt
    query=body.query # handled by pydantic

    async def streamChunks():
        # Thread that checks for similar queries recieved in the past.
        report_ids=await asyncio.to_thread(check_pipeline,query) # type:ignore
        if len(report_ids):
            # extract the reports from database
            docs=[]
            if(db!=None):
                for id in report_ids:
                    result=await db.find_one({"_id":id})
                    docs.append(result.content)
                # get the formatted report from report_merger
                try:
                    resultant_report=await merger(query,docs)
                    if(len(resultant_report)):
                        # yield the output
                        yield json.dumps({
                            "type":"final_report",
                            "content":resultant_report
                        })
                        return
                except Exception as e:
                    logger.error(f'Merger agent error: {e}')
                    # we have to simply perform the research if report was not generated.

        research_plan=""
        async for event in research_planner(query):
            if  event["type"]=="chunk":
                research_plan+=event["content"]
                yield json.dumps(
                    {
                    "type":"chunk",
                    "content":event["content"]
                    }
                )
            elif event["type"]=="plan":
                research_plan=event["content"]
            elif event["type"]=="error":
                yield json.dumps(
                    {
                        "type":"error",
                        "status":event["status"],
                        "content":event["content"]
                    }
                )
        subTaskList=""
        async for event in task_splitter(research_plan=research_plan):
            if event["type"]=="subTaskList":
                subTaskList=event["content"]
            else:
                yield json.dumps(
                    {
                        "type":event["type"],
                        "status":event["status"],
                        "content":event["content"]
                    }
                )
                return

        final_report=""
        async for event in orchestrator(user_query=query,research_plan=research_plan,subtasks=subTaskList):# type:ignore
            if event["type"]=="final_report":
                final_report=event["content"]
            else:
                yield json.dumps(
                    {
                        "type":event["type"],
                        "status":event["status"],
                        "content":event["content"]
                    }
                )
                return
            
        report=reports(
            query=query,
            content=final_report, # type:ignore
            owner=user_id,
            created_at=datetime.now(timezone.utc)
        )

        document_id=""
        try:
            yield json.dumps(
                {
                    "type":"final_report",
                    "content":final_report
                }
            )
            # Store the report and query in the vector store by calling insert_pipeline.
            # report type is a class, not dict.we need to convert this to a dict
            # motor will convert into BSON and will store it in database.
            if(db!=None):
                response=await db.reports.insert_one(report.model_dump()) 
                document_id=str(response.inserted_id())
            # clear this user's entries from redis cache
            # Thread that inserts the generated result.
        except PyMongoError as e:
            logger.error(f"Report Insetion to database failed: {e}")
            yield json.dumps(
                {
                    "type":"error",
                    "status":500,
                    "content":""
                }
            )
        except Exception as e:
            logger.error(f"database error: {e}")
            yield json.dumps(
                {
                    "type":"error",
                    "status":500,
                    "content":""
                }
            )

        
        if(document_id):
            message=await asyncio.to_thread(insert_pipeline,query,str(document_id)) # type:ignore
            logger.info(message)

    return StreamingResponse(
        streamChunks(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"   
        }
    )
from fastapi import APIRouter,Depends,Request
from authentication.auth import verify_jwt
from db.db import db
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
import asyncio
import json

router=APIRouter()

@router.get(f'/api/documents/:${id}')
async def returnDocuments(user=Depends(verify_jwt)):
    # Fetch the documents from the database for this user and return to the frontend.
    pass

@router.post(
    '/api/research',
)
@limiter.limit("5/minute")
async def deepResearch(
    request:Request,
    body:ResearchRequest,
    user=Depends(verify_jwt)
):
    
    user_id=user["sub"] # handeled by verify_jwt
    query=body.query # handled by pydantic

    async def streamChunks():
        # Thread that checks for similar queries recieved in the past.
        event_type,event_content=await asyncio.to_thread(check_pipeline,query) # type:ignore
        if event_type=="report_ids":
            report_ids=event_content
            # extract the reports from database
            docs=[]
            for id in report_ids:
                result=await db.find_one({"_id":id})
                docs.append(result.content)
            # get the formatted report from report_merger
            try:
                resultant_report=await merger(query,docs)
                # yield the output
                yield json.dumps({
                    "type":"final_report",
                    "content":resultant_report
                })
                return
            except Exception:
                pass # we have to simply perform the research if report was not generated.

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
            response=await db.reports.insert_one(report.model_dump()) 
            document_id=response.inserted_id()
            # Thread that inserts the generated result.
        except PyMongoError as e:
            yield json.dumps(
                {
                    "type":"error",
                    "status":500,
                    "content":f"Report Insetion to database failed: {e}"
                }
            )

        try:
            event_type,event_content=await asyncio.to_thread(insert_pipeline,query,str(document_id)) # type:ignore
            yield json.dumps(
                {
                    "type":event_type,
                    "content":event_content
                }
            )
        except Exception:
            yield json.dumps(
                {
                    "type":event_type,
                    "content":event_content
                }
            )

    return StreamingResponse(
        streamChunks(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"   
        }
    )
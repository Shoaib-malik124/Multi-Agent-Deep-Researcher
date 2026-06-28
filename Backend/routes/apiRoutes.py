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

        try:
            yield json.dumps(
                {
                    "type":"final_report",
                    # "content":final_report
                }
            )
            await db.reports.insert_one(report.model_dump()) # report type is a class, not dict.we need to convert this to a dict
        #                                                    #, motor will convert into BSON and will store it in database.
        except PyMongoError as e:
            yield json.dumps(
                {
                    "type":"error",
                    "status":500,
                    "content":"Report Insetion to database failed"
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
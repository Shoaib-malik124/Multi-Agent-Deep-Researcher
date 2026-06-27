from fastapi import APIRouter,Depends,HTTPException,status
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
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter
import json

router=APIRouter()

@router.get(f'/api/documents/:${id}')
async def returnDocuments(user=Depends(verify_jwt)):
    # Fetch the documents from the database for this user and return to the frontend.
    pass

@router.post(
    '/api/research',
    dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(5,Duration.HOUR*1))))]
)
async def deepResearch(
    body:ResearchRequest,
    user=Depends(verify_jwt)
):
    
    user_id=user["sub"] # handeled by verify_jwt
    query=body.query # handled by pydantic

    async def streamChunks():
        research_plan=""
        async for event in research_planner(query):
            if event["type"]=="chunk":
                research_plan+=event["content"]
                yield json.dumps(
                    {
                      "type":"chunk",
                      "content":event["content"]
                    }
                )
            elif event["type"]=="plan":
                research_plan=event["content"]
            elif event["type"]=="error" and event["status"]==502:
                yield json.dumps(
                    {
                        "type":"error",
                        "status":event["status"],
                        "content":event["content"]
                    }
                )
            
        subtasks=await task_splitter(research_plan=research_plan) # handled by task_splitter
        final_report=await orchestrator(user_query=query,research_plan=research_plan,subtasks=subtasks) # handled by orchestrator
        report=reports(
            content=final_report, # type:ignore
            owner=user_id,
            created_at=datetime.now(timezone.utc)
        )

        try:
            yield json.dumps(
                {
                    "type":"final_report",
                    "content":final_report
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
            "X-Accel-Buffering": "no"   # important — disables nginx buffering if you deploy
        }
    )
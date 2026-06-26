from fastapi import APIRouter,Depends
from authentication.auth import verify_jwt
from db.db import db
from schemas.query import ResearchRequest
from components.orchestrator import orchestrator
from components.task_splitter import task_splitter
from components.research_planner import research_planner
from schemas.document import reports
from datetime import datetime,timezone
import json

router=APIRouter()

@router.get(f'/api/documents/:${id}')
async def returnDocuments(user=Depends(verify_jwt)):
    # Fetch the documents from the database for this user and return to the frontend.
    pass

@router.post(f'/api/research')
async def deepResearch(
    body:ResearchRequest,
    user=Depends(verify_jwt)
):
    user_id=user["sub"]
    query=body.query
    
    async def stramChunks():
        research_plan=""
        async for event in research_planner(query):
            if event["type"]=="chunk":
                research_plan+=event["content"]
                yield json.dumps(
                    {
                       "chunk":event["content"]
                    }
                )
            elif event["type"]=="plan":
               research_plan=event["content"]
        
        subtasks=await task_splitter(research_plan=research_plan) 
        final_report=await orchestrator(user_query=query,research_plan=research_plan,subtasks=subtasks)
        report=reports(
            content=final_report, # type:ignore
            owner=user_id,
            created_at=datetime.now(timezone.utc)
        )
        await db.reports.insert_one(report.model_dump()) # report type is a class, not dict.we need to convert this to a dict
        #                                                #, motor will convert into BSON and will store it in database.
    


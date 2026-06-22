from fastapi import APIRouter,Depends
from authentication.auth import verify_jwt
from db.db import db_connection
from schemas.query import ResearchRequest

router=APIRouter()

@router.get(f'/api/documents/:${id}')
async def returnDocuments(user=Depends(verify_jwt)):
    # Fetch the documents from the database for this user and return to the frontend.
    db=db_connection()
    pass

@router.post(f'/api/research')
async def deepResearch(
    body:ResearchRequest,
    user=Depends(verify_jwt)
):
    query=body.query
    user_id=user["sub"]
    # The pipeline for research starts here.
    pass


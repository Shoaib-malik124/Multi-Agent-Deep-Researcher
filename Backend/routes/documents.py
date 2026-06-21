from fastapi import APIRouter
from fastapi import Depends
from auth import verify_jwt
from db import db_connection

router=APIRouter()

@router.get(f'/documents/:${id}')
def returnDocuments(user=Depends(verify_jwt)):
    # Fetch the documents from the database for this user and return to the frontend.
    db=db_connection()
    pass
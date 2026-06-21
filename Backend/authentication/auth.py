from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from dotenv import load_dotenv
load_dotenv()
import os

CLERK_JWKS_URL=os.environ["CLERK_JWKS_URL"]

jwks_client=PyJWKClient(CLERK_JWKS_URL)
security=HTTPBearer()

def verify_jwt(credentials:HTTPAuthorizationCredentials=Depends(security)):
    token=credentials.credentials
    try:
        signing_key=jwks_client.get_signing_key_from_jwt(token)
        payload=jwt.decode(
           token,
           signing_key.key,
           algorithms=["RS256"],
           options={"verify_aud": False},  # checkPoint
        )
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Unauthorized User'
        )
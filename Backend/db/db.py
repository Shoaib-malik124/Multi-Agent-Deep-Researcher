import os
from motor.motor_asyncio import AsyncIOMotorClient

def get_database():
    try:
        MONGO_URI=os.environ["MONGO_URI"]
        DB_NAME=os.environ["DB_NAME"]

        client=AsyncIOMotorClient(MONGO_URI)
        db=client[DB_NAME]
        return db
    except Exception:
        return None
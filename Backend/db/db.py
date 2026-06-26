import os
from dotenv import load_dotenv
load_dotenv()
from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URI=os.environ["MONGO_URI"]
DB_NAME=os.environ["DB_NAME"]

client=AsyncIOMotorClient(MONGO_URI)
db=client[DB_NAME]
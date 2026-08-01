from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.apiRoutes import router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from utils.limiter import limiter
from motor.motor_asyncio import AsyncIOMotorClient
import redis
import os

load_dotenv()

def _check_env_vars():
    required = [
        "FIRECRAWL_API_KEY",
        "HF_TOKEN",
        "MCP_URL",
        "CLERK_JWKS_URL",
        "MONGO_URI",
        "DB_NAME",
        "PLANNER_MODEL_ID",
        "TASK_SPLITTER_MODEL_ID",
        "ORCHESTRATOR_COORDINATOR_MODEL_ID",
        "ORCHESTRATOR_SUBAGENT_MODEL_ID",
        "PINECONE_API_KEY",
        "PINECONE_INDEX_HOST",
        "REDIS_URL",
        "ALLOWED_ORIGINS"
    ]
    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

def _init_mongo():
    try:
        MONGO_URI = os.environ["MONGO_URI"]
        DB_NAME = os.environ["DB_NAME"]
        client = AsyncIOMotorClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000 
        )
        return client[DB_NAME]
    except Exception as e:
        raise RuntimeError(f"MongoDB connection failed: {e}")


def _init_redis():
    try:
        REDIS_URL = os.environ["REDIS_URL"]
        r = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=5)
        r.ping()  
        return r
    except Exception as e:
        raise RuntimeError(f"Redis connection failed: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _check_env_vars()
        app.state.db = _init_mongo()
        await app.state.db.command("ping")
        app.state.redis = _init_redis()
    except RuntimeError as e:
        raise 

    yield 

    if hasattr(app.state, "db"):
        app.state.db.client.close()
    if hasattr(app.state,"redis"):
        app.state.redis.close()

ALLOWED_ORIGINS=os.environ.get("ALLOWED_ORIGINS","").split(",")
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler) # type: ignore 

app.include_router(router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Research copilot server is alive"}
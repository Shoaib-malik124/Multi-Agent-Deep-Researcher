from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.apiRoutes import router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
load_dotenv()
from utils.limiter import limiter


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",       # Vite dev server
        "http://localhost:3000",       # React dev server
        "https://multi-agent-deep-researcher.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler) # type: ignore 

app.include_router(router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Research copilot backend is alive"}
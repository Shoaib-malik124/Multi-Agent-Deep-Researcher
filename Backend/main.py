from fastapi import FastAPI
from routes.apiRoutes import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Research copilot backend is alive"}
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Research copilot backend is alive"}
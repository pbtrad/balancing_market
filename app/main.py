from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="Balancing Market API")

app.include_router(api_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "Running", "message": "Balancing Market API is live"}

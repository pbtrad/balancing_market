from fastapi import FastAPI
from app.api.routes.forecast import router as forecast_router

app = FastAPI(title="Balancing Market API")

app.include_router(forecast_router, prefix="/api/forecast")


@app.get("/")
def health_check():
    return {"status": "Running", "message": "Balancing Market API is live"}

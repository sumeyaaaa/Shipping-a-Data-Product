# src/api/main.py
from fastapi import FastAPI
from src.api import crud, schemas
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Ethiomed Analytical API",
    version="1.0.0",
    description="Exposes Telegram data insights via REST endpoints."
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/reports/top-products", response_model=list[schemas.TopProduct])
def top_products(limit: int = 10):
    return crud.get_top_products(limit)

@app.get("/api/channels/{channel}/activity", response_model=schemas.ChannelActivity)
def channel_activity(channel: str):
    return crud.get_channel_activity(channel)

@app.get("/api/reports/posting-trends", response_model=list[schemas.PostingTrend])
def posting_trends(interval: str = "daily"):
    return crud.get_posting_trends(interval)

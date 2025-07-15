from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .schemas import TopProduct, ChannelActivity, PostingTrend
from .crud import get_top_products, get_channel_activity, get_posting_trends

app = FastAPI(
    title="Ethiomed Analytical API",
    version="1.0.0",
    description="Exposes Telegram data insights via REST endpoints."
)

@app.get("/api/reports/top-products", response_model=list[TopProduct])
def top_products(limit: int = 10, db: Session = Depends(get_db)):
    return get_top_products(limit)

@app.get("/api/channels/{channel}/activity", response_model=ChannelActivity)
def channel_activity(channel: str, db: Session = Depends(get_db)):
    return get_channel_activity(channel)

@app.get("/api/reports/posting-trends", response_model=list[PostingTrend])
def posting_trends(interval: str = "daily", db: Session = Depends(get_db)):
    return get_posting_trends(interval)

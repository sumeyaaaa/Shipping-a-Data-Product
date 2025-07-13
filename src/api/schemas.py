from pydantic import BaseModel
from datetime import datetime

class TopProduct(BaseModel):
    product: str
    mentions: int

class ChannelActivity(BaseModel):
    channel: str
    count: int

class PostingTrend(BaseModel):
    period: str
    posts: int

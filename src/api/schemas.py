from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TopProduct(BaseModel):
    product: Optional[str]
    mentions: int

class ChannelActivity(BaseModel):
    channel: str
    count: int

class PostingTrend(BaseModel):
    period: str
    posts: int

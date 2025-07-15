from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import SessionLocal
from .schemas import TopProduct, ChannelActivity, PostingTrend

def get_top_products(limit: int):
    sql = text(
        """
        SELECT
          COALESCE(message_text, '')     AS product,
          COUNT(*)                       AS mentions
        FROM raw.messages
        GROUP BY 1
        ORDER BY mentions DESC
        LIMIT :limit
        """
    )
    with SessionLocal() as session:
        rows = session.execute(sql, {"limit": limit}).all()
    return [TopProduct(product=row[0], mentions=row[1]) for row in rows]

def get_top_detected_objects(limit: int):
    sql = text(
        """
        SELECT
          object_class     AS product,
          COUNT(*)         AS mentions
        FROM analytics.fct_image_detections
        GROUP BY object_class
        ORDER BY mentions DESC
        LIMIT :limit
        """
    )
    with SessionLocal() as session:
        rows = session.execute(sql, {"limit": limit}).all()
    return [TopProduct(product=row[0], mentions=row[1]) for row in rows]

def get_channel_activity(channel: str):
    sql = text(
        """
        SELECT :channel AS channel, COUNT(*) AS count
        FROM raw.messages
        WHERE channel = :channel
        """
    )
    with SessionLocal() as session:
        row = session.execute(sql, {"channel": channel}).first()
        return ChannelActivity(channel=row[0], count=row[1])


def get_posting_trends(interval: str):
    if interval not in ("daily", "weekly"): raise ValueError("Invalid interval")
    group = "date_trunc('day', message_date)" if interval=='daily' else "date_trunc('week', message_date)"
    sql = text(f"""
        SELECT {group}::text AS period, COUNT(*) AS posts
        FROM raw.messages
        GROUP BY 1
        ORDER BY 1
        """
    )
    with SessionLocal() as session:
        result = session.execute(sql).all()
        return [PostingTrend(period=row[0], posts=row[1]) for row in result]

# src/loader_schema.py
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g.: postgres://user:pass@postgres:5432/etl_db


def create_raw_schema_and_tables():
    """
    Create `raw` schema and its tables:
      - raw.messages (one row per Telegram message)
      - raw.images   (one row per downloaded image)
    """
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Create raw schema
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    # raw.messages table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw.messages (
      message_id    BIGINT       PRIMARY KEY,
      channel       TEXT         NOT NULL,
      sender_id     BIGINT,
      message_date  TIMESTAMPTZ,
      message_text  TEXT,
      raw           JSONB        NOT NULL
    );
    """
    )

    # raw.images table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw.images (
      image_id      TEXT         PRIMARY KEY,
      channel       TEXT         NOT NULL,
      message_id    BIGINT       REFERENCES raw.messages(message_id),
      file_path     TEXT         NOT NULL,
      download_date TIMESTAMPTZ  DEFAULT NOW()
    );
    """
    )

    conn.commit()
    cur.close()
    conn.close()


def create_analytics_schema_and_tables():
    """
    Create `analytics` schema and enrichment tables:
      - analytics.fct_image_detections
    """
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Create analytics schema
    cur.execute("CREATE SCHEMA IF NOT EXISTS analytics;")

    # analytics.fct_image_detections table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS analytics.fct_image_detections (
      id                SERIAL      PRIMARY KEY,
      message_id        BIGINT      NOT NULL REFERENCES raw.messages(message_id),
      object_class      TEXT        NOT NULL,
      confidence_score  REAL        NOT NULL,
      detection_time    TIMESTAMPTZ DEFAULT NOW()
    );
    """
    )

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    # Initialize raw and analytics schemas/tables
    create_raw_schema_and_tables()
    create_analytics_schema_and_tables()

"""
Module: loader_schema.py

This module defines functions to initialize the Postgres database schemas and tables
for both raw data ingestion and analytics/enrichment layers.

Functions:
  - create_raw_schema_and_tables():
      Creates the `raw` schema and tables to store Telegram messages and images.

  - create_analytics_schema_and_tables():
      Creates the `analytics` schema and tables for image detection enrichment data.

When run as a script, both functions are executed to ensure the database is initialized.
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g.: postgres://user:pass@host:port/dbname


def create_raw_schema_and_tables():
    """
    Create the `raw` schema and its tables in the database:

    Tables:
      - raw.messages:
          Stores one row per Telegram message, preserving raw JSON payloads.

      - raw.images:
          Stores one row per downloaded image, referencing the corresponding message.

    This function connects to the database with autocommit mode, ensures schemas
    exist, and creates tables if they do not already exist.
    """
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Create raw schema if it doesn't exist
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    # Create raw.messages table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw.messages (
      message_id    BIGINT       PRIMARY KEY,
      channel       TEXT         NOT NULL,
      sender_id     BIGINT,
      message_date  TIMESTAMPTZ,
      message_text  TEXT,
      raw           JSONB        NOT NULL
    );
    """)

    # Create raw.images table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw.images (
      image_id      TEXT         PRIMARY KEY,
      channel       TEXT         NOT NULL,
      message_id    BIGINT       REFERENCES raw.messages(message_id),
      file_path     TEXT         NOT NULL,
      download_date TIMESTAMPTZ  DEFAULT NOW()
    );
    """)

    conn.commit()
    cur.close()
    conn.close()


def create_analytics_schema_and_tables():
    """
    Create the `analytics` schema and enrichment tables:

    Tables:
      - analytics.fct_image_detections:
          Stores object detection results for images, linking back to messages.

    This function connects to the database with autocommit mode, ensures schemas
    exist, and creates tables if they do not already exist.
    """
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Create analytics schema if it doesn't exist
    cur.execute("CREATE SCHEMA IF NOT EXISTS analytics;")

    # Create analytics.fct_image_detections table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS analytics.fct_image_detections (
      id                SERIAL      PRIMARY KEY,
      message_id        BIGINT      NOT NULL REFERENCES raw.messages(message_id),
      object_class      TEXT        NOT NULL,
      confidence_score  REAL        NOT NULL,
      detection_time    TIMESTAMPTZ DEFAULT NOW()
    );
    """)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    # Initialize raw and analytics schemas/tables
    create_raw_schema_and_tables()
    create_analytics_schema_and_tables()

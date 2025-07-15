"""
Module: raw_loader.py

This module defines functions to bulk load raw Telegram messages and images
from the local data lake into the Postgres database `raw` schema.

Functions:
  - load_messages(date_str: str = None):
      Reads JSON files from `data/raw/telegram_messages/YYYY-MM-DD/*.json`,
      truncates the `raw.messages` table, and upserts records into it.

  - load_images(date_str: str = None):
      Reads downloaded image files from
      `data/raw/telegram_images/YYYY-MM-DD/<channel>/*.jpg`,
      truncates the `raw.images` table, and inserts metadata rows,
      associating each image with its Telegram message.

When run as a script, both functions are executed for the current UTC date.
"""
import os
import json
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

from dotenv import load_dotenv
from loader_schema import create_raw_schema_and_tables

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def load_messages(date_str: str = None):
    """
    Load raw JSON message files into the `raw.messages` table.

    Steps:
      1. Ensure raw schema and tables exist by calling
         `create_raw_schema_and_tables()`.
      2. Connect to the database and truncate `raw.messages`.
      3. Iterate over JSON files in
         `data/raw/telegram_messages/YYYY-MM-DD/` (uses `date_str`).
      4. Parse each file and batch insert rows with:
         (message_id, channel, sender_id, message_date,
          message_text, raw JSON payload).
      5. Commit and close the database connection.

    Args:
        date_str (str): Date partition folder in 'YYYY-MM-DD' format.
                        Defaults to current UTC date.
    """
    create_raw_schema_and_tables()

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("TRUNCATE raw.messages CASCADE;")

    date_str = date_str or datetime.utcnow().strftime("%Y-%m-%d")
    folder = Path("data/raw/telegram_messages") / date_str

    total = 0
    for file_path in folder.glob("*.json"):
        channel = file_path.stem
        data = json.loads(file_path.read_text(encoding="utf-8"))
        rows = [
            (
                rec["id"],
                channel,
                rec.get("sender_id"),
                rec.get("date"),
                rec.get("message"),
                json.dumps(rec)
            )
            for rec in data
        ]
        sql = (
            """
            INSERT INTO raw.messages
              (message_id, channel, sender_id, message_date, message_text, raw)
            VALUES %s
            """
        )
        execute_values(cur, sql, rows)
        total += len(rows)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {total} messages into raw.messages for date {date_str}.")


def load_images(date_str: str = None):
    """
    Load image metadata into the `raw.images` table.

    Steps:
      1. Ensure raw schema and tables exist.
      2. Connect to the database and truncate `raw.images`.
      3. Determine valid message IDs from `raw.messages`.
      4. Iterate over image files in
         `data/raw/telegram_images/YYYY-MM-DD/<channel>/*.jpg`.
      5. For each valid image (with message_id in DB), insert a row with:
         (image_id, channel, message_id, file_path).
      6. Commit and close the database connection.

    Args:
        date_str (str): Date partition folder in 'YYYY-MM-DD' format.
                        Defaults to current UTC date.
    """
    create_raw_schema_and_tables()

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("TRUNCATE raw.images;")

    date_str = date_str or datetime.utcnow().strftime("%Y-%m-%d")
    base = Path("data/raw/telegram_images") / date_str

    # Fetch valid message IDs
    cur.execute("SELECT message_id FROM raw.messages")
    valid_ids = {row[0] for row in cur.fetchall()}

    total = 0
    skipped = 0
    for channel_dir in base.iterdir():
        if not channel_dir.is_dir():
            continue
        channel = channel_dir.name
        for img_file in channel_dir.glob("*.jpg"):
            image_id = img_file.stem
            try:
                msg_id = int(image_id)
            except ValueError:
                msg_id = None

            if msg_id not in valid_ids:
                skipped += 1
                continue

            rows = [(image_id, channel, msg_id, str(img_file))]
            sql = (
                """
                INSERT INTO raw.images
                  (image_id, channel, message_id, file_path)
                VALUES %s
                """
            )
            execute_values(cur, sql, rows)
            total += 1

    conn.commit()
    cur.close()
    conn.close()
    print(
        f"Loaded {total} images into raw.images for date {date_str}. "
        f"Skipped {skipped} unmatched images."
    )


if __name__ == "__main__":
    load_messages()
    load_images()


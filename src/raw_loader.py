# src/loader/raw_loader.py
import os
import json
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

from dotenv import load_dotenv
from loader_schema import create_raw_schema_and_tables

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def load_messages(date_str: str = None):
    """
    Load JSON files under data/raw/telegram_messages/YYYY-MM-DD/*.json
    into raw.messages (upserting on message_id). Truncates table first for clean reload.
    """
    create_raw_schema_and_tables()

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("TRUNCATE raw.messages CASCADE;")

    date_str = date_str or datetime.utcnow().strftime("%Y-%m-%d")
    folder = Path(r"C:\Users\ABC\Desktop\10Acadamy\week_7\Shipping-a-Data-Product\data\raw\telegram_messages") / date_str

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
        sql = """
        INSERT INTO raw.messages
          (message_id, channel, sender_id, message_date, message_text, raw)
        VALUES %s
        """
        execute_values(cur, sql, rows)
        total += len(rows)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {total} messages into raw.messages for date {date_str}.")


def load_images(date_str: str = None):
    """
    Load image metadata into raw.images from data/raw/telegram_images/YYYY-MM-DD/**.
    Truncates table first for clean reload and associates message_id.
    """
    create_raw_schema_and_tables()

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("TRUNCATE raw.images;")

    date_str = date_str or datetime.utcnow().strftime("%Y-%m-%d")
    base = Path(r"C:\Users\ABC\Desktop\10Acadamy\week_7\Shipping-a-Data-Product\data\raw\telegram_images") / date_str

    # Fetch valid message_ids
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
            sql = """
            INSERT INTO raw.images
              (image_id, channel, message_id, file_path)
            VALUES %s
            """
            execute_values(cur, sql, rows)
            total += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"Loaded {total} images into raw.images for date {date_str}. Skipped {skipped} unmatched images.")


if __name__ == "__main__":
    load_messages()
    load_images()

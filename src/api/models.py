"""
Module: scrapper.py (Task 1 Data Scraper)

This module handles scraping of Telegram channels for both text messages and
photo media, writing raw JSON and image files into the local data lake.

Key Functions:
  - scrape_messages(limit: int = 100):
      Connects to Telegram, fetches the latest text messages from channels
      defined in `TELEGRAM_TEXT_CHANNELS`, and saves them as JSON.

  - scrape_images(limit: int = 50):
      Connects to Telegram, fetches photo media from channels defined in
      `TELEGRAM_IMAGE_CHANNELS`, and downloads images to disk.

  - main():
      CLI entrypoint that runs both text and image scraping in sequence.

Environment Variables (loaded from `.env`):
  - TELEGRAM_API_ID
  - TELEGRAM_API_HASH
  - TELEGRAM_TEXT_CHANNELS (comma-separated list)
  - TELEGRAM_IMAGE_CHANNELS (comma-separated list)

Data Lake Structure:
```
data/raw/
├── telegram_messages/YYYY-MM-DD/<channel>.json
└── telegram_images/YYYY-MM-DD/<channel>/<message_id>.jpg
```
Logging:
  Uses Python's `logging` module to output INFO and ERROR logs.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path

from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_ID      = int(os.getenv("TELEGRAM_API_ID"))
API_HASH    = os.getenv("TELEGRAM_API_HASH")
TEXT_CHANS  = os.getenv("TELEGRAM_TEXT_CHANNELS", "").split(",")
IMAGE_CHANS = os.getenv("TELEGRAM_IMAGE_CHANNELS", "").split(",")

# Base paths for raw data lake
BASE_RAW = Path("data/raw")
TXT_BASE = BASE_RAW / "telegram_messages"
IMG_BASE = BASE_RAW / "telegram_images"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)


def _today_str() -> str:
    """Return current UTC date as YYYY-MM-DD."""
    return datetime.utcnow().strftime("%Y-%m-%d")


def _ensure_dir(path: Path):
    """Create a directory (and parents) if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def scrape_messages(limit: int = 100):
    """
    Task 1.1: Scrape text messages and store as JSON files.

    1. Create date-partitioned output folder under `data/raw/telegram_messages/YYYY-MM-DD`.
    2. Connect to Telegram using Telethon.
    3. For each channel in TEXT_CHANS, fetch up to `limit` messages.
    4. Serialize each message to dict and write to `<channel>.json`.
    5. Log success or errors per channel.
    """
    date = _today_str()
    out_dir = TXT_BASE / date
    _ensure_dir(out_dir)

    with TelegramClient("session", API_ID, API_HASH) as client:
        logging.info("Connected to Telegram for text scraping")
        for chan in TEXT_CHANS:
            try:
                logging.info(f"Fetching up to {limit} messages from {chan}")
                msgs = client.get_messages(chan, limit=limit)
                records = [m.to_dict() for m in msgs]
                dest = out_dir / f"{chan}.json"
                with open(dest, "w", encoding="utf-8") as f:
                    json.dump(records, f, ensure_ascii=False, default=str, indent=2)
                logging.info(f"Saved {len(records)} messages to {dest}")
            except Exception as e:
                logging.error(f"Error scraping {chan}: {e}", exc_info=True)


def scrape_images(limit: int = 50):
    """
    Task 1.2: Download photo media for object detection enrichment.

    1. Create date-partitioned image folder under `data/raw/telegram_images/YYYY-MM-DD/<channel>/`.
    2. Connect to Telegram using Telethon.
    3. For each channel in IMAGE_CHANS, fetch up to `limit` messages.
    4. If a message contains photo media, download it as `<message_id>.jpg`.
    5. Log number of images downloaded or errors per channel.
    """
    date = _today_str()
    out_base = IMG_BASE / date
    _ensure_dir(out_base)

    with TelegramClient("session", API_ID, API_HASH) as client:
        logging.info("Connected to Telegram for image scraping")
        for chan in IMAGE_CHANS:
            try:
                channel_folder = out_base / chan
                _ensure_dir(channel_folder)
                logging.info(f"Downloading up to {limit} images from {chan}")
                count = 0
                for msg in client.get_messages(chan, limit=limit):
                    if isinstance(msg.media, MessageMediaPhoto):
                        path = channel_folder / f"{msg.id}.jpg"
                        client.download_media(msg, file=str(path))
                        count += 1
                logging.info(f"Downloaded {count} images to {channel_folder}")
            except Exception as e:
                logging.error(f"Error downloading images from {chan}: {e}", exc_info=True)


def main():
    """CLI entrypoint that runs both text and image scraping."""
    scrape_messages(limit=100)
    scrape_images(limit=50)


if __name__ == "__main__":
    main()

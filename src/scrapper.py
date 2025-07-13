# scraper.py
# src/scrapper.py

import os
import json
from datetime import datetime
from pathlib import Path

from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv

# Load once at import-time
load_dotenv()
API_ID   = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")

# src/scraper.py

import os
import json
import logging
from datetime import datetime
from pathlib import Path

from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv

# ————— Configuration from .env —————
load_dotenv()  
API_ID       = int(os.getenv("TELEGRAM_API_ID"))
API_HASH     = os.getenv("TELEGRAM_API_HASH")
TEXT_CHANS   = os.getenv("TELEGRAM_TEXT_CHANNELS", "").split(",")
IMAGE_CHANS  = os.getenv("TELEGRAM_IMAGE_CHANNELS", "").split(",")

# Base paths for raw data
BASE_RAW     = Path("data/raw")
TXT_BASE     = BASE_RAW / "telegram_messages"
IMG_BASE     = BASE_RAW / "telegram_images"

# ————— Logging setup —————
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def _today_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")

def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def scrape_messages(limit: int = 100):
    """Task 1.1: Scrape text messages and store as JSON."""
    date = _today_str()
    out_dir = TXT_BASE / date
    _ensure_dir(out_dir)

    with TelegramClient("session", API_ID, API_HASH) as client:
        logging.info("Connected to Telegram for text scraping")
        for chan in TEXT_CHANS:
            try:
                logging.info(f"Fetching up to {limit} messages from {chan}")
                msgs = client.get_messages(chan, limit=limit)  # :contentReference[oaicite:0]{index=0}
                records = [m.to_dict() for m in msgs]
                dest = out_dir / f"{chan}.json"
                with open(dest, "w", encoding="utf-8") as f:
                    json.dump(records, f, ensure_ascii=False, default=str, indent=2)
                logging.info(f"Saved {len(records)} messages to {dest}")
            except Exception as e:
                logging.error(f"Error scraping {chan}: {e}", exc_info=True)

def scrape_images(limit: int = 50):
    """Task 1.2: Download photo media for object detection enrichment."""
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
                for msg in client.get_messages(chan, limit=limit):  # :contentReference[oaicite:1]{index=1}
                    if isinstance(msg.media, MessageMediaPhoto):
                        path = channel_folder / f"{msg.id}.jpg"
                        client.download_media(msg, file=str(path))
                        count += 1
                logging.info(f"Downloaded {count} images to {channel_folder}")
            except Exception as e:
                logging.error(f"Error downloading images from {chan}: {e}", exc_info=True)

def main():
    """CLI entrypoint: run both text and image scraping."""
    scrape_messages(limit=100)
    scrape_images(limit=50)

if __name__ == "__main__":
    main()

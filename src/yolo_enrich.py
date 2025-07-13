# src/enrichment/yolo_enrich.py

import os
from pathlib import Path
from ultralytics import YOLO
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# ─ Load config
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
RAW_IMG_ROOT = Path("data/raw/telegram_images")

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)

def enrich_images(date_str: str = None, model_name: str = "yolov8n.pt"):
    """
    Detect objects in each image under data/raw/telegram_images/YYYY-MM-DD/**.jpg
    and insert (message_id, object_class, confidence_score) into analytics.fct_image_detections.
    """
    from datetime import datetime, timezone
    date_str = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    img_dir = RAW_IMG_ROOT / date_str

    # Load YOLOv8 nano model
    model = YOLO(model_name)

    # Collect detections
    records = []
    for channel_dir in img_dir.iterdir():
        if not channel_dir.is_dir():
            continue
        for img_path in channel_dir.glob("*.jpg"):
            try:
                message_id = int(img_path.stem)
            except ValueError:
                # skip files not named as an integer
                continue

            # run detection
            results = model(img_path)
            for res in results:
                for box in res.boxes.data.cpu().numpy():
                    conf = float(box[4])
                    cls  = int(box[5])
                    class_name = model.names[cls]
                    records.append((message_id, class_name, conf))

    # Insert into Postgres
    if records:
        conn = get_db_conn()
        cur  = conn.cursor()
        sql = """
          INSERT INTO analytics.fct_image_detections
            (message_id, object_class, confidence_score)
          VALUES %s
        """
        execute_values(cur, sql, records)
        conn.commit()
        cur.close()
        conn.close()
        print(f"Inserted {len(records)} detections.")
    else:
        print("No detections found for", date_str)

if __name__ == "__main__":
    enrich_images()

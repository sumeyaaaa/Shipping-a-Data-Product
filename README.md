# Shipping a Data Product – Week 7 Challenge

## Overview & Motivation  
This project builds an end-to-end **ELT pipeline** that scrapes public Ethiopian medical Telegram channels, transforms the data, enriches it with computer vision, and serves analytics via an API. We aim to answer questions like “most mentioned medical products” or “channel posting trends” by collecting raw Telegram data into a **data lake**, loading it into a **PostgreSQL** warehouse, applying **dbt** transformations (star-schema modeling), detecting objects in images with **YOLOv8**, and exposing results through **FastAPI** endpoints. This modern stack ensures data is **reproducible, testable, and ready for analysis**, aligning with the challenge goals of delivering a robust data product.

## Tech Stack  
- **Python:** General-purpose programming language for scripting and services.  
- **Docker:** Container platform for packaging applications and dependencies into isolated, portable containers.  
- **PostgreSQL:** Advanced open-source object-relational database for warehousing our data.  
- **dbt (Data Build Tool):** SQL-based transformation framework (in-warehouse ELT), used for building staging tables and a dimensional star schema.  
- **FastAPI:** Modern, high-performance Python web framework for building RESTful APIs.  
- **YOLOv8 (Ultralytics):** State-of-the-art object detection model (“You Only Look Once” v8) that is fast and accurate for image analysis.  
- **Dagster:** A modern data orchestrator for defining, scheduling, and monitoring complex pipelines.  

## Project Structure  
```
.
├── .dbt/                # dbt configuration (profiles.yml, etc.)
├── data/               
│   ├── raw/             # Raw data lake (JSON outputs)
│   │   ├── telegram_messages/
│   │   └── telegram_images/
│   └── clean/           # (For future cleaned data)
├── notebooks/           # Jupyter notebooks for development tasks
│   ├── task_1/scraping.ipynb
│   ├── task_2/load_and_dbt.ipynb
│   └── task_3/yolo_enrich.ipynb
├── models/              # dbt models (SQL files)
│   ├── staging/         # Staging tables
│   └── marts/           # Dimensional models (facts, dims)
├── src/                 # Source code
│   ├── api/             # FastAPI application code
│   ├── scrapper.py      # Telegram scraping script (Task 1)
│   ├── raw_loader.py    # Loads raw JSON into Postgres (Task 2)
│   └── yolo_enrich.py   # YOLOv8 image processing (Task 3)
├── Dockerfile           # Docker image for the application
├── docker-compose.yml   # Compose for app + Postgres
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (secrets, not in Git)
└── README.md            # Project documentation (this file)
```

## Tasks Completed  

- **Task 0 – Project Setup & Environment:**  
  - Initialized Git repo, created `requirements.txt`, `.env`, `Dockerfile`, and `docker-compose.yml`.  
- **Task 1 – Data Scraping & Collection:**  
  - Scraped Telegram messages and images; stored raw JSON and images under `data/raw/`.  
- **Task 2 – Loading & dbt Transformations:**  
  - Loaded raw data into PostgreSQL; built staging and mart models with dbt; added tests and documentation.  
- **Task 3 – Image Enrichment with YOLOv8:**  
  - Ran YOLOv8 inference on scraped images; inserted detections into `analytics.fct_image_detections`.  

- **Task 4 – Analytical API (FastAPI):**  
  - Build endpoints to answer business questions (top products, channel activity, posting trends).  
- **Task 5 – Pipeline Orchestration (Dagster):**  
  - Orchestrate scraping, loading, transformations, and enrichment on a schedule via Dagster.  

## Setup & Usage  

1. **Clone & configure**:  
   ```bash
   git clone <repo-url>
   cd project-root
   cp .env.example .env
   # fill in your TELEGRAM_API_ID, etc.
   ```
2. **Docker (recommended)**:  
   ```bash
   docker-compose up -d
   ```
3. **Without Docker**:  
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Run Scraper**:  
   ```bash
   python src/scrapper.py
   ```
5. **dbt**:  
   ```bash
   cd dbt_project
   dbt deps && dbt run && dbt test
   ```
6. **YOLO Enrichment**:  
   ```bash
   python src/yolo_enrich.py
   ```
7. **Start API**:  
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```
8. **Dagster (future)**:  
   ```bash
   pip install dagster dagster-webserver
   dagster dev

## Tech Stack

- **Python**: Core scripting language for ETL, model inference, and API  
- **Telethon**: Telegram API client for scraping messages & media  
- **psycopg2**: PostgreSQL driver for schema setup and raw data loading  
- **SQLAlchemy**: ORM & session management for the FastAPI application  
- **PostgreSQL**: Data warehouse with `raw` and `analytics` schemas  
- **dbt (Data Build Tool)**: In-warehouse ELT for staging and dimensional (star-schema) modeling, testing, and documentation  
- **Ultralytics YOLOv8**: State-of-the-art object-detection model for image enrichment  
- **FastAPI**: High-performance Python web framework for REST endpoints  
- **Uvicorn**: ASGI server for serving the FastAPI app  
- **Dagster**: Pipeline orchestration, scheduling, and observability  
- **Docker & Docker Compose**: Containerization of services (API, dbt, Postgres, etc.)  
- **python-dotenv**: Secure management of environment variables via a `.env` file  
   ```

## Example API Requests  
```bash
curl "http://localhost:8000/api/reports/top-products?limit=5"
curl "http://localhost:8000/api/channels/lobelia4cosmetics/activity"
curl "http://localhost:8000/api/reports/posting-trends?interval=weekly"
```
--

## 📄 License

This project is open-source and available under the [Apache License](LICENSE).

## Next recommended Steps  
- Improve YOLO model accuracy with custom training data  
- Add authentication and user roles to the API  
- Deploy to a cloud environment with CI/CD
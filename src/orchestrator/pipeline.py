"""
Module: pipeline.py (Dagster Pipeline)

This module defines Dagster ops and the orchestration job for the end-to-end
workflow of the Shipping-a-Data-Product pipeline.

Components:
  - scrape_telegram_data: Op to scrape Telegram messages and images.
  - load_raw_to_postgres: Op to bulk-load raw data into Postgres schemas.
  - run_dbt_transformations: Op to execute dbt ELT models and tests.
  - run_yolo_enrichment: Op to run YOLOv8 object detection enrichment.

Job:
  - weekly_data_pipeline: A sequential job wiring the above ops to perform:
      1. Telegram data scraping
      2. Raw JSON and image ingestion
      3. dbt transformations (staging and marts)
      4. YOLO-based data enrichment

Usage:
  Include this module in the Dagster workspace configuration (workspace.yaml)
  using the `python_module: src.orchestrator.pipeline` target so that Dagit
  can discover and visualize the pipeline graph.
"""
import os
import subprocess
from dagster import job, op, get_dagster_logger

# Determine the project root for locating the dbt project\ nPROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

@op

def scrape_telegram_data():
    """
    Op: scrape_telegram_data

    Connects to Telegram and pulls text messages and images from configured
    channels. Logs progress at start and completion.
    """
    from src.scrapper import scrape_messages as fn
    get_dagster_logger().info("Starting Telegram scrape…")
    fn()
    get_dagster_logger().info("Telegram scrape complete.")

@op

def load_raw_to_postgres():
    """
    Op: load_raw_to_postgres

    Ensures raw Postgres schemas exist, then bulk loads JSON and image metadata
    into the `raw` schema tables using the raw_loader module.
    """
    from src.raw_loader import load_messages, load_images
    get_dagster_logger().info("Loading raw JSON into Postgres…")
    load_messages()
    load_images()
    get_dagster_logger().info("Raw data load complete.")

@op

def run_dbt_transformations():
    """
    Op: run_dbt_transformations

    Executes dbt commands to run all models and tests in the project's dbt
    directory, ensuring staging and mart tables are built and validated.
    """
    get_dagster_logger().info("Running dbt transformations…")
    dbt_dir = os.path.join(PROJECT_ROOT, "dbt")
    subprocess.run([
        "dbt", "run", "--profiles-dir", dbt_dir, "--project-dir", dbt_dir
    ], check=True)
    subprocess.run([
        "dbt", "test", "--profiles-dir", dbt_dir, "--project-dir", dbt_dir
    ], check=True)
    get_dagster_logger().info("dbt transformations complete.")

@op

def run_yolo_enrichment():
    """
    Op: run_yolo_enrichment

    Runs the YOLOv8 enrichment script that detects objects in scraped images
    and writes results into the analytics schema table.
    """
    from src.yolo_enrich import run_yolo_enrichment as fn
    get_dagster_logger().info("Starting YOLO enrichment…")
    fn()
    get_dagster_logger().info("YOLO enrichment complete.")

@job

def weekly_data_pipeline():
    """
    Job: weekly_data_pipeline

    Orchestrates the full pipeline by sequentially invoking:
      1. scrape_telegram_data
      2. load_raw_to_postgres
      3. run_dbt_transformations
      4. run_yolo_enrichment

    Each step runs only after the previous completes successfully.
    """
    # Alias ops for clarity in Dagster UI
    scrape_step = scrape_telegram_data.alias("scrape_step")
    load_step = load_raw_to_postgres.alias("load_step")
    dbt_step = run_dbt_transformations.alias("dbt_step")
    yolo_step = run_yolo_enrichment.alias("yolo_step")

    # Invoke in sequence
    scrape_step()
    load_step()
    dbt_step()
    yolo_step()

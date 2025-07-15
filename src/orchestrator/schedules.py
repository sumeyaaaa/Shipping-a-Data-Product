"""
Module: schedules.py (Dagster Schedules)

This module defines scheduled jobs for orchestrating the weekly_data_pipeline
at the specified cron schedule.

Schedules:
  - daily_schedule:
      Triggers the `weekly_data_pipeline` job every day at 03:00 Africa/Addis_Ababa time.

Usage:
  Include this file in the Dagster workspace configuration (workspace.yaml) using
  the `python_module: src.orchestrator.schedules` target so that Dagit and
dagster-daemon can discover and activate the schedule.
"""
from dagster import ScheduleDefinition
from .pipeline import weekly_data_pipeline

# Schedule: run pipeline daily at 03:00 Africa/Addis_Ababa timezone
daily_schedule = ScheduleDefinition(
    job=weekly_data_pipeline,
    cron_schedule="0 3 * * *",  # every day at 03:00 server time
    execution_timezone="Africa/Addis_Ababa",
)

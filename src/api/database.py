"""
Module: db_session.py

This module initializes the SQLAlchemy engine and session factory for connecting
and interacting with the configured PostgreSQL database.

Environment Variable:
  - DATABASE_URL: Full database URL in the form
      postgresql://user:password@host:port/database

Definitions:
  - engine: A SQLAlchemy Engine instance with `pool_pre_ping=True` to ensure
    connections are healthy before use.

  - SessionLocal: A SQLAlchemy sessionmaker factory configured for manual commit
    control (autocommit=False, autoflush=False) and bound to the engine.

Usage:
  Import `SessionLocal()` to obtain a session and use it to query or modify the DB.
  Remember to close the session when done.

Example:
```python
from db_session import SessionLocal

db = SessionLocal()
try:
    # work with db
    result = db.query(MyModel).all()
finally:
    db.close()
```
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")  # e.g.: postgres://user:pass@host:port/dbname

# Create the SQLAlchemy engine with pre-ping to recycle stale connections
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a configured "SessionLocal" class
# autocommit=False: Explicitly commit transactions
# autoflush=False: Avoid automatic flush before queries
# bind=engine: Use the defined engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

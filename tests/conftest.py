import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import sqlite3
import database.connection
from database.schema import create_tables
from database.seed import seed_database
from database.migrations.add_day_close import run_migration

@pytest.fixture(autouse=True)
def db_session(monkeypatch):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    
    def mock_get_connection():
        return conn
        
    monkeypatch.setattr(database.connection, "get_connection", mock_get_connection)
    
    create_tables(conn)
    seed_database()
    run_migration()
    
    yield conn
    conn.close()

import sqlite3
import os

_db_connection = None

def get_connection():
    """
    Returns a singleton SQLite connection with WAL journal mode
    and foreign keys enabled.
    """
    global _db_connection
    if _db_connection is None:
        db_path = "smart_pos.db" # Database is stored in cwd for now
        
        _db_connection = sqlite3.connect(db_path, check_same_thread=False)
        _db_connection.row_factory = sqlite3.Row
        
        # Enable foreign key support and WAL mode
        _db_connection.execute("PRAGMA foreign_keys = ON;")
        _db_connection.execute("PRAGMA journal_mode = WAL;")
        
    return _db_connection

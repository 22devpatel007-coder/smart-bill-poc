from database.connection import get_connection

def run_migration():
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            
            # Check if day_closed column exists in invoices
            cursor.execute("PRAGMA table_info(invoices)")
            columns = [col['name'] for col in cursor.fetchall()]
            
            if 'day_closed' not in columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN day_closed INTEGER DEFAULT 0")
            
            if 'day_closed_at' not in columns:
                cursor.execute("ALTER TABLE invoices ADD COLUMN day_closed_at TEXT")
                
            # Create day_close_log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS day_close_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    close_date TEXT NOT NULL,
                    cash_total REAL DEFAULT 0,
                    upi_total REAL DEFAULT 0,
                    card_total REAL DEFAULT 0,
                    credit_total REAL DEFAULT 0,
                    grand_total REAL DEFAULT 0,
                    invoice_count INTEGER DEFAULT 0,
                    user_id INTEGER REFERENCES users(id),
                    created_at TEXT DEFAULT (datetime('now','localtime'))
                )
            ''')
            print("Migration add_day_close completed.")
    except Exception as e:
        print(f"Migration add_day_close failed: {e}")

if __name__ == '__main__':
    run_migration()

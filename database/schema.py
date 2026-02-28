SCHEMA_SQL = '''
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
 
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,   -- bcrypt hash
    full_name   TEXT NOT NULL,
    role        TEXT DEFAULT 'staff',  -- admin | staff
    is_active   INTEGER DEFAULT 1,
    created_at  TEXT DEFAULT (datetime('now','localtime'))
);
 
CREATE TABLE IF NOT EXISTS categories (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT UNIQUE NOT NULL
);
 
CREATE TABLE IF NOT EXISTS gst_rates (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,   -- '5%', '12%', '18%', 'Exempt'
    rate  REAL NOT NULL    -- 5.0, 12.0, 0.0
);
 
CREATE TABLE IF NOT EXISTS products (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    sku           TEXT UNIQUE,
    barcode       TEXT UNIQUE,
    category_id   INTEGER REFERENCES categories(id),
    gst_rate_id   INTEGER REFERENCES gst_rates(id),
    unit          TEXT DEFAULT 'pcs',  -- pcs|kg|box|ltr|ml
    cost_price    REAL NOT NULL DEFAULT 0,
    sell_price    REAL NOT NULL DEFAULT 0,
    stock         REAL NOT NULL DEFAULT 0,
    low_stock_qty REAL DEFAULT 5,
    expiry_date   TEXT,  -- NULL for non-perishables
    is_active     INTEGER DEFAULT 1,
    created_at    TEXT DEFAULT (datetime('now','localtime'))
);
 
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    phone       TEXT UNIQUE,
    email       TEXT,
    address     TEXT,
    outstanding REAL DEFAULT 0,  -- dues / udhar
    created_at  TEXT DEFAULT (datetime('now','localtime'))
);
 
CREATE TABLE IF NOT EXISTS invoices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number  TEXT UNIQUE NOT NULL,
    customer_id     INTEGER REFERENCES customers(id),
    user_id         INTEGER REFERENCES users(id),
    subtotal        REAL NOT NULL,
    discount_pct    REAL DEFAULT 0,
    discount_amt    REAL DEFAULT 0,
    cgst_amt        REAL DEFAULT 0,
    sgst_amt        REAL DEFAULT 0,
    total           REAL NOT NULL,
    payment_mode    TEXT DEFAULT 'cash',  -- cash|upi|card|credit
    payment_status  TEXT DEFAULT 'paid',  -- paid|pending
    notes           TEXT,
    created_at      TEXT DEFAULT (datetime('now','localtime'))
);
 
CREATE TABLE IF NOT EXISTS invoice_items (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id   INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    product_id   INTEGER NOT NULL REFERENCES products(id),
    product_name TEXT NOT NULL,  -- snapshot at time of sale
    qty          REAL NOT NULL,
    unit_price   REAL NOT NULL,
    discount     REAL DEFAULT 0,
    gst_rate     REAL DEFAULT 0,
    gst_amt      REAL DEFAULT 0,
    line_total   REAL NOT NULL
);
 
CREATE TABLE IF NOT EXISTS inventory_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES products(id),
    change_qty  REAL NOT NULL,  -- positive=in, negative=out
    reason      TEXT,           -- sale|purchase|adjustment|damage
    invoice_id  INTEGER REFERENCES invoices(id),
    user_id     INTEGER REFERENCES users(id),
    created_at  TEXT DEFAULT (datetime('now','localtime'))
);
 
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS dues_payments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    amount      REAL NOT NULL,
    user_id     INTEGER REFERENCES users(id),
    notes       TEXT,
    created_at  TEXT DEFAULT (datetime('now','localtime'))
);
'''

def create_tables(connection):
    """Execute the schema to create tables."""
    with connection:
        connection.executescript(SCHEMA_SQL)

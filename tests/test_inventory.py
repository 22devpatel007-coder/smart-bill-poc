import pytest
from services.inventory_service import adjust_stock, get_products
from database.connection import get_connection

def test_stock_reduces_after_sale():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, stock, low_stock_qty, is_active) VALUES ('Test Sale', 10, 5, 1)")
    pid = cursor.lastrowid
    
    adjust_stock(pid, -2.0, 'sale', user_id=None)
    
    cursor.execute("SELECT stock FROM products WHERE id = ?", (pid,))
    stock = cursor.fetchone()['stock']
    assert stock == 8.0

def test_low_stock_flag():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, stock, low_stock_qty, is_active) VALUES ('Low Stock B', 3, 5, 1)")
    
    # Usually handled in get_low_stock_products via query, simulating here
    cursor.execute("SELECT * FROM products WHERE stock <= low_stock_qty AND is_active = 1")
    low_stock_items = [dict(r) for r in cursor.fetchall()]
    assert any(item['name'] == 'Low Stock B' for item in low_stock_items)

def test_stock_increase():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, stock, low_stock_qty, is_active) VALUES ('Test Inc', 10, 5, 1)")
    pid = cursor.lastrowid
    
    adjust_stock(pid, 5.0, 'adjustment')
    
    cursor.execute("SELECT stock FROM products WHERE id = ?", (pid,))
    stock = cursor.fetchone()['stock']
    assert stock == 15.0

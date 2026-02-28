from database.connection import get_connection

def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE is_active = 1")
    return cursor.fetchall()

def adjust_stock(product_id: int, change_qty: float, reason: str, user_id: int = None):
    conn = get_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (change_qty, product_id))
        cursor.execute("INSERT INTO inventory_logs (product_id, change_qty, reason, user_id) VALUES (?, ?, ?, ?)", 
                       (product_id, change_qty, reason, user_id))

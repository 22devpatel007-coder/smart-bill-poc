from database.connection import get_connection
import csv

def get_daily_summary(date_str: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(id) as bills, SUM(total) as sales, SUM(cgst_amt + sgst_amt) as tax
        FROM invoices WHERE date(created_at) = date(?)
    """, (date_str,))
    row = cursor.fetchone()
    return {
        "bills": row['bills'] or 0,
        "sales": row['sales'] or 0.0,
        "tax": row['tax'] or 0.0
    }

def get_day_summary(date_str: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(id) as invoice_count, SUM(total) as grand_total,
               SUM(CASE WHEN payment_mode='cash' THEN total ELSE 0 END) as cash_total,
               SUM(CASE WHEN payment_mode='upi' THEN total ELSE 0 END) as upi_total,
               SUM(CASE WHEN payment_mode='card' THEN total ELSE 0 END) as card_total,
               SUM(CASE WHEN payment_mode='credit' THEN total ELSE 0 END) as credit_total,
               SUM(cgst_amt) as cgst_total, SUM(sgst_amt) as sgst_total,
               MAX(day_closed) as already_closed
        FROM invoices WHERE date(created_at) = date(?)
    """, (date_str,))
    row = cursor.fetchone()
    
    inv_count = row['invoice_count'] or 0
    grand = row['grand_total'] or 0.0
    
    return {
        "cash_total": row['cash_total'] or 0.0,
        "upi_total": row['upi_total'] or 0.0,
        "card_total": row['card_total'] or 0.0,
        "credit_total": row['credit_total'] or 0.0,
        "grand_total": grand,
        "invoice_count": inv_count,
        "avg_bill": grand / inv_count if inv_count > 0 else 0.0,
        "cgst_total": row['cgst_total'] or 0.0,
        "sgst_total": row['sgst_total'] or 0.0,
        "already_closed": bool(row['already_closed'])
    }

def close_day(date_str: str, user_id: int):
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            
            # Get summary
            summary = get_day_summary(date_str)
            if summary['already_closed']:
                raise ValueError("Day is already closed.")
                
            now = __import__('datetime').datetime.now().isoformat()
            
            # Lock invoices
            cursor.execute("""
                UPDATE invoices 
                SET day_closed = 1, day_closed_at = ? 
                WHERE date(created_at) = date(?)
            """, (now, date_str))
            
            # Create log
            cursor.execute("""
                INSERT INTO day_close_log 
                (close_date, cash_total, upi_total, card_total, credit_total, grand_total, invoice_count, user_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (date_str, summary['cash_total'], summary['upi_total'], summary['card_total'], summary['credit_total'],
                  summary['grand_total'], summary['invoice_count'], user_id, now))
    except Exception as e:
        raise ValueError(f"Failed to close day: {e}")

def get_product_sales(start_date: str, end_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.name, SUM(ii.qty) as qty_sold, SUM(ii.line_total) as revenue
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.id
        JOIN products p ON ii.product_id = p.id
        WHERE date(i.created_at) BETWEEN date(?) AND date(?)
        GROUP BY p.id
        ORDER BY qty_sold DESC
    """, (start_date, end_date))
    return [dict(row) for row in cursor.fetchall()]

def get_gst_summary(start_date: str, end_date: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ii.gst_rate, 
               SUM(ii.line_total - ii.gst_amt) as taxable_value, 
               SUM(ii.gst_amt / 2) as cgst, 
               SUM(ii.gst_amt / 2) as sgst, 
               SUM(ii.gst_amt) as total_tax
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.id
        WHERE date(i.created_at) BETWEEN date(?) AND date(?)
        GROUP BY ii.gst_rate
    """, (start_date, end_date))
    return [dict(row) for row in cursor.fetchall()]
    
def export_csv(data: list, filepath: str):
    if not data: return
    keys = data[0].keys()
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

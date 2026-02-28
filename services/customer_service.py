import sqlite3
from typing import List, Optional, Dict
from models.customer import Customer
from database.connection import get_connection
from dataclasses import dataclass

@dataclass
class InvoiceSummary:
    id: int
    invoice_number: str
    total: float
    payment_mode: str
    created_at: str

def get_all_customers(search: Optional[str] = None) -> List[Customer]:
    conn = get_connection()
    cursor = conn.cursor()
    
    if search:
        query = """
            SELECT * FROM customers 
            WHERE name LIKE ? OR phone LIKE ? 
            ORDER BY name ASC
        """
        like_search = f"%{search}%"
        cursor.execute(query, (like_search, like_search))
    else:
        query = "SELECT * FROM customers ORDER BY name ASC"
        cursor.execute(query)
        
    rows = cursor.fetchall()
    return [Customer(**dict(row)) for row in rows]

def add_customer(name: str, phone: str, email: str = '', address: str = '') -> Customer:
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            
            # Check for unique phone
            if phone:
                cursor.execute("SELECT id FROM customers WHERE phone = ?", (phone,))
                if cursor.fetchone():
                    raise ValueError(f"Customer with phone '{phone}' already exists.")
            
            cursor.execute("""
                INSERT INTO customers (name, phone, email, address)
                VALUES (?, ?, ?, ?)
            """, (name, phone, email, address))
            
            customer_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            return Customer(**dict(row))
    except sqlite3.IntegrityError as e:
        raise ValueError(f"Database error: {str(e)}")

def get_customer_invoices(customer_id: int) -> List[InvoiceSummary]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, invoice_number, total, payment_mode, created_at 
        FROM invoices 
        WHERE customer_id = ? 
        ORDER BY created_at DESC 
        LIMIT 10
    """, (customer_id,))
    rows = cursor.fetchall()
    return [InvoiceSummary(**dict(row)) for row in rows]

def get_customer_dues(customer_id: int) -> float:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT outstanding FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    if row:
        return float(row['outstanding'] or 0.0)
    return 0.0

def settle_dues(customer_id: int, amount: float, user_id: int) -> None:
    if amount <= 0:
        raise ValueError("Amount to settle must be positive")
        
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            
            # Double check current outstanding
            cursor.execute("SELECT outstanding FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Customer not found")
                
            current_outstanding = float(row['outstanding'] or 0.0)
            if amount > current_outstanding:
                raise ValueError(f"Cannot settle more than outstanding amount: {current_outstanding}")
            
            # Reduce outstanding
            cursor.execute("""
                UPDATE customers 
                SET outstanding = outstanding - ? 
                WHERE id = ?
            """, (amount, customer_id))
            
            # Create dues_payment log
            cursor.execute("""
                INSERT INTO dues_payments (customer_id, amount, user_id, notes)
                VALUES (?, ?, ?, ?)
            """, (customer_id, amount, user_id, f"Settled {amount} dues"))
    except Exception as e:
        raise ValueError(f"Failed to settle dues: {str(e)}")

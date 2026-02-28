import re
from PySide6.QtWidgets import QApplication
from database.connection import get_connection

def is_barcode(text):
    """
    Returns True if text is exactly 8-13 digits only.
    Matches EAN-8, UPCA (12), EAN-13, etc.
    """
    return bool(re.match(r'^\d{8,13}$', text))

class BarcodeHandler:
    def __init__(self):
        pass
        
    def handle_search_input(self, text, on_product_found, on_not_found):
        """
        If text is a barcode, look it up in DB.
        If found, calls on_product_found(product_dict).
        If not found, calls on_not_found(text).
        """
        text = text.strip()
        if not is_barcode(text):
            return False # Not a barcode, ignore
            
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products WHERE barcode = ? AND is_active = 1", (text,))
        row = cursor.fetchone()
        
        if row:
            QApplication.beep()
            on_product_found(dict(row))
        else:
            on_not_found(text)
            
        return True


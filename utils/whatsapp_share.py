import urllib.parse
import webbrowser
from PySide6.QtWidgets import QInputDialog, QMessageBox

def format_receipt_text(invoice_data):
    """
    Format receipt as plain text for WhatsApp.
    invoice_data should be a dict containing:
    shop_name, invoice_number, date, items (list of dicts), grand_total, payment_mode
    """
    shop_name = invoice_data.get('shop_name', 'Smart POS')
    inv_num = invoice_data.get('invoice_number', '')
    date = invoice_data.get('date', '')
    
    lines = [
        f"*{shop_name}*",
        f"Invoice: {inv_num}",
        f"Date: {date}",
        "-" * 20
    ]
    
    for item in invoice_data.get('items', []):
        name = item.get('name', '')[:15] # Truncate long names
        qty = item.get('qty', 1)
        total = item.get('total', 0)
        lines.append(f"{qty}x {name} - Rs {total:.2f}")
        
    lines.append("-" * 20)
    lines.append(f"*Total: Rs {invoice_data.get('grand_total', 0):.2f}*")
    lines.append(f"Paid via: {invoice_data.get('payment_mode', 'cash').upper()}")
    lines.append("Thank you for your visit!")
    
    return "\n".join(lines)

def open_whatsapp(phone_number, invoice_data, parent_widget=None):
    if not phone_number:
        # Ask for phone number
        phone, ok = QInputDialog.getText(parent_widget, "WhatsApp Number", 
                                        "Enter WhatsApp number\n(10 digits, no +91 needed):")
        if ok and phone:
            phone_number = phone.strip()
        else:
            return False # Cancelled
            
    # Clean phone number
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    if len(clean_phone) == 10:
        clean_phone = "91" + clean_phone
        
    text = format_receipt_text(invoice_data)
    encoded_text = urllib.parse.quote(text)
    
    url = f"https://wa.me/{clean_phone}?text={encoded_text}"
    webbrowser.open(url)
    return True

def open_whatsapp_pdf(invoice_data, parent_widget=None):
    from services.printer_service import print_to_pdf
    try:
        pdf_path = print_to_pdf(invoice_data)
        QMessageBox.information(parent_widget, "PDF Generated", 
            f"PDF generated at:\n{pdf_path}\n\nOpening WhatsApp Web to share it manually.")
        webbrowser.open("https://web.whatsapp.com/")
        return True
    except Exception as e:
        if parent_widget:
            QMessageBox.warning(parent_widget, "Error", f"Failed to open WhatsApp PDF: {e}")
        return False

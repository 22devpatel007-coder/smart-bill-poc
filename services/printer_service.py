# services/printer_service.py
# Production-ready thermal receipt printer for 58mm and 80mm paper

import qrcode, io, os, textwrap
from datetime import datetime
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdf_canvas
from database.connection import get_connection

try:
    from escpos.printer import Usb, Serial, Network
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False


# ── Settings helpers ─────────────────────────────────────────────────────
def get_setting(key, default=''):
    conn = get_connection()
    row = conn.execute('SELECT value FROM settings WHERE key=?',[key]).fetchone()
    return row[0] if row else default


def get_paper_width():
    width = get_setting('paper_width', '80')
    return 48 if width == '80' else 32  # characters per line


# ── Text alignment helpers ────────────────────────────────────────────────
def center(text, width):
    return text.center(width)

def left_right(left, right, width):
    space = width - len(left) - len(right)
    if space < 1: space = 1
    return left + ' ' * space + right

def divider(char='-', width=48):
    return char * width

def item_line(name, qty, rate, total, width=48):
    # Truncate name if too long
    max_name = width - 18
    if len(name) > max_name:
        name = name[:max_name-2] + '..'
    qty_str   = f'{qty:.0f}' if qty == int(qty) else f'{qty:.2f}'
    rate_str  = f'{rate:.2f}'
    total_str = f'{total:.2f}'
    # Format: NAME(left) QTY(5) RATE(7) TOTAL(7)
    right_part = f'{qty_str:>4} {rate_str:>7} {total_str:>7}'
    name_width = width - len(right_part) - 1
    return f'{name:<{name_width}} {right_part}'


# ── QR Code generator ────────────────────────────────────────────────────
def make_upi_qr(upi_id, shop_name, amount):
    upi_string = f'upi://pay?pa={upi_id}&pn={shop_name}&am={amount:.2f}&cu=INR'
    qr = qrcode.QRCode(version=2, box_size=4, border=1)
    qr.add_data(upi_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img = img.convert('RGB')
    img = img.resize((128, 128), Image.LANCZOS)
    return img


# ── Build receipt lines ───────────────────────────────────────────────────
def build_receipt_lines(invoice_data):
    W = get_paper_width()
    shop_name    = get_setting('shop_name',    'MY SHOP')
    shop_address = get_setting('shop_address', '')
    shop_phone   = get_setting('shop_phone',   '')
    gst_number   = get_setting('gst_number',   '')
    footer_msg   = get_setting('receipt_footer','Thank you! Visit Again.')
    upi_id       = get_setting('upi_id',       '')

    lines = []
    D = divider('-', W)
    E = divider('=', W)

    # HEADER
    lines.append(('center_bold', shop_name.upper()))
    if shop_address:
        for addr_line in textwrap.wrap(shop_address, W-2):
            lines.append(('center', addr_line))
    if shop_phone or gst_number:
        ph_gst = f'Ph:{shop_phone}  GST:{gst_number}' if gst_number else f'Ph:{shop_phone}'
        lines.append(('center_small', ph_gst))
    lines.append(('divider', D))

    # INVOICE META
    inv_no = invoice_data.get('invoice_number', 'N/A')
    inv_date = invoice_data.get('created_at', datetime.now().strftime('%d/%m/%Y %H:%M'))
    if isinstance(inv_date, str) and len(inv_date) > 16:
        inv_date = inv_date[:16]
    cashier  = invoice_data.get('cashier_name', 'Staff')
    customer = invoice_data.get('customer_name', 'Walk-in')
    payment  = invoice_data.get('payment_mode', 'Cash').upper()

    lines.append(('lr', f'Invoice:{inv_no}', inv_date))
    lines.append(('lr', f'Cashier:{cashier}', f'Customer:{customer}'))
    lines.append(('divider', D))

    # ITEMS HEADER
    hdr = item_line('ITEM', 'QTY', 'RATE', 'TOTAL', W)
    lines.append(('normal', hdr))
    lines.append(('divider', D))

    # ITEMS
    for item in invoice_data.get('items', []):
        name    = item.get('product_name', item.get('name', 'Item'))
        qty     = item.get('qty', 1)
        rate    = item.get('unit_price', 0)
        total   = item.get('line_total', qty * rate)
        gst_r   = item.get('gst_rate', 0)
        gst_amt = item.get('gst_amt', 0)
        disc    = item.get('discount', 0)

        lines.append(('normal', item_line(name, qty, rate, total, W)))
        if gst_r > 0 or disc > 0:
            note_parts = []
            if disc > 0: note_parts.append(f'Disc {disc:.0f}%')
            if gst_r > 0: note_parts.append(f'GST {gst_r:.0f}%: Rs{gst_amt:.2f}')
            lines.append(('small', '  ' + '  '.join(note_parts)))

    lines.append(('divider', D))

    # TOTALS
    subtotal = invoice_data.get('subtotal', 0)
    disc_amt = invoice_data.get('discount_amt', 0)
    cgst     = invoice_data.get('cgst_amt', 0)
    sgst     = invoice_data.get('sgst_amt', 0)
    total    = invoice_data.get('total', 0)
    received = invoice_data.get('amount_received', total)
    change   = received - total

    lines.append(('lr', 'Subtotal:', f'Rs{subtotal:.2f}'))
    if disc_amt > 0:
        lines.append(('lr', 'Discount:', f'-Rs{disc_amt:.2f}'))
    lines.append(('lr', 'CGST:', f'Rs{cgst:.2f}'))
    lines.append(('lr', 'SGST:', f'Rs{sgst:.2f}'))
    lines.append(('divider', E))
    lines.append(('lr_bold', 'TOTAL:', f'Rs{total:.2f}'))
    lines.append(('divider', E))

    if payment == 'CASH':
        lines.append(('lr', 'Cash Received:', f'Rs{received:.2f}'))
        lines.append(('lr', 'Change Due:', f'Rs{change:.2f}'))
    lines.append(('lr', 'Payment Mode:', payment))
    lines.append(('divider', D))

    # QR CODE PLACEHOLDER (actual image handled separately)
    if upi_id:
        lines.append(('qr_marker', upi_id))
        lines.append(('center_small', f'Scan to pay: {upi_id}'))
        lines.append(('divider', D))

    # FOOTER
    for fline in textwrap.wrap(footer_msg, W-2):
        lines.append(('center', fline))
    lines.append(('center_small', 'Powered by Smart POS'))
    lines.append(('blank', ''))
    lines.append(('blank', ''))
    lines.append(('blank', ''))

    return lines, upi_id


# ── Thermal printer (ESC/POS) ─────────────────────────────────────────────
def print_invoice(invoice_data, printer_port=None):
    if not ESCPOS_AVAILABLE:
        print_to_pdf(invoice_data, '/tmp/receipt_fallback.pdf')
        return False, 'ESC/POS not installed. PDF saved.'

    W = get_paper_width()
    upi_id    = get_setting('upi_id', '')
    shop_name = get_setting('shop_name', 'Smart POS')
    total     = invoice_data.get('total', 0)

    try:
        # Auto-detect USB printer
        printer = None
        if printer_port:
            printer = Serial(printer_port, baudrate=9600)
        else:
            # Try common Epson/Star/Generic USB IDs
            for vendor_id, product_id in [(0x04b8,0x0202),(0x0519,0x0003),(0x6868,0x0500)]:
                try:
                    printer = Usb(vendor_id, product_id)
                    break
                except Exception:
                    continue

        if printer is None:
            raise Exception('No printer found. Check USB connection.')

        lines, _ = build_receipt_lines(invoice_data)

        printer.set(align='center', font='a', bold=False, underline=0, width=1, height=1)

        for tag, content in lines:
            if tag == 'center_bold':
                printer.set(align='center', bold=True, width=2, height=2)
                printer.textln(content)
                printer.set(align='center', bold=False, width=1, height=1)
            elif tag == 'center':
                printer.set(align='center'); printer.textln(content)
            elif tag == 'center_small':
                printer.set(align='center'); printer.textln(content)
            elif tag == 'lr':
                left, right = content if isinstance(content,tuple) else (content,'')
                printer.set(align='left'); printer.textln(left_right(left, right, W))
            elif tag == 'lr_bold':
                left, right = content if isinstance(content,tuple) else (content,'')
                printer.set(align='left', bold=True, width=1, height=2)
                printer.textln(left_right(left, right, W))
                printer.set(bold=False, width=1, height=1)
            elif tag == 'normal':
                printer.set(align='left'); printer.textln(content)
            elif tag == 'small':
                printer.set(align='left'); printer.textln(content)
            elif tag == 'divider':
                printer.set(align='left'); printer.textln(content)
            elif tag == 'blank':
                printer.textln('')
            elif tag == 'qr_marker' and upi_id:
                try:
                    qr_img = make_upi_qr(upi_id, shop_name, total)
                    printer.set(align='center')
                    printer.image(qr_img, impl='bitImageRaster')
                except Exception as e:
                    printer.textln(f'[QR: {upi_id}]')

        printer.cut()
        printer.close()
        return True, 'Printed successfully'

    except Exception as e:
        # Fallback to PDF
        pdf_path = f'receipt_{invoice_data.get("invoice_number","unknown")}.pdf'
        print_to_pdf(invoice_data, pdf_path)
        return False, f'Printer error: {e}. PDF saved to {pdf_path}'


# ── PDF fallback (for WhatsApp sharing) ──────────────────────────────────
def print_to_pdf(invoice_data, filepath):
    W_mm = 80 if get_setting('paper_width','80')=='80' else 58
    page_width  = W_mm * mm
    page_height = 297 * mm

    c = pdf_canvas.Canvas(filepath, pagesize=(page_width, page_height))
    y = page_height - 10*mm
    margin = 3*mm

    shop_name    = get_setting('shop_name',    'MY SHOP')
    shop_address = get_setting('shop_address', '')
    shop_phone   = get_setting('shop_phone',   '')
    gst_number   = get_setting('gst_number',   '')
    footer_msg   = get_setting('receipt_footer','Thank you!')
    upi_id       = get_setting('upi_id',       '')
    total        = invoice_data.get('total', 0)

    def draw_text(text, font='Helvetica', size=8, align='left', bold=False):
        nonlocal y
        f = 'Helvetica-Bold' if bold else font
        c.setFont(f, size)
        if align == 'center':
            c.drawCentredString(page_width/2, y, text)
        else:
            c.drawString(margin, y, text)
        y -= (size + 2)

    def draw_divider(char='-'):
        draw_text(char * int((page_width - 2*margin) / 4.2))

    # HEADER
    draw_text(shop_name.upper(), size=11, align='center', bold=True)
    if shop_address: draw_text(shop_address, align='center')
    if shop_phone:   draw_text(f'Ph: {shop_phone}  GST: {gst_number}', align='center')
    draw_divider()

    # META
    inv_no   = invoice_data.get('invoice_number','N/A')
    inv_date = str(invoice_data.get('created_at',''))[:16]
    cashier  = invoice_data.get('cashier_name','Staff')
    draw_text(f'Invoice: {inv_no}   Date: {inv_date}')
    draw_text(f'Cashier: {cashier}')
    draw_divider()

    # ITEMS
    draw_text('ITEM                    QTY   RATE   TOTAL', bold=True)
    draw_divider()
    for item in invoice_data.get('items',[]):
        name    = item.get('product_name', item.get('name','Item'))[:22]
        qty     = item.get('qty',1)
        rate    = item.get('unit_price',0)
        itotal  = item.get('line_total', qty*rate)
        gst_r   = item.get('gst_rate',0)
        gst_amt = item.get('gst_amt',0)
        draw_text(f'{name:<22} {qty:>3.0f} {rate:>7.2f} {itotal:>7.2f}')
        if gst_r > 0: draw_text(f'  GST {gst_r:.0f}%: Rs{gst_amt:.2f}')
    draw_divider()

    # TOTALS
    subtotal = invoice_data.get('subtotal',0)
    disc_amt = invoice_data.get('discount_amt',0)
    cgst     = invoice_data.get('cgst_amt',0)
    sgst     = invoice_data.get('sgst_amt',0)
    pay_mode = invoice_data.get('payment_mode','Cash').upper()
    received = invoice_data.get('amount_received', total)
    change   = received - total

    draw_text(f'Subtotal:        Rs{subtotal:>8.2f}')
    if disc_amt > 0: draw_text(f'Discount:       -Rs{disc_amt:>8.2f}')
    draw_text(f'CGST:            Rs{cgst:>8.2f}')
    draw_text(f'SGST:            Rs{sgst:>8.2f}')
    draw_divider('=')
    draw_text(f'TOTAL:           Rs{total:>8.2f}', size=10, bold=True)
    draw_divider('=')
    if pay_mode=='CASH':
        draw_text(f'Received: Rs{received:.2f}  Change: Rs{change:.2f}')
    draw_text(f'Payment: {pay_mode}')
    draw_divider()

    # QR CODE
    if upi_id:
        try:
            qr_img = make_upi_qr(upi_id, shop_name, total)
            qr_buf = io.BytesIO(); qr_img.save(qr_buf, format='PNG')
            qr_buf.seek(0)
            from reportlab.lib.utils import ImageReader
            qr_size = 20*mm
            qr_x = (page_width - qr_size) / 2
            c.drawImage(ImageReader(qr_buf), qr_x, y-qr_size, qr_size, qr_size)
            y -= qr_size + 4*mm
            draw_text(f'Scan to pay: {upi_id}', align='center')
        except Exception:
            pass
    draw_divider()
    draw_text(footer_msg, align='center')
    draw_text('Powered by Smart POS', align='center')

    c.save()
    return filepath

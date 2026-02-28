from PySide6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QComboBox, QDoubleSpinBox, QFormLayout, 
                               QFrame, QCompleter, QStyledItemDelegate)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from services.billing_service import BillingCart
from database.connection import get_connection
from utils.barcode_handler import BarcodeHandler
from utils.whatsapp_share import open_whatsapp

class QtyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0.01)
        editor.setMaximum(9999.99)
        editor.setDecimals(2)
        return editor

class BillingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.cart = BillingCart()
        self.products_data = {} # barcode/name -> product_dict map for quick lookup
        self.barcode_handler = BarcodeHandler()
        self.setup_ui()
        self.setup_shortcuts()
        self.load_products()

    def load_products(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT p.*, g.rate as gst_rate FROM products p LEFT JOIN gst_rates g ON p.gst_rate_id = g.id WHERE p.is_active=1")
        self.products_data.clear()
        
        completer_list = []
        for row in cursor.fetchall():
            p_dict = dict(row)
            p_dict['product_id'] = p_dict['id']
            p_dict['unit_price'] = p_dict['sell_price']
            p_dict['discount_pct'] = 0.0 # Default
            p_dict['gst_rate'] = p_dict['gst_rate'] or 0.0
            
            name = p_dict['name']
            barcode = p_dict['barcode']
            
            if barcode:
                self.products_data[barcode] = p_dict
                completer_list.append(barcode)
            
            self.products_data[name] = p_dict
            completer_list.append(name)
            
        completer = QCompleter(completer_list, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_input.setCompleter(completer)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # LEFT PANEL (65%)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel, stretch=65)
        
        # Search Box
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_bar")
        self.search_input.setPlaceholderText("Scan barcode or type product name... [F2]")
        self.search_input.returnPressed.connect(self.handle_search_return)
        self.search_input.textChanged.connect(self.handle_search_changed)
        
        self.lbl_search_msg = QLabel("")
        self.lbl_search_msg.setStyleSheet("color: #EF4444; font-size: 13px; font-weight: bold;")
        self.lbl_search_msg.hide()
        
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.lbl_search_msg)
        
        # Cart Table
        self.cart_table = QTableWidget(0, 9)
        self.cart_table.setHorizontalHeaderLabels([
            "#", "Product", "Qty", "Unit", "Price", "Disc%", "GST", "Total", ""
        ])
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Fixed)
        self.cart_table.setColumnWidth(8, 50) # Small remove btn column
        self.cart_table.setItemDelegateForColumn(2, QtyDelegate(self))
        self.cart_table.cellChanged.connect(self.handle_cell_changed)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        left_layout.addWidget(self.cart_table)
        
        # RIGHT PANEL (35%)
        right_panel = QFrame()
        right_panel.setObjectName("card")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)
        main_layout.addWidget(right_panel, stretch=35)
        
        # Customer Section
        cust_layout = QHBoxLayout()
        cust_layout.addWidget(QLabel("Customer:"))
        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True)
        self.customer_combo.addItem("Walk-in")
        cust_layout.addWidget(self.customer_combo)
        right_layout.addLayout(cust_layout)
        
        # Totals Display
        self.lbl_subtotal = QLabel("Rs 0.00")
        self.lbl_subtotal.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_discount = QLabel("Rs 0.00")
        self.lbl_discount.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_cgst = QLabel("Rs 0.00")
        self.lbl_cgst.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_sgst = QLabel("Rs 0.00")
        self.lbl_sgst.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.lbl_grand_total = QLabel("Rs 0.00")
        self.lbl_grand_total.setObjectName("grand_total")
        self.lbl_grand_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.addRow("Subtotal:", self.lbl_subtotal)
        form_layout.addRow("Discount (-):", self.lbl_discount)
        form_layout.addRow("CGST (+):", self.lbl_cgst)
        form_layout.addRow("SGST (+):", self.lbl_sgst)
        
        # Add a divider line before total
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #E2E8F0;")
        right_layout.addLayout(form_layout)
        right_layout.addWidget(divider)
        
        total_layout = QHBoxLayout()
        lbl_t = QLabel("TOTAL:")
        lbl_t.setStyleSheet("font-size: 16px; font-weight: bold; color: #64748B;")
        total_layout.addWidget(lbl_t)
        total_layout.addWidget(self.lbl_grand_total)
        right_layout.addLayout(total_layout)
        
        # Bill Options
        discount_layout = QHBoxLayout()
        discount_layout.addWidget(QLabel("Bill Discount %:"))
        self.bill_discount_input = QDoubleSpinBox()
        self.bill_discount_input.setMaximum(100.0)
        self.bill_discount_input.valueChanged.connect(self.update_totals)
        discount_layout.addWidget(self.bill_discount_input)
        right_layout.addLayout(discount_layout)
        
        pay_layout = QHBoxLayout()
        pay_layout.addWidget(QLabel("Payment:"))
        self.payment_mode = QComboBox()
        self.payment_mode.addItems(["Cash", "UPI", "Card", "Credit"])
        pay_layout.addWidget(self.payment_mode)
        right_layout.addLayout(pay_layout)
        
        recv_layout = QHBoxLayout()
        recv_layout.addWidget(QLabel("Amt Received:"))
        self.amt_received = QDoubleSpinBox()
        self.amt_received.setMaximum(999999.0)
        recv_layout.addWidget(self.amt_received)
        
        self.lbl_change = QLabel("Change: Rs 0.00")
        recv_layout.addWidget(self.lbl_change)
        right_layout.addLayout(recv_layout)
        
        # Action Buttons
        right_layout.addStretch()
        
        btn_print = QPushButton("PRINT BILL [F10]")
        btn_print.setObjectName("btn_primary")
        
        btn_wa = QPushButton("WHATSAPP RECEIPT [F11]")
        btn_wa.setObjectName("btn_whatsapp")
        btn_wa.clicked.connect(self.send_whatsapp)
        QShortcut(QKeySequence(Qt.Key_F11), self).activated.connect(self.send_whatsapp)
        
        btn_new = QPushButton("NEW BILL [F1]")
        btn_new.setObjectName("btn_action")
        
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)
        actions_layout.addWidget(btn_print)
        actions_layout.addWidget(btn_wa)
        actions_layout.addWidget(btn_new)
        
        right_layout.addLayout(actions_layout)
        
        QTimer.singleShot(0, self.search_input.setFocus)

    def setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key_F1), self).activated.connect(self.new_bill)
        QShortcut(QKeySequence(Qt.Key_F2), self).activated.connect(self.search_input.setFocus)
        QShortcut(QKeySequence(Qt.Key_F10), self).activated.connect(self.print_bill)
        # Add F3 hold bill
        QShortcut(QKeySequence(Qt.Key_F3), self).activated.connect(self.hold_bill)
        
    def hold_bill(self):
        # Place holder action
        print("Bill held.")
        
    def handle_search_changed(self, text):
        def on_found(prod):
            self.cart.add_item(prod)
            self.refresh_cart_table()
            self.search_input.clear()
            
        def on_not_found(barcode):
            self.lbl_search_msg.setText(f"Barcode not found: {barcode}")
            self.lbl_search_msg.setStyleSheet("color: red; font-size: 12px;")
            self.lbl_search_msg.show()
            QTimer.singleShot(3000, self.lbl_search_msg.hide)
            
        self.barcode_handler.handle_search_input(text, on_found, on_not_found)
        
    def handle_search_return(self):
        text = self.search_input.text().strip()
        if not text: return
        
        if text in self.products_data:
            self.cart.add_item(self.products_data[text])
            self.refresh_cart_table()
            self.search_input.clear()

    def refresh_cart_table(self):
        self.cart_table.blockSignals(True)
        totals = self.cart.calculate_totals()
        items = totals['items']
        
        self.cart_table.setRowCount(len(items))
        for row, item in enumerate(items):
            pid = item['product_id']
            # #
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(row+1)))
            # Name
            self.cart_table.setItem(row, 1, QTableWidgetItem(item['name']))
            
            # Qty
            qty_item = QTableWidgetItem(str(item['qty']))
            qty_item.setData(Qt.UserRole, pid) # store product_id safely
            self.cart_table.setItem(row, 2, qty_item)
            
            # Unit
            unit = self.products_data.get(item['name'], {}).get('unit', 'pcs')
            self.cart_table.setItem(row, 3, QTableWidgetItem(unit))
            
            # Price
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            
            # Discount
            self.cart_table.setItem(row, 5, QTableWidgetItem(f"{item['discount_pct']:.2f}%"))
            
            # GST
            self.cart_table.setItem(row, 6, QTableWidgetItem(f"{item['gst_amt']:.2f}"))
            
            # Total
            self.cart_table.setItem(row, 7, QTableWidgetItem(f"{item['line_total']:.2f}"))
            
            # Remove Button
            btn_remove = QPushButton("✕")
            btn_remove.setObjectName("btn_danger")
            btn_remove.setFixedSize(30, 30)
            btn_remove.setCursor(Qt.PointingHandCursor)
            btn_remove.clicked.connect(lambda checked=False, p=pid: self.remove_item(p))
            
            # Center the button in the cell
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(btn_remove)
            
            self.cart_table.setCellWidget(row, 8, btn_container)
            
        self.cart_table.blockSignals(False)
        self.update_totals()
        
    def handle_cell_changed(self, row, col):
        if col == 2: # Qty changed
            item = self.cart_table.item(row, col)
            if item:
                pid = item.data(Qt.UserRole)
                try:
                    new_qty = float(item.text())
                    self.cart.update_qty(pid, new_qty)
                    self.refresh_cart_table()
                except ValueError:
                    self.refresh_cart_table() # revert

    def remove_item(self, product_id):
        self.cart.remove_item(product_id)
        self.refresh_cart_table()

    def update_totals(self):
        self.cart.set_bill_discount(self.bill_discount_input.value())
        t = self.cart.calculate_totals()
        
        self.lbl_subtotal.setText(f"Rs {t['subtotal']:.2f}")
        self.lbl_discount.setText(f"Rs {t['discount_amt']:.2f}")
        self.lbl_cgst.setText(f"Rs {t['cgst_total']:.2f}")
        self.lbl_sgst.setText(f"Rs {t['sgst_total']:.2f}")
        self.lbl_grand_total.setText(f"Rs {t['grand_total']:.2f}")
        
    def new_bill(self):
        self.cart.clear()
        self.bill_discount_input.setValue(0.0)
        self.refresh_cart_table()
        self.search_input.setFocus()
        
    def print_bill(self):
        totals = self.cart.calculate_totals()
        if not totals['items']:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Empty Cart', 'Add items before printing.')
            return
            
        from services.invoice_service import create_invoice
        from services.printer_service import print_invoice
        import os, sys, subprocess
        from PySide6.QtWidgets import QMessageBox
        
        # 1. Save invoice to database
        user_id = getattr(self, 'current_user', None)
        user_id = user_id.id if user_id else 1
        
        # Determine customer id
        cust_name = self.customer_combo.currentText()
        cust_id = None
        if cust_name != "Walk-in":
            from services.customer_service import get_all_customers
            customers = get_all_customers(search=cust_name)
            for c in customers:
                if c.name == cust_name:
                    cust_id = c.id
                    break
        
        pay_mode = self.payment_mode.currentText()
        received = float(self.amt_received.value())
        if received <= 0:
            received = totals['grand_total']
            
        try:
            invoice = create_invoice(
                user_id=user_id,
                customer_id=cust_id,
                cart_totals=totals,
                payment_mode=pay_mode,
                amount_received=received
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {e}")
            return
            
        # 2. Build invoice_data dict for printer
        user_name = getattr(self, 'current_user', None)
        user_name = user_name.full_name if user_name else 'Admin'
        
        invoice_data = {
            'invoice_number': invoice.invoice_number,
            'created_at': invoice.created_at,
            'cashier_name': user_name,
            'customer_name': cust_name,
            'items': totals['items'],
            'subtotal': totals['subtotal'],
            'discount_amt': totals['discount_amt'],
            'cgst_amt': totals['cgst_total'],
            'sgst_amt': totals['sgst_total'],
            'total': totals['grand_total'],
            'payment_mode': pay_mode,
            'amount_received': received
        }
        
        # 3. Send to printer
        success, message = print_invoice(invoice_data)
        
        if success:
            self.new_bill()
            QMessageBox.information(self, "Success", "Bill printed!")
        else:
            self.new_bill()
            reply = QMessageBox.question(
                self, 'Printer Issue',
                f'{message}\nOpen PDF instead?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                pdf_path = f'receipt_{invoice.invoice_number}.pdf'
                if os.path.exists(pdf_path):
                    if sys.platform == 'win32':
                        os.startfile(pdf_path)
                    else:
                        subprocess.Popen(['xdg-open', pdf_path])

    def send_whatsapp(self):
        if not self.cart.items:
            return
            
        # Get customer phone
        from services.customer_service import get_all_customers
        phone = None
        c_name = self.customer_combo.currentText()
        if c_name != "Walk-in":
            # Very naive lookup by exact name
            customers = get_all_customers(search=c_name)
            for c in customers:
                if c.name == c_name:
                    phone = c.phone
                    break
                    
        # Construct invoice data
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'shop_name'")
        shop_name = cursor.fetchone()
        shop_name = shop_name['value'] if shop_name else 'Smart POS'
        
        t = self.cart.calculate_totals()
        import datetime
        invoice_data = {
            'shop_name': shop_name,
            'invoice_number': 'TEMP-1234', # Will be replaced when officially saving
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'items': [{'name': i['name'], 'qty': i['qty'], 'total': i['line_total']} for i in t['items']],
            'grand_total': t['grand_total'],
            'payment_mode': self.payment_mode.currentText()
        }
        
        self.lbl_search_msg.setText("Opening WhatsApp...")
        self.lbl_search_msg.setStyleSheet("color: green; font-size: 12px;")
        self.lbl_search_msg.show()
        QTimer.singleShot(2000, self.lbl_search_msg.hide)
        
        open_whatsapp(phone, invoice_data, self)

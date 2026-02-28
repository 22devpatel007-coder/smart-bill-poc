from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QDialog, QFormLayout, QMessageBox, QFrame,
                               QSplitter, QScrollArea, QDoubleSpinBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from services.customer_service import (get_all_customers, add_customer, 
                                       get_customer_invoices, get_customer_dues, settle_dues)

class StatCard(QFrame):
    def __init__(self, title, initial_value, color):
        super().__init__()
        self.setStyleSheet(f"background-color: white; border: 1px solid #E5E7EB; border-radius: 8px;")
        layout = QVBoxLayout(self)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 14px; color: #6B7280;")
        self.lbl_value = QLabel(str(initial_value))
        self.lbl_value.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addStretch()
        self.setMinimumWidth(200)

class AddCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Customer")
        self.setFixedSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.address_input = QLineEdit()
        
        layout.addRow("Name *:", self.name_input)
        layout.addRow("Phone:", self.phone_input)
        layout.addRow("Email:", self.email_input)
        layout.addRow("Address:", self.address_input)
        
        btn_save = QPushButton("Save Customer")
        btn_save.setStyleSheet("background-color: #3B82F6; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)
        
    def save(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Error", "Name is required")
            return
            
        try:
            add_customer(name, phone, email, address)
            QMessageBox.information(self, "Success", "Customer added successfully")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

class CollectPaymentDialog(QDialog):
    def __init__(self, customer_id, outstanding, parent=None):
        super().__init__(parent)
        self.customer_id = customer_id
        self.outstanding = outstanding
        self.setWindowTitle("Collect Payment")
        self.setFixedSize(300, 200)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        lbl_out = QLabel(f"Current Outstanding: Rs {self.outstanding:.2f}")
        lbl_out.setStyleSheet("font-size: 16px; font-weight: bold; color: #EF4444;")
        layout.addWidget(lbl_out)
        
        form = QFormLayout()
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, self.outstanding)
        self.amount_input.setValue(self.outstanding)
        self.amount_input.setPrefix("Rs ")
        form.addRow("Amount Received:", self.amount_input)
        layout.addLayout(form)
        
        btn_pay = QPushButton("Mark Paid")
        btn_pay.setStyleSheet("background-color: #10B981; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_pay.clicked.connect(self.process_payment)
        layout.addWidget(btn_pay)
        
    def process_payment(self):
        amt = self.amount_input.value()
        try:
            # Hardcoding user_id=1 for now, ideally pass current logged in user
            settle_dues(self.customer_id, amt, user_id=1)
            QMessageBox.information(self, "Success", f"Collected Rs {amt:.2f}")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


class CustomersScreen(QWidget):
    # This signal will be connected in main_window.py to switch to billing screen
    # sending the customer dict or ID
    new_bill_requested = Signal(object)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Main List
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers by name or phone...")
        self.search_input.textChanged.connect(self.load_data)
        
        btn_add = QPushButton("+ Add Customer")
        btn_add.setStyleSheet("background-color: #10B981; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_add.clicked.connect(self.open_add_dialog)
        
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(btn_add)
        left_layout.addLayout(toolbar)
        
        # Summary Strip
        summary_layout = QHBoxLayout()
        self.card_total = StatCard("Total Customers", "0", "#3B82F6")
        self.card_dues_count = StatCard("Customers With Dues", "0", "#F59E0B")
        self.card_total_dues = StatCard("Total Outstanding", "Rs 0.00", "#EF4444")
        summary_layout.addWidget(self.card_total)
        summary_layout.addWidget(self.card_dues_count)
        summary_layout.addWidget(self.card_total_dues)
        summary_layout.addStretch()
        left_layout.addLayout(summary_layout)
        
        # Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Name", "Phone", "Outstanding", "Joined", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        left_layout.addWidget(self.table)
        
        # Right side - Detail Panel
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("background-color: white; border-left: 1px solid #E5E7EB;")
        self.right_panel.setMinimumWidth(350)
        self.right_panel.setMaximumWidth(450)
        rp_layout = QVBoxLayout(self.right_panel)
        rp_layout.setContentsMargins(15, 15, 15, 15)
        
        self.lbl_detail_name = QLabel("Select a customer")
        self.lbl_detail_name.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.lbl_detail_phone = QLabel("")
        rp_layout.addWidget(self.lbl_detail_name)
        rp_layout.addWidget(self.lbl_detail_phone)
        
        self.lbl_detail_dues = QLabel("")
        self.lbl_detail_dues.setStyleSheet("font-size: 16px; font-weight: bold; color: #EF4444; margin-top: 10px;")
        rp_layout.addWidget(self.lbl_detail_dues)
        
        self.btn_collect = QPushButton("Collect Payment")
        self.btn_collect.setStyleSheet("background-color: #3B82F6; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        self.btn_collect.clicked.connect(self.collect_payment)
        self.btn_collect.hide()
        rp_layout.addWidget(self.btn_collect)
        
        rp_layout.addWidget(QLabel("<b>Recent Invoices</b>"))
        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(["Inv #", "Total", "Date"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        rp_layout.addWidget(self.history_table)
        
        rp_layout.addStretch()
        self.right_panel.hide()
        
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        
        main_layout.addWidget(self.splitter)
        
        # State
        self.current_customer_id = None
        
    def load_data(self):
        search = self.search_input.text().strip()
        customers = get_all_customers(search if search else None)
        
        total_customers = len(customers)
        dues_count = sum(1 for c in customers if c.outstanding > 0)
        total_dues = sum(c.outstanding for c in customers)
        
        self.card_total.lbl_value.setText(str(total_customers))
        self.card_dues_count.lbl_value.setText(str(dues_count))
        self.card_total_dues.lbl_value.setText(f"Rs {total_dues:.2f}")
        
        self.table.setRowCount(len(customers))
        for row, c in enumerate(customers):
            self.table.setItem(row, 0, QTableWidgetItem(c.name))
            self.table.setItem(row, 1, QTableWidgetItem(c.phone or ''))
            
            due_item = QTableWidgetItem(f"Rs {c.outstanding:.2f}")
            if c.outstanding > 0:
                due_item.setForeground(QColor("#EF4444")) # Red
            else:
                due_item.setForeground(QColor("#10B981")) # Green
            self.table.setItem(row, 2, due_item)
            
            created_at_short = c.created_at.split(' ')[0] if c.created_at else ''
            self.table.setItem(row, 3, QTableWidgetItem(created_at_short))
            
            # Actions
            actions_widget = QWidget()
            h_layout = QHBoxLayout(actions_widget)
            h_layout.setContentsMargins(2, 2, 2, 2)
            
            btn_view = QPushButton("View")
            btn_view.setCursor(Qt.PointingHandCursor)
            btn_view.setStyleSheet("background-color: #F3F4F6; padding: 4px 8px; border-radius: 4px;")
            
            btn_bill = QPushButton("New Bill")
            btn_bill.setCursor(Qt.PointingHandCursor)
            btn_bill.setStyleSheet("background-color: #3B82F6; color: white; padding: 4px 8px; border-radius: 4px;")
            
            # Use lambda to capture the customer data accurately
            btn_view.clicked.connect(lambda checked=False, cid=c.id: self.show_customer_detail(cid))
            btn_bill.clicked.connect(lambda checked=False, cobj=c: self.request_new_bill(cobj))
            
            h_layout.addWidget(btn_view)
            h_layout.addWidget(btn_bill)
            self.table.setCellWidget(row, 4, actions_widget)
            
    def request_new_bill(self, customer_obj):
        self.new_bill_requested.emit(customer_obj)
        
    def show_customer_detail(self, customer_id):
        self.current_customer_id = customer_id
        # Find customer from DB again to get latest info
        customers = get_all_customers()
        c = next((c for c in customers if c.id == customer_id), None)
        if not c: return
        
        self.lbl_detail_name.setText(c.name)
        self.lbl_detail_phone.setText(f"Phone: {c.phone}" if c.phone else "No Phone")
        
        if c.outstanding > 0:
            self.lbl_detail_dues.setText(f"Outstanding: Rs {c.outstanding:.2f}")
            self.btn_collect.show()
        else:
            self.lbl_detail_dues.setText("Outstanding: Rs 0.00")
            self.lbl_detail_dues.setStyleSheet("font-size: 16px; font-weight: bold; color: #10B981; margin-top: 10px;")
            self.btn_collect.hide()
            
        invoices = get_customer_invoices(customer_id)
        self.history_table.setRowCount(len(invoices))
        for i, inv in enumerate(invoices):
            self.history_table.setItem(i, 0, QTableWidgetItem(inv.invoice_number))
            self.history_table.setItem(i, 1, QTableWidgetItem(f"{inv.total:.2f}"))
            date_short = inv.created_at.split(' ')[0] if inv.created_at else ''
            self.history_table.setItem(i, 2, QTableWidgetItem(date_short))
            
        self.right_panel.show()
        
    def open_add_dialog(self):
        dlg = AddCustomerDialog(self)
        if dlg.exec() == QDialog.Accepted:
            self.load_data()
            
    def collect_payment(self):
        if not self.current_customer_id: return
        
        outstanding = get_customer_dues(self.current_customer_id)
        if outstanding <= 0:
            QMessageBox.information(self, "Info", "No outstanding dues.")
            return
            
        dlg = CollectPaymentDialog(self.current_customer_id, outstanding, self)
        if dlg.exec() == QDialog.Accepted:
            self.load_data()
            self.show_customer_detail(self.current_customer_id) # Refresh right panel


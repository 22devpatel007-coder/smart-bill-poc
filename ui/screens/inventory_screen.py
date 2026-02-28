from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QCheckBox, QDialog, QFormLayout, 
                               QComboBox, QDoubleSpinBox, QMessageBox, QDateEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from database.connection import get_connection

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Product")
        self.setFixedSize(400, 500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit()
        self.sku_input = QLineEdit()
        self.barcode_input = QLineEdit()
        
        self.cat_combo = QComboBox()
        self.cat_combo.addItem("General", 1)
        
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["pcs", "kg", "box", "ltr", "ml"])
        
        self.cost_price = QDoubleSpinBox()
        self.cost_price.setMaximum(99999.0)
        
        self.sell_price = QDoubleSpinBox()
        self.sell_price.setMaximum(99999.0)
        
        self.gst_combo = QComboBox()
        self.gst_combo.addItem("0%", 1)
        self.gst_combo.addItem("5%", 2)
        self.gst_combo.addItem("12%", 3)
        self.gst_combo.addItem("18%", 4)
        self.gst_combo.addItem("28%", 5)
        
        self.stock_input = QDoubleSpinBox()
        self.stock_input.setMaximum(99999.0)
        
        self.low_stock = QDoubleSpinBox()
        self.low_stock.setValue(5.0)
        
        self.expiry = QDateEdit()
        self.expiry.setCalendarPopup(True)
        self.expiry.setDate(QDate.currentDate().addYears(1))
        
        layout.addRow("Name *", self.name_input)
        layout.addRow("SKU", self.sku_input)
        layout.addRow("Barcode", self.barcode_input)
        layout.addRow("Category", self.cat_combo)
        layout.addRow("Unit", self.unit_combo)
        layout.addRow("Cost Price", self.cost_price)
        layout.addRow("Sell Price", self.sell_price)
        layout.addRow("GST Rate", self.gst_combo)
        layout.addRow("Initial Stock", self.stock_input)
        layout.addRow("Low Stock Alert", self.low_stock)
        layout.addRow("Expiry Date", self.expiry)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        
    def save(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Error", "Name is required.")
            return
            
        if self.sell_price.value() < self.cost_price.value():
            reply = QMessageBox.warning(self, "Warning", "Sell price is lower than cost price. Continue?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No: return
            
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO products (name, sku, barcode, category_id, unit, cost_price, 
                    sell_price, gst_rate_id, stock, low_stock_qty, expiry_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.name_input.text().strip(),
                    self.sku_input.text().strip() or None,
                    self.barcode_input.text().strip() or None,
                    self.cat_combo.currentData(),
                    self.unit_combo.currentText(),
                    self.cost_price.value(),
                    self.sell_price.value(),
                    self.gst_combo.currentData(),
                    self.stock_input.value(),
                    self.low_stock.value(),
                    self.expiry.date().toString(Qt.ISODate)
                ))
                
                product_id = cursor.lastrowid
                
                if self.stock_input.value() > 0:
                    cursor.execute("""
                        INSERT INTO inventory_logs (product_id, change_qty, reason)
                        VALUES (?, ?, 'purchase')
                    """, (product_id, self.stock_input.value()))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))

class StockAdjustDialog(QDialog):
    def __init__(self, product_id, current_stock, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("Adjust Stock")
        self.setup_ui(current_stock)
        
    def setup_ui(self, current_stock):
        layout = QFormLayout(self)
        
        layout.addRow("Current Stock:", QLabel(str(current_stock)))
        
        self.change_input = QDoubleSpinBox()
        self.change_input.setMinimum(-99999.0)
        self.change_input.setMaximum(99999.0)
        layout.addRow("Change Qty (+/-):", self.change_input)
        
        self.reason = QComboBox()
        self.reason.addItems(["Purchase", "Return", "Damage", "Adjustment"])
        layout.addRow("Reason:", self.reason)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
    def save(self):
        change = self.change_input.value()
        if change == 0:
            self.reject()
            return
            
        conn = get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (change, self.product_id))
                cursor.execute("""
                    INSERT INTO inventory_logs (product_id, change_qty, reason)
                    VALUES (?, ?, ?)
                """, (self.product_id, change, self.reason.currentText().lower()))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))


class InventoryScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Top Bar
        top_bar = QHBoxLayout()
        
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search products...")
        self.search.textChanged.connect(self.load_data)
        top_bar.addWidget(self.search)
        
        self.low_stock_filter = QCheckBox("Low Stock Only")
        self.low_stock_filter.stateChanged.connect(self.load_data)
        top_bar.addWidget(self.low_stock_filter)
        
        btn_add = QPushButton("Add Product")
        btn_add.clicked.connect(self.show_add_dialog)
        top_bar.addWidget(btn_add)
        
        layout.addLayout(top_bar)
        
        # Table
        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "SKU/Barcode", "Category", "Unit", 
            "Cost", "Sell", "Stock", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table)
        
    def load_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT p.*, c.name as cat_name FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.is_active=1"
        params = []
        
        search_text = self.search.text().strip()
        if search_text:
            query += " AND (p.name LIKE ? OR p.sku LIKE ? OR p.barcode LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])
            
        if self.low_stock_filter.isChecked():
            query += " AND p.stock <= p.low_stock_qty"
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(row['name']))
            
            sku_bc = f"{row['sku'] or ''} / {row['barcode'] or ''}".strip(' /')
            self.table.setItem(i, 2, QTableWidgetItem(sku_bc))
            self.table.setItem(i, 3, QTableWidgetItem(row['cat_name'] or '---'))
            self.table.setItem(i, 4, QTableWidgetItem(row['unit']))
            self.table.setItem(i, 5, QTableWidgetItem(f"{row['cost_price']:.2f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{row['sell_price']:.2f}"))
            
            stock_item = QTableWidgetItem(f"{row['stock']}")
            if row['stock'] <= row['low_stock_qty']:
                stock_item.setBackground(QColor("#FEE2E2")) # Light red
            self.table.setItem(i, 7, stock_item)
            
            # Actions
            action_widget = QWidget()
            h_layout = QHBoxLayout(action_widget)
            h_layout.setContentsMargins(0, 0, 0, 0)
            
            btn_edit = QPushButton("Edit")
            btn_adj = QPushButton("Adjust Stock")
            btn_adj.clicked.connect(lambda checked=False, pid=row['id'], stk=row['stock']: self.show_adjust_dialog(pid, stk))
            
            h_layout.addWidget(btn_edit)
            h_layout.addWidget(btn_adj)
            self.table.setCellWidget(i, 8, action_widget)
            
    def show_add_dialog(self):
        dlg = AddProductDialog(self)
        if dlg.exec():
            self.load_data()
            
    def show_adjust_dialog(self, product_id, current_stock):
        dlg = StockAdjustDialog(product_id, current_stock, self)
        if dlg.exec():
            self.load_data()

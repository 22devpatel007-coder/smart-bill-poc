from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, QTimer, QDate
from services.report_service import get_daily_summary, get_product_sales
from database.connection import get_connection

class StatCard(QFrame):
    def __init__(self, title, value, color):
        super().__init__()
        self.setObjectName("stat_card") # Link to main.qss QFrame#stat_card
        self.setStyleSheet(f"QFrame#stat_card {{ border-top: 4px solid {color}; }}")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        lbl_title = QLabel(title.upper())
        lbl_title.setObjectName("stat_label")
        
        self.lbl_value = QLabel(str(value))
        self.lbl_value.setObjectName("stat_value")
        
        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addStretch()

class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        self.timer.start(60000) # 60s refresh
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Dashboard Overview")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #0F172A;")
        layout.addWidget(header)
        
        # Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.card_sales = StatCard("Today's Sales", "Rs 0", "#3B82F6")
        self.card_bills = StatCard("Bills Today", "0", "#10B981")
        self.card_low_stock = StatCard("Low Stock Items", "0", "#EF4444")
        self.card_dues = StatCard("Outstanding Dues", "Rs 0", "#F59E0B")
        
        stats_layout.addWidget(self.card_sales)
        stats_layout.addWidget(self.card_bills)
        stats_layout.addWidget(self.card_low_stock)
        stats_layout.addWidget(self.card_dues)
        layout.addLayout(stats_layout)
        
        # Tables area
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(20)
        
        # Top Products
        prod_panel = QFrame()
        prod_panel.setObjectName("card")
        prod_layout = QVBoxLayout(prod_panel)
        lbl_top = QLabel("Top 5 Products Today")
        lbl_top.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E3A5F; padding-bottom: 8px;")
        prod_layout.addWidget(lbl_top)
        
        self.top_products = QTableWidget(0, 3)
        self.top_products.setHorizontalHeaderLabels(["Product", "Qty", "Revenue"])
        self.top_products.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.top_products.setSelectionBehavior(QTableWidget.SelectRows)
        self.top_products.setEditTriggers(QTableWidget.NoEditTriggers)
        self.top_products.verticalHeader().setVisible(False)
        self.top_products.setShowGrid(False)
        prod_layout.addWidget(self.top_products)
        tables_layout.addWidget(prod_panel, stretch=1)
        
        # Recent Invoices
        inv_panel = QFrame()
        inv_panel.setObjectName("card")
        inv_layout = QVBoxLayout(inv_panel)
        lbl_inv = QLabel("Recent Invoices")
        lbl_inv.setStyleSheet("font-size: 14px; font-weight: bold; color: #1E3A5F; padding-bottom: 8px;")
        inv_layout.addWidget(lbl_inv)
        
        self.recent_inv = QTableWidget(0, 4)
        self.recent_inv.setHorizontalHeaderLabels(["Inv #", "Amount", "Mode", "Time"])
        self.recent_inv.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.recent_inv.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_inv.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_inv.verticalHeader().setVisible(False)
        self.recent_inv.setShowGrid(False)
        inv_layout.addWidget(self.recent_inv)
        tables_layout.addWidget(inv_panel, stretch=1)
        
        # Low Stock
        stock_panel = QFrame()
        stock_panel.setObjectName("card")
        stock_layout = QVBoxLayout(stock_panel)
        lbl_stock = QLabel("Low Stock Alerts")
        lbl_stock.setStyleSheet("font-size: 14px; font-weight: bold; color: #EF4444; padding-bottom: 8px;")
        stock_layout.addWidget(lbl_stock)
        
        self.low_stock_list = QTableWidget(0, 2)
        self.low_stock_list.setHorizontalHeaderLabels(["Product", "Stock"])
        self.low_stock_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.low_stock_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.low_stock_list.setEditTriggers(QTableWidget.NoEditTriggers)
        self.low_stock_list.verticalHeader().setVisible(False)
        self.low_stock_list.setShowGrid(False)
        stock_layout.addWidget(self.low_stock_list)
        tables_layout.addWidget(stock_panel, stretch=1)
        
        layout.addLayout(tables_layout)
        layout.setStretch(2, 1)

    def load_data(self):
        today = QDate.currentDate().toString(Qt.ISODate)
        
        try:
            # 1. Summary Cards
            summary = get_daily_summary(today)
            self.card_sales.lbl_value.setText(f"Rs {summary['sales']:.2f}")
            self.card_bills.lbl_value.setText(str(summary['bills']))
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= low_stock_qty AND is_active=1")
            low_stock_count = cursor.fetchone()[0]
            self.card_low_stock.lbl_value.setText(str(low_stock_count))
            
            cursor.execute("SELECT SUM(outstanding) FROM customers")
            dues = cursor.fetchone()[0] or 0.0
            self.card_dues.lbl_value.setText(f"Rs {dues:.2f}")
            
            # 2. Top Products
            top_p = get_product_sales(today, today)
            self.top_products.setRowCount(min(5, len(top_p)))
            for i, p in enumerate(top_p[:5]):
                self.top_products.setItem(i, 0, QTableWidgetItem(p['name']))
                self.top_products.setItem(i, 1, QTableWidgetItem(str(p['qty_sold'])))
                self.top_products.setItem(i, 2, QTableWidgetItem(f"{p['revenue']:.2f}"))
                
            # 3. Recent Invoices
            cursor.execute("SELECT invoice_number, total, payment_mode, time(created_at) as t FROM invoices ORDER BY id DESC LIMIT 5")
            invs = cursor.fetchall()
            self.recent_inv.setRowCount(len(invs))
            for i, inv in enumerate(invs):
                self.recent_inv.setItem(i, 0, QTableWidgetItem(inv['invoice_number']))
                self.recent_inv.setItem(i, 1, QTableWidgetItem(f"{inv['total']:.2f}"))
                self.recent_inv.setItem(i, 2, QTableWidgetItem(inv['payment_mode']))
                self.recent_inv.setItem(i, 3, QTableWidgetItem(inv['t']))
                
            # 4. Low stock List
            cursor.execute("SELECT name, stock FROM products WHERE stock <= low_stock_qty AND is_active=1 LIMIT 10")
            stocks = cursor.fetchall()
            self.low_stock_list.setRowCount(len(stocks))
            for i, st in enumerate(stocks):
                self.low_stock_list.setItem(i, 0, QTableWidgetItem(st['name']))
                self.low_stock_list.setItem(i, 1, QTableWidgetItem(str(st['stock'])))
                
        except Exception as e:
            print("Dashboard load error:", e)

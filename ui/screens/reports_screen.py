from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QDateEdit, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QDate
import csv
from services.report_service import get_daily_summary, get_product_sales, get_gst_summary, get_day_summary, close_day
from PySide6.QtGui import QColor

class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        
        self.tab_day_close = QWidget()
        self.setup_day_close_tab()
        self.tabs.addTab(self.tab_day_close, "Day Close")
        
        self.tab_daily = QWidget()
        self.setup_daily_tab()
        self.tabs.addTab(self.tab_daily, "GST Report")
        
        self.tab_products = QWidget()
        self.setup_products_tab()
        self.tabs.addTab(self.tab_products, "Product Sales")
        
        layout.addWidget(self.tabs)
        
    def setup_day_close_tab(self):
        layout = QVBoxLayout(self.tab_day_close)
        
        # Date selection
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Select Date:"))
        self.dc_date = QDateEdit(QDate.currentDate())
        self.dc_date.setCalendarPopup(True)
        self.dc_date.dateChanged.connect(self.load_day_close_data)
        date_layout.addWidget(self.dc_date)
        
        btn_refresh = QPushButton("Refresh")
        btn_refresh.clicked.connect(self.load_day_close_data)
        date_layout.addWidget(btn_refresh)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # Summary Cards
        self.lbl_grand = QLabel("Rs 0.00")
        self.lbl_grand.setStyleSheet("font-size: 32px; font-weight: bold; color: #1E3A5F;")
        
        self.lbl_inv_count = QLabel("0 Invoices")
        self.lbl_avg_bill = QLabel("Avg: Rs 0.00")
        
        main_summary = QHBoxLayout()
        main_summary.addWidget(QLabel("<b>Grand Total:</b>"))
        main_summary.addWidget(self.lbl_grand)
        main_summary.addWidget(self.lbl_inv_count)
        main_summary.addWidget(self.lbl_avg_bill)
        main_summary.addStretch()
        layout.addLayout(main_summary)
        
        # Payment breakdown
        pay_layout = QHBoxLayout()
        self.lbl_cash = QLabel("Cash: Rs 0.00")
        self.lbl_upi = QLabel("UPI: Rs 0.00")
        self.lbl_card = QLabel("Card: Rs 0.00")
        self.lbl_credit = QLabel("Credit: Rs 0.00")
        
        for lbl in [self.lbl_cash, self.lbl_upi, self.lbl_card, self.lbl_credit]:
            lbl.setStyleSheet("padding: 10px; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 4px;")
            pay_layout.addWidget(lbl)
        layout.addLayout(pay_layout)
        
        # GST breakdown
        gst_layout = QHBoxLayout()
        self.lbl_dc_cgst = QLabel("CGST: Rs 0.00")
        self.lbl_dc_sgst = QLabel("SGST: Rs 0.00")
        gst_layout.addWidget(self.lbl_dc_cgst)
        gst_layout.addWidget(self.lbl_dc_sgst)
        gst_layout.addStretch()
        layout.addLayout(gst_layout)
        
        layout.addStretch()
        
        # Buttons
        self.btn_close_day = QPushButton("Close the Day")
        self.btn_close_day.setStyleSheet("background-color: #F59E0B; color: white; padding: 12px; font-weight: bold; font-size: 16px; border-radius: 4px;")
        self.btn_close_day.clicked.connect(self.do_close_day)
        
        self.btn_print_day = QPushButton("Print Day Summary")
        self.btn_print_day.setStyleSheet("padding: 12px; font-weight: bold; font-size: 16px;")
        self.btn_print_day.clicked.connect(self.print_day_close)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_close_day)
        btn_layout.addWidget(self.btn_print_day)
        layout.addLayout(btn_layout)
        
        self.load_day_close_data()
        
    def load_day_close_data(self):
        d_str = self.dc_date.date().toString(Qt.ISODate)
        try:
            summary = get_day_summary(d_str)
            self.lbl_grand.setText(f"Rs {summary['grand_total']:.2f}")
            self.lbl_inv_count.setText(f"{summary['invoice_count']} Invoices")
            self.lbl_avg_bill.setText(f"Avg: Rs {summary['avg_bill']:.2f}")
            
            self.lbl_cash.setText(f"Cash: Rs {summary['cash_total']:.2f}")
            self.lbl_upi.setText(f"UPI: Rs {summary['upi_total']:.2f}")
            self.lbl_card.setText(f"Card: Rs {summary['card_total']:.2f}")
            self.lbl_credit.setText(f"Credit: Rs {summary['credit_total']:.2f}")
            
            self.lbl_dc_cgst.setText(f"CGST Collected: Rs {summary['cgst_total']:.2f}")
            self.lbl_dc_sgst.setText(f"SGST Collected: Rs {summary['sgst_total']:.2f}")
            
            if summary['already_closed']:
                self.btn_close_day.setText("Day Closed ✅")
                self.btn_close_day.setEnabled(False)
                self.btn_close_day.setStyleSheet("background-color: #10B981; color: white; padding: 12px; font-weight: bold; font-size: 16px; border-radius: 4px;")
            else:
                self.btn_close_day.setText("Close the Day")
                self.btn_close_day.setEnabled(True)
                self.btn_close_day.setStyleSheet("background-color: #F59E0B; color: white; padding: 12px; font-weight: bold; font-size: 16px; border-radius: 4px;")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load day summary: {e}")
            
    def do_close_day(self):
        d_str = self.dc_date.date().toString(Qt.ISODate)
        reply = QMessageBox.question(self, "Confirm", "This will lock today's records. Cannot be undone.\nAre you sure?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                # user_id should be real logged in user
                close_day(d_str, user_id=1)
                QMessageBox.information(self, "Success", "Day closed successfully.")
                self.load_day_close_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
                
    def print_day_close(self):
        QMessageBox.information(self, "Print", "Print day summary (to be implemented).")

    def setup_daily_tab(self):
        layout = QVBoxLayout(self.tab_daily)
        
        # Filter Bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Start Date:"))
        self.dt_start = QDateEdit(QDate.currentDate())
        self.dt_start.setCalendarPopup(True)
        filter_layout.addWidget(self.dt_start)
        
        filter_layout.addWidget(QLabel("End Date:"))
        self.dt_end = QDateEdit(QDate.currentDate())
        self.dt_end.setCalendarPopup(True)
        filter_layout.addWidget(self.dt_end)
        
        btn_gen = QPushButton("Generate")
        btn_gen.clicked.connect(self.generate_daily_report)
        filter_layout.addWidget(btn_gen)
        
        btn_exp = QPushButton("Export CSV")
        btn_exp.clicked.connect(self.export_daily)
        filter_layout.addWidget(btn_exp)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # GST Table
        self.gst_table = QTableWidget(0, 5)
        self.gst_table.setHorizontalHeaderLabels(["GST Rate", "Taxable Value", "CGST", "SGST", "Total Tax"])
        self.gst_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("<b>GST Summary</b>"))
        layout.addWidget(self.gst_table)
        
        self.daily_data = []
        
    def generate_daily_report(self):
        start = self.dt_start.date().toString(Qt.ISODate)
        end = self.dt_end.date().toString(Qt.ISODate)
        
        try:
            self.daily_data = get_gst_summary(start, end)
            self.gst_table.setRowCount(len(self.daily_data))
            for i, row in enumerate(self.daily_data):
                self.gst_table.setItem(i, 0, QTableWidgetItem(f"{row['gst_rate']}%"))
                self.gst_table.setItem(i, 1, QTableWidgetItem(f"{row['taxable_value']:.2f}"))
                self.gst_table.setItem(i, 2, QTableWidgetItem(f"{row['cgst']:.2f}"))
                self.gst_table.setItem(i, 3, QTableWidgetItem(f"{row['sgst']:.2f}"))
                self.gst_table.setItem(i, 4, QTableWidgetItem(f"{row['total_tax']:.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def export_daily(self):
        if not self.daily_data: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "gst_report.csv", "CSV Files (*.csv)")
        if file_path:
            keys = self.daily_data[0].keys()
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.daily_data)
            QMessageBox.information(self, "Success", "Exported successfully.")
            
    def setup_products_tab(self):
        layout = QVBoxLayout(self.tab_products)
        
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Date:"))
        self.dt_prod = QDateEdit(QDate.currentDate())
        self.dt_prod.setCalendarPopup(True)
        filter_layout.addWidget(self.dt_prod)
        
        btn_gen = QPushButton("Generate")
        btn_gen.clicked.connect(self.generate_product_report)
        filter_layout.addWidget(btn_gen)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        self.prod_table = QTableWidget(0, 3)
        self.prod_table.setHorizontalHeaderLabels(["Product Name", "Qty Sold", "Revenue"])
        self.prod_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.prod_table)
        
    def generate_product_report(self):
        date_str = self.dt_prod.date().toString(Qt.ISODate)
        try:
            data = get_product_sales(date_str, date_str)
            self.prod_table.setRowCount(len(data))
            for i, row in enumerate(data):
                self.prod_table.setItem(i, 0, QTableWidgetItem(row['name']))
                self.prod_table.setItem(i, 1, QTableWidgetItem(str(row['qty_sold'])))
                self.prod_table.setItem(i, 2, QTableWidgetItem(f"{row['revenue']:.2f}"))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

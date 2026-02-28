from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                               QHBoxLayout, QListWidget, QStackedWidget, QLabel, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from ui.screens.login_screen import LoginScreen
from ui.screens.dashboard_screen import DashboardScreen
from ui.screens.billing_screen import BillingScreen
from ui.screens.inventory_screen import InventoryScreen
from ui.screens.reports_screen import ReportsScreen
from ui.screens.customers_screen import CustomersScreen
from ui.screens.settings_screen import SettingsScreen
from services.backup_service import check_backup_reminder

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Billing System")
        self.resize(1280, 800)
        
        self.login_screen = LoginScreen()
        self.login_screen.login_success.connect(self.on_login_success)
        
        self.setCentralWidget(self.login_screen)
        
    def on_login_success(self, user):
        self.user = user
        self.billing = BillingScreen()
        self.billing.current_user = user # Set current user for invoice saving
        self.setup_main_ui()
        
    def setup_main_ui(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        self.sidebar_container = QWidget()
        self.sidebar_container.setObjectName("sidebar")
        
        sidebar_layout = QVBoxLayout(self.sidebar_container)
        sidebar_layout.setContentsMargins(0, 20, 0, 0)
        sidebar_layout.setSpacing(5)
        
        # Logo area inside sidebar
        lbl_logo = QLabel("SMART POS")
        lbl_logo.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding-left: 20px; padding-bottom: 20px;")
        sidebar_layout.addWidget(lbl_logo)
        
        # Buttons list instead of QListWidget for better styling control
        self.nav_buttons = []
        self.stacked = QStackedWidget()
        
        # Screens
        self.dashboard = DashboardScreen()
        self.customers = CustomersScreen()
        
        self.customers.new_bill_requested.connect(self.switch_to_billing_with_customer)
        
        # Add core screens
        self.add_screen("Billing (POS)", self.billing)
        self.add_screen("Dashboard", self.dashboard)
        self.add_screen("Customers", self.customers)
        
        # Admin screens
        if self.user.role == 'admin':
            self.inventory = InventoryScreen()
            self.reports = ReportsScreen()
            self.settings = SettingsScreen(current_user=self.user)
            
            self.add_screen("Inventory", self.inventory)
            self.add_screen("Reports", self.reports)
            self.add_screen("Settings", self.settings)
        else:
            # Add access denied screens for staff
            self.add_screen("Inventory", self.create_denied_screen())
            self.add_screen("Reports", self.create_denied_screen())
            self.add_screen("Settings", self.create_denied_screen())
            
        sidebar_layout.addStretch()
        
        # User role indicator at bottom of sidebar
        lbl_user = QLabel(f"👤 {self.user.full_name}\n({self.user.role.title()})")
        lbl_user.setStyleSheet("color: #94A3B8; font-size: 12px; padding: 20px;")
        sidebar_layout.addWidget(lbl_user)
        
        # Right Side (Topbar + Content)
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #F8FAFC;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Topbar
        topbar = QWidget()
        topbar.setObjectName("topbar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_page_title = QLabel("Billing (POS)")
        self.lbl_page_title.setObjectName("page_title")
        topbar_layout.addWidget(self.lbl_page_title)
        
        right_layout.addWidget(topbar)
        right_layout.addWidget(self.stacked)
        
        layout.addWidget(self.sidebar_container)
        layout.addWidget(right_panel, stretch=1)
        self.setCentralWidget(container)
        
        # Set initial selection
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
        
        # Backup reminder
        if self.user.role == 'admin' and check_backup_reminder():
            # delay slightly so it shows after layout is complete
            QTimer.singleShot(1000, lambda: QMessageBox.information(self, "Backup Reminder", 
                  "Reminder: Last backup was more than 7 days ago. Go to Settings > Backup."))

    def add_screen(self, title, widget):
        from PySide6.QtWidgets import QPushButton
        idx = self.stacked.count()
        
        btn = QPushButton(title)
        btn.setObjectName("nav_button")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        
        btn.clicked.connect(lambda checked=False, i=idx, t=title: self.switch_screen(i, t))
        
        self.sidebar_container.layout().insertWidget(self.sidebar_container.layout().count() - 2, btn)
        self.nav_buttons.append(btn)
        self.stacked.addWidget(widget)
        
    def switch_screen(self, index, title):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.stacked.setCurrentIndex(index)
        self.lbl_page_title.setText(title)
        
    def create_denied_screen(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel("Access Denied\nOnly Admins can view this screen.")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 24px; color: red;")
        l.addWidget(lbl)
        return w
        
    def switch_to_billing_with_customer(self, customer_obj):
        # Find billing index (it's always 0 in this flow)
        self.switch_screen(0, "Billing (POS)")
        
        # Try to find customer in combo box and set it
        c_combo = self.billing.customer_combo
        c_name = customer_obj.name
        idx_combo = c_combo.findText(c_name)
        if idx_combo >= 0:
            c_combo.setCurrentIndex(idx_combo)
        else:
            c_combo.addItem(c_name)
            c_combo.setCurrentText(c_name)

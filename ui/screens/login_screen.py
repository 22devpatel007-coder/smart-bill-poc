from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QFrame, QHBoxLayout, QGraphicsDropShadowEffect, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QCursor
from forms.login_form import LoginForm

class LoginScreen(QWidget):
    login_success = Signal(object) # Emits User object

    def __init__(self):
        super().__init__()
        self.form = LoginForm()
        self.setup_ui()

    def setup_ui(self):
        # Using a very light grey for the main background to contrast with the white card
        self.setStyleSheet("LoginScreen { background-color: #F4F5F7; }")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        main_layout.addStretch(1)

        # Center Container for Card
        center_layout = QHBoxLayout()
        center_layout.addStretch(1)

        # White Card
        card = QFrame()
        card.setFixedSize(400, 480)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)
        
        # Soft drop shadow for modern look
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(35, 35, 35, 35)
        card_layout.setSpacing(18)

        # Top Icon (Cash Register in light blue circle)
        icon_container = QWidget()
        icon_container.setStyleSheet("border: none; background: transparent;")
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        lbl_icon = QLabel("📠")
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setFixedSize(56, 56)
        lbl_icon.setStyleSheet("""
            background-color: #E0F2FE;
            color: #0284C7;
            font-size: 26px;
            border-radius: 28px;
            border: none;
        """)
        icon_layout.addWidget(lbl_icon)

        # Title / Subtitle 
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        title_label = QLabel("Welcome Back")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #0F172A; font-size: 22px; font-weight: 800; border: none; background: transparent;")
        
        subtitle = QLabel("Sign in to your RetailFlow POS terminal")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748B; font-size: 13px; border: none; background: transparent;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle)

        # Username Input
        user_layout = QVBoxLayout()
        user_layout.setSpacing(6)
        user_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet("color: #1E293B; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        
        user_input_frame = QFrame()
        user_input_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background-color: white;
            }
        """)
        user_input_layout = QHBoxLayout(user_input_frame)
        user_input_layout.setContentsMargins(12, 0, 12, 0)
        user_input_layout.setSpacing(10)
        
        lbl_user_icon = QLabel("👤")
        lbl_user_icon.setStyleSheet("color: #94A3B8; font-size: 14px; border: none; background: transparent;")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your ID or username")
        self.username_input.setMinimumHeight(42)
        self.username_input.setStyleSheet("border: none; font-size: 13px; color: #0F172A; background: transparent;")
        
        user_input_layout.addWidget(lbl_user_icon)
        user_input_layout.addWidget(self.username_input)
        
        user_layout.addWidget(lbl_user)
        user_layout.addWidget(user_input_frame)

        # Password Input
        pass_layout = QVBoxLayout()
        pass_layout.setSpacing(6)
        pass_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet("color: #1E293B; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        
        pass_input_frame = QFrame()
        pass_input_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                background-color: white;
            }
        """)
        pass_input_layout = QHBoxLayout(pass_input_frame)
        pass_input_layout.setContentsMargins(12, 0, 12, 0)
        pass_input_layout.setSpacing(10)
        
        lbl_pass_icon = QLabel("🔒")
        lbl_pass_icon.setStyleSheet("color: #94A3B8; font-size: 14px; border: none; background: transparent;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your PIN or password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(42)
        self.password_input.setStyleSheet("border: none; font-size: 13px; color: #0F172A; background: transparent;")
        
        pass_input_layout.addWidget(lbl_pass_icon)
        pass_input_layout.addWidget(self.password_input)
        
        pass_layout.addWidget(lbl_pass)
        pass_layout.addWidget(pass_input_frame)

        # Error Label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: bold; border: none; background: transparent;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.hide()

        # Login Button
        login_btn = QPushButton("➔  Sign In")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setMinimumHeight(42)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        login_btn.clicked.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        self.username_input.returnPressed.connect(self.password_input.setFocus)

        self.forgot_link = QLabel("<a href='#' style='color: #2563EB; text-decoration: none; font-size: 13px; font-weight: 500;'>Forgot your password?</a>")
        self.forgot_link.setAlignment(Qt.AlignCenter)
        self.forgot_link.setStyleSheet("border: none; background: transparent;")
        self.forgot_link.linkActivated.connect(self.handle_forgot_password)

        # Add to card layout
        card_layout.addWidget(icon_container)
        card_layout.addLayout(title_layout)
        card_layout.addSpacing(5)
        card_layout.addLayout(user_layout)
        card_layout.addLayout(pass_layout)
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(6)
        card_layout.addWidget(login_btn)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.forgot_link)
        
        card_layout.addStretch()

        center_layout.addWidget(card)
        center_layout.addStretch(1)

        main_layout.addLayout(center_layout)
        main_layout.addStretch(1)

        # Footer
        footer_layout = QVBoxLayout()
        footer_layout.setAlignment(Qt.AlignCenter)
        footer_layout.setSpacing(4)
        
        lbl_footer_title = QLabel("RetailFlow POS")
        lbl_footer_title.setAlignment(Qt.AlignCenter)
        lbl_footer_title.setStyleSheet("color: #1E293B; font-size: 13px; font-weight: bold; background: transparent;")
        
        lbl_footer_status = QLabel("v2.4.0  •  <span style='color:#10B981;'>●</span> System Operational")
        lbl_footer_status.setAlignment(Qt.AlignCenter)
        lbl_footer_status.setStyleSheet("color: #64748B; font-size: 12px; background: transparent;")
        
        footer_layout.addWidget(lbl_footer_title)
        footer_layout.addWidget(lbl_footer_status)
        
        main_layout.addLayout(footer_layout)
        main_layout.addSpacing(30)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_error("Please enter both username and password.")
            return

        try:
            user = self.form.validate(username, password)
            self.error_label.hide()
            self.login_success.emit(user)
        except ValueError as e:
            self.show_error(str(e))
            
    def handle_forgot_password(self, link):
        QMessageBox.information(self, "Forgot Password", "Please contact your system administrator to reset your credentials.")

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

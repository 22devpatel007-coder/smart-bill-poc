# Smart POS System

A production-ready retail point of sale (POS) system built with Python, PySide6, and SQLite, tailored for the Indian retail market.

## Key Features
- **Billing**: Full POS screen with live product search, barcode scanning, and F-key shortcuts.
- **GST Calculation**: Compliant with Indian GST standards (calculates CGST and SGST correctly after discounts).
- **Inventory Management**: Track stock levels, set low-stock warnings, and view product sales.
- **Customers & Dues**: Track customer purchases and manage outstanding "udhar" balances.
- **Reports & Day Close**: Generate daily sales reports, GST return summaries, and lock invoices at the end of the day.
- **Thermal Printing & WhatsApp**: Print professional receipts on USB thermal printers, generate PDF receipts, and share them via WhatsApp.
- **Data Safety**: Offline-first SQLite database (`smart_pos.db`) with simple USB and local backups.

## Setup Instructions

### Prerequisites
- Windows OS (recommended for easy POS hardware integration)
- Python 3.11+
- USB Thermal Receipt Printer (optional but recommended)

### Installation
1. Clone the repository or navigate to the source code directory.
2. Create and activate a virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate.bat
   ```
3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

## Running the Application

### First-Time Setup Wizard
If this is the first time running the system, initialize the database and store primary settings using the setup wizard:
```cmd
python first_run_setup.py
```
*Note: This wizard seeds the database with an initial `admin` user with the password `admin123`.*

### Starting the App
After completing the initial setup wizard, launch the main POS application:
```cmd
python main.py
```

### Packaging for Production
To build a standalone `.exe` you can install on any Windows machine without requiring Python dependencies:
1. Double-click or run `build.bat` in the project root.
2. Once complete, you will find the executable bundle inside `dist\SmartPOS\`. 
3. Copy the entire `SmartPOS` folder to a USB drive to install on the target PC.

## Default Credentials
- **Username:** `admin`
- **Password:** `admin123`

## Important Notes for Shop Owners
1. **Settings / Shop Info:** Before creating your first bill, log in as `admin`, go to **Settings**, and complete your Shop Name, GST Number, and UPI ID. The printed invoices will extract metadata directly from here.
2. **Backups:** Remember to create a backup at least once a week from the Settings page to prevent data loss. You will receive an automated warning badge locally if your backup gets outdated.
3. **Closing the Day:** Use the "Reports" -> "Day Close" tab at the end of your shift to summarize payments and lock all invoices for that specific day.

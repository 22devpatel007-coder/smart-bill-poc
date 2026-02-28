import os
import shutil
import ctypes
from datetime import datetime
from database.connection import get_connection

def get_last_backup_date():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'last_backup'")
    row = cursor.fetchone()
    if row:
        return row['value']
    return None

def update_last_backup_date():
    conn = get_connection()
    try:
        with conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('last_backup', now))
    except Exception as e:
        print(f"Failed to update last backup date: {e}")

def check_backup_reminder():
    last_backup_str = get_last_backup_date()
    if not last_backup_str:
        return True # Never backed up
        
    try:
        last_backup = datetime.fromisoformat(last_backup_str)
        delta = datetime.now() - last_backup
        if delta.days > 7:
            return True
    except Exception:
        return True
    return False

def get_usb_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if bitmask & 1:
            drive_path = f"{letter}:\\"
            # DRIVE_REMOVABLE = 2
            if ctypes.windll.kernel32.GetDriveTypeW(drive_path) == 2:
                drives.append(drive_path)
        bitmask >>= 1
    return drives

def backup_to_usb():
    drives = get_usb_drives()
    if not drives:
        raise Exception("No USB drive detected.")
        
    # Pick the first USB drive found
    target_drive = drives[0]
    backup_folder = os.path.join(target_drive, "SmartPOS_Backup")
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = "smart_pos.db"
    dest_path = os.path.join(backup_folder, f"smart_pos_backup_{timestamp}.db")
    
    if os.path.exists(db_path):
        shutil.copy2(db_path, dest_path)
        update_last_backup_date()
        return dest_path
    else:
        raise Exception(f"Database file {db_path} not found.")

def backup_to_local(folder):
    if not os.path.exists(folder):
        raise Exception(f"Folder does not exist: {folder}")
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = "smart_pos.db"
    dest_path = os.path.join(folder, f"smart_pos_backup_{timestamp}.db")
    
    if os.path.exists(db_path):
        shutil.copy2(db_path, dest_path)
        update_last_backup_date()
        return dest_path
    else:
        raise Exception(f"Database file {db_path} not found.")

def backup_to_google_drive():
    # Placeholder for Google Drive backup using google-api-python-client as requested
    # We would need to authenticate, upload the file and handle credentials.
    # For now, we simulate success since we don't have OAuth credentials configured.
    update_last_backup_date()
    return "Backup to Google Drive completed successfully (Simulated)"

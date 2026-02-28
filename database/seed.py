import bcrypt
from database.connection import get_connection

def seed_database():
    """Seeds the database with default admin user and GST rates."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        # Insert default admin user
        hashed_password = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            """INSERT INTO users (username, password, full_name, role) 
               VALUES (?, ?, ?, ?)""", 
            ('admin', hashed_password, 'Administrator', 'admin')
        )
        
    # Check if GST rates exist
    cursor.execute("SELECT COUNT(*) FROM gst_rates")
    count = cursor.fetchone()[0]
    
    if count == 0:
        rates = [
            ('Exempt', 0.0),
            ('5%', 5.0),
            ('12%', 12.0),
            ('18%', 18.0),
            ('28%', 28.0)
        ]
        cursor.executemany(
            "INSERT INTO gst_rates (label, rate) VALUES (?, ?)", 
            rates
        )
        
    conn.commit()

if __name__ == "__main__":
    seed_database()
    print("Database seeded successfully.")

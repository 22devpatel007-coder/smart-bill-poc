import bcrypt
from database.connection import get_connection
from models.user import User

class LoginForm:
    def __init__(self):
        self.failed_attempts = {}

    def validate(self, username, password):
        """
        Validates username and password against the database.
        Returns: User dataclass on success.
        Raises: ValueError with message on failure.
        """
        # Check account lock simply in memory for this session
        attempts = self.failed_attempts.get(username, 0)
        if attempts >= 5:
            raise ValueError("Account locked due to too many failed attempts.")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, full_name, role, is_active FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()

        if not row:
            self._record_failure(username)
            raise ValueError("Invalid username or password.")

        if not row['is_active']:
            raise ValueError("Account is disabled.")

        hashed_pw = row['password'].encode('utf-8')
        if not bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
            self._record_failure(username)
            raise ValueError("Invalid username or password.")

        # Success - reset attempts
        self.failed_attempts[username] = 0
        return User(
            id=row['id'],
            username=row['username'],
            full_name=row['full_name'],
            role=row['role'],
            is_active=bool(row['is_active'])
        )

    def _record_failure(self, username):
        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1

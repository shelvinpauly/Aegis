# auth.py
from .db import get_db_connection
from .models import User
from .utils import hash_password, verify_password

def register_user(username, password):
    hashed_password = hash_password(password)
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO auth.users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()

def login_user(username, password):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password FROM auth.users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result and verify_password(password, result[0]):
                return True  # Login successful
    return False
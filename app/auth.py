import re
import sqlite3
import bcrypt

DB_PATH = "app.db"


def get_next_user_id():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # récupérer le max ID existant
    cursor.execute("SELECT MAX(id) FROM users")
    max_id = cursor.fetchone()[0]

    conn.close()

    # séparation stricte
    MIN_USER_ID = 1000

    if max_id is None:
        return MIN_USER_ID + 1

    return max(max_id + 1, MIN_USER_ID + 1)


def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def create_user(email, password, first_name="", last_name=""):
    if not is_valid_email(email):
        raise ValueError("Invalid email format")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    new_user_id = get_next_user_id()

    cursor.execute("""
    INSERT INTO users (id, email, password, first_name, last_name)
    VALUES (?, ?, ?, ?, ?)
    """, (new_user_id, email, hashed_pw, first_name, last_name))

    conn.commit()
    conn.close()


def authenticate_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, email, password, first_name, last_name
        FROM users WHERE email = ?
    """, (email,))

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return None

    user_id, email, hashed_pw, first_name, last_name = user

    if bcrypt.checkpw(password.encode(), hashed_pw):
        return {
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        }

    return None

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


def create_user(email, password, confirm_password, first_name="", last_name=""):
    if not email or not password or not confirm_password or not first_name or not last_name:
        raise ValueError("Tous les champs sont obligatoires")

    if not is_valid_email(email):
        raise ValueError("Format d'email invalide")

    if password != confirm_password:
        raise ValueError("Les mots de passe ne correspondent pas")

    if len(password) < 6:
        raise ValueError("Le mot de passe doit contenir au moins 6 caractères")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # vérifier si email existe déjà
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Cet email est déjà utilisé")

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

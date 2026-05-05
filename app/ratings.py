import sqlite3

DB_PATH = "app.db"


def get_user_rating(user_id, movie_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT rating FROM ratings
        WHERE user_id = ? AND movie_id = ?
    """, (user_id, movie_id))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def rate_movie(user_id, movie_id, rating):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # vérifier si déjà noté
    cursor.execute("""
        SELECT id FROM ratings
        WHERE user_id = ? AND movie_id = ?
    """, (user_id, movie_id))

    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE ratings
            SET rating = ?, timestamp = strftime('%s','now')
            WHERE user_id = ? AND movie_id = ?
        """, (rating, user_id, movie_id))
    else:
        cursor.execute("""
            INSERT INTO ratings (user_id, movie_id, rating, timestamp)
            VALUES (?, ?, ?, strftime('%s','now'))
        """, (user_id, movie_id, rating))

    conn.commit()
    conn.close()
    
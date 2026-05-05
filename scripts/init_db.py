import sqlite3
import pandas as pd

DB_PATH = "app.db"
USER_ID_OFFSET = 1000


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        first_name TEXT,
        last_name TEXT,
        profile_picture TEXT,
        birth_date TEXT,
        gender TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        genres TEXT,
        year INTEGER,
        tmdb_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        movie_id INTEGER,
        rating REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(movie_id) REFERENCES movies(id)
    )
    """)

    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ratings_movie ON ratings(movie_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_tmdb ON movies(tmdb_id)")

    conn.commit()


def insert_movies(conn):
    movies = pd.read_csv("data/movies_clean.csv")

    movies = movies.rename(columns={
        "movieId": "id",
        "tmdbId": "tmdb_id"
    })

    movies.to_sql("movies", conn, if_exists="append", index=False)


def insert_ratings(conn):
    ratings = pd.read_csv("data/ratings_clean.csv")

    ratings = ratings.rename(columns={
        "userId": "user_id",
        "movieId": "movie_id"
    })

    ratings = ratings[["user_id", "movie_id", "rating"]]

    ratings.to_sql("ratings", conn, if_exists="append", index=False)


def set_user_autoincrement(conn):
    cursor = conn.cursor()

    # Force SQLite to start user IDs at USER_ID_OFFSET
    cursor.execute(f"""
        INSERT OR IGNORE INTO users (id, email, password)
        VALUES ({USER_ID_OFFSET}, 'init@system.local', 'init')
    """)
    cursor.execute(f"DELETE FROM users WHERE id = {USER_ID_OFFSET}")

    conn.commit()


def main():
    conn = sqlite3.connect(DB_PATH)

    create_tables(conn)
    insert_movies(conn)
    insert_ratings(conn)
    set_user_autoincrement(conn)

    conn.close()
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()

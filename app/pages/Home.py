import streamlit as st
import sqlite3
from recommender import *
from tmdb import get_movie_poster
from utils import extract_genres

st.set_page_config(layout="wide")

DB_PATH = "app.db"


# ---------------- CSS ---------------
st.markdown("""
<style>

.movie-title {
    font-size: 0.75rem;
    line-height: 1.2em;
    height: 2.4em;
    overflow: hidden;
    margin-top: 5px;
}

.movie-card img {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- CARD ----------------
def render_card(movie):
    poster = get_movie_poster(movie.get("tmdb_id"))
    title = movie.get("title", "Unknown")

    if poster:
        st.image(poster, use_container_width=True)
    else:
        st.write("")

    st.caption(title)


# ---------------- GRID STABLE ----------------
def render_grid(movies):
    if movies.empty:
        st.info("Aucun film trouvé")
        return

    cols_per_row = 6

    for i in range(0, len(movies), cols_per_row):
        row = movies.iloc[i:i + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, (_, movie) in zip(cols, row.iterrows()):
            with col:
                render_card(movie)


# ---------------- DATA ----------------
ratings, movies = load_data()
user = st.session_state.get("user")

if not user:
    st.warning("Veuillez vous connecter")
    st.stop()


# ---------------- SEARCH / FILTER ----------------
st.title("Accueil")

col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input("Rechercher un film")

with col2:
    genres = extract_genres(movies)
    selected_genre = st.selectbox("Genre", ["Tous"] + genres)


# DB search (important)
def search_movies(query, genre):
    conn = sqlite3.connect(DB_PATH)

    sql = "SELECT * FROM movies WHERE 1=1"
    params = []

    if query:
        sql += " AND title LIKE ?"
        params.append(f"%{query}%")

    if genre != "Tous":
        sql += " AND genres LIKE ?"
        params.append(f"%{genre}%")

    sql += " LIMIT 60"

    df = pd.read_sql(sql, conn, params=params)
    conn.close()

    return df


search_results = search_movies(search_query, selected_genre)


# ---------------- PERSONNALISÉ ----------------
user_ratings = ratings[ratings["user_id"] == user["id"]]

if len(user_ratings) >= 5:
    st.subheader("Recommandés pour vous")

    matrix, user_map, movie_map = build_sparse_matrix(ratings)
    sim = compute_item_similarity(matrix)

    rec_ids = recommend_items(
        user["id"], ratings, matrix, user_map, movie_map, sim, 20
    )

    recs_personal = movies[movies["id"].isin(rec_ids)]

    render_grid(recs_personal)


# ---------------- POPULAIRES ----------------
st.subheader("Films populaires")

recs_pop = get_popular_movies(30)

render_grid(recs_pop)


# ---------------- SEARCH ----------------
if search_query or selected_genre != "Tous":
    st.subheader("Résultats")

    render_grid(search_results)
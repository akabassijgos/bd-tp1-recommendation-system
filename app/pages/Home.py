import streamlit as st
import sqlite3
from recommender import *
from tmdb import get_movie_poster
from utils import extract_genres

st.set_page_config(layout="wide")

DB_PATH = "app.db"

# ---------- CSS ----------
st.markdown("""
<style>

/* GRID */
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 16px;
}

/* SCROLL */
.scroll-container {
    display: flex;
    flex-wrap: nowrap;
    overflow-x: auto;
    gap: 12px;
    padding-bottom: 10px;
}

.scroll-item {
    width: 90px;
    flex: 0 0 auto;
}

/* CARD */
.movie-card {
    width: 100%;
}

/* IMAGE */
.movie-card img {
    width: 100%;
    border-radius: 10px;
    display: block;
}

/* TITLE */
.movie-title {
    font-size: 0.7rem;
    line-height: 1.2em;
    height: 2.4em;
    overflow: hidden;
    margin-top: 4px;
}

/* REMOVE vertical scroll glitch */
section.main > div {
    overflow: visible !important;
}

</style>
""", unsafe_allow_html=True)

# ---------- DB SEARCH ----------
def search_movies_db(query=None, genre=None, limit=50):
    conn = sqlite3.connect(DB_PATH)

    sql = "SELECT * FROM movies WHERE 1=1"
    params = []

    if query:
        sql += " AND title LIKE ?"
        params.append(f"%{query}%")

    if genre and genre != "Tous":
        sql += " AND genres LIKE ?"
        params.append(f"%{genre}%")

    sql += " LIMIT ?"
    params.append(limit)

    df = pd.read_sql(sql, conn, params=params)
    conn.close()

    return df


# ---------- CARD ----------
def render_card(movie):
    poster = get_movie_poster(movie.get("tmdb_id"))
    title = movie.get("title", "Unknown")

    if poster:
        st.image(poster, use_container_width=True)
    else:
        st.write("")

    st.caption(title)


# ---------- GRID ----------
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


# ---------- SCROLL ----------
def render_scroll(movies):
    if movies.empty:
        return

    cols = st.columns(len(movies))

    for col, (_, movie) in zip(cols, movies.iterrows()):
        with col:
            render_card(movie)


# ---------- LOAD ----------
ratings, movies = load_data()

user = st.session_state.get("user")

if not user:
    st.warning("Veuillez vous connecter")
    st.stop()

# ---------- HEADER ----------
st.title("Accueil")

view_mode = st.radio(
    "Affichage",
    ["Scroll", "Grid"],
    horizontal=True
)

# ---------- SEARCH ----------
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input("Rechercher un film")

with col2:
    genres = extract_genres(movies)
    selected_genre = st.selectbox("Genre", ["Tous"] + genres)

search_results = search_movies_db(search_query, selected_genre, 50)

# ---------- PERSONNALISÉ ----------
user_ratings = ratings[ratings["user_id"] == user["id"]]

if len(user_ratings) >= 5:
    st.markdown("## Recommandés pour vous")

    matrix, user_map, movie_map = build_sparse_matrix(ratings)
    sim = compute_item_similarity(matrix)

    rec_ids = recommend_items(
        user["id"], ratings, matrix, user_map, movie_map, sim, 20
    )

    recs_personal = movies[movies["id"].isin(rec_ids)]

    if view_mode == "Scroll":
        render_scroll(recs_personal)
    else:
        render_grid(recs_personal)

# ---------- POPULAIRES ----------
st.markdown("## Films populaires")

recs_pop = get_popular_movies(30)

if view_mode == "Scroll":
    render_scroll(recs_pop)
else:
    render_grid(recs_pop)

# ---------- SEARCH RESULTS ----------
if search_query or selected_genre != "Tous":
    st.markdown("## Résultats de recherche")

    if view_mode == "Scroll":
        render_scroll(search_results)
    else:
        render_grid(search_results)

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

/* GRID RESPONSIVE */
.grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 16px;
}

/* SCROLL HORIZONTAL */
.scroll-container {
    display: flex;
    overflow-x: auto;
    gap: 16px;
    padding-bottom: 10px;
}

.scroll-item {
    min-width: 160px;
    flex-shrink: 0;
}

/* CARD */
.movie-card {
    display: flex;
    flex-direction: column;
}

/* IMAGE */
.movie-card img {
    border-radius: 12px;
    width: 100%;
    height: auto;
    object-fit: cover;
    transition: transform 0.2s ease;
}

.movie-card img:hover {
    transform: scale(1.05);
}

/* TITLE FIXED HEIGHT */
.movie-title {
    margin-top: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    line-height: 1.2em;
    height: 2.4em;
    overflow: hidden;
}

/* SCROLLBAR CLEAN */
.scroll-container::-webkit-scrollbar {
    height: 6px;
}

.scroll-container::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 10px;
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
    poster = get_movie_poster(movie["tmdb_id"])

    img_html = f"<img src='{poster}'/>" if poster else ""

    return f"""
    <div class="movie-card">
        {img_html}
        <div class="movie-title">{movie['title']}</div>
    </div>
    """


# ---------- GRID ----------
def render_grid(movies):
    if movies.empty:
        st.info("Aucun film trouvé")
        return

    html = '<div class="grid-container">'
    for _, movie in movies.iterrows():
        html += render_card(movie)
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


# ---------- SCROLL ----------
def render_scroll(movies):
    if movies.empty:
        return

    html = '<div class="scroll-container">'
    for _, movie in movies.iterrows():
        html += f'<div class="scroll-item">{render_card(movie)}</div>'
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


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
recs_pop = recs_pop.merge(movies, on="id")

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

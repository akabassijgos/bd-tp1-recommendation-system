import streamlit as st
import sqlite3
import pandas as pd
from streamlit_modal import Modal

from recommender import (
    load_data,
    build_sparse_matrix,
    compute_item_similarity,
    recommend_items,
    get_popular_movies
)

from tmdb import get_movie_poster, get_movie_details, get_movie_trailer
from ratings import get_user_rating, rate_movie


# ---------------- MENU ----------------
with st.sidebar:
    if st.button("Logout"):
        st.session_state.user = None
        st.switch_page("pages/0_Login.py")


# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")

DB_PATH = "app.db"
PAGE_SIZE = 20


# ---------------- STATE ----------------
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

modal = Modal(
    "🎬 Détails du film",
    key="movie_modal",
    max_width=800
)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               

if "page" not in st.session_state:
    st.session_state.page = 0

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if "results" not in st.session_state:
    st.session_state.results = pd.DataFrame()


# ---------------- CSS (SAFE) ----------------
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


# ---------------- DATA LOAD ----------------
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("pages/0_Login.py")
    st.stop()

ratings, movies = load_data()

user = st.session_state.get("user")


# ---------------- CARD ----------------
def render_card(movie, source="global"):
    poster = get_movie_poster(movie.get("tmdb_id"))
    title = movie.get("title", "Unknown")

    if poster:
        st.image(poster, width="stretch")
    else:
        st.warning("Image non disponible")

    st.caption(title)
    render_rating_widget(movie, st.session_state.user, source)

    if st.button("Voir les détails", key=f"view_{source}_{movie['id']}"):
        st.session_state.selected_movie = movie.to_dict()
        modal.open()


def render_rating_widget(movie, user, source="global"):
    movie_id = movie["id"]

    current_rating = get_user_rating(user["id"], movie_id)

    # valeur affichée dans le slider
    display_value = current_rating if current_rating is not None else 0.5

    new_rating = st.slider(
        "_Votre note_" if current_rating else "_Pas encore noté_",
        0.5,
        5.0,
        float(display_value),
        step=0.5,
        key=f"rating_{source}_{movie_id}"
    )

    # éviter les écritures automatiques au premier rendu
    if current_rating is None:
        # première apparition du slider → on ne fait rien
        if new_rating != 0.5:
            rate_movie(user["id"], movie_id, new_rating)
            load_data.clear()
            st.rerun()

    else:
        # modification réelle d'une note existante
        if new_rating != current_rating:
            rate_movie(user["id"], movie_id, new_rating)
            load_data.clear()
            st.rerun()


# ---------------- GRID ----------------
def render_grid(df, source):
    if df.empty:
        st.info("Aucun résultat")
        return

    cols_per_row = 5

    for i in range(0, len(df), cols_per_row):
        row = df.iloc[i:i + cols_per_row]
        cols = st.columns(cols_per_row)

        for col, (_, movie) in zip(cols, row.iterrows()):
            with col:
                with st.container():
                    render_card(movie, source)


# ---------------- SEARCH FUNCTION ----------------
def search_movies(query, genre, limit, offset):
    conn = sqlite3.connect(DB_PATH)

    sql = "SELECT * FROM movies WHERE 1=1"
    params = []

    if query:
        sql += " AND title LIKE ?"
        params.append(f"%{query}%")

    if genre != "Tous":
        sql += " AND genres LIKE ?"
        params.append(f"%{genre}%")

    sql += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    df = pd.read_sql(sql, conn, params=params)
    conn.close()

    return df


# ---------------- UI HEADER ----------------
st.title("🎬 Système de Recommandation de Films")


# ---------------- SEARCH UI ----------------
col1, col2 = st.columns([3, 1])

with col1:
    search_query = st.text_input("Rechercher un film")

with col2:
    def extract_genres(df):
        all_genres = set()

        for g in df["genres"].dropna():
            for genre in g.split("|"):
                all_genres.add(genre.strip())

        return sorted(all_genres)
    genres = extract_genres(movies)
    selected_genre = st.selectbox("Genre", ["Tous"] + genres)


# ---------------- RESET PAGINATION ----------------
current_query = f"{search_query}-{selected_genre}"

if current_query != st.session_state.last_query:
    st.session_state.page = 0
    st.session_state.last_query = current_query


search_active = search_query.strip() != "" or selected_genre != "Tous"


# =====================================================
# MODE 1 : SEARCH MODE (FULL RESULTS ONLY)
# =====================================================
if search_active:

    st.subheader("Résultats")

    offset = st.session_state.page * PAGE_SIZE

    new_results = search_movies(
        search_query,
        selected_genre,
        PAGE_SIZE,
        st.session_state.page * PAGE_SIZE
    )

    if st.session_state.page == 0:
        st.session_state.results = new_results
    else:
        st.session_state.results = (
            pd.concat([st.session_state.results, new_results])
            .drop_duplicates(subset="id")
            .sort_values("id")
            .reset_index(drop=True)
        )

    render_grid(st.session_state.results, source="search")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Charger plus"):
        st.session_state.page += 1
        st.rerun()

# =====================================================
# MODE 2 : HOME MODE (RECO + POPULAR)
# =====================================================
else:

    user_ratings = ratings[ratings["user_id"] == user["id"]]

    if len(user_ratings) >= 5:
        st.subheader("Recommandés pour vous")

        matrix, user_map, movie_map = build_sparse_matrix(ratings)
        sim = compute_item_similarity(matrix)

        rec_ids = recommend_items(
            user["id"],
            ratings,
            matrix,
            user_map,
            movie_map,
            sim,
            30
        )

        recs_personal = movies[movies["id"].isin(rec_ids)]
        recs_personal = recs_personal.sort_values("id").reset_index(drop=True)
        render_grid(recs_personal, source="reco")

    st.subheader("Films populaires")

    recs_pop = get_popular_movies(30)
    render_grid(recs_pop, source="popular")


# =====================================================
# MODAL
# =====================================================
def render_modal_content():
    movie = st.session_state.selected_movie

    if not movie:
        return

    tmdb_id = movie.get("tmdb_id")

    details = get_movie_details(tmdb_id)
    trailer = get_movie_trailer(tmdb_id)

    col1, col2 = st.columns([1, 2])

    with col1:
        poster = get_movie_poster(tmdb_id)
        if poster:
            st.image(poster, width="stretch")
        else:
            st.warning("Image non disponible")

    with col2:
        st.title(movie.get("title", "Unknown"))
        st.write("Genres :", movie.get("genres", "").replace("|", " - "))
        st.write("Année de sortie :", int(movie.get("year", 0)))

        # Synopsis
        if details and details.get("overview"):
            st.markdown("### Synopsis")
            st.write(details["overview"])

        # Trailer
        if trailer:
            st.markdown("### Bande annonce")
            st.video(trailer)

        render_rating_widget(movie, st.session_state.user, source="modal")


if modal.is_open():
    with modal.container():
        render_modal_content()

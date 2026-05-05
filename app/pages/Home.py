import streamlit as st
from recommender import *
from components import movie_card
from tmdb import get_movie_poster

st.set_page_config(layout="wide")

# CSS UI avancé
st.markdown("""
<style>
.movie-card {
    text-align: center;
}

.movie-title {
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 5px;
    height: 2.5em;
    overflow: hidden;
    text-overflow: ellipsis;
}

.poster {
    border-radius: 12px;
    transition: transform 0.2s ease-in-out;
}

.poster:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)


# ---------- UTILS UI ----------

def extract_genres(movies_df):
    genres_set = set()

    for genres in movies_df["genres"]:
        for g in genres.split("|"):
            genres_set.add(g)

    return sorted(genres_set)


def render_movie_card(movie):
    poster = get_movie_poster(movie["tmdb_id"])

    with st.container():
        if poster:
            st.image(poster, use_container_width=True)
        else:
            st.write("")

        st.markdown(
            f"<div class='movie-title'>{movie['title']}</div>",
            unsafe_allow_html=True
        )


def horizontal_scroll_section(movies, title):
    if movies.empty:
        return

    st.markdown(f"## {title}")

    cols = st.columns(8)

    for i, (_, movie) in enumerate(movies.iterrows()):
        with cols[i % 8]:
            render_movie_card(movie)


def grid_section(movies, title):
    if movies.empty:
        st.info("Aucun film trouvé")
        return

    st.markdown(f"## {title}")

    cols_per_row = 5
    rows = [movies[i:i+cols_per_row] for i in range(0, len(movies), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (_, movie) in zip(cols, row.iterrows()):
            with col:
                render_movie_card(movie)


# ---------- DATA ----------

ratings, movies = load_data()

user = st.session_state.get("user")

if not user:
    st.warning("Veuillez vous connecter")
    st.stop()


# ---------- CONTROLES UI ----------

view_mode = st.radio(
    "Affichage",
    ["Scroll", "Grid"],
    horizontal=True
)

search_query = st.text_input("Rechercher un film")

genres = extract_genres(movies)
selected_genre = st.selectbox("Genre", ["Tous"] + genres)


# ---------- FILTRAGE ----------

filtered_movies = movies.copy()

if search_query:
    filtered_movies = filtered_movies[
        filtered_movies["title"].str.contains(search_query, case=False)
    ]

if selected_genre != "Tous":
    filtered_movies = filtered_movies[
        filtered_movies["genres"].str.contains(selected_genre)
    ]


# ---------- PERSONNALISÉ ----------

user_ratings = ratings[ratings["user_id"] == user["id"]]

recs_personal = None

if len(user_ratings) >= 5:
    matrix, user_map, movie_map = build_sparse_matrix(ratings)
    sim = compute_item_similarity(matrix)

    rec_ids = recommend_items(
        user["id"], ratings, matrix, user_map, movie_map, sim, 20
    )

    recs_personal = filtered_movies[
        filtered_movies["id"].isin(rec_ids)
    ]


# ---------- POPULAIRE ----------

recs_pop = get_popular_movies(30)
recs_pop = recs_pop.merge(filtered_movies, on="id")


# ---------- RENDER ----------

# PERSONNALISÉ EN HAUT
if recs_personal is not None and not recs_personal.empty:
    if view_mode == "Scroll":
        horizontal_scroll_section(recs_personal, "Recommandés pour vous")
    else:
        grid_section(recs_personal, "Recommandés pour vous")


# POPULAIRE TOUJOURS
if view_mode == "Scroll":
    horizontal_scroll_section(recs_pop, "Films populaires")
else:
    grid_section(recs_pop, "Films populaires")

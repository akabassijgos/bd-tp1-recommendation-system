import streamlit as st
from recommender import *
from components import horizontal_scroll, movie_card
from utils import extract_genres

st.set_page_config(layout="wide")

ratings, movies = load_data()

user = st.session_state.get("user")

if not user:
    st.warning("Veuillez vous connecter")
    st.stop()


# Recherche
search_query = st.text_input("Rechercher un film")


# Filtre par genre
genres_list = extract_genres(movies)
selected_genre = st.selectbox("Filtrer par genre", ["Tous"] + genres_list)


# Appliquer Recherche et Filtre
filtered_movies = movies.copy()

if search_query:
    filtered_movies = filtered_movies[
        filtered_movies["title"].str.contains(search_query, case=False)
    ]

if selected_genre != "Tous":
    filtered_movies = filtered_movies[
        filtered_movies["genres"].str.contains(selected_genre)
    ]

# Toggle affichage
view_mode = st.radio(
    "Mode d'affichage",
    ["Scroll", "Grid"],
    horizontal=True
)

# Mode recommandation
mode = get_recommendation_mode(user["id"], ratings)

if mode == "popular":
    st.warning("Recommandations générales (popularité)")
    recs = get_popular_movies(20)
    recs = recs.merge(filtered_movies, left_on="id", right_on="id")

else:
    st.success("Recommandations personnalisées")
    matrix, user_map, movie_map = build_sparse_matrix(ratings)
    sim = compute_item_similarity(matrix)

    rec_ids = recommend_items(user["id"], ratings, matrix, user_map, movie_map, sim, 20)
    recs = filtered_movies[filtered_movies["id"].isin(rec_ids)]

# Affichage
if view_mode == "Scroll":
    horizontal_scroll(recs.head(15), "Recommandés pour vous")

else:
    st.subheader("Recommandés pour vous")
    cols = st.columns(5)

    for i, (_, movie) in enumerate(recs.iterrows()):
        with cols[i % 5]:
            movie_card(movie)

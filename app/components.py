import streamlit as st
from utils import get_poster_url


def movie_card(movie, show_title=True):
    poster = get_poster_url(movie["tmdb_id"])

    if poster:
        st.image(poster, use_container_width=True)

    if show_title:
        st.caption(movie["title"])


def horizontal_scroll(movies, title):
    st.subheader(title)

    cols = st.columns(len(movies))

    for col, (_, movie) in zip(cols, movies.iterrows()):
        with col:
            movie_card(movie)

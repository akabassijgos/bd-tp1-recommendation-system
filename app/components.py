import streamlit as st
from tmdb import get_movie_poster


def movie_card(movie, show_title=True):
    poster = get_movie_poster(movie["tmdb_id"])

    if poster:
        st.image(poster, use_container_width=True)
    else:
        st.write("No image")

    if show_title:
        st.caption(movie["title"])


def horizontal_scroll(movies, title):
    if movies.empty:
        st.info("Aucun film trouvé")
        return

    st.markdown(f"### {title}")

    container = st.container()

    with container:
        cols = st.columns(min(len(movies), 10))

        for i, (_, movie) in enumerate(movies.iterrows()):
            with cols[i % len(cols)]:
                movie_card(movie)

import streamlit as st

st.set_page_config(
    page_title="Movie Recommender",
    layout="wide"
)

if "user" not in st.session_state:
    st.session_state.user = None

st.title("Movie Recommendation System")

st.write("Use the sidebar to navigate.")

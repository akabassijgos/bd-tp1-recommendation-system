import streamlit as st
from recommender import *

st.title("Movie Recommendation System")

ratings, movies = load_data()

user = st.session_state.get("user")

if not user:
    st.warning("Please login")
    st.stop()

mode = get_recommendation_mode(user["id"], ratings)

if mode == "popular":
    st.subheader("Trending Movies")
    st.info("General recommendations based on popularity")
    recs = get_popular_movies()

else:
    st.subheader("Recommended for you")
    st.success("Personalized recommendations")
    recs = get_popular_movies()  # temporaire (on branchera item-item ensuite)

for _, row in recs.iterrows():
    st.write(row["title"])

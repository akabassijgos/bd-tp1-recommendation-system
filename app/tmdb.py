import requests
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/movie"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


@st.cache_data
def get_movie_poster(tmdb_id):
    if not tmdb_id:
        return None

    url = f"{BASE_URL}/{tmdb_id}?api_key={API_KEY}"

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        poster_path = data.get("poster_path")

        if poster_path:
            return f"{IMAGE_BASE}{poster_path}"

    except Exception:
        return None

    return None

import sqlite3
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

DB_PATH = "app.db"


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)

    ratings = pd.read_sql("SELECT user_id, movie_id, rating FROM ratings", conn)
    movies = pd.read_sql("SELECT id, title FROM movies", conn)

    conn.close()
    return ratings, movies


@st.cache_data
def build_sparse_matrix(ratings):
    user_ids = ratings["user_id"].unique()
    movie_ids = ratings["movie_id"].unique()

    user_map = {u: i for i, u in enumerate(user_ids)}
    movie_map = {m: i for i, m in enumerate(movie_ids)}

    rows = ratings["user_id"].map(user_map)
    cols = ratings["movie_id"].map(movie_map)

    sparse_matrix = csr_matrix(
        (ratings["rating"], (rows, cols)),
        shape=(len(user_ids), len(movie_ids))
    )

    return sparse_matrix, user_map, movie_map


def compute_item_similarity(sparse_matrix):
    item_matrix = sparse_matrix.T
    similarity = cosine_similarity(item_matrix, dense_output=False)
    return similarity


def recommend_items(user_id, ratings, sparse_matrix, user_map, movie_map, similarity, top_n=10):
    if user_id not in user_map:
        return []

    user_idx = user_map[user_id]
    user_vector = sparse_matrix[user_idx]

    scores = similarity.dot(user_vector.T).toarray().flatten()

    movie_inv_map = {v: k for k, v in movie_map.items()}

    seen_items = set(
        ratings[ratings["user_id"] == user_id]["movie_id"]
    )

    recommendations = []

    for idx in np.argsort(scores)[::-1]:
        movie_id = movie_inv_map[idx]

        if movie_id not in seen_items:
            recommendations.append((movie_id, scores[idx]))

        if len(recommendations) >= top_n:
            break

    return [movie_id for movie_id, _ in recommendations]
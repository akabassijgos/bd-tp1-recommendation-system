import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

from auth import update_profile_picture, delete_all_user_ratings
from ratings import get_user_rating
from tmdb import get_movie_poster
from recommender import load_data


# ---------------- MENU ----------------
with st.sidebar:
    if st.button("Logout"):
        st.session_state.user = None
        st.switch_page("pages/0_Login.py")


# ---------------- CONFIG ----------------
DB_PATH = "app.db"

st.set_page_config(layout="wide")


# ---------------- LOAD USER ----------------
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("pages/0_Login.py")
    st.stop()

user = st.session_state.get("user")


# ---------------- FETCH USER DATA ----------------
def get_user_data(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, email, first_name, last_name,
               profile_picture, birth_date, gender
        FROM users
        WHERE id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    return row


def get_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT rating, movie_id
        FROM ratings
        WHERE user_id = ?
    """, conn, params=(user_id,))

    conn.close()

    if df.empty:
        return 0, 0

    return len(df), df["rating"].mean()


def get_user_history(user_id):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT r.movie_id, r.rating, m.title, m.tmdb_id
        FROM ratings r
        JOIN movies m ON r.movie_id = m.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        LIMIT 12
    """, conn, params=(user_id,))

    conn.close()
    return df


def compute_taste_profile(user_id):
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("""
        SELECT r.rating, m.genres
        FROM ratings r
        JOIN movies m ON r.movie_id = m.id
        WHERE r.user_id = ?
    """, conn, params=(user_id,))

    conn.close()

    if df.empty:
        return pd.DataFrame()

    rows = []

    for _, row in df.iterrows():
        genres = row["genres"].split("|")
        for g in genres:
            rows.append({
                "genre": g.strip(),
                "rating": row["rating"]
            })

    genre_df = pd.DataFrame(rows)

    if genre_df.empty:
        return pd.DataFrame()

    summary = genre_df.groupby("genre").agg(
        avg_rating=("rating", "mean"),
        count=("rating", "count")
    ).reset_index()

    summary = summary.sort_values("avg_rating", ascending=False)

    return summary


# ---------------- UI HEADER ----------------
st.title("Mon profil")

data = get_user_data(user["id"])

user_id, email, first_name, last_name, profile_pic, birth_date, gender = data


# ---------------- PROFILE HEADER ----------------
col1, col2 = st.columns([1, 3])

with col1:
    if profile_pic and os.path.exists(profile_pic):
        st.image(profile_pic, width=150)
    else:
        st.image("https://via.placeholder.com/150", width=150)

    uploaded_file = st.file_uploader("Photo de profil", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        os.makedirs("uploads", exist_ok=True)

        path = f"uploads/user_{user_id}.png"

        with open(path, "wb") as f:
            f.write(uploaded_file.read())

        update_profile_picture(user_id, path)
        st.success("Photo mise à jour")
        st.rerun()


with col2:
    st.subheader("Informations personnelles")

    first_name_in = st.text_input("Prénom", value=first_name or "")
    last_name_in = st.text_input("Nom", value=last_name or "")

    gender_in = st.selectbox(
        "Genre",
        ["", "Homme", "Femme", "Autre"],
        index=["", "Homme", "Femme", "Autre"].index(gender) if gender in ["Homme", "Femme", "Autre"] else 0
    )

    birth_date_in = st.text_input("Date de naissance (YYYY-MM-DD)", value=birth_date or "")

    if st.button("Sauvegarder les informations"):
        from auth import update_user_info

        update_user_info(
            user_id,
            first_name_in,
            last_name_in,
            birth_date_in,
            gender_in
        )

        st.success("Profil mis à jour")
        st.session_state.user = {
            **st.session_state.user,
            "first_name": first_name_in,
            "last_name": last_name_in
        }
        st.rerun()


# ---------------- STATS ----------------
st.markdown("---")

count, avg = get_user_stats(user_id)

c1, c2 = st.columns(2)

c1.metric("Films notés", count)
c2.metric("Note moyenne", round(avg, 2) if count > 0 else "N/A")


# ---------------- TASTE PROFILE ----------------
st.markdown("### 🍿 Profil de goût")

taste = compute_taste_profile(user_id)

if taste.empty:
    st.info("Pas assez de données pour analyser vos goûts")
else:
    top = taste.head(5)

    st.write("Genres préférés :")

    st.bar_chart(
        top.set_index("genre")["avg_rating"]
    )

    fav_genres = ", ".join(top["genre"].tolist())

    st.success(f"Vous aimez principalement : {fav_genres}")


# ---------------- HISTORY ----------------
st.markdown("### 🎬 Films notés récemment")

history = get_user_history(user_id)

if history.empty:
    st.info("Aucun film noté")
else:
    cols = st.columns(4)

    for i, row in enumerate(history.itertuples()):
        with cols[i % 4]:
            poster = get_movie_poster(row.tmdb_id) if row.tmdb_id else None

            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.warning("Image non disponible")

            st.caption(row.title)
            st.write(f"⭐ {row.rating}")


# ---------------- RESET RATINGS ----------------
st.markdown("### ⚠️ Zone de danger")

st.warning("Cette action supprimera toutes vos notes de films.")

confirm = st.checkbox("Je confirme vouloir supprimer toutes mes notes")

if st.button("Supprimer toutes mes notes"):
    if confirm:
        delete_all_user_ratings(user_id)

        # reset cache / session
        st.session_state["refresh_reco"] = True

        st.success("Toutes vos notes ont été supprimées")

        load_data.clear()
        st.rerun()
    else:
        st.error("Veuillez confirmer la suppression")

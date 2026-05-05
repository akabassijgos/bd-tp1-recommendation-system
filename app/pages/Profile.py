import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

from auth import update_profile_picture
from ratings import get_user_rating
from tmdb import get_movie_poster

DB_PATH = "app.db"

st.set_page_config(layout="wide")

# ---------------- LOAD USER ----------------
user = st.session_state.get("user")

if not user:
    st.warning("Veuillez vous connecter")
    st.stop()


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


# ---------------- HISTORY ----------------
st.markdown("### 🎬 Films notés récemment")

history = get_user_history(user_id)

if history.empty:
    st.info("Aucun film noté")
else:
    cols = st.columns(4)

    for i, row in enumerate(history.itertuples()):
        with cols[i % 4]:
            st.image(
                get_movie_poster(row.tmdb_id) if row.tmdb_id else "",
                use_container_width=True
            )
            st.caption(row.title)
            st.write(f"⭐ {row.rating}")

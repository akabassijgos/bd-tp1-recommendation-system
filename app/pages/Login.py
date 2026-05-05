import streamlit as st
from auth import authenticate_user

st.title("Connexion")

email = st.text_input("Email")
password = st.text_input("Mot de passe", type="password")

if st.button("Se connecter"):
    user = authenticate_user(email, password)

    if user:
        st.session_state.user = user
        st.success("Connexion réussie")
    else:
        st.error("Identifiants invalides")

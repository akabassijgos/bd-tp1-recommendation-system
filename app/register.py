import streamlit as st
from auth import create_user

st.title("Créer un compte")

email = st.text_input("Email")
first_name = st.text_input("Prénom")
last_name = st.text_input("Nom")
password = st.text_input("Mot de passe", type="password")

if st.button("Créer"):
    create_user(email, password, first_name, last_name)
    st.success("Compte créé")

import streamlit as st
from auth import create_user

st.set_page_config(layout="centered")

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

st.title("Inscription")

with st.form("register_form"):
    email = st.text_input("Email")
    first_name = st.text_input("Prénom")
    last_name = st.text_input("Nom")
    password = st.text_input("Mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le mot de passe", type="password")

    submitted = st.form_submit_button("Créer un compte")

    if submitted:
        try:
            create_user(
                email,
                password,
                confirm_password,
                first_name,
                last_name
            )
            st.success("Compte créé avec succès")
            st.switch_page("pages/0_Login.py")

        except ValueError as e:
            st.error(str(e))

st.markdown("Déjà un compte ?")
if st.button("Se connecter"):
    st.switch_page("pages/0_Login.py")

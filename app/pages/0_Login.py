import streamlit as st
from user import authenticate_user


if "user" in st.session_state and st.session_state.user is not None:
    st.switch_page("pages/2_Home.py")
    st.stop()


st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="centered")

st.title("Connexion")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    submitted = st.form_submit_button("Se connecter")

    if submitted:
        user = authenticate_user(email, password)
        if user:
            st.session_state.user = user
            st.switch_page("pages/2_Home.py")
        else:
            st.error("Identifiants invalides")

st.markdown("Pas de compte ?")
if st.button("Créer un compte"):
    st.switch_page("pages/1_Register.py")

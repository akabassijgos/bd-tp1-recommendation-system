import streamlit as st
from auth import authenticate_user, create_user

st.markdown("""
<style>
img {
    border-radius: 10px;
}

[data-testid="column"] {
    min-width: 150px;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

def login_ui():
    st.markdown("## Connexion")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")

        submitted = st.form_submit_button("Se connecter")

        if submitted:
            user = authenticate_user(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Identifiants invalides")


def register_ui():
    st.markdown("## Inscription")

    with st.form("register_form"):
        email = st.text_input("Email")
        first_name = st.text_input("Prénom")
        last_name = st.text_input("Nom")
        password = st.text_input("Mot de passe", type="password")

        submitted = st.form_submit_button("Créer un compte")

        if submitted:
            try:
                create_user(email, password, first_name, last_name)
                st.success("Compte créé")
            except Exception as e:
                st.error(str(e))


if st.session_state.user is None:
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        login_ui()

    with tab2:
        register_ui()

    st.stop()

st.success(f"Bienvenue {st.session_state.user['first_name']}")

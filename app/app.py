import streamlit as st

st.set_page_config(layout="wide")

# init session
if "user" not in st.session_state:
    st.session_state.user = None


# ---------------- ROUTING ----------------
if st.session_state.user is None:
    st.switch_page("auth_pages/Login.py")
else:
    st.switch_page("pages/Home.py")

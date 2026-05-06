import streamlit as st

st.set_page_config(layout="wide")

# init session
if "user" not in st.session_state:
    st.session_state.user = None


# ---------------- ROUTING ----------------
if st.session_state.user is None:
    st.switch_page("pages/0_Login.py")
else:
    st.switch_page("pages/2_Home.py")

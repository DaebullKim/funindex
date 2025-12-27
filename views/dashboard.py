import streamlit as st
import streamlit.components.v1 as components

st.title("Tableau 대시보드")
st.write("Tableau Embed Code 받아서 넣어야함")

tableau_embed_code = """
내놔!
"""

# HTML 렌더링
components.html(tableau_embed_code, height=800, scrolling=True)
import streamlit as st

st.set_page_config(layout="wide")

st.title("Hello, you!")

st.write("How are you today my friend?")

st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Python_logo_and_wordmark.svg/486px-Python_logo_and_wordmark.svg.png")

st.button("Let it snow, let it snow, let it snow", on_click=st.snow)

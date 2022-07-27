import streamlit as st
from gsheetsdb import connect
st.write("hello")
conn = connect()
sheet_url = st.secrets["public_gsheets_url"]
st.write(sheet_url)

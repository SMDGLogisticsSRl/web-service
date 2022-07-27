import streamlit as st
from gsheetsdb import connect


# Create a connection object.
conn = connect()

sheet_url = st.secrets["public_gsheets_url"]
rows = conn.execute(query, headers=1)
st.write(sheet_url)

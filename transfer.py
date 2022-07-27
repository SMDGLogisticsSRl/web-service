import streamlit as st
from gsheetsdb import connect

conn = connect()
result = conn.execute("""
    SELECT
        country
      , SUM(cnt)
    FROM
        "https://docs.google.com/spreadsheets/d/1pCrJ9O3T6le6ptl-xUbbdGLhJ_J3SK6zgldJ5MJw6pA/edit?usp=sharing"
    GROUP BY
        country
""", headers=1)

for row in result:
    print(row)

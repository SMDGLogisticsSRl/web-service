import streamlit as st

page_names_to_funcs = {
    "—": "",
    "清关材料制作": "",
    "海关码查询": "",
    "DataFrame Demo": ""
}

demo_name = st.sidebar.selectbox("SMDG精品服务", page_names_to_funcs.keys())

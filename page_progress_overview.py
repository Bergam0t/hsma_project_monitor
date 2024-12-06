import streamlit as st
from datetime import datetime, timezone
import pandas as pd
from supabase import create_client
from streamlit_gsheets import GSheetsConnection
from time import sleep
from streamlit_extras.stylable_container import stylable_container

# Use wide layout
st.set_page_config(layout="wide",
                   page_icon="hsma_icon.png",
                   page_title="HSMA Project Progress Tracker")

# Import stylesheet for font and page margin setting
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.title("Progress Overview")

st.write("Coming Soon!")

col1, col2, col3 = st.columns(3)

col1.subheader("Projects with No Updates Received")



col2.subheader("Projects with Update Overdue")



col3.subheader("Recent Updates")

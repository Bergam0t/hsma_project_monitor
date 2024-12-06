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

st.title("Record Extra Details")

st.write("Coming Soon!")

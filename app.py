import streamlit as st
from datetime import datetime, timezone
import pandas as pd
from time import sleep
from streamlit_extras.stylable_container import stylable_container
from utils import get_gs_connection, init_supabase_connection

pg = st.navigation(
    [st.Page("page_progress_overview.py", title="Project Overview"),
     st.Page("page_progress_explorer.py", title="Progress Explorer"),
     st.Page("page_submit_notes.py", title="Record Extra Details")
     ]
     )

pg.run()

st.session_state.gs_conn = get_gs_connection()
st.session_state.supabase = init_supabase_connection()

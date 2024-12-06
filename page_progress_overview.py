import streamlit as st
from datetime import datetime, timezone
import pandas as pd
from supabase import create_client
from streamlit_gsheets import GSheetsConnection
from time import sleep
from streamlit_extras.stylable_container import stylable_container
from utils import get_gs_connection, init_supabase_connection, get_proj_register_df, get_projects_df

# Use wide layout
st.set_page_config(layout="wide",
                   page_icon="hsma_icon.png",
                   page_title="HSMA Project Progress Tracker")

# Import stylesheet for font and page margin setting
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

if 'gs_conn' not in st.session_state:
    st.session_state.gs_conn = get_gs_connection()
if 'supabase' not in st.session_state:
    st.session_state.supabase = init_supabase_connection()

get_projects_df(st.session_state.supabase)
hsma_proj_reg_df = get_proj_register_df(st.session_state.gs_conn)

most_recent_update = st.session_state.existing_projects.sort_values('created_at', ascending=False).groupby('project_code').head(1)

full_df = pd.merge(
    hsma_proj_reg_df, most_recent_update,
    left_on="Project Code", right_on="project_code", how="left")

st.title("Progress Overview")

st.subheader("Projects with No Updates Received")

no_updates = full_df[full_df["display_date"].isnull()][['Project Code', 'Project Title', 'Lead', 'Lead Org']]

st.write(f"{len(no_updates)} of {len(hsma_proj_reg_df)} projects have had no updates submitted")

st.dataframe(no_updates, hide_index=True, use_container_width=True)

st.subheader("Projects with Update Overdue")

overdue_filter_input = st.number_input("Select to filter to only show projects that haven't had an update in this many days",
                min_value=1, max_value=365, value=30)

full_df['days_since_last_update'] = pd.to_numeric(full_df['days_since_last_update'], errors='coerce')

overdue_df = full_df[full_df["days_since_last_update"] >= overdue_filter_input][['Project Code', 'Project Title', 'Lead', 'Lead Org', 'days_since_last_update', 'display_date']].sort_values('display_date', ascending=True)

if len(overdue_df) > 0:
    st.write(f"{len(overdue_df)} of {len(hsma_proj_reg_df)} projects have an overdue update")
    st.dataframe(overdue_df,
                use_container_width=True, hide_index=True)
else:
    st.success(f"No projects (of those that have had updates) with a last update more than {overdue_filter_input} days ago")


st.subheader("Recent Updates")

st.write("""Note that for now, if a user has submitted an entry via the structured log, only one part of their submission will be shown. This will be fixed in a later version of the app.
         Full project logs can be found on the 'Progress Explorer' Page.""")

st.dataframe(full_df[~full_df["display_date"].isnull()][['Project Code', 'Project Title', 'display_date', 'entry_type', 'entry']].sort_values('display_date', ascending=False),
             use_container_width=True, hide_index=True)

# st.dataframe(st.session_state.existing_projects)
# st.dataframe(most_recent_update)
# st.dataframe(hsma_proj_reg_df)

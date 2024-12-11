import streamlit as st
from supabase import create_client
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Create a Google Sheets Connection
@st.cache_resource
def get_gs_connection():
    return st.connection("gsheets", type=GSheetsConnection)

# Function to initialise a Supabase DB connection from details stored in secrets
@st.cache_resource
def init_supabase_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

@st.cache_data(ttl=10)
def get_proj_register_df(_gs_conn):
    hsma_proj_reg_df = _gs_conn.read()
    hsma_proj_reg_df = hsma_proj_reg_df.sort_values("Project Code")
    hsma_proj_reg_df["Full Project Title"] = hsma_proj_reg_df["Project Code"].astype('str') + ": " + hsma_proj_reg_df["Project Title"]
    hsma_proj_reg_df["Full Project Title and Leads"] = hsma_proj_reg_df["Full Project Title"] + " (" + hsma_proj_reg_df["Lead"] + ")"
    return hsma_proj_reg_df

# Function to grab everything in the Supabase table of project logs
def run_query_main(supabase):
    return supabase.table("ProjectLogs").select("*").execute()

@st.cache_data(ttl=10)
def get_projects_df(_supabase):
    existing_projects = pd.DataFrame(run_query_main(_supabase).data)
    existing_projects["display_date"] = pd.to_datetime(existing_projects["created_at"]).dt.strftime("%A, %B %d %Y at %H:%M")
    existing_projects["update_dt"] = pd.to_datetime(existing_projects["created_at"])
    today = pd.Timestamp.now(tz="UTC").ceil('D')
    existing_projects['days_since_last_update'] = (today - pd.to_datetime(existing_projects["update_dt"])).dt.days

    st.session_state.existing_projects = existing_projects
    return existing_projects

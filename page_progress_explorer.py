import streamlit as st
from datetime import datetime, timezone
import pandas as pd
from time import sleep
from streamlit_extras.stylable_container import stylable_container
from utils import get_gs_connection, init_supabase_connection, get_proj_register_df, get_projects_df

# Use wide layout
st.set_page_config(layout="wide",
                   page_icon="hsma_icon.png",
                   page_title="HSMA Project Progress Tracker")

if 'gs_conn' not in st.session_state:
    st.session_state.gs_conn = get_gs_connection()
if 'supabase' not in st.session_state:
    st.session_state.supabase = init_supabase_connection()
if 'project_code' not in st.session_state:
    st.session_state.project_code = None
if 'existing_projects' not in st.session_state:
    st.session_state.existing_projects = pd.DataFrame()

# Import stylesheet for font and page margin setting
with open("style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.title("Progress Explorer")

get_projects_df(st.session_state.supabase)

hsma_proj_reg_df = get_proj_register_df(st.session_state.gs_conn)
project_list = ["Please Select a Project"]
project_list =  project_list + hsma_proj_reg_df['Full Project Title and Leads'].tolist()

st.session_state.project = st.selectbox(
            """**What Project Do You Want to Explore?**
            \n\nStart typing a project code, title or team member to filter the project list, or scroll down to find your project.
            """,
            project_list,
            help="Note that only projects that have been registered via the 'new project airlock' channel on Slack will appear in this list."
        )

if st.session_state.project != "Please Select a Project":
    st.session_state.project_code = hsma_proj_reg_df[hsma_proj_reg_df['Full Project Title and Leads'] == st.session_state.project]['Project Code'].values[0]
else:
    st.session_state.project_code = None

project_updates = st.session_state.existing_projects[st.session_state.existing_projects["project_code"] == st.session_state.project_code].sort_values("display_date", ascending=False)

project_updates = project_updates[['display_date', 'entry_type', 'submitter', 'entry']].reset_index(drop=True)

if len(project_updates) == 0:
    st.info("No Updates received for this project yet")
elif st.session_state.project == "Please Select a Project":
    st.empty()
else:
    with st.expander("Click here to view as a table"):
        st.dataframe(project_updates,
                     use_container_width=True,
                     column_config={
                         'display_date': 'Display Date',
                         'entry_type': 'Type',
                         'submitter': 'Submitter',
                         'entry': st.column_config.TextColumn(label='Entry', width="large")
                     })

    text_string = ""

    text_string += f"### Project Updates for {st.session_state.project}\n\n"

    for index, row in project_updates.iterrows():
        text_string += f"\n\n{row['display_date']}"
        text_string += f"\n\nSubmitted by {row['submitter']}"
        text_string += f"\n\n**{row['entry_type']}**"
        text_string += f"\n\n{row['entry']}"

        text_string += "\n\n---"

    st.markdown(text_string)

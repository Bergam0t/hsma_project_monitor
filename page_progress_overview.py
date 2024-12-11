import streamlit as st
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta
import pandas as pd
from supabase import create_client
from streamlit_gsheets import GSheetsConnection
from time import sleep
from streamlit_extras.stylable_container import stylable_container
from utils import get_gs_connection, init_supabase_connection, get_proj_register_df, get_projects_df
import plotly.express as px

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
if 'existing_projects' not in st.session_state:
    st.session_state.existing_projects = get_projects_df(st.session_state.supabase)
if 'project_code' not in st.session_state:
    st.session_state.project_code = 9999

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

overdue_filter_input = st.number_input("Select to filter to only show projects that haven't had an update in this many days or more",
                min_value=1, max_value=365, value=30)

full_df['days_since_last_update'] = pd.to_numeric(full_df['days_since_last_update'], errors='coerce')

overdue_df = full_df[full_df["days_since_last_update"] >= overdue_filter_input][['Project Code', 'Project Title', 'Lead', 'Lead Org', 'days_since_last_update', 'display_date']].sort_values('display_date', ascending=True)

if len(overdue_df) > 0:
    st.write(f"{len(overdue_df)} of {len(hsma_proj_reg_df) - len(no_updates)} the projects that have previously had an update are overdue their next update")
    st.dataframe(overdue_df,
                use_container_width=True, hide_index=True)
else:
    st.success(f"No projects (of those that have had updates) with a last update more than {overdue_filter_input} days ago")


st.subheader("Recent Updates")

st.write("""The most recent update received for each project is shown below.
         \n*Note that for now, if a user has submitted an entry via the structured log, only one part of their submission will be shown. This will be fixed in a later version of the app.*
         \nFull project logs can be found on the 'Progress Explorer' Page.""")

st.dataframe(full_df[~full_df["display_date"].isnull()][['Project Code', 'Project Title', 'display_date', 'entry_type', 'entry']].sort_values('display_date', ascending=False),
             use_container_width=True, hide_index=True)

# st.dataframe(st.session_state.existing_projects)
# st.dataframe(most_recent_update)
# st.dataframe(hsma_proj_reg_df)

# st.dataframe(full_df)

full_df["Project Code Str"] = full_df["Project Code"].astype(str)


full_df["Full Project Title Wrapped"] = full_df["Full Project Title"].str.wrap(70).str.replace('\n', "<br>")

fig = px.scatter(full_df, x="update_dt", y="Full Project Title Wrapped",
                            hover_data=["submitter","entry"],
                            color="Project Code Str",
                            height=3000,
                            title="Project Updates for Active Projects Over Time")

fig.update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y",
    range = [date.today() - relativedelta(months=12), date.today() + relativedelta(months=1)]
)

fig.update_layout(showlegend=False,
                  xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="1m",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6m",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="YTD",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="1y",
                     step="year",
                     stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    ))

st.plotly_chart(fig, use_container_width=True)

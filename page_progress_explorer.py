import streamlit as st
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta
import pandas as pd
from time import sleep
from streamlit_extras.stylable_container import stylable_container
from utils import get_gs_connection, init_supabase_connection, get_proj_register_df, get_projects_df
import plotly.express as px

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

filter_projects_with_updates = st.toggle("Filter to only projects with an update", value=False)

if filter_projects_with_updates:
    hsma_proj_reg_df = hsma_proj_reg_df[hsma_proj_reg_df["Project Code"].isin(st.session_state.existing_projects["project_code"].unique())]

sorting = st.radio("Choose sort order", ["By Project Code", "By Last Updated Date (most recent first)"])

most_recent_update = st.session_state.existing_projects.sort_values('created_at', ascending=False).groupby('project_code').head(1)[["project_code", "created_at"]]

if sorting == "By Last Updated Date (most recent first)":
    hsma_proj_reg_df = pd.merge(hsma_proj_reg_df, most_recent_update, left_on="Project Code", right_on="project_code", how="left")
    hsma_proj_reg_df = hsma_proj_reg_df.sort_values("created_at", ascending=False)

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

project_updates_full = st.session_state.existing_projects[st.session_state.existing_projects["project_code"] == st.session_state.project_code].sort_values("display_date", ascending=False)

project_updates = project_updates_full[['display_date', 'entry_type', 'submitter', 'entry']].reset_index(drop=True)

if st.session_state.project == "Please Select a Project":
    st.empty()
elif len(project_updates) == 0:
    st.info("No updates received for this project yet")
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

    st.write("""\n*Note that for now, if a user has submitted an entry via the structured log, each box will be shown as a separate submission. This will be fixed in a later version of the app.*""")

    fig = px.scatter(project_updates_full, x="update_dt", y="entry_type",
                               hover_data=["submitter","entry"],
                               color="submitter")

    fig.update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y",
        range = [date.today() - relativedelta(months=12), date.today() + relativedelta(months=1)]
    )

    fig.update_layout(showlegend=True,
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

    st.plotly_chart(fig)

    text_string = ""

    text_string += f"### Project Updates for {st.session_state.project}\n\n"

    for index, row in project_updates.iterrows():
        text_string += f"\n\n{row['display_date']}"
        text_string += f"\n\nSubmitted by {row['submitter']}"
        text_string += f"\n\n**{row['entry_type']}**"
        text_string += f"\n\n{row['entry']}"

        text_string += "\n\n---"

    st.markdown(text_string)

import streamlit as st
st.set_page_config(page_title="TheTransitClock", layout="wide")

import streamlit_debug
streamlit_debug.set(flag=False, wait_for_client=True, host='localhost', port=8765)

import env
env.verify()

from authlib.auth import auth, authenticated, requires_auth
from authlib.common import trace_activity

st.title("The Transit Clock")
user = auth(sidebar=False, show_msgs=False)

# Custom imports 
from multipage import MultiPage
from pages import api, schdAhr, positionByRoutes, reports, status, extentions, allPositions # import your pages here
from streamlit_autorefresh import st_autorefresh

count = st_autorefresh(interval=20000, key="auto")


# Create an instance of the app 
app = MultiPage()
if authenticated():
    app.add_page("Vehicles by Route", positionByRoutes.app)
    app.add_page("Vehicle positions", allPositions.app)
    app.add_page("Schedule Adherance", schdAhr.app)
    app.add_page("Reports", reports.app)
    #app.add_page("Status", status.app)
    #app.add_page("API",api.app)
    #app.add_page("Extentions",extentions.app)

    # The main app
    app.run()
    hide_st_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
    st.markdown(hide_st_style, unsafe_allow_html=True)
else:
    st.warning(f'Not authenticated')

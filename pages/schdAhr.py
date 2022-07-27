from streamlit_folium import folium_static
import streamlit as st

from map_utils import *

#@st.cache
def app():

    st.title("Schedule adherance map")
    try:
        m = createScheduleAherance(assignedStatus = True)
        folium_static(m)
    except:
        st.write("No Data returned for currently assigned vehicle status")


# Import necessary libraries
from map_utils import *
import streamlit as st
from streamlit_folium import folium_static
from folium.plugins import Fullscreen
import time

from streamlit_autorefresh import st_autorefresh
count = st_autorefresh(interval=20000, key="autor")

def app():
    """This application helps in running machine learning models without having to write explicit code 
    by the user. It runs some basic models and let's the user select the X and y variables. 
    """
    st.title("Live vehicle positions")
    vehicleStatus = st.radio("Select vehicle status",("all","assigned"))
    if count % 20 == 0:
        try:
            if vehicleStatus == "all":
                m = folium_static(getLivePositions(assignedStatus = False))
                m
            elif vehicleStatus == "assigned":
                m = folium_static(getLivePositions(assignedStatus = True))
                m
        except:
            st.title("No data returned by APIs")

import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import Fullscreen
import pandas as pd

from map_utils import *

#@st.cache
def app():
    st.title("Vehicles on Route details")    
    routeMaster = getRouteIds()
    option = st.selectbox("Select Route",routeMaster.keys())

    #Get and parse raw data
    df_forward, df_vehicles,  geojson = parse_routes(routeMaster[option])

    m = folium.Map(
    location=[df_forward["lat"].mean(), df_forward["lon"].mean()],
    zoom_start=10)

    folium.GeoJson(geojson, name="geojson").add_to(m)

    bus_icon = "https://www.svgrepo.com/show/33642/bus.svg"

    for index, row in df_vehicles.iterrows():
        gps_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((row["loc.time"] + 3600)))
        popup = f'<div class="leaflet-popup-content" style="width: 301px;"><b>Vehicle:</b> {row["id"]} <br><b>Route:</b> {row["routeName"]} <br><b>Longitude:</b> {row["loc.lon"]} <br><b>Lattitude:</b> {row["loc.lat"]} <br><b>Heading:</b> {row["loc.heading"]} <br><b>Going To:</b> {row["headsign"]} <br><b>Schedule stat:</b> {row["schAdhStr"]} <br><b>Direction:</b> {row["direction"]} <br><b>GPS Time:</b> {gps_time} <br><b>Block:</b> {row["block"]} <br><b>Next Stop:</b> {row["nextStopName"]} </div>'
        folium.Marker(
        location=[row["loc.lat"], row["loc.lon"]],
        popup=popup,
        icon = folium.features.CustomIcon(bus_icon,icon_size=(44, 40))
        ).add_to(m)

    icon_url = "https://www.svgrepo.com/show/130693/bus-stop.svg"
    for index, row in df_forward.iterrows():
        popup = f'<div class="leaflet-popup-content" style="width: 301px;"><b>Stop name:</b> {row["name"]} <br><b>Lat:</b> {row["lat"]} <br><b>Lon:</b> {row["lon"]} <br><b> </div>'
        folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=popup,
        icon = folium.features.CustomIcon(icon_url),
        ).add_to(m)
    Fullscreen().add_to(m)
    folium_static(m)

import requests
import folium
import time
import numpy as np
import streamlit as st
from streamlit_keplergl import keplergl_static
from folium.plugins import Fullscreen
from keplergl import KeplerGl
import json
import time
import pandas as pd
from configparser import ConfigParser

config = ConfigParser()
config.read("transitimeconf.ini")
transitimeServer = f'{config["main"]["api_url"]}/{config["main"]["auth_key"]}' 

headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest'}

@st.experimental_singleton(show_spinner=False)
def getRouteIds():
    url = transitimeServer + "/command/routes" 
    routes = requests.get(url, headers=headers, verify=False)
    routes = routes.json()
    routeIds = [i["name"] for i in routes["routes"]]
    dictMapping = {}
    for i in routeIds:
        dictMapping[i] = i.split(" - ")[0]
    return dictMapping

@st.experimental_singleton(show_spinner=False)
def getVehicleIds():
    url = transitimeServer + "/command/vehicleIds"
    response = requests.get(url, headers=headers)
    return response.json()

def getVehiclesStatus():
    url = transitimeServer + "command/vehicleDetails"
    params = (
        ('r', ''),
        ('onlyAssigned', 'true'),
    )

    response = requests.get(url, headers=headers, params=params)
    assignedVehicles =  [i["id"] for i in response.json()["vehicles"]]
    allVehicles = getVehicleIds()
    unassignedVehicles = [i for i in allVehicles["ids"] if i not in assignedVehicles]
    return assignedVehicles, unassignedVehicles


@st.experimental_singleton(show_spinner=False)
def getVehicleDetails(vehicleStatus = "unassigned"):
    url = transitimeServer + "command/vehicleDetails"
    assigned, unassigned = getVehiclesStatus()

    if vehicleStatus == "assigned":
        vehicleIds = assigned
    elif vehicleStatus == "all" :
        vehicleIds = getVehicleIds()["ids"]
    else:
        vehicleIds = unassigned

    params = (
        ('r', ''),
        ('v', vehicleIds ),
        ('onlyAssigned', 'false'),
    )

    response = requests.get(url, headers=headers, params=params)
    return response.json()



def getVehicleDetailsOnRoute(routeId):
    url = transitimeServer + "command/vehicleDetails"

    params = (
        ('r', routeId),
    )

    response = requests.get(url, headers=headers, params=params, verify=False)
    vehiclesOnRoute = pd.json_normalize(response.json()["vehicles"])
    vehiclesOnRoute["icon"] = "car"

    return vehiclesOnRoute

@st.experimental_singleton(show_spinner=False)
def getRouteDetails(routeIds):
    url = transitimeServer + "/command/routeDetails"
    headers = {'accept': 'application/json'}

    params = (
        ('r', routeIds),
    )

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()["routes"]
    else:
        return None

@st.experimental_singleton(show_spinner=False)
def generate_route_geojson(title,coordinates):
    geojson = {
          "type": "FeatureCollection",
          "features": [
            {
              "type": "Feature",
              "properties": {
                "direction": title
              },
              "geometry": {
                "type": "LineString",
                "coordinates": coordinates

              }
            }
          ]
        }

    return geojson

@st.experimental_singleton(show_spinner=False)
def parse_routes(routeId,rid=0):
    raw_data = getRouteDetails(routeId)


    df_forward = pd.DataFrame(raw_data[0]["direction"][rid]["stop"])
    coordinates_forward = [[i["lon"],i["lat"],0,0] for i in raw_data[0]["shape"][0]["loc"]]

    geojson = generate_route_geojson(raw_data[0]["direction"][rid]["title"],coordinates_forward)

    #df_reverse = pd.DataFrame(raw_data[0]["direction"][1]["stop"])
    #coordinates_reverse = [[i["lon"],i["lat"],0,0] for i in raw_data[0]["shape"][1]["loc"]]
    df_forward["icon"] = "place"

    df_vehicles = getVehicleDetailsOnRoute(routeId) 

    return df_forward, df_vehicles,  geojson


def getSchdAdhrDf():
    url = transitimeServer + "/command/vehicleDetails"
    params = (
    ('onlyAssigned', 'true'),
    )

    response = requests.get(url, headers=headers, params=params, verify=False)

    raw_data = response.json()["vehicles"]

    for i in raw_data:
        if "early" in i["schAdhStr"]:
            i["status"] = 1
        elif "late" in i["schAdhStr"]:
            i["status"] = -1
        else:
            i["status"] = 0

    df = pd.json_normalize(raw_data)
    df["schAdh"] = abs(df["schAdh"].astype(int))
    df.drop(["routeId","routeShortName","blockMthd","isCanceled","isAtStop","nextStopId","isScheduledService"], axis=1,inplace=True)

    return df


def createScheduleAherance(assignedStatus = True):

    url = transitimeServer + "/command/vehicleDetails"
    params = (
    ('onlyAssigned', assignedStatus),
    )

    response = requests.get(url, headers=headers, params=params, verify=False)

    raw_data = response.json()["vehicles"]

    df = pd.json_normalize(raw_data)
    df['radiusNormalized'] = df.apply((lambda x: x["schAdh"]/500/60), axis=1)
    #df.drop(["routeId","routeShortName","blockMthd","isCanceled","isAtStop","nextStopId","isScheduledService"], axis=1,inplace=True)

    m = folium.Map(
        location=[df["loc.lat"].mean(), df["loc.lon"].mean()],
        tiles ='OpenStreetMap',
        zoom_start=9
    )


    for index, row in df.iterrows():

        if row["schAdh"] > 60000:
            circler_color = "red"
        elif row["schAdh"] < -180000:
            circler_color = "yellow"
        else:
            circler_color = "green"

        #popup = f'{row["id"]} : {row["schAdhStr"]}'
        popup = f'<div class="leaflet-popup-content" style="width: 301px;"><b>Vehicle:</b> {row["id"]} <br><b>Route:</b> {row["routeName"]} <br><b>Going To:</b> {row["headsign"]} <br><b>Schedule stat:</b> {row["schAdhStr"]} <br><b>Block:</b> {row["block"]} <br><b>Next Stop:</b> {row["nextStopName"]} </div>'

        folium.CircleMarker([row["loc.lat"], row["loc.lon"]],
                            radius=abs(row['radiusNormalized']) + 5,
                            popup=popup,
                            color=circler_color,
                            fill=True,
                            fill_opacity=0.7,
                            parse_html=False).add_to(m)
    Fullscreen().add_to(m)

    return m



def getLivePositions(assignedStatus = False):
    url = transitimeServer + "/command/vehicleDetails"
    headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    }

    params = (
        ('onlyAssigned', assignedStatus),
        )

    response = requests.get(url, headers=headers, params=params, verify=False)

    raw_data = response.json()["vehicles"]

    df = pd.json_normalize(raw_data)

    m = folium.Map(
    location=[df["loc.lat"].mean(), df["loc.lon"].mean()])
    #zoom_start=8)
    bus_icon = "https://www.svgrepo.com/show/33642/bus.svg"
    for index, row in df.iterrows():
        gps_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((row["loc.time"] + 3600)))
        popup = f'<div class="leaflet-popup-content" style="width: 301px;"><b>Vehicle:</b> {row["id"]} <br><b>Route:</b> {row["routeName"]} <br><b>Longitude:</b> {row["loc.lon"]} <br><b>Lattitude:</b> {row["loc.lat"]} <br><b>Heading:</b> {row["loc.heading"]} <br><b>Going To:</b> {row["headsign"]} <br><b>Schedule stat:</b> {row["schAdhStr"]} <br><b>Direction:</b> {row["direction"]} <br><b>GPS Time:</b> {gps_time} <br><b>Block:</b> {row["block"]} <br><b>Next Stop:</b> {row["nextStopName"]} </div>'
        folium.Marker(
        location=[row["loc.lat"], row["loc.lon"]],
        popup=popup,
        icon = folium.features.CustomIcon(bus_icon)
        #icon=folium.Icon(color="red", icon="info-sign")
        #icon=folium.Icon(icon_size=(4,4),colour = "blue")
        ).add_to(m)

    Fullscreen().add_to(m)
    return m

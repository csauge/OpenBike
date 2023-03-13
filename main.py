import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium


@st.cache_data(ttl=300)  # Every 5 minutes
def get_station_status():
    url_station_status = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json"
    data = requests.get(url_station_status).json()
    df_station_status = pd.json_normalize(data["data"]["stations"])
    df_station_status[['mechanical', 'ebike']] = df_station_status['num_bikes_available_types'].apply(lambda x: pd.Series([x[0]["mechanical"], x[1]["ebike"]]))
    return df_station_status.drop(columns=["stationCode", "numBikesAvailable", "numDocksAvailable", "num_bikes_available_types"])

@st.cache_data(ttl=3600)  # Every hour
def get_station_info():
    url_station_info = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_information.json"
    data = requests.get(url_station_info).json()
    df_station_info = pd.json_normalize(data["data"]["stations"])
    return df_station_info.drop(columns=["stationCode"])

df = pd.merge(get_station_info(), get_station_status(), on="station_id").set_index("station_id")
st.write(df)

def get_map(df):
    m = folium.Map(control_scale=True)
    for row in df.itertuples():
        html = (
            f"<b>{row.name}</b><br>"
        )
        folium.Marker(
            location=[row.lat, row.lon],
            popup=folium.Popup(html, min_width=400, max_width=400),
            tooltip=row.name,
        ).add_to(m)

    # Centrage de la carte en fonctions des stations
    df_loc = df[["lat", "lon"]]
    south_west = df_loc.min().values.tolist()
    north_east = df_loc.max().values.tolist()
    m.fit_bounds([south_west, north_east])
    return m

#st_folium(get_map(df))
st.map(df)





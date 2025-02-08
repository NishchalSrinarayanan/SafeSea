import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import zipfile
import os
import random
import requests
from datetime import datetime

# Function to load CSV from a local zip file
@st.cache_data
def load_csv_from_zip(zip_file_path):
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as z:
            csv_file_name = [f for f in z.namelist() if f.endswith('.csv')][0]
            with z.open(csv_file_name) as f:
                df = pd.read_csv(f, low_memory=False)
        return df
    except Exception as e:
        st.error(f"Error loading CSV from zip file: {e}")
        st.stop()

# Load Data
zip_file_path = 'Book3.zip'
if os.path.exists(zip_file_path):
    df = load_csv_from_zip(zip_file_path)
    df = df.head(100)
else:
    st.error(f"Zip file '{zip_file_path}' not found!")
    st.stop()

# Identify latitude and longitude columns
lat_col, lon_col = "latitude", "longitude"
df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
df = df.dropna(subset=[lat_col, lon_col])

if df.empty:
    st.error("No valid latitude/longitude data.")
    st.stop()

st.write(f"Loaded {df.shape[0]} coral locations.")

# Function to randomly zoom to a coral
def zoom_to_random():
    random_coral = df.sample(1).iloc[0]
    return [random_coral[lat_col], random_coral[lon_col]]

# Simulate WiFi signal detection (Replace this with actual WebSocket/API call)
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Set markers for sailors
def get_sailor_markers():
    markers = []
    for _ in range(100):
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        markers.append([lat, lon])
    return markers

# Reset the sailor markers every hour
current_time = datetime.now()
if 'last_marker_reset' not in st.session_state or current_time.hour != st.session_state.last_marker_reset:
    st.session_state.sailor_markers = get_sailor_markers()
    st.session_state.last_marker_reset = current_time.hour

# Function to get the user's location based on their IP
def get_user_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        loc = data['loc'].split(',')
        return [float(loc[0]), float(loc[1])]
    except:
        return [0, 0]  # Default location if the API fails

# Home Page
if st.session_state.page == 'home':
    st.title("Welcome to SafeSea")
    col1, col2 = st.columns(2)
    
    if col1.button("I am a Sailor", key="sailor"):
        st.session_state.page = 'sailor_checkin'
    if col2.button("I am a Diver", key="diver"):
        st.session_state.page = 'diver_checkin'

# Sailor Check-in Page
elif st.session_state.page == 'sailor_checkin':
    st.title("Sailor Check-in")
    st.write("Please enter your details:")
    sailor_name = st.text_input("Name")
    if st.button("Submit Check-in", key="submit_sailor"):
        st.write(f"Thank you, {sailor_name}! Your check-in is complete.")
        st.session_state.page = 'map'

# Diver Check-in Page (Placeholder)
elif st.session_state.page == 'diver_checkin':
    st.title("Diver Check-in (Coming Soon!)")
    st.write("This page is under development.")
    if st.button("Go Back", key="go_back"):
        st.session_state.page = 'home'

# Map Page
elif st.session_state.page == 'map':
    st.title("Coral Map")

    # Get the user's location
    user_location = get_user_location()

    # Default map location
    default_location = [df[lat_col].mean(), df[lon_col].mean()]
    map_location = st.session_state.get("zoom_location", default_location)

    # Create map
    m = folium.Map(location=map_location, zoom_start=8)
    marker_cluster = MarkerCluster().add_to(m)

    # Add coral locations
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row[lat_col], row[lon_col]],
            radius=5,
            color='red',
            fill=True,
            fill_color='red'
        ).add_to(marker_cluster)

    # Add sailor markers
    for lat, lon in st.session_state.sailor_markers:
        folium.Marker([lat, lon], popup="Sailor Location").add_to(marker_cluster)

    # Pinpoint user's location on the map
    folium.Marker(user_location, popup="Your Location", icon=folium.Icon(color='blue')).add_to(m)

    st_folium(m, width=700, height=500)

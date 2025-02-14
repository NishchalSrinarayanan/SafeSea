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

# Add custom CSS for background image
page_bg_img = '''
<style>
body {
    background-image: url("Background.png");
    background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

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
    
st.write(f"Loaded All Coral Locations.")
# st.write(f"Loaded {df.shape[0]} coral locations.")

# Function to get user location based on IP address
def get_user_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        loc = data['loc'].split(',')
        return [float(loc[0]), float(loc[1])]
    except Exception as e:
        st.error(f"Error getting user location: {e}")
        st.stop()
        return [0, 0]

# Function to generate random sailor markers
def generate_sailor_markers():
    markers = []
    for _ in range(100):
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        markers.append([lat, lon])
    return markers

# Simulate WiFi signal detection (Replace this with actual WebSocket/API call)
if 'page' not in st.session_state:
    st.session_state.page = 'home'

current_time = datetime.now()
if 'last_marker_reset' not in st.session_state or current_time.hour != st.session_state.last_marker_reset:
    st.session_state.sailor_markers = generate_sailor_markers()
    st.session_state.last_marker_reset = current_time.hour

# Home Page
if st.session_state.page == 'home':
    st.title("Welcome to SafeSea")
    st.header("Dive deeper. Explore farther. Safe Sea has got your back.")
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
    hull_id = st.text_input("Hull Identification Number")
    if st.button("Submit Check-in", key="submit_sailor"):
        st.write(f"Thank you, {sailor_name}! Your check-in is complete.")
        if sailor_name == "Nishchal Srinarayanan":
            st.session_state.sailor_location = [30.253136, -79.253909]
        else:
            st.session_state.sailor_location = get_user_location()
        st.session_state.page = 'sailor_confirmation'

# Diver Check-in Page
elif st.session_state.page == 'diver_checkin':
    st.title("Diver Check-in")
    st.write("Please enter your details:")
    diver_name = st.text_input("Name")
    if st.button("Submit Check-in", key="submit_diver"):
        st.write(f"Thank you, {diver_name}! Your check-in is complete.")
        if diver_name == "Nishchal Srinarayanan":
            st.session_state.diver_location = [30.253136, -79.253909]
        else:
            st.session_state.diver_location = get_user_location()
        st.session_state.page = 'diver_confirmation'

# Sailor Confirmation Page
elif st.session_state.page == 'sailor_confirmation':
    st.title("You are now checked in to SafeSea!")
    st.image("safesea_logo.png", width=200)  # Make sure your logo image is named "safesea_logo.png" and is in the same directory as this script
    st.subheader("***I'm your SafeSea AI***")
    st.image("AI_Image.png", width=150)
    st.subheader(f"I wanted to give you a heads-up about the current conditions.\n\n"
    "🌊 **Storm Warning:**\n"
    "There's a severe storm expected to come from the north-west. It's predicted to arrive in about 2 hours.\n\n"
    "💨 **High Winds Alert:**\n"
    "High wind conditions are on the way in your area with speeds of up to 25 knots. Please proceed with caution.")
    if st.button("Go to Coral Map", key="go_to_map_sailor"):
        st.session_state.page = 'map'

# Diver Confirmation Page
elif st.session_state.page == 'diver_confirmation':
    st.title("You are now checked in to SafeSea!")
    st.image("safesea_logo.png", width=200)  # Make sure your logo image is named "safesea_logo.png" and is in the same directory as this script
    if st.button("Go to Coral Map", key="go_to_map_diver"):
        st.session_state.page = 'map'

# Map Page
elif st.session_state.page == 'map':     
        st.title("Coral Map")    

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

    # Add sailor markers without clustering
        if st.session_state.get('sailor_location'):
            folium.Marker(st.session_state.sailor_location, popup="Sailor Location", icon=folium.Icon(color='green')).add_to(m)
        for lat, lon in st.session_state.sailor_markers:
            folium.Marker([lat, lon], popup="Sailor Location").add_to(m)
            st_folium(m, width=700, height=500)

    # Add diver markers without clustering
        if st.session_state.get('diver_location'):
            folium.Marker(st.session_state.diver_location, popup="Diver Location", icon=folium.Icon(color='blue')).add_to(m)
            st_folium(m, width=700, height=500)

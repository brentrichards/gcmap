import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import googlemaps
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load data
train_stations = pd.read_csv("gold_coast_train_stations.csv")
tram_stops = pd.read_csv("gold_coast_tram_stops.csv")
hospitals = pd.read_csv("queensland_hospitals.csv")

# Constants
def get_coordinates(address):
    geolocator = Nominatim(user_agent="geoapi", timeout=10)
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        st.error(f"Geocoding service is unavailable: {e}")
        return None

@st.cache_data
def cached_calculate_route_distance(coord1, coord2, mode):
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))
    try:
        result = gmaps.distance_matrix(origins=[coord1], destinations=[coord2], mode=mode)
        distance = result['rows'][0]['elements'][0]['distance']['value'] / 1000  # Convert meters to kilometers
        return distance
    except Exception as e:
        st.error(f"Error calculating route distance: {e}")
        return None

def calculate_route_distance(coord1, coord2):
    driving_distance = cached_calculate_route_distance(coord1, coord2, mode="driving")
    if driving_distance is not None and driving_distance < 1:
        walking_distance = cached_calculate_route_distance(coord1, coord2, mode="walking")
        return walking_distance
    return driving_distance

def find_nearest(location, data):
    distances = data.apply(lambda row: calculate_route_distance(location, (row['Latitude'], row['Longitude'])), axis=1)
    nearest_index = distances.idxmin()
    return data.iloc[nearest_index], distances[nearest_index]

# Streamlit app
st.title("Gold Coast Distance Calculator")

# User input
st.write("Enter your address (Gold Coast, QLD):")
col1, col2 = st.columns(2)
with col1:
    street = st.text_input("Street:", placeholder="1 hospital boulevard")
with col2:
    suburb = st.text_input("Suburb:", placeholder="southport")

# Ensure the default index is a Python int
default_hospital_index = hospitals[hospitals["Hospital"] == "Princess Alexandra Hospital"].index
if not default_hospital_index.empty:
    default_index = int(default_hospital_index[0])
else:
    default_index = 0

# Dropdown for hospital selection
hospital_name = st.selectbox("Select a hospital:", hospitals["Hospital"], index=default_index)
hospital_coords = (hospitals.loc[hospitals["Hospital"] == hospital_name, "Latitude"].values[0],
                   hospitals.loc[hospitals["Hospital"] == hospital_name, "Longitude"].values[0])

if street and suburb:
    user_address = f"{street}, {suburb}, Gold Coast, QLD"
    user_coords = get_coordinates(user_address)
    if user_coords:
        # Calculate distance to selected hospital
        hospital_distance = calculate_route_distance(user_coords, hospital_coords)
        st.write(f"Distance to {hospital_name}: {hospital_distance:.2f} km")

        # Find nearest and next nearest train stations
        train_distances = train_stations.apply(lambda row: calculate_route_distance(user_coords, (row['Latitude'], row['Longitude'])), axis=1)
        nearest_train_indices = train_distances.nsmallest(2).index
        nearest_train_1 = train_stations.iloc[nearest_train_indices[0]]
        nearest_train_2 = train_stations.iloc[nearest_train_indices[1]]
        st.write(f"Nearest Train Station: {nearest_train_1['Station']} ({train_distances[nearest_train_indices[0]]:.2f} km)")
        st.write(f"Next Nearest Train Station: {nearest_train_2['Station']} ({train_distances[nearest_train_indices[1]]:.2f} km)")

        # Find nearest and next nearest tram stops
        tram_distances = tram_stops.apply(lambda row: calculate_route_distance(user_coords, (row['Latitude'], row['Longitude'])), axis=1)
        nearest_tram_indices = tram_distances.nsmallest(2).index
        nearest_tram_1 = tram_stops.iloc[nearest_tram_indices[0]]
        nearest_tram_2 = tram_stops.iloc[nearest_tram_indices[1]]
        st.write(f"Nearest Tram Stop: {nearest_tram_1['Tram Stop']} ({tram_distances[nearest_tram_indices[0]]:.2f} km)")
        st.write(f"Next Nearest Tram Stop: {nearest_tram_2['Tram Stop']} ({tram_distances[nearest_tram_indices[1]]:.2f} km)")

        # Create a map
        map_center = user_coords
        map_object = folium.Map(location=map_center, zoom_start=12)

        # Add user location
        folium.Marker(user_coords, popup="Your Location", icon=folium.Icon(color='blue')).add_to(map_object)

        # Add selected hospital location
        folium.Marker(hospital_coords, popup=hospital_name, icon=folium.Icon(color='red')).add_to(map_object)

        # Add nearest train stations
        folium.Marker((nearest_train_1['Latitude'], nearest_train_1['Longitude']),
                      popup=f"Train Station: {nearest_train_1['Station']}",
                      icon=folium.Icon(color='green')).add_to(map_object)
        folium.Marker((nearest_train_2['Latitude'], nearest_train_2['Longitude']),
                      popup=f"Train Station: {nearest_train_2['Station']}",
                      icon=folium.Icon(color='darkgreen')).add_to(map_object)

        # Add nearest tram stops
        folium.Marker((nearest_tram_1['Latitude'], nearest_tram_1['Longitude']),
                      popup=f"Tram Stop: {nearest_tram_1['Tram Stop']}",
                      icon=folium.Icon(color='orange')).add_to(map_object)
        folium.Marker((nearest_tram_2['Latitude'], nearest_tram_2['Longitude']),
                      popup=f"Tram Stop: {nearest_tram_2['Tram Stop']}",
                      icon=folium.Icon(color='orange')).add_to(map_object)

        # Display the map in Streamlit
        st_folium(map_object, width=700, height=500)

        # Add links below the map
        st.markdown("### Useful Links")
        st.markdown("- [Gold Coast to Brisbane Train Timetable](https://jp.translink.com.au/plan-your-journey/timetables/train/T/gold-coast-line)")
        st.markdown("- [Gold Coast Bus and Tram Network Map](https://translink.widen.net/s/2hzwft5bhv/240923-gold-coast-network-map)")
        st.markdown("- [Gold Coast High Frequency Bus and Tram Network Map](https://translink.widen.net/s/pwds2jqbvr/220329-gold-coast-high-frequency)")
    else:
        st.error("Could not find the location. Please check the address and try again.")
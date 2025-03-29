# Gold Coast Distance Calculator (app.py)

`app.py` is a Streamlit application that calculates the distance from a user-provided address to a selected hospital in Queensland. It also identifies the nearest and next-nearest train stations and tram stops to the user's location. The application provides an interactive map to visualize these locations and their distances.

## Features

- **Hospital Selection**: Choose a hospital from a dropdown list populated from `queensland_hospitals.csv`. The default hospital is "Princess Alexandra Hospital."
- **Distance Calculation**: Calculates driving or walking distances from the user's address to the selected hospital.
- **Nearest Locations**: Identifies the nearest and next-nearest train stations and tram stops.
- **Interactive Map**: Displays the user's location, the selected hospital, and the nearest train and tram stops on an interactive map.
- **Useful Links**: Provides links to public transport timetables and network maps.

## Files Used

- `gold_coast_train_stations.csv`: Contains data on train station locations.
- `gold_coast_tram_stops.csv`: Contains data on tram stop locations.
- `queensland_hospitals.csv`: Contains data on hospital names and their coordinates.

## How to Run

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up the `.env` file with your Google Maps API key:
   ```
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open the application in your browser and enter your address (street and suburb) to calculate distances and view the map.

## Notes

- Ensure that the Google Maps Distance Matrix API is enabled for your API key.
- The application uses cached results to improve performance and reduce redundant API calls.

## Example

1. Enter your street and suburb (e.g., "1 hospital boulevard" and "southport").
2. Select a hospital from the dropdown list (e.g., "Gold Coast University Hospital").
3. View the calculated distances and the interactive map showing your location, the hospital, and nearby train and tram stops.

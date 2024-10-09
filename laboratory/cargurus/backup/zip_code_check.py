import requests
import json

# Initialize the zip code and country code
zip_code = '77008'
country_code = 'us'
api_key = '4b84ff4ad9a74c79ad4a1a945a4e5be1'  # Replace with your OpenCage API key

# Construct the API URL
url = f"https://api.opencagedata.com/geocode/v1/json?q={zip_code},{country_code}&key={api_key}"

response = requests.get(url)

zip_location_data = response.json()

# Check if the geometry data exists
if 'results' in zip_location_data and len(zip_location_data['results']) > 0 and 'geometry' in zip_location_data['results'][0]:
    latitude = zip_location_data['results'][0]['geometry']['lat']
    longitude = zip_location_data['results'][0]['geometry']['lng']
    city_name = zip_location_data['results'][0]['components'].get('city', '')
    
    # Print the results
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")
    print(f"City Name: {city_name}")
else:
    print("No location data found")
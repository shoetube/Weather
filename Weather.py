#!/usr/bin/python3
import requests
from geopy.geocoders import Nominatim
from datetime import datetime


def celsiusToFahrenheit(temperature):
    return (temperature * 9/5) + 32


input_location = 'Encino, CA'  # Location input
geolocator = Nominatim(user_agent="app")  # Set app name for Nominatim
latitude = round(geolocator.geocode(input_location).latitude, 4)
longitude = round(geolocator.geocode(input_location).longitude, 4)

# Find the first weather station associated with coordinates
find_station = requests.get(
    f"https://api.weather.gov/points/{latitude},{longitude}/stations")

# Get information about station
station = requests.get(find_station.json()['features'][0]['properties']['@id'])
location = station.json()['properties']['name']

# Get station observation data
observation = requests.get(
        find_station.json()['features'][0]['properties']['@id'] +
        '/observations/latest')

# Get temperature value from station
raw_temp = observation.json()['properties']['temperature']['value']
temp = round(celsiusToFahrenheit(raw_temp), 1)

# Obtain weather report time stamp
raw_time_stamp = observation.json()['properties']['timestamp']
formatted_time_stamp = raw_time_stamp[:-3] + raw_time_stamp[-2:]
utc_time = datetime.strptime(formatted_time_stamp, '%Y-%m-%dT%H:%M:%S%z')

local_time = utc_time.astimezone()  # Convert to local timezone

print(f'At {local_time.strftime("%I:%M %p")}, the temperature at {location}'
      f' was {temp}\u00b0F!')

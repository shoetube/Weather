#!/usr/bin/python3
import requests
from geopy.geocoders import Nominatim
from datetime import datetime
from sys import exit
from sys import argv
from os import path


def precision_four(func):
    def wrapper(arg1, arg2):
        return round(func(arg1, arg2), 4)
    return wrapper


def get_location(program_directory):
    if len(argv) > 1:
        input_location = ' '.join(argv[1:])
    else:
        is_config_file = True
        try:
            iFile = open(f'{program_directory}/.weatherconfig')
        except IOError:
            print('No ".weatherconfig" file detected.')
            is_config_file = False
        finally:
            if is_config_file:
                input_location = iFile.read().strip()
                iFile.close()
            else:
                input_location = input(
                    "For which location would you like weather information?\n")
    return input_location


def celsiusToFahrenheit(temperature):
    return (temperature * 9/5) + 32


def format_time(time_stamp):
    return time_stamp.strftime("%I:%M %p")


def get_local_time(raw_time_stamp):
    formatted_time_stamp = raw_time_stamp[:-3] + raw_time_stamp[-2:]
    utc_time = datetime.strptime(formatted_time_stamp, '%Y-%m-%dT%H:%M:%S%z')
    return utc_time.astimezone()  # Convert to local timezone


@precision_four
def get_latitude(geolocator, input_location):
    latitude = geolocator.geocode(input_location).latitude
    return latitude


@precision_four
def get_longitude(geolocator, input_location):
    longitude = geolocator.geocode(input_location).longitude
    return longitude


API_URL = "http://api.weather.gov"  # location of api
program_directory = path.dirname(path.realpath(argv[0]))
input_location = get_location(program_directory)
print(f'Retrieving weather information for {input_location}...')

# Get latitude and Longitude of input_location
geolocator = Nominatim(user_agent="app")  # Set app name for Nominatim
latitude = get_latitude(geolocator, input_location)
longitude = get_longitude(geolocator, input_location)

try:
    forecast_office = requests.get(
        f"{API_URL}/points/{latitude},{longitude}").json()['properties']
except KeyError:
    print('Location not found. Please try a different location name')
    print('If the format "City, ST" does not yield results, Try ' +
          '"City, County, ST".')
    exit()

forecast = requests.get(
        forecast_office['forecast']).json()['properties']['periods']

hourly_forecast = requests.get(
        forecast_office['forecastHourly']).json()['properties']['periods']

city = forecast_office['relativeLocation']['properties']['city']
state = forecast_office['relativeLocation']['properties']['state']
time_of_day = forecast[1]['name'].lower()
hourly_time_utc = hourly_forecast[1]['startTime']
hourly_time_local = get_local_time(hourly_time_utc)
formatted_time = format_time(hourly_time_local)
temperature = hourly_forecast[1]['temperature']
temp_unit = hourly_forecast[1]['temperatureUnit']

print(f"Data retrieved from a weather station located in {city}, {state}.")
print(f"The forecast for {time_of_day} is as follows:")
print(forecast[1]['detailedForecast'])
print(f"At {formatted_time}, the temperature will be " +
      f"{temperature}\u00b0{temp_unit}.")

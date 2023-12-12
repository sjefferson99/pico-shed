"""
Open meteo classes for working weather data from the internet.
This module was written on python v3.9.2
"""

from json import loads
from time import localtime
import urequests
import config
from ulogging import uLogger
from display import Display
import gc

class Weather_API:
    """
    Class for interacting with the Open_Meteo API
    """
    def __init__(self, log_level: int, display: Display) -> None:
        self.logger = uLogger("Open-Meteo", log_level)
        self.display = display
        self.latlong = config.lat_long
        self.display.add_text_line("Init weather API")
        self.display.add_text_line(f"LatLong: {self.latlong}")
        self.baseurl = "https://api.open-meteo.com/v1/forecast?latitude={}&longitude={}".format(self.latlong[0], self.latlong[1])
        self.parameters = "&hourly=temperature_2m,dewpoint_2m,relative_humidity_2m,weathercode,pressure_msl,windspeed_10m,winddirection_10m,windgusts_10m&current_weather=true&past_days=1&forecast_days=1&windspeed_unit=kn&timezone=GB&timeformat=unixtime"
        self.url = self.baseurl + self.parameters
        
        #Weather codes from: https://www.meteomatics.com/en/api/available-parameters/derived-weather-and-convenience-parameters/general-weather-state/#weather_symb
        self.weather_code_map = {
            "snow": [71, 73, 75, 77, 85, 86],
            "rain": [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82],
            "cloud": [1, 2, 3, 45, 48],
            "sun": [0],
            "storm": [95, 96, 99],
            "wind": []
        }

    def get_weather(self, offset_hours: int = 0) -> dict:
        """
        Get weather information for a configured location as of now and offset_hours in the past to a maximum of 24
        Returns a dictionary of weather information with human readable key names - Nautical metric units.
        """
        gc.collect()
        weather = {}
        self.logger.info(self.url)
        response = urequests.get(self.url)
        self.logger.info(f"response data: {response.text}")
        self.logger.info(f"response code: {response.status_code}")

        if response.status_code == 200:
            weather = self.process_weather(loads(response.text), offset_hours)
        else:
            self.logger.error("Failure to get weather data.\nStatus code: {}\nResponse text: {}".format(response.status_code, response.text))

        response.close()
        gc.collect()

        return weather

    def lookup_weather_code(self, code) -> str:
        for weather, codes in self.weather_code_map.items():
            if code in codes:
                return weather
        return "Unknown"        
    
    def process_weather(self, response_text_json: dict, offset_hours: int) -> dict:
        weather = {}
        data = response_text_json["hourly"]
        self.logger.info(f"JSON data: {data}\n")
        hour = localtime()[3]
        current_hour = hour + 24
        offset_hour = current_hour - offset_hours
        
        weather["temperature"] = data["temperature_2m"][current_hour]
        weather["dewpoint"] = data["dewpoint_2m"][current_hour]
        weather["humidity"] = data["relative_humidity_2m"][current_hour]
        weather["weather_code"] = data["weathercode"][current_hour]
        weather["pressure"] = data["pressure_msl"][current_hour]
        weather["wind_speed"] = data["windspeed_10m"][current_hour]
        weather["wind_direction"] = data["winddirection_10m"][current_hour]
        weather["wind_gusts"] = data["windgusts_10m"][current_hour]
        weather["weather_description"] = self.lookup_weather_code(weather["weather_code"])

        if offset_hour > 0:
            weather["offset_temperature"] = data["temperature_2m"][offset_hour]
            weather["offset_dewpoint"] = data["dewpoint_2m"][offset_hour]
            weather["offset_humidity"] = data["relative_humidity_2m"][offset_hour]
            weather["offset_weather_code"] = data["weathercode"][offset_hour]
            weather["offset_pressure"] = data["pressure_msl"][offset_hour]
            weather["offset_wind_speed"] = data["windspeed_10m"][offset_hour]
            weather["offset_wind_direction"] = data["winddirection_10m"][offset_hour]
            weather["offset_wind_gusts"] = data["windgusts_10m"][offset_hour]
            weather["offset_weather_description"] = self.lookup_weather_code(weather["offset_weather_code"])

        self.logger.info(weather)

        return weather
    
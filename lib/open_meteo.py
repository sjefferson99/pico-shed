"""
Open meteo classes for working weather data from the internet.
"""

from json import loads
from time import localtime
import config
from lib.ulogging import uLogger
import gc

class Weather_API:
    """
    Class for interacting with the Open_Meteo API
    """
    def __init__(self, log_level: int) -> None:
        self.logger = uLogger("Open-Meteo", log_level)
        self.logger.info("Init Open-Meteo")
        self.latlong = config.lat_long
        self.baseurl = "http://api.open-meteo.com/v1/forecast?latitude={}&longitude={}".format(self.latlong[0], self.latlong[1])
        
    async def get_humidity_async(self) -> dict:
        import uaiohttpclient

        gc.collect()
        self.parameters = "&hourly=relative_humidity_2m&current_weather=false&past_days=1&forecast_days=1&windspeed_unit=kn&timezone=GB&timeformat=unixtime"
        self.url = self.baseurl + self.parameters
        weather = {}
        self.logger.info(self.url)
        request = await uaiohttpclient.request("GET", self.url)
        self.logger.info(f"request: {request}")
        response = await request.read()
        self.logger.info(f"response data: {response}")
        
        if request.status == 200:
            weather = self.process_weather(loads(response))
        else:
            self.logger.error("Failure to get weather data.\nStatus code: {}\nResponse text: {}".format(request.status, response))

        gc.collect()

        return weather
    
    def process_weather(self, response_text_json: dict) -> dict:
        weather = {}
        data = response_text_json["hourly"]
        self.logger.info(f"JSON data: {data}\n")
        hour = localtime()[3]
        current_hour = hour + 24

        weather["humidity"] = data["relative_humidity_2m"][current_hour]

        self.logger.info(weather)

        return weather
    
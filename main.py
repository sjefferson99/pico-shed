from networking import Wireless_Network
from open_meteo import weather_api
from bme_280 import BME_280
from machine import Pin
from time import sleep
import config
from helpers import flash_led
from fan import Fan

fan = Fan()

wlan = Wireless_Network()
weather = weather_api()
sensor = BME_280()

while wlan.wlan.status() != 3:
    try:
        wlan.connect_wifi(config.wifi_auto_reconnect_tries)
    except:
        print("Error connecting to wifi after configured retries")
        fan.switch_on()
        flash_led(20, 4)

while True:
    weather_data = weather.get_weather()
    readings = sensor.get_readings()

    print(f"Weather data: {weather_data}\n")
    print(f"Sensor data: {readings}\n")

    outside_humidity = weather_data["humidity"]
    inside_humidity = readings["humidity"]

    if inside_humidity > outside_humidity:
        print("Turning on fan")
        fan.switch_on()
    else:
        print("Turning off fan")
        fan.switch_off()

    sleep(config.weather_poll_frequency_in_seconds)
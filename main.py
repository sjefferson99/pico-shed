from networking import Wireless_Network
from open_meteo import weather_api
from bme_280 import BME_280
from machine import Pin
from time import sleep
import config

fan_pin = Pin(config.fan_gpio_pin, Pin.OUT)

wlan = Wireless_Network()
wlan.connect_wifi()

weather = weather_api()
sensor = BME_280()

while True:
    weather_data = weather.get_weather()
    readings = sensor.get_readings()

    print(f"Weather data: {weather_data}\n")
    print(f"Sensor data: {readings}\n")

    outside_humidity = weather_data["humidity"]
    inside_humidity = readings["humidity"]

    if inside_humidity > outside_humidity:
        print("Turning on fan")
        fan_pin.on()
    else:
        print("Turning off fan")
        fan_pin.off()

    sleep(300)
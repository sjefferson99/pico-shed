from machine import Pin
import config
from networking import Wireless_Network
from helpers import flash_led
from open_meteo import Weather_API
from bme_280 import BME_280
from ulogging import uLogger

class Fan:
    def __init__(self) -> None:
        self.fan_pin = Pin(config.fan_gpio_pin, Pin.OUT)
        self.fan_pin.off()
        self.wlan = Wireless_Network()
        self.weather = Weather_API()
        self.sensor = BME_280()
        self.logger = uLogger("Fan", 0)

    def switch_on(self) -> None:
        self.fan_pin.on()
        self.logger.info("Fan switched on")

    def switch_off(self) -> None:
        self.fan_pin.off()
        self.logger.info("Fan switched off")
    
    def set_fan_from_humidity(self, inside_humidity: float, outside_humidity: float) -> None:
        if inside_humidity > outside_humidity:
            self.logger.info("Turning on fan")
            self.switch_on()
        else:
            self.logger.info("Turning off fan")
            self.switch_off()

    def assess_fan_state(self) -> None:
        self.logger.info("Assessing fan state")
        self.check_network_access()
        
        weather_data = self.weather.get_weather()
        readings = self.sensor.get_readings()

        self.set_fan_from_humidity(readings["humidity"], weather_data["humidity"])

    def check_network_access (self) -> None:
        self.logger.info("Checking for network access")
        while self.wlan.get_status() != 3:
            try:
                self.wlan.connect_wifi(config.wifi_auto_reconnect_tries)
            except:
                self.logger.error(f"Error connecting to wifi after {config.wifi_auto_reconnect_tries} retries")
                self.switch_on()
                flash_led(20, 4)

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
        self.led_retry_backoff_frequency = 4

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
        network_access = self.check_network_access()
        if network_access == True:
            weather_data = self.weather.get_weather()
            readings = self.sensor.get_readings()
            self.set_fan_from_humidity(readings["humidity"], weather_data["humidity"])

    def network_retry_backoff(self) -> None:
        self.logger.info(f"Backing off retry for {config.wifi_retry_backoff_seconds} seconds")
        flash_led((config.wifi_retry_backoff_seconds * self.led_retry_backoff_frequency), self.led_retry_backoff_frequency)

    def check_network_access (self) -> bool:
        self.logger.info("Checking for network access")
        retries = 0
        while self.wlan.get_status() != 3 and retries <= config.wifi_connect_retries:
            try:
                self.wlan.connect_wifi()
                return True
            except Exception:
                self.logger.warn(f"Error connecting to wifi on attempt {retries + 1} of {config.wifi_connect_retries + 1}")
                retries += 1
                self.network_retry_backoff()

        if self.wlan.get_status == 3:
            self.logger.info("Connected to wireless network")
            return True
        else:
            self.logger.warn("Unable to connect to wireless network")
            self.switch_on()
            return False

# Requires the pico to be running a Pimoroni specific micropython build:
# https://github.com/pimoroni/pimoroni-pico/releases

from breakout_bme280 import BreakoutBME280
from pimoroni_i2c import PimoroniI2C
import config
from ulogging import uLogger
from display import Display
from helpers import print_to_startup_display

class BME_280:
    
    def __init__(self, log_level: int, display: Display|None) -> None:
        self.logger = uLogger("BME280", log_level)
        self.display = display
        print_to_startup_display("Init BME280", self.display)
        print_to_startup_display(f"I2c Pins: scl: {config.i2c_pins['scl']} sda: {config.i2c_pins['sda']}", self.display)
        self.i2c = PimoroniI2C(**config.i2c_pins)
        self.bme = BreakoutBME280(self.i2c)

    def get_readings(self) -> dict:
        temperature, pressure, humidity = self.bme.read()
        readings = {}
        readings["temperature"] = round(temperature, 2)
        readings["pressure"] = round(pressure / 100, 2)
        readings["humidity"] = round(humidity, 2)

        self.logger.info(f"BME 280 readings collected: {readings}")

        return readings
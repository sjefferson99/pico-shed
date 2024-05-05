"""
Built against Pimoroni Micropython version: v1.22.2 (https://github.com/pimoroni/pimoroni-pico/releases/download/v1.22.2/pimoroni-picow-v1.22.2-micropython.uf2)
"""

from breakout_bme280 import BreakoutBME280
from pimoroni_i2c import PimoroniI2C
import config
from lib.ulogging import uLogger

class BME_280:
    
    def __init__(self, log_level: int) -> None:
        self.logger = uLogger("BME280", log_level)
        self.logger.info("Init BME280")
        self.i2c = PimoroniI2C(**config.i2c_pins)
        self.bme = BreakoutBME280(self.i2c)
        self.get_readings() # Clear incorrect first value after startup

    def get_readings(self) -> dict:
        temperature, pressure, humidity = self.bme.read()
        readings = {}
        readings["temperature"] = round(temperature, 2)
        readings["pressure"] = round(pressure / 100, 2)
        readings["humidity"] = round(humidity, 2)

        self.logger.info(f"BME 280 readings collected: {readings}")

        return readings
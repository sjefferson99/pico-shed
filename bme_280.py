# Requires the pico to be running a Pimoroni specific micropython build:
# https://github.com/pimoroni/pimoroni-pico/releases

from breakout_bme280 import BreakoutBME280
from pimoroni_i2c import PimoroniI2C
import config
from ulogging import uLogger
from display import Display

class BME_280:
    
    def __init__(self, log_level: int, display: Display) -> None:
        self.logger = uLogger("BME280", log_level)
        self.display = display
        self.display.add_text_line("Init BME280")
        self.display.add_text_line(f"I2c Pins: scl: {config.i2c_pins['scl']} sda: {config.i2c_pins['sda']}")
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
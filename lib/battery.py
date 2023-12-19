from machine import ADC
import config
from ulogging import uLogger
import uasyncio
from time import time

class Battery_Monitor:
    def __init__(self, log_level: int) -> None:
        self.logger = uLogger("Battery monitor", log_level)
        self.r1 = config.r1
        self.r2 = config.r2
        self.voltage_correction = config.voltage_correction
        self.scaling_factor = (1 / (self.r2 / (self.r1 + self.r2)))
        self.battery_ADC = ADC(config.battery_adc_pin)
        self.reading_updated = uasyncio.Event()

    def read_battery_voltage(self) -> float:
        adc_value = self.battery_ADC.read_u16()
        self.logger.info(f"ADC value: {adc_value}")
        uncalibrated_adc_voltage = adc_value * (3.3 / 65535)
        self.logger.info(f"Uncalibrated ADC voltage: {uncalibrated_adc_voltage}")
        uncalibrated_battery_voltage = uncalibrated_adc_voltage * self.scaling_factor
        self.logger.info(f"Uncalibrated battery voltage: {uncalibrated_battery_voltage}")
        adc_offset = self.voltage_correction / self.scaling_factor
        self.logger.info(f"ADC calibration offset: {adc_offset}")
        calibrated_adc_voltage = uncalibrated_adc_voltage + adc_offset
        self.logger.info(f"Calibrated ADC voltage: {calibrated_adc_voltage}")
        calibrated_battery_voltage = calibrated_adc_voltage * self.scaling_factor
        self.logger.info(f"Calibrated battery voltage: {calibrated_battery_voltage}")
        return calibrated_battery_voltage
    
    async def poll_battery_voltage(self) -> None:
        while True:
            self.last_reading = self.read_battery_voltage()
            self.last_reading_time = time()
            self.reading_updated.set()
            await uasyncio.sleep(60)
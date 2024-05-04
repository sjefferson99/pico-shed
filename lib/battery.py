from machine import ADC
import config
from lib.ulogging import uLogger
import uasyncio
from time import time
from display import Display

class Battery_Monitor:
    def __init__(self, log_level: int, display: Display) -> None:
        self.logger = uLogger("Battery monitor", log_level)
        self.logger.info(f"Init battery monitor")
        self.r1 = config.r1
        self.r2 = config.r2
        self.voltage_correction = config.voltage_correction
        self.scaling_factor = (1 / (self.r2 / (self.r1 + self.r2)))
        self.battery_ADC = ADC(config.battery_adc_pin)
        self.reading_updated = uasyncio.Event()
        self.last_reading = 0
        self.last_reading_time = 0
        self.display = display

    def init_service(self) -> None:
        self.logger.info("Init battery voltage poll")
        uasyncio.create_task(self.poll_battery_voltage())
        if self.display.enabled:
            self.logger.info("Init battery voltage display updater")
            uasyncio.create_task(self.battery_display_updater())
        else:
            self.logger.info("Display disabled, skipping battery display updater service")

    def read_battery_voltage(self) -> float:
        adc_value = self.battery_ADC.read_u16()
        self.logger.info(f"ADC value: {adc_value}")
        uncalibrated_adc_voltage = adc_value * (3.3 / 65535)
        self.logger.info(f"Uncalibrated ADC voltage: {uncalibrated_adc_voltage}")
        uncalibrated_battery_voltage = uncalibrated_adc_voltage * self.scaling_factor
        self.logger.info(f"Uncalibrated battery voltage: {uncalibrated_battery_voltage}")
        calibrated_battery_voltage = uncalibrated_battery_voltage + self.voltage_correction
        self.logger.info(f"Calibrated battery voltage: {calibrated_battery_voltage}")

        return calibrated_battery_voltage
    
    async def poll_battery_voltage(self) -> None:
        while True:
            self.last_reading = self.read_battery_voltage()
            self.last_reading_time = time()
            self.reading_updated.set()
            await uasyncio.sleep(5)

    async def battery_display_updater(self) -> None:
        while True:
            await self.reading_updated.wait()
            self.reading_updated.clear()
            self.logger.info(f"{self.last_reading_time}: Battery voltage: {self.last_reading}")
            self.display.update_main_display_values({"battery_voltage": str(round(self.last_reading, 2)) + "v"})
    
    def get_latest_voltage(self) -> float:
        return self.last_reading    
    
    def get_all_data(self) -> dict:
        all_data = {}
        all_data['voltage'] = self.get_latest_voltage()
        return all_data
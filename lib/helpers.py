from time import sleep
from machine import Pin
import uasyncio
from lib.ulogging import uLogger

class Status_LED:
    def __init__(self, log_level: int) -> None:
        self.logger = uLogger("Status_LED", log_level)
        self.status_led = Pin("LED", Pin.OUT)
    
    def on(self) -> None:
        self.logger.info("LED on")
        self.status_led.on()

    def off(self) -> None:
        self.logger.info("LED off")
        self.status_led.off()

    async def flash(self, count: int, hz: float) -> None:
        self.off()
        sleep_duration = (1 / hz) / 2
        for unused in range(count):
            await uasyncio.sleep(sleep_duration)
            self.on()
            await uasyncio.sleep(sleep_duration)
            self.off()
    
    def flash_no_async(self, count: int, hz: float) -> None:
        self.off()
        sleep_duration = (1 / hz) / 2
        for unused in range(count):
            sleep(sleep_duration)
            self.on()
            sleep(sleep_duration)
            self.off()

def decimal_to_percent_str(decimal) -> str:
    value = decimal * 100
    string = str(value) + "%"
    return string
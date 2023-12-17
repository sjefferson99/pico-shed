from machine import Pin
import uasyncio
from ulogging import uLogger
from display import Display

class Button:

    def __init__(self, log_level: int, GPIO_pin: int, display: Display) -> None:
        self.log_level = log_level
        self.logger = uLogger(f"Button {GPIO_pin}", log_level)
        self.pin = Pin(GPIO_pin, Pin.IN, Pin.PULL_UP)
        self.display = display

    async def wait_for_press(self) -> None:
        self.logger.info("Starting button press watcher")
        
        while True:
            previous_value = self.pin.value()
            while (self.pin.value() == previous_value):
                previous_value = self.pin.value()
                await uasyncio.sleep(0.04)
            
            self.logger.info("Button pressed")
            self.display.backlight_on()
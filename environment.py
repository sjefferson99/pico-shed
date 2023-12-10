from fan import Fan
from display import Display
from ulogging import uLogger
from time import sleep, time
import config
import uasyncio

class Environment:
    def __init__(self, log_level: int) -> None:
        self.log_level = log_level
        self.logger = uLogger("Environment", log_level)
        self.display = Display(self.log_level)
        self.fan = Fan(self.log_level, self.display)
        sleep(config.auto_page_scroll_pause)
        self.display.mode = "main"
        self.display.update_main_display()
        self.last_weather_poll_s = 0

    async def main_loop(self) -> None:
        uasyncio.create_task(self.display.backlight_timeout())
        uasyncio.create_task(self.fan.start_fan_management())

        while True:
            self.logger.info("In main loop")
            await uasyncio.sleep(1)
    
    def start(self) -> None:
        uasyncio.run(self.main_loop())

from fan import Fan
from display import Display
from ulogging import uLogger
from time import sleep, time
import config
import uasyncio
from lib.button import Button

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
        self.button_a = Button(self.log_level, self.display.BUTTON_A, self.display)

    def main_loop(self) -> None:
        uasyncio.run_until_complete(self.fan.fan_test())

        loop = uasyncio.get_event_loop()
        uasyncio.create_task(self.display.manage_backlight_timeout())
        uasyncio.create_task(self.button_a.wait_for_press())
        uasyncio.create_task(self.fan.start_fan_management())
        loop.run_forever()

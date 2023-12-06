from fan import Fan
from display import Display
from ulogging import uLogger
from time import sleep, time
import config

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

    def main_loop(self) -> None:
        while True:
            if self.last_weather_poll_s < (time() - config.weather_poll_frequency_in_seconds):
                self.last_weather_poll_s = time()
                self.assess_fan_state()
            
            self.display.check_backlight() # Not perfect, but fairly close - need uasyncio or interrupts or similar magic.
    
    def assess_fan_state(self) -> None:
        self.fan.assess_fan_state()

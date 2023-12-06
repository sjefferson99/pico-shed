from fan import Fan
from display import Display
from ulogging import uLogger
from time import sleep
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

    # Not used yet - maybe never?
    # def get_cached_indoor_humidity(self) -> float:
    #     try:
    #         return self.fan.readings["humidity"]
    #     except:
    #         return False
    
    # def get_cached_outdoor_humidity(self) -> float:
    #     try:
    #         return self.fan.weather_data["humidity"]
    #     except:
    #         return False
    
    def assess_fan_state(self) -> None:
        self.fan.assess_fan_state()

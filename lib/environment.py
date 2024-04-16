from lib.fan import Fan
from lib.display import Display
from lib.ulogging import uLogger
from time import sleep
import config
import uasyncio
from lib.battery import Battery_Monitor
from lib.networking import Wireless_Network
from http.website import Web_App
from motion import Motion_Detector

class Environment:
    def __init__(self, log_level: int) -> None:
        """
        Init environment and create objects
        Run "init_modules" to configure available module services ahead of executing "main_loop"
        """
        self.log_level = log_level
        self.logger = uLogger("Environment", log_level)
        self.version = "1.6.0"
        self.display = Display(self.log_level)
        self.display.add_text_line("Configuring WiFi")
        self.wlan = Wireless_Network(log_level, self.display)
        self.display.add_text_line(f"MAC: {self.wlan.mac}")
        self.display.add_text_line("Configuring Fan")
        self.fan = Fan(self.log_level, self.display, self.wlan)
        self.display.add_text_line(f"Configuring battery monitor")
        self.battery = Battery_Monitor(log_level, self.display)
        self.display.add_text_line("Configuring motion detector")
        self.motion = Motion_Detector(self.log_level)
        self.display.add_text_line(f"Configuring web server")
        self.modules = {
                        'fan': self.fan,
                        'battery_monitor': self.battery,
                        'motion': self.motion,
                        'light': self.motion.light,
                        'wlan': self.wlan,
                        'display': self.display,
                        'environment': self
                        }
        self.web_app = Web_App(self.log_level, self.modules)
        self.modules['web_app'] = self.web_app
        self.service_modules = self.modules
        self.service_modules.pop('environment')

    def main_loop(self) -> None:                
        self.display.add_text_line(f"Entering main loop")
        sleep(config.auto_page_scroll_pause_s)
        self.display.mode = "main"
        self.display.update_main_display()
        self.loop_running = True
        loop = uasyncio.get_event_loop()
        loop.run_forever()
    
    def init_modules(self) -> None:
        """Load all module services into asyncio loop ready to start"""
        for module in self.service_modules:
            self.logger.info(f"Loading {module} service")
            self.display.add_text_line(f"Loading {module} service")
            self.modules[module].init_service()

    def get_version(self) -> str:
        """Get current firmware version of Pico Environemt Control"""
        return self.version
    
    def get_all_data(self) -> dict:
        all_data = {}
        all_data['version'] = self.get_version()
        return all_data

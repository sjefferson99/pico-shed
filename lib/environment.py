from lib.fan import Fan
from lib.display import Display
from lib.ulogging import uLogger
from time import sleep
import config
from lib.battery import Battery_Monitor
from lib.networking import Wireless_Network
from http.website import Web_App
from motion import Motion_Detector
from button import Button
from uasyncio import create_task, get_event_loop

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
        self.display.add_text_line("Configuring fan")
        self.fan = Fan(self.log_level, self.display, self.wlan)
        self.display.add_text_line(f"Configuring battery monitor")
        self.battery = Battery_Monitor(log_level, self.display)
        self.display.add_text_line("Configuring motion detector")
        self.motion = Motion_Detector(self.log_level)
        self.display.add_text_line(f"Configuring pico display buttons")
        self.buttons = self.init_pico_display_buttons()
        self.modules = {
                        'fan': self.fan,
                        'battery_monitor': self.battery,
                        'motion': self.motion,
                        'light': self.motion.light,
                        'wlan': self.wlan,
                        'display': self.display,
                        'environment': self
                        }
        self.display.add_text_line(f"Configuring web server")
        self.web_app = Web_App(self.log_level, self.modules)
        self.modules['web_app'] = self.web_app
        self.service_modules = self.modules

    def main_loop(self) -> None:                
        self.logger.info("Entering main loop")
        self.display.add_text_line(f"Entering main loop")
        sleep(config.auto_page_scroll_pause_s)
        self.display.mode = "main"
        self.display.update_main_display()
        self.loop_running = True
        loop = get_event_loop()
        loop.run_forever()
    
    def init_modules(self) -> None:
        """Load all module services into asyncio loop ready to start"""
        for module in self.service_modules:
            self.logger.info(f"Loading {module} service")
            self.display.add_text_line(f"Loading {module} service")
            self.modules[module].init_service()

    def init_pico_display_buttons(self) -> dict:
        self.logger.info("Init pico buttons")
        buttons_to_create = {"A": 12, "B": 13, "X": 14, "Y": 15}
        buttons = {}
        
        for button in buttons_to_create:
            self.logger.info(f"Init pico button {button}")
            buttons[button] = Button(buttons_to_create[button], button, self.log_level)
        
        return buttons
    
    def do_button_function(self, button_name: str) -> None:
        self.logger.info(f"Doing button function for button {button_name}")
    
    async def button_pressed_event_watcher(self, button: Button) -> None:
        self.logger.info(f"Starting button pressed watcher for {button.name}")
        while True:
            await button.pressed_event.wait()
            self.logger.info(f"Button {button.name} pressed")
            button.clear_pressed()
            
            backlight_was_on = self.display.get_backlight_state()
            self.display.backlight_on()

            if backlight_was_on:
                self.do_button_function(button.name)
                
    def init_service(self) -> None:
        for button in self.buttons:
            self.logger.info(f"Init pico button watcher for {button}")
            button_object: Button = self.buttons[button]
            create_task(button_object.wait_for_press())
            self.logger.info(f"Init pico button pressed watcher for {button}")
            create_task(self.button_pressed_event_watcher(button_object))

    def get_version(self) -> str:
        """Get current firmware version of Pico Environemt Control"""
        return self.version
    
    def get_all_data(self) -> dict:
        all_data = {}
        all_data['version'] = self.get_version()
        return all_data

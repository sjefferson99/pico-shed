from lib.fan import Fan
from lib.display import Display
from lib.ulogging import uLogger
from time import sleep
import config
import uasyncio
from lib.button import Button
from lib.battery import Battery_Monitor
from lib.networking import Wireless_Network
from http.website import Web_App
from motion import Motion_Detector

class Environment:
    def __init__(self, log_level: int) -> None:
        self.log_level = log_level
        self.logger = uLogger("Environment", log_level)
        self.display = Display(self.log_level)
        self.display.add_text_line("Configuring WiFi")
        self.wlan = Wireless_Network(log_level, self.display)
        self.display.add_text_line(f"MAC: {self.wlan.mac}")
        self.display.add_text_line("Configuring Fan")
        self.fan = Fan(self.log_level, self.display, self.wlan)
        self.buttons = []
        if self.display.enabled:
            self.display.add_text_line(f"Configuring buttons")
            self.init_pico_display_buttons()
        self.display.add_text_line(f"Init battery monitor")
        self.battery = Battery_Monitor(log_level, self.display)
        self.display.add_text_line(f"Init web server")
        self.display.add_text_line("Init motion detector")
        self.motion = Motion_Detector(self.log_level)
        self.modules = {'fan': self.fan, 'battery_monitor': self.battery, 'motion': self.motion, 'light': self.motion.light, 'wlan': self.wlan}
        self.web_app = Web_App(self.log_level, self.modules, self.display)
        self.modules['web_app'] = self.web_app
        if config.enable_startup_fan_test and config.enable_fan:
            self.fan.fan_test()
        self.last_weather_poll_s = 0

    def init_pico_display_buttons(self) -> None:    
        self.button_a = Button(self.log_level, self.display.BUTTON_A, self.display)
        self.button_b = Button(self.log_level, self.display.BUTTON_B, self.display)
        self.button_x = Button(self.log_level, self.display.BUTTON_X, self.display)
        self.button_y = Button(self.log_level, self.display.BUTTON_Y, self.display)
        self.buttons = [self.button_a, self.button_b, self.button_x, self.button_y]

    def main_loop(self) -> None:        
        if config.display_enabled:
            self.display.add_text_line(f"Loading backlight monitor")
            uasyncio.create_task(self.display.manage_backlight_timeout())
        
        if len(self.buttons) > 0:
            self.display.add_text_line(f"Loading button service")
            self.enable_button_watchers()
            self.button_a.set_function_on_press(Button.test_button_function, [])
        
        self.display.add_text_line(f"Entering main loop")
        sleep(config.auto_page_scroll_pause_s)
        self.display.mode = "main"
        self.display.update_main_display()
        self.loop_running = True
        loop = uasyncio.get_event_loop()
        loop.run_forever()

    def enable_button_watchers(self) -> None:
        for button in self.buttons:
            uasyncio.create_task(button.wait_for_press())
    
    def init_modules(self) -> None:
        for module in self.modules:
            self.logger.info(f"Loading {module} service")
            self.display.add_text_line(f"Loading {module} service")
            self.modules[module].init_service()
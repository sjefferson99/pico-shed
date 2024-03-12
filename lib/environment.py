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
        self.wlan = Wireless_Network(log_level)
        self.display.add_text_line(f"MAC: {self.wlan.mac}")
        self.display.add_text_line("Configuring Fan")
        self.fan = Fan(self.log_level, self.display, self.wlan)
        self.buttons = []
        if self.display.enabled:
            self.display.add_text_line(f"Configuring buttons")
            self.init_pico_display_buttons()
        self.display.add_text_line(f"Init battery monitor")
        self.battery = Battery_Monitor(log_level)
        self.display.add_text_line(f"Init web server")
        self.display.add_text_line("Init motion detector")
        self.motion = Motion_Detector(self.log_level)
        modules = {'fan_module': self.fan, 'battery_monitor': self.battery, 'motion': self.motion, 'light': self.motion.light}
        self.web_app = Web_App(modules)
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
        loop = uasyncio.get_event_loop()

        self.display.add_text_line(f"Loading webserver")
        self.web_app.load_into_loop()
        self.display.add_text_line(f"Loading web monitor")
        uasyncio.create_task(self.website_status_monitor())
        self.display.add_text_line(f"Loading net monitor")
        uasyncio.create_task(self.network_status_monitor())
        
        if config.display_enabled:
            self.display.add_text_line(f"Loading backlight monitor")
            uasyncio.create_task(self.display.manage_backlight_timeout())
        
        if len(self.buttons) > 0:
            self.display.add_text_line(f"Loading button service")
            self.enable_button_watchers()
            self.button_a.set_function_on_press(Button.test_button_function, [])
        
        self.display.add_text_line(f"Loading battery monitor")
        self.enable_battery_monitor()

        self.display.add_text_line(f"Loading motion monitor")
        uasyncio.create_task(self.motion.motion_monitor())
        self.display.add_text_line(f"Loading motion light timer")
        uasyncio.create_task(self.motion.motion_light_off_timer())
        
        if config.enable_fan:
            self.display.add_text_line(f"Starting fan management")
            uasyncio.create_task(self.start_fan_management())
        
        self.display.add_text_line(f"Entering main loop")
        sleep(config.auto_page_scroll_pause_s)
        self.display.mode = "main"
        self.display.update_main_display()

        self.loop_running = True
        loop.run_forever()

    def enable_button_watchers(self) -> None:
        for button in self.buttons:
            uasyncio.create_task(button.wait_for_press())
    
    def enable_battery_monitor(self) -> None:
        uasyncio.create_task(self.battery.poll_battery_voltage())
        uasyncio.create_task(self.battery_monitor())

    async def battery_monitor(self) -> None:
        while True:
            await self.battery.reading_updated.wait()
            self.battery.reading_updated.clear()
            self.logger.info(f"{self.battery.last_reading_time}: Battery voltage: {self.battery.last_reading}")
            self.display.update_main_display_values({"battery_voltage": str(round(self.battery.last_reading, 2)) + "v"})

    async def start_fan_management(self) -> None:
        while True:
            uasyncio.create_task(self.fan.assess_fan_state())
            await uasyncio.sleep(config.weather_poll_frequency_in_seconds)
    
    async def network_status_monitor(self) -> None:
        while True:
            status = self.wlan.dump_status()
            if status == 3:
                self.display.update_main_display_values({"wifi_status": "Connected"})
            elif status >= 0:
                self.display.update_main_display_values({"wifi_status": "Connecting"})
            else:
                self.display.update_main_display_values({"wifi_status": "Error"})
            await uasyncio.sleep(5)

    async def website_status_monitor(self) -> None:
        while True:
            if self.wlan.dump_status() == 3 and self.web_app.running:
                self.display.update_main_display_values({"web_server": str(self.wlan.ip) + ":" + str(config.web_port)})
            else:
                self.display.update_main_display_values({"web_server": "Stopped"})
            await uasyncio.sleep(5)
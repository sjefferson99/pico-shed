from fan import Fan
from display import Display
from ulogging import uLogger
from time import sleep
import config
import uasyncio
from lib.button import Button
from lib.battery import Battery_Monitor

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
        self.buttons = []
        if self.display.enabled:
            self.init_pico_display_buttons()
        self.battery = Battery_Monitor(log_level)

    def init_pico_display_buttons(self) -> None:    
        self.button_a = Button(self.log_level, self.display.BUTTON_A, self.display)
        self.button_b = Button(self.log_level, self.display.BUTTON_B, self.display)
        self.button_x = Button(self.log_level, self.display.BUTTON_X, self.display)
        self.button_y = Button(self.log_level, self.display.BUTTON_Y, self.display)
        self.buttons = [self.button_a, self.button_b, self.button_x, self.button_y]

    def main_loop(self) -> None:
        uasyncio.run_until_complete(self.fan.fan_test())

        loop = uasyncio.get_event_loop()
        
        uasyncio.create_task(self.display.manage_backlight_timeout())
        
        if len(self.buttons) > 0:
            self.enable_button_watchers()
            self.button_a.set_function_on_press(Button.test_button_function, [])
        
        self.enable_battery_monitor()
        
        uasyncio.create_task(self.fan.start_fan_management())
        loop.run_forever()

    def enable_button_watchers(self) -> None:
        for button in self.buttons:
            uasyncio.create_task(button.wait_for_press())
    
    def enable_battery_monitor(self) -> None:
        uasyncio.create_task(self.battery.poll_battery_voltage())
        uasyncio.create_task(self.battery_monitor())

    async def battery_monitor(self) -> None:
        await self.battery.reading_updated.wait()
        self.battery.reading_updated.clear()
        self.logger.info(f"{self.battery.last_reading_time}: Battery voltage: {self.battery.last_reading}")
        self.display.update_main_display({"battery_voltage": str(round(self.battery.last_reading, 2)) + "v"})
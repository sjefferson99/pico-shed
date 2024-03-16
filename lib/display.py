from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_RGB332
from pimoroni import RGBLED
from lib.ulogging import uLogger
import config
from time import sleep
from utime import ticks_ms
import uasyncio
from lib.button import Button

class Display:
    def __init__(self, log_level: int) -> None:
        self.log_level = log_level
        self.logger = uLogger("Display", self.log_level)
        self.logger.info("Init Display")
        self.enabled = config.enable_display
        if self.enabled:
            self.init_display()
        else:
            self.logger.info("Display disabled in config")
    
        self.buttons = []
        self.BUTTON_A = 12
        self.BUTTON_B = 13
        self.BUTTON_X = 14
        self.BUTTON_Y = 15

    def init_display(self) -> None:
        self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_RGB332, rotate=0)
        self.auto_page_scroll_pause_s = config.auto_page_scroll_pause_s
        self.GREEN = self.display.create_pen(0, 255, 0)
        self.BACKGROUND = self.display.create_pen(51, 153, 102)
        self.WHITE = self.display.create_pen(255, 255, 255)
        self.display.set_font("bitmap8")
        self.font_height = 8
        self.line_spacing = 2
        self.WIDTH, self.HEIGHT = self.display.get_bounds()
        self.top_margin = 10
        self.bottom_margin = 0
        self.left_margin = 10
        self.right_margin = 0
        self.useable_width = self.WIDTH - self.left_margin - self.right_margin
        self.logger.info(f"useable width: {self.useable_width}")
        self.current_y = 0
        self.header_font_scale = 3
        self.normal_font_scale = 2
        self.display_data = {"indoor_humidity": ["IHum", "Unknown"], "outdoor_humidity": ["OHum", "Unknown"], "fan_speed": ["Fan", "Unknown"], "wifi_status": ["Net", "Unknown"], "battery_voltage": ["Batt", "Unknown"], "web_server": ["Web", "Unknown"]}
        self.startup_display()
    
    def startup_display(self) -> None:
        self.mode = "startup"
        self.logger.info("Startup Display")
        self.rgb_led = RGBLED(2, 0, 0)
        self.backlight_on()
        self.print_startup_text()

    def init_service(self) -> None:
        self.logger.info("Loading backlight monitor")
        uasyncio.create_task(self.manage_backlight_timeout())
        self.logger.info("Init buttons")
        self.init_pico_display_buttons()
        self.logger.info("Loading button service")
        self.enable_button_watchers()
        self.logger.info("Configuring button A")
        self.button_a.set_function_on_press(Button.test_button_function, [])
    
    def init_pico_display_buttons(self) -> None:    
        self.button_a = Button(self.log_level, self.BUTTON_A, self)
        self.button_b = Button(self.log_level, self.BUTTON_B, self)
        self.button_x = Button(self.log_level, self.BUTTON_X, self)
        self.button_y = Button(self.log_level, self.BUTTON_Y, self)
        self.buttons = [self.button_a, self.button_b, self.button_x, self.button_y]

    def enable_button_watchers(self) -> None:
        for button in self.buttons:
            uasyncio.create_task(button.wait_for_press())

    def backlight_on(self) -> None:
        self.logger.info("Backlight on")
        self.display.set_backlight(1.0)
        self.backlight_on_time_ms = ticks_ms()

    def backlight_off(self) -> None:
        self.logger.info("Backlight off")
        self.display.set_backlight(0)
        self.backlight_on_time_ms = 0
    
    def should_backlight_be_switched_off(self) -> bool:
        if self.backlight_on_time_ms > 0 and (self.backlight_on_time_ms + (config.backlight_timeout_s * 1000)) < ticks_ms() and self.mode != "startup":
            return True
        else:
            return False
    
    async def manage_backlight_timeout(self) -> None:
        if self.enabled:
            self.logger.info("Starting backlight timeout management")
            while True:
                if self.should_backlight_be_switched_off():
                    self.backlight_off()
                await uasyncio.sleep(0.1)
        else:
            self.logger.info("Display not enabled - backlight monitor not started")

    def clear_screen(self) -> None:
        self.display.set_pen(self.BACKGROUND)
        self.display.clear()
        self.current_y = self.top_margin

    def print_startup_text(self) -> None:
        self.clear_screen()
        self.display.set_pen(self.WHITE)
        self.display.text("Starting up...", self.left_margin, self.top_margin, self.useable_width, self.header_font_scale)
        self.display.update()
        self.current_y = self.current_y + (self.header_font_scale * self.font_height) + self.line_spacing
    
    def get_text_line_count(self, text: str, scale: float) -> int:
        line_count = 1
        text_width = self.display.measure_text(text, scale)
        self.logger.info(f"Text width: {text_width}")
        
        while text_width > self.useable_width:
            text_width -= self.useable_width
            line_count += 1
            self.logger.info(f"Adding line_count, new text width is {text_width}")
            
        return line_count
    
    def add_text_line(self, text: str) -> None:
        if self.enabled:
            next_y_start = self.current_y
            next_y_end = next_y_start + (((self.font_height * self.normal_font_scale) + self.line_spacing) * self.get_text_line_count(text, self.normal_font_scale))
            self.logger.info(f"Calculated next_y_end: {next_y_end}")
            
            if next_y_end > (self.HEIGHT - self.bottom_margin):
                sleep(self.auto_page_scroll_pause_s)
                self.clear_screen()
                next_y_start = self.current_y
                next_y_end = next_y_start + (((self.font_height * self.normal_font_scale) + self.line_spacing) * self.get_text_line_count(text, self.normal_font_scale))
                self.logger.info(f"Reset to top of page and calculated next_y_end: {next_y_end}")
            
            self.display.set_pen(self.WHITE)
            self.display.text(text, self.left_margin, next_y_start, self.useable_width, self.normal_font_scale)
            self.display.update()
            self.current_y = next_y_end
            self.logger.info(f"Current_y now set to : {self.current_y}")
        else:
            self.logger.info(f"Display text not shown as display disabled: {text}")

    def update_main_display_values(self, display_data: dict) -> None:
        for key in display_data:
            if key in self.display_data:
                self.display_data[key][1] = display_data[key]
                self.logger.info(f"Updating display item {key} to {display_data[key]}")
            else:
                self.logger.warn("Invalid display update item")
        self.update_main_display()

    def update_main_display(self) -> None:
        if self.mode == "main":
            self.clear_screen()
            self.display.set_pen(self.WHITE)
            next_y_start = self.current_y
            for item in self.display_data:
                text = self.display_data[item][0] + ": " + str(self.display_data[item][1])
                self.display.text(text, self.left_margin, next_y_start, self.useable_width, self.normal_font_scale)
                next_y_start = next_y_start + ((self.font_height * self.normal_font_scale) + self.line_spacing)
            self.display.update()
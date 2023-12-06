from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_RGB332
from pimoroni import RGBLED
from ulogging import uLogger
import config
from time import sleep

class Display:
    def __init__(self, log_level: int) -> None:
        self.logger = uLogger("Display", log_level)
        self.logger.info("Init Display")
        self.enabled = config.display_enabled
        if self.enabled:
            self.init_display()
        else:
            self.logger.info("Display disabled in config")

    def init_display(self) -> None:
        self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_RGB332, rotate=0)
        self.auto_page_scroll_pause = config.auto_page_scroll_pause
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
        self.display_data = {"indoor_humidity": "Unknown", "outdoor_humidity": "Unknown", "fan_speed": "Unknown", "wifi_status": "Unknown"}
        self.startup_display()
    
    def startup_display(self) -> None:
        self.mode = "startup"
        self.logger.info("Startup Display")
        self.rgb_led = RGBLED(2, 0, 0)
        self.display.set_backlight(1.0)
        self.print_startup_text()

    def clear_screen(self) -> None:
        self.display.set_pen(self.BACKGROUND)
        self.display.clear()
        self.current_y = self.top_margin
        self.display.update()

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
                sleep(self.auto_page_scroll_pause)
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
                self.display_data[key] = display_data[key]
                self.logger.info(f"Updating display item {key} to {display_data[key]}")
            else:
                self.logger.warn("Invalid display update item")

    def update_main_display(self, display_data: dict = {}) -> None:
        if self.enabled:
            self.update_main_display_values(display_data)
            if self.mode == "main":
                self.clear_screen()
                self.add_text_line(f"Indoor humidity: {self.display_data['indoor_humidity']}")
                self.add_text_line(f"Outdoor humidity: {self.display_data['outdoor_humidity']}")
                self.add_text_line(f"Fan speed: {self.display_data['fan_speed']}")
                self.add_text_line(f"Network Status: {self.display_data['wifi_status']}")
        else:
            self.logger.info(f"Display update not shown as display disabled: {display_data}")
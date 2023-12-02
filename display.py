from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_RGB332
from pimoroni import RGBLED
from ulogging import uLogger

class Display:
    def __init__(self, log_level: int) -> None:
        self.logger = uLogger("Display", log_level)
        self.logger.info("Init Display")
        self.display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_RGB332, rotate=0)
        self.GREEN = self.display.create_pen(0, 255, 0)
        self.BACKGROUND = self.display.create_pen(51, 153, 102)
        self.WHITE = self.display.create_pen(255, 255, 255)
        self.display.set_font("bitmap8")
        self.font_height = 8
        self.line_spacing = 2
        self.WIDTH, self.HEIGHT = self.display.get_bounds()
        self.top_margin = 10
        self.left_margin = 10
        self.bottom_margin = 0
        self.current_y = 0
        self.header_font_scale = 3
        self.normal_font_scale = 2
        self.startup_display()
    
    def startup_display(self) -> None:
        self.logger.info("Startup Display")
        self.rgb_led = RGBLED(2, 0, 0)
        self.display.set_backlight(1.0)
        self.print_startup_text()

    def print_startup_text(self) -> None:
        self.display.set_pen(self.BACKGROUND)
        self.display.clear()
        self.display.set_pen(self.WHITE)
        self.current_y = self.top_margin
        self.display.text("Starting up...", self.left_margin, self.top_margin, self.WIDTH - self.left_margin, self.header_font_scale)
        self.display.update()
        self.current_y = self.current_y + (self.header_font_scale * self.font_height)
    
    def add_startup_text_line(self, text: str) -> None:
        self.display.set_pen(self.WHITE)
        next_y_start = self.current_y + self.line_spacing
        next_y_end = next_y_start + (self.font_height * self.normal_font_scale)
        if next_y_end > (self.HEIGHT - self.bottom_margin):
            self.print_startup_text()
            next_y_start = self.current_y + self.line_spacing
            next_y_end = next_y_start + (self.font_height * self.normal_font_scale)
        self.display.text(text, self.left_margin, next_y_start, self.WIDTH - self.left_margin, self.normal_font_scale)
        self.display.update()
        self.current_y = next_y_end # Doesn't take account of any wrapping
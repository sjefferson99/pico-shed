from ulogging import uLogger
import config
from machine import Pin, PWM

class Light:
    def __init__(self, log_level: int) -> None:
        self.log_level = log_level
        self.logger = uLogger("Light", log_level)
        self.pin = config.led_pin
        self.max_pwm_duty = 65535
        self.pwm_pin = PWM(Pin(self.pin, Pin.OUT))
        self.pwm_pin.freq(1000)
        self.brightness = config.default_brightness
        self.off()
    
    def brightness_to_corrected_duty(self, brightness: float) -> float:
        decimal = brightness / 10
        square = decimal * decimal
        return square
    
    def off(self) -> None:
        self.pwm_pin.duty_u16(0)

    def on(self) -> None:
        duty = int(self.max_pwm_duty * self.brightness_to_corrected_duty(self.brightness))
        self.pwm_pin.duty_u16(duty)
    
    def set_brightness(self, brightness: float) -> None:
        self.brightness = brightness
        duty = int(self.max_pwm_duty * self.brightness_to_corrected_duty(brightness))
        self.pwm_pin.duty_u16(duty)
        
    def get_state(self) -> bool:
        state = self.pwm_pin.duty_u16()
        if state > 0:
            return True
        else:
            return False
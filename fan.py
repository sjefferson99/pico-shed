from machine import Pin
import config

class Fan:
    def __init__(self) -> None:
        self.fan_pin = Pin(config.fan_gpio_pin, Pin.OUT)
        self.fan_pin.off()

    def switch_on(self) -> None:
        self.fan_pin.on()

    def switch_off(self) -> None:
        self.fan_pin.off()

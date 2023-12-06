from time import sleep
from machine import Pin
from display import Display

status_led = Pin("LED", Pin.OUT)

def flash_led(count: int, hz: float) -> None:
    status_led.off()
    sleep_duration = (1 / hz) / 2
    for unused in range(count):
        sleep(sleep_duration)
        status_led.on()
        sleep(sleep_duration)
        status_led.off()

def decimal_to_percent_str(decimal) -> str:
    value = decimal * 100
    string = str(value) + "%"
    return string
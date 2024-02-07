from ulogging import uLogger
import config
from machine import Pin
import uasyncio
from light import Light
from time import time

class Motion_Detector:
    def __init__(self, log_level: int) -> None:
        self.log_level = log_level
        self.logger = uLogger("Motion", log_level)
        self.logger.info("Init motion detector")
        self.pin = Pin(config.pir_pin, Pin.IN, Pin.PULL_DOWN)
        self.ON = 1
        self.OFF = -1
        self.motion_detected = 0
        self.motion_updated = uasyncio.Event()
        self.light = Light(log_level)
        self.light_off_delay = config.motion_light_off_delay
        self.light_off_time = 0

    async def motion_monitor(self) -> None:
        old_motion_value = 0
        while True:
            new_motion_value = self.pin.value()
            transition = new_motion_value - old_motion_value
            
            if transition == self.ON:
                await self.trigger_motion_detected()
            if transition == self.OFF:
                await self.trigger_motion_no_longer_detected()
            
            old_motion_value = new_motion_value
            await uasyncio.sleep_ms(500)
    
    async def trigger_motion_detected(self) -> None:
        self.logger.info("Motion detected")
        self.motion_detected = 1
        self.motion_updated.set()
        self.light.on()

    async def trigger_motion_no_longer_detected(self) -> None:
        self.logger.info("Motion no longer detected")
        self.light_off_time = time() + self.light_off_delay
        self.logger.info(f"Time now: {time()} - Light off time {self.light_off_time}")
        self.motion_detected = 0
        self.motion_updated.set()
    
    async def motion_light_off_timer(self) -> None:
        while True:
            if self.motion_detected == 0 and self.light_off_time < time() and self.light.get_state():
                self.logger.info("Motion light timeout exceeded")
                self.light.off()
            await uasyncio.sleep_ms(100)

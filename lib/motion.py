"""
Built against Pimoroni Micropython version: v1.22.2 (https://github.com/pimoroni/pimoroni-pico/releases/download/v1.22.2/pimoroni-picow-v1.22.2-micropython.uf2)
"""

from ulogging import uLogger
import config
from machine import Pin
from asyncio import Event, create_task, sleep
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
        self.motion_detected = False
        self.motion_updated = Event()
        self.light = Light(log_level)
        self.light_off_delay = config.motion_light_off_delay
        self.light_off_time = 0
        self.enabled = True
        self.config_enabled = config.enable_motion_detection

    def init_service(self) -> None:
        self.logger.info("Loading motion monitor")
        create_task(self.motion_monitor())
        self.logger.info("Loading motion light timer")
        create_task(self.motion_light_off_timer())
    
    async def motion_monitor(self) -> None:
        if self.config_enabled == False:
            self.logger.info("Motion disabled in config - motion monitor disabled")
            return
        
        old_motion_value = 0
        while True:
            if self.enabled:
                new_motion_value = self.pin.value()
                transition = new_motion_value - old_motion_value
                
                if transition == self.ON:
                    await self.trigger_motion_detected()
                if transition == self.OFF:
                    await self.trigger_motion_no_longer_detected()
                
                old_motion_value = new_motion_value
            await sleep(0.5)
    
    async def trigger_motion_detected(self) -> None:
        self.logger.info("Motion detected")
        self.motion_detected = True
        self.motion_updated.set()
        self.light.on()

    async def trigger_motion_no_longer_detected(self) -> None:
        self.logger.info("Motion no longer detected")
        self.light_off_time = time() + self.light_off_delay
        self.logger.info(f"Time now: {time()} - Light off time {self.light_off_time}")
        self.motion_detected = False
        self.motion_updated.set()
    
    async def motion_light_off_timer(self) -> None:
        if self.config_enabled == False:
            self.logger.info("Motion disabled in config - motion light off timer disabled")
            return
        
        while True:
            if self.motion_detected == 0 and self.light_off_time < time() and self.light.get_state() and self.enabled:
                self.logger.info("Motion light timeout exceeded")
                self.light.off()
            await sleep(0.1)
    
    def get_state(self) -> bool:
        return self.motion_detected
    
    def enable(self) -> None:
        self.logger.info("Motion detection enabled")
        self.enabled = True
        return

    def disable(self) -> None:
        self.logger.info("Motion detection disabled")
        self.enabled = False
        return
    
    def get_enabled(self) -> bool:
        return self.enabled
    
    def get_all_data(self) -> dict:
        all_data = {}
        all_data['state'] = self.get_state()
        all_data['enabled'] = self.get_enabled()        
        return all_data
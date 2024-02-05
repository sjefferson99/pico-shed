from ulogging import uLogger
import config
from machine import Pin, PWM
import uasyncio

class Motion_Detector:
    def __init__(self, log_level: int) -> None:
        self.log_level = log_level
        self.logger = uLogger("Motion", log_level)
        self.logger.info("Init motion detector")
        self.pin = Pin(config.pir_pin, Pin.IN, Pin.PULL_DOWN)
        self.ON = 1
        self.OFF = 0
        self.motion_detected = 0
        self.motion_updated = uasyncio.Event()

        self.max_pwm_duty = 65535
        self.light_pwm_pin = PWM(Pin(20, Pin.OUT))
        self.light_pwm_pin.freq(1000)
        self.light_pwm_pin.duty_u16(0)

    async def motion_monitor(self) -> None:
        current_motion_value = 0
        while True:
            new_motion_value = self.pin.value()
            transition = new_motion_value - current_motion_value
            
            if transition == self.ON:
                await self.trigger_motion_detected()
            if transition == self.OFF:
                await self.trigger_motion_no_longer_detected()
            
            current_motion_value = new_motion_value
            await uasyncio.sleep_ms(500)
    
    async def trigger_motion_detected(self) -> None:
        self.motion_detected = 1
        self.motion_updated.set()
        self.logger.info("Motion detected")
        self.light_pwm_pin.duty_u16(self.max_pwm_duty)

    async def trigger_motion_no_longer_detected(self) -> None:
        self.motion_detected = 0
        self.motion_updated.set()
        self.logger.info("Motion no longer detected")
        self.light_pwm_pin.duty_u16(0)

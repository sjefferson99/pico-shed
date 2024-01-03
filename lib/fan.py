from machine import Pin, PWM
import config
from lib.networking import Wireless_Network
from lib.helpers import Status_LED, decimal_to_percent_str
from lib.open_meteo import Weather_API
from lib.bme_280 import BME_280
from lib.ulogging import uLogger
from lib.display import Display
import uasyncio

class Fan:
    def __init__(self, log_level: int, display: Display, wlan: Wireless_Network) -> None:
        self.logger = uLogger("Fan", log_level)
        self.status_led = Status_LED(log_level)
        self.display = display
        self.max_pwm_duty = 65535
        self.fan_pwm_pin = PWM(Pin(config.fan_gpio_pin, Pin.OUT))
        self.fan_pwm_pin.freq(1000)
        self.switch_off()
        self.wlan = wlan
        self.weather = Weather_API(log_level, self.display)
        self.sensor = BME_280(log_level, self.display)
        self.humidity_hysteresis_pc = config.humidity_hysteresis_pc
    
    def pwm_fan_test(self) -> None:
        self.set_speed(0.1)
        self.display.add_text_line("Testing fan - 1/10 speed")
        self.status_led.flash_no_async(4, 2)
        self.set_speed(0.5)
        self.display.add_text_line("Testing fan - 1/2 speed")
        self.status_led.flash_no_async(10, 5)
    
    def fan_test(self) -> None:
        self.logger.info("Testing fan")
        self.display.add_text_line("Testing fan")
        if config.enable_PWM_fan_speed:
           self.pwm_fan_test()
        self.set_speed(1)
        self.display.add_text_line("Testing fan - full speed")
        self.status_led.flash_no_async(40, 10)
        self.set_speed(0)
        self.logger.info("Fan test complete")
        self.display.add_text_line("Fan test complete")
    
    def switch_on(self) -> None:
        self.set_speed(1)
        self.logger.info("Fan switched on")

    def switch_off(self) -> None:
        self.set_speed(0)
        self.logger.info("Fan switched off")

    def set_speed(self, speed: float) -> None:
        """
        Speed argument is decimal value between 0 (stopped) to 1(max speed)
        """
        duty = int(self.max_pwm_duty * speed)
        self.fan_pwm_pin.duty_u16(duty)
        self.logger.info(f"Fan speed set to speed {speed}, which is duty {duty}")
        self.display.update_main_display({"fan_speed": decimal_to_percent_str(speed)})
    
    def calculate_required_fan_speed(self, inside_humidity, outside_humidity) -> float:
        speed = 0
        humidity_difference = inside_humidity - (outside_humidity + self.humidity_hysteresis_pc)
        if humidity_difference > 0:
            if config.enable_PWM_fan_speed:
                speed = min(1, (humidity_difference / 10))
            else:
                speed = 1
        self.logger.info(f"calculated fan speed is {speed}")
        return speed
    
    async def set_fan_from_humidity(self, inside_humidity: float, outside_humidity: float) -> None:
        if inside_humidity >= outside_humidity + self.humidity_hysteresis_pc:
            self.logger.info("Turning on fan")
            await self.status_led.flash(1, 1)
            self.set_speed(self.calculate_required_fan_speed(inside_humidity, outside_humidity))
        if inside_humidity <= outside_humidity:
            self.logger.info("Turning off fan")
            await self.status_led.flash(2, 1)
            self.switch_off()

    def parse_humidity_data(self) -> bool:
        data_ok = True
        if "humidity" not in self.weather_data:
            self.weather_data["humidity"] = "Data missing"
            data_ok = False
        if "humidity" not in self.readings:
            self.readings["humidity"] = "Data missing"
            data_ok = False
        
        return data_ok
    
    async def assess_fan_state(self) -> None:
        self.logger.info("Assessing fan state")
        await self.status_led.flash(4, 4)
        network_access = await self.wlan.check_network_access()
        
        if network_access == True:
            self.weather_data = await self.weather.get_weather_async()
            self.readings = self.sensor.get_readings()
            data_ok = self.parse_humidity_data()
            self.display.update_main_display({"indoor_humidity": self.readings["humidity"], "outdoor_humidity": self.weather_data["humidity"]})
            if data_ok:
                await self.set_fan_from_humidity(self.readings["humidity"], self.weather_data["humidity"])
            else:
                self.logger.error("Humidity data not available - setting fan to 100%")
                self.switch_on()
        else:
            self.logger.error("No network access - setting fan to 100%")
            self.switch_on()
        
    async def start_fan_management(self) -> None:
        while True:
            uasyncio.create_task(self.assess_fan_state())
            await uasyncio.sleep(config.weather_poll_frequency_in_seconds)

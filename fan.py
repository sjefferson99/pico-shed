from machine import Pin, PWM
import config
from networking import Wireless_Network
from helpers import flash_led
from open_meteo import Weather_API
from bme_280 import BME_280
from ulogging import uLogger
from display import Display

class Fan:
    def __init__(self, log_level: int, display: Display | None = None) -> None:
        self.logger = uLogger("Fan", log_level)
        self.display = display
        self.max_pwm_duty = 65535
        self.fan_pwm_pin = PWM(Pin(config.fan_gpio_pin, Pin.OUT))
        self.fan_pwm_pin.freq(1000)
        self.switch_off()
        self.fan_test()
        self.print_to_startup_display("Starting networking")
        self.wlan = Wireless_Network(log_level)
        self.print_to_startup_display("Configuring weather API")
        self.weather = Weather_API(log_level)
        self.print_to_startup_display("Initialising BME280 sensor module")
        self.sensor = BME_280(log_level)
        self.led_retry_backoff_frequency = 4
        self.humidity_hysteresis_pc = config.humidity_hysteresis_pc

    def print_to_startup_display(self, text: str) -> None:
        if self.display != None:
            self.display.add_startup_text_line(text)
    
    def fan_test(self) -> None:
        self.logger.info("Testing fan")
        self.print_to_startup_display("Testing fan")
        self.set_speed(0.1)
        self.print_to_startup_display("Testing fan - 1/10 speed")
        flash_led(4, 2)
        self.set_speed(0.5)
        self.print_to_startup_display("Testing fan - 1/2 speed")
        flash_led(10, 5)
        self.set_speed(1)
        self.print_to_startup_display("Testing fan - full speed")
        flash_led(20, 10)
    
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
    
    def calculate_required_fan_speed(self, inside_humidity, outside_humidity) -> float:
        speed = 0
        humidity_difference = inside_humidity - (outside_humidity + self.humidity_hysteresis_pc)
        if humidity_difference > 0:
            speed = min(1, (humidity_difference / 10))
        self.logger.info(f"calculated fan speed is {speed}")
        return speed
    
    def set_fan_from_humidity(self, inside_humidity: float, outside_humidity: float) -> None:
        if inside_humidity >= outside_humidity + self.humidity_hysteresis_pc:
            self.logger.info("Turning on fan")
            flash_led(1, 1)
            self.set_speed(self.calculate_required_fan_speed(inside_humidity, outside_humidity))
        if inside_humidity <= outside_humidity:
            self.logger.info("Turning off fan")
            flash_led(2, 1)
            self.switch_off()

    def assess_fan_state(self) -> None:
        self.logger.info("Assessing fan state")
        flash_led(4, 4)
        network_access = self.check_network_access()
        if network_access == True:
            self.weather_data = self.weather.get_weather()
            self.readings = self.sensor.get_readings()
            self.set_fan_from_humidity(self.readings["humidity"], self.weather_data["humidity"])

    def network_retry_backoff(self) -> None:
        self.logger.info(f"Backing off retry for {config.wifi_retry_backoff_seconds} seconds")
        flash_led((config.wifi_retry_backoff_seconds * self.led_retry_backoff_frequency), self.led_retry_backoff_frequency)

    def check_network_access (self) -> bool:
        self.logger.info("Checking for network access")
        retries = 0
        while self.wlan.get_status() != 3 and retries <= config.wifi_connect_retries:
            try:
                self.wlan.connect_wifi()
                return True
            except Exception:
                self.logger.warn(f"Error connecting to wifi on attempt {retries + 1} of {config.wifi_connect_retries + 1}")
                retries += 1
                self.network_retry_backoff()

        if self.wlan.get_status == 3:
            self.logger.info("Connected to wireless network")
            return True
        else:
            self.logger.warn("Unable to connect to wireless network")
            self.switch_on()
            return False

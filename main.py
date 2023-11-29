from time import sleep
import config
from fan import Fan

fan = Fan(log_level=0)

while True:

    fan.assess_fan_state()

    sleep(config.weather_poll_frequency_in_seconds)
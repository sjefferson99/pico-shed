from time import sleep
import config
from fan import Fan

fan = Fan()

while True:

    fan.assess_fan_state()

    sleep(config.weather_poll_frequency_in_seconds)
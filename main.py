from time import sleep
import config
from environment import Environment

env = Environment(log_level=4)

sleep(2)

while True:

    env.assess_fan_state()

    sleep(config.weather_poll_frequency_in_seconds)
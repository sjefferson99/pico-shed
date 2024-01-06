## Wifi
wifi_ssid = ""
wifi_password = ""
wifi_country = "GB"

wifi_connect_timeout_seconds = 10
wifi_connect_retries = 1
wifi_retry_backoff_seconds = 5

## Open Meteo
# lat and long in decimal format array with Lattitude in 0
# postion and Longitude in 1
# e.g. latlong[50.9048, -1.4043] for Southampton UK
lat_long = [50.9048, -1.4043]
weather_poll_frequency_in_seconds = 300

## BME280
i2c_pins = {"sda": 0, "scl": 1}

## Fan
fan_gpio_pin = 2
# How much dryer in RH % outside before the fan turns on
humidity_hysteresis_pc = 1
# Use PWM to gradually increase fan speed or simply turn fan on and off
enable_PWM_fan_speed = False

## Display Supports Pico Display and Pico Display 2 (with extra space as unused border)
display_enabled = True
# Seconds to pause each auto scrolling information page (startup) for troubleshooting
auto_page_scroll_pause_s = 0
backlight_timeout_s = 30

## Battery monitor
# Set a valid ADC GP pin (26-28)
battery_adc_pin = 28
# Voltage divider resistor values in ohms - see documentation for diagram
r1 = 21600
r2 = 5040
# What value to add or subtract to correct a reported voltage
voltage_correction = 0.12

## Web interface
web_port = 80
wifi_ssid = ""
wifi_password = ""
wifi_country = "GB"

wifi_status_led = True
# -1 = retry forever
wifi_auto_reconnect_tries = -1

# lat and long in decimal format array with Lattitude in 0
# postion and Longitude in 1
# e.g. latlong[50.9048, -1.4043] for Southampton UK
lat_long = [50.9048, -1.4043]
weather_poll_frequency_in_seconds = 300

i2c_pins = {"sda": 0, "scl": 1}

fan_gpio_pin = 2
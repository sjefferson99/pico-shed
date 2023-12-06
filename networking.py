from utime import ticks_ms, sleep
from math import ceil
import rp2
import network
from ubinascii import hexlify
import config
from machine import Pin
from ulogging import uLogger
from helpers import flash_led
from display import Display

class Wireless_Network:

    def __init__(self, log_level: int, display: Display) -> None:
        self.logger = uLogger("WIFI", log_level)
        self.display = display
        self.wifi_ssid = config.wifi_ssid
        self.wifi_password = config.wifi_password
        self.wifi_country = config.wifi_country
        rp2.country(self.wifi_country)
        self.disable_power_management = 0xa11140
        self.status_led_enable = config.wifi_status_led
        
        # Reference: https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf
        self.CYW43_LINK_DOWN = 0
        self.CYW43_LINK_JOIN = 1
        self.CYW43_LINK_NOIP = 2
        self.CYW43_LINK_UP = 3
        self.CYW43_LINK_FAIL = -1
        self.CYW43_LINK_NONET = -2
        self.CYW43_LINK_BADAUTH = -3
        self.status_names = {
        self.CYW43_LINK_DOWN: "Link is down",
        self.CYW43_LINK_JOIN: "Connected to wifi",
        self.CYW43_LINK_NOIP: "Connected to wifi, but no IP address",
        self.CYW43_LINK_UP: "Connect to wifi with an IP address",
        self.CYW43_LINK_FAIL: "Connection failed",
        self.CYW43_LINK_NONET: "No matching SSID found (could be out of range, or down)",
        self.CYW43_LINK_BADAUTH: "Authenticatation failure",
        }

        self.configure_wifi()

    def configure_wifi(self) -> None:
        self.display.add_text_line("Configuring WiFi")
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.config(pm=self.disable_power_management)
        mac = hexlify(self.wlan.config('mac'),':').decode()
        self.logger.info("MAC: " + mac)
        self.display.add_text_line(f"MAC: {mac}")
    
    def dump_status(self):
        status = self.wlan.status()
        self.logger.info(f"active: {1 if self.wlan.active() else 0}, status: {status} ({self.status_names[status]})")
        return status
    
    def wait_status(self, expected_status, *, timeout=config.wifi_connect_timeout_seconds, tick_sleep=0.5) -> bool:
        for unused in range(ceil(timeout / tick_sleep)):
            sleep(tick_sleep)
            status = self.dump_status()
            if status == expected_status:
                return True
            if status < 0:
                raise Exception(self.status_names[status])
        return False
    
    def disconnect_wifi_if_necessary(self) -> None:
        status = self.dump_status()
        if status >= self.CYW43_LINK_JOIN and status <= self.CYW43_LINK_UP:
            self.logger.info("Disconnecting...")
            self.wlan.disconnect()
            try:
                self.wait_status(self.CYW43_LINK_DOWN)
            except Exception as x:
                raise Exception(f"Failed to disconnect: {x}")
        self.logger.info("Ready for connection!")
    
    def generate_connection_info(self, elapsed_ms) -> None:
        ip, subnet, gateway, dns = self.wlan.ifconfig()
        self.logger.info(f"IP: {ip}, Subnet: {subnet}, Gateway: {gateway}, DNS: {dns}")
        
        self.logger.info(f"Elapsed: {elapsed_ms}ms")
        if elapsed_ms > 5000:
            self.logger.warn(f"took {elapsed_ms} milliseconds to connect to wifi")

    def connection_error(self) -> None:
        flash_led(2, 2)
        self.display.update_main_display({"wifi_status": "Error"})

    def connection_success(self) -> None:
        flash_led(1, 2)
        self.display.update_main_display({"wifi_status": "Connected"})

    def attempt_ap_connect(self) -> None:
        self.logger.info(f"Connecting to SSID {self.wifi_ssid} (password: {self.wifi_password})...")
        self.disconnect_wifi_if_necessary()
        self.wlan.connect(self.wifi_ssid, self.wifi_password)
        try:
            self.wait_status(self.CYW43_LINK_UP)
        except Exception as x:
            self.connection_error()
            raise Exception(f"Failed to connect to SSID {self.wifi_ssid} (password: {self.wifi_password}): {x}")
        self.connection_success()
        self.logger.info("Connected successfully!")
    
    def connect_wifi(self) -> None:
        self.logger.info("Connecting to wifi")
        start_ms = ticks_ms()
        try:
            self.attempt_ap_connect()
        except Exception:
            raise Exception(f"Failed to connect to network")

        elapsed_ms = ticks_ms() - start_ms
        self.generate_connection_info(elapsed_ms)

    def get_status(self) -> int:
        return self.wlan.status()
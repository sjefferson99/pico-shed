from utime import ticks_ms, sleep
from math import ceil
import rp2
import network
from ubinascii import hexlify
import config
from machine import Pin
from ulogging import uLogger
from helpers import flash_led

class Wireless_Network:

    def __init__(self) -> None:
        self.wifi_ssid = config.wifi_ssid
        self.wifi_password = config.wifi_password
        self.wifi_country = config.wifi_country
        rp2.country(self.wifi_country)
        self.disable_power_management = 0xa11140
        self.status_led_enable = config.wifi_status_led
        self.logger = uLogger("WIFI", 0)
        
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
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.config(pm=self.disable_power_management)
        mac = hexlify(self.wlan.config('mac'),':').decode()
        self.logger.info("MAC: " + mac)
        flash_led(1, 1)
    
    def dump_status(self):
        status = self.wlan.status()
        self.logger.info(f"active: {1 if self.wlan.active() else 0}, status: {status} ({self.status_names[status]})")
        return status
    
    def wait_status(self, expected_status, *, timeout=10, tick_sleep=0.5) -> bool:
        for i in range(ceil(timeout / tick_sleep)):
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
    
    def assess_connection_time(self, elapsed_ms) -> None:
        if elapsed_ms > 5000:
            self.logger.warn(f"took {elapsed_ms} milliseconds to connect to wifi")

    def connect_wifi(self, retry_count) -> None:
        self.logger.info(f"Connecting to wifi network '{self.wifi_ssid}'")

        retries = 0
        try:
            self.connect_to_ap()
        except Exception:
            if retries <= retry_count or retry_count < 0:
                flash_led(2, 2)
                retries += 1
                self.logger.warn(f"Retrying wifi connection, retry count: {retries} of {retry_count}")
                self.connect_to_ap()
            else:
                raise Exception(f"Failed to connect to wifi after retry count of {retry_count} exceeded")
        
        self.logger.info(f"Connected to wifi with {retries} retries")

    def connect_to_ap(self) -> None:

        start_ms = ticks_ms()

        self.disconnect_wifi_if_necessary()
        
        self.logger.info(f"Connecting to SSID {self.wifi_ssid} (password: {self.wifi_password})...")
        self.wlan.connect(self.wifi_ssid, self.wifi_password)
        try:
            self.wait_status(self.CYW43_LINK_UP)
        except Exception as x:
            raise Exception(f"Failed to connect to SSID {self.wifi_ssid} (password: {self.wifi_password}): {x}")
        self.logger.info("Connected successfully!")

        ip, subnet, gateway, dns = self.wlan.ifconfig()
        self.logger.info(f"IP: {ip}, Subnet: {subnet}, Gateway: {gateway}, DNS: {dns}")
        
        elapsed_ms = ticks_ms() - start_ms
        self.logger.info(f"Elapsed: {elapsed_ms}ms")
        self.assess_connection_time(elapsed_ms)

        flash_led(1, 2)
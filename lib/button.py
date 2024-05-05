"""
Built against Pimoroni Micropython version: v1.22.2 (https://github.com/pimoroni/pimoroni-pico/releases/download/v1.22.2/pimoroni-picow-v1.22.2-micropython.uf2)
"""

from machine import Pin
from ulogging import uLogger
from asyncio import Event, sleep

class Button:
    """
    Async button class that instantiates a coroutine to watch for button pin state changes, debounces and sets appropriate asyncio events.
    """
    def __init__(self, GPIO_pin: int, name: str, log_level: int = 2, pull_up: bool = True, pressed_event: Event | None = None, released_event: Event | None = None) -> None:
        """
        Provide buttons details to set up a logged async button watcher on a GPIO pin. Pull_up true for buttons connected to ground and False for pins connected to 3.3v
        The two event arguments should be of type asyncio.Event and used elsewhere to take action on button state changes.
        You can provide only a GPIO pin and a name and a default pull up button will be created with events accessible as object attributes.
        """
        self.log_level = log_level
        self.logger = uLogger(f"Button {GPIO_pin}", log_level)
        self.logger.info(f"Init button {name}")
        self.gpio = GPIO_pin
        self.pin_pull = Pin.PULL_DOWN
        if pull_up:
            self.pin_pull = Pin.PULL_UP
        self.pin = Pin(GPIO_pin, Pin.IN, self.pin_pull)
        self.name = name
        self.pressed_event: Event = pressed_event if pressed_event is not None else Event()
        self.released_event: Event = released_event if released_event is not None else Event()
   
    async def wait_for_press(self) -> None:
        """
        Async coroutine to monitor for a change in button state. On state change, input is debounced and appropriate pushed or released event is set.
        Call clear_pressed or clear_released as appropriate in function responding to button events.
        """
        self.logger.info(f"Starting button press watcher for button: {self.name}")

        while True:
            current_value = self.pin.value()
            active = 0
            while active < 20:
                if self.pin.value() != current_value:
                    active += 1
                else:
                    active = 0
                await sleep(0.001)

            if self.pin.value() == 0:
                self.logger.info(f"Button pressed: {self.name}")
                self.pressed_event.set()
            else:
                self.logger.info(f"Button released: {self.name}")
                self.released_event.set()

    def clear_pressed(self) -> None:
        self.pressed_event.clear()
    
    def clear_released(self) -> None:
        self.released_event.clear()
    
    def get_name(self) -> str:
        """Get button name"""
        return self.name
    
    def get_pin(self) -> int:
        """Get GPIO pin connected to button"""
        return self.gpio

    def get_pull_pin(self) -> int:
        """Get pull up configuration, True is up, False is down"""
        return self.pin_pull
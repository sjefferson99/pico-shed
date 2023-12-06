# Pico-shed
## Introduction
Environmental reporting and control for a shed or any similar space

## Features
First version is simply to control the induction fan on my shed to only run when the humidity outside is dryer than the humidity inside the shed to keep the enviroment as dry as possible.
The fan pin should be run through a transistor and not directly connected for current/dynamic loading reasons. A transistor is required instead of a relay to support the PWM speed control.

- Open-meteo API lookup for local area weather conditions
- BME280 local environment sensing (temperature, humidity, pressure)
- GPIO on/off control based on comparisons of local area vs environment conditions
- Debug logging capability - inherited from top fan class
- Configurable network retries
- Basic network status feedback via onboard LED
- Fan fails to on state if no network
- Ensures network for API calls with configurable retries 
- Hysteresis on fan state change
- PWM fan speed control based on humidity differential
- Fan startup test with LED feedback
- Pico display pack support (tested with [Pico Dsiplay Pack 240x135](https://shop.pimoroni.com/products/pico-display-pack?variant=32368664215635)) 
  - Startup information 
  - Indoor humidity
  - Outdoor humidity
  - Fan speed
  - Network status
  - Configurable backlight timeout

##  Firmware
This code requires the Pimoroni micropython firmware and was written on [v1.21.0](https://github.com/pimoroni/pimoroni-pico/releases/tag/v1.21.0)

## Hardware
Pico W with standard header pins is attached via the stacking headers (to allow easy removal of the Pico) to a pico display, sandwiching a pico proto board between allowing breakout of the I2C and GPIO output controls.

- [Pico W](https://shop.pimoroni.com/products/raspberry-pi-pico-w?variant=40059369619539)
- [Pico Display Pack](https://shop.pimoroni.com/products/pico-display-pack?variant=32368664215635)
- [Pico Proto](https://shop.pimoroni.com/products/pico-proto?variant=32369530110035)
- [Pico stacking headers](https://shop.pimoroni.com/products/pico-stacking-headers?variant=39272657682515)
- [BME280](https://shop.pimoroni.com/products/bme280-breakout?variant=29420960677971)
- [JST connectors](https://www.amazon.co.uk/gp/product/B09LQGDHV2)
- [PWM transistor](https://www.amazon.co.uk/gp/product/B07QVZK39F)
- [Transistor heatsinks](https://www.amazon.co.uk/gp/product/B081GS15N6)

## Execution order
1. Fan test
2. Fan speed evaluation
   - Network connection
     - Attempt connection
     - If failure to connect, retry for back off period and attempt reconnect
     - Repeat backoff and reconnect up to retry count
     - If failure to connect after retry count, set fan to 100% speed, skip API poll and fan speed adjustment
   - Poll Open-Meteo API
   - Calculate appropriate fan speed and adjust PWM output
3. Sleep and loop back to fan speed evaluation

## LED status key
The LED shows the status of the board, which combined with the execution order above and activity output tables below will tell you what is going on without a display attached.

|Activity|Output|Meaning|
|--------|------|-------|
|Fan test|4 flashes @ 2Hz|10% duty cycle| 
|Fan test|10 flashes @ 5Hz|50% duty cycle|
|Fan test|20 flashes @ 10Hz|100% duty cycle|
|Fan speed evaluation|4 flashes @ 4Hz|Waking up to evaluate humidity for fan speed|
|Network connection|1 flash @ 2Hz| Connected successfully|
|Network connection|2 flashes @ 2Hz| Failed to connect|
|Network connection back off|Flash @ 4Hz for backoff duration in config file|Waiting to retry connection|
|Set fan speed|1 flash @ 1Hz|Fan turned on|
|Set fan speed|2 flashes @ 1Hz|Fan turned off|
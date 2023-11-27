# Pico-shed
## Introduction
Environmental reporting and control for a shed or any similar space

## Features
First version is simply to control the induction fan on my shed to only run when the humidity outside is dryer than the humidity inside the shed to keep the enviroment as dry as possible.
The fan pin should be run through a relay or transistor and not directly connected for current/dynamic loading reasons. A transistor is best as that will support PWM (*spoilers*)

- Open-meteo API lookup for local area weather conditions
- BME280 local environment sensing (temperature, humidity, pressure)
- GPIO on/off control based on comparisons of local area vs environment conditions
- Debug logging capability
- Configurable network retries
- Basic network status feedback via onboard LED
- Hysteresis on fan state change

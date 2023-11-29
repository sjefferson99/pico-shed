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
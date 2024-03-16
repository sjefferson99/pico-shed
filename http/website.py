from http.webserver import webserver
import config
from lib.fan import Fan
from lib.battery import Battery_Monitor
from json import dumps
from lib.light import Light
from lib.motion import Motion_Detector
from logging import Logger
import uasyncio

class Web_App:

    def __init__(self, log_level: int, module_list: dict) -> None:
        """
        module_list is a dictionary of required modules, this should take the structure:
        {'fan_module': Fan, 'battery_monitor': Battery_Monitor}
        """
        self.logger = Logger(log_level)
        self.app = webserver()
        self.fan = module_list['fan']
        self.battery_monitor = module_list['battery_monitor']
        self.motion = module_list['motion']
        self.light = module_list['light']
        self.wlan = module_list['wlan']
        self.display = module_list['display']
        self.running = False
        self.create_js()
        self.create_style_css()
        self.create_light_control_css()
        self.create_homepage()
        self.create_api()
        self.create_light_control()

    def init_service(self):
        network_access = uasyncio.run(self.wlan.check_network_access())

        if network_access == True:
            self.logger.info("Starting web server")
            self.app.run(host='0.0.0.0', port=config.web_port, loop_forever=False)
            self.running = True
            self.logger.info("Starting web monitor")
            uasyncio.create_task(self.status_monitor())
        else:
            self.logger.error("No network access - web server not started")
    
    async def status_monitor(self) -> None:
        while True:
            if self.wlan.dump_status() == 3 and self.running:
                self.display.update_main_display_values({"web_server": str(self.wlan.ip) + ":" + str(config.web_port)})
            else:
                self.display.update_main_display_values({"web_server": "Stopped"})
            await uasyncio.sleep(5)

    def create_js(self):
        @self.app.route('/js/control.js')
        async def index(request, response):
            await response.send_file('/http/js/control.js', content_type='application/javascript')
    
    def create_style_css(self):
        @self.app.route('/css/style.css')
        async def index(request, response):
            await response.send_file('/http/css/style.css', content_type='text/css')

    def create_light_control_css(self):
        @self.app.route('/css/light_control.css')
        async def index(request, response):
            await response.send_file('/http/css/light_control.css', content_type='text/css')
    
    def create_light_control(self):
        @self.app.route('/html/light_control')
        async def index(request, response):
            await response.send_file('/http/html/light_control.html')

    def create_homepage(self) -> None:
        @self.app.route('/')
        async def index(request, response):
            await response.start_html()
            ih = self.fan.get_latest_indoor_humidity()
            oh = self.fan.get_latest_outdoor_humidity()
            fs = self.fan.get_fan_speed() * 100
            bv = round(self.battery_monitor.read_battery_voltage(), 2)
            lb = self.light.get_brightness_pc()
            ls = self.light.get_state()
            ms = self.motion.get_state()
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <link rel="stylesheet" href="/css/style.css">
            </head>
                <body>
                    <h1>Pico environment control</h1>
                    <h2>Live values</h2>
                    <ul>
                        <li>Indoor humidity: {indoor_humidity}%</li>
                        <li>Outdoor humidity: {outdoor_humidity}%</li>
                        <li>Fan speed: {fan_speed}%</li>
                        <li>Battery voltage: {battery_voltage}%</li>
                        <li>Light brightness: {light_brightness}%</li>
                        <li>Light state: {light_state}</li>
                        <li>Motion state: {motion_state}</li>
                    </ul>

                    <a href='html/light_control'>Light control</a>
                    <p />
                    <a href='/api'>API</a>
                </body>
            </html>
            
            """.format(indoor_humidity = ih, outdoor_humidity = oh, fan_speed = fs, battery_voltage = bv, light_brightness = lb, light_state = ls, motion_state = ms)
            await response.send(html)

    def create_api(self) -> None:
        @self.app.route('/api')
        async def api(request, response):
            await response.start_html()
            html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <link rel="stylesheet" href="/css/style.css">
            </head>
                <body>
                    <h1>Pico environment control - API</h1>
                    <h2>Endpoints</h2>
                    <ul>
                        <li>Indoor humidity: <a href="/api/fan/indoor_humidity">/api/fan/indoor_humidity</a></li>
                        <li>Outdoor humidity: <a href="/api/fan/outdoor_humidity">/api/fan/outdoor_humidity</a></li>
                        <li>Fan speed: <a href="/api/fan/speed">/api/fan/speed</a></li>
                        <li>Battery voltage: <a href="/api/battery/voltage">/api/battery/voltage</a></li>
                        <li>Light brightness (GET): <a href="/api/light/brightness">/api/light/brightness</a></li>
                        <li>Light brightness (PUT): Brightness = 0-100 - curl: curl -X PUT http://(IP:port)/api/light/brightness -d "value=50"</li>
                        <li>Light state (GET): <a href="/api/light/state">/api/light/state</a></li>
                        <li>Light state (PUT): State = on/off/auto - e.g. curl: curl -X PUT http://(IP:port)/api/light/state -d "state=on"</li>
                        <li>Motion state: <a href="/api/motion/state">/api/motion/state</a></li>
                    </ul>

                    <p />

                    <a href="/">Home</a>
                </body>
            </html>
            
            """
            await response.send(html)
        
        self.app.add_resource(indoor_humidity, '/api/fan/indoor_humidity', fan = self.fan)
        self.app.add_resource(outdoor_humidity, '/api/fan/outdoor_humidity', fan = self.fan)
        self.app.add_resource(fan_speed, '/api/fan/speed', fan = self.fan)
        self.app.add_resource(battery_voltage, '/api/battery/voltage', battery_monitor = self.battery_monitor)
        self.app.add_resource(light_brightness, '/api/light/brightness', light = self.light)
        self.app.add_resource(light_state, '/api/light/state', light = self.light, motion = self.motion)
        self.app.add_resource(motion_state, '/api/motion/state', motion = self.motion)

class indoor_humidity():

    def get(self, data, fan: Fan):
        html = dumps(fan.get_latest_indoor_humidity())
        return html

class outdoor_humidity():

    def get(self, data, fan: Fan):
        html = dumps(fan.get_latest_outdoor_humidity())
        return html
    
class fan_speed():

    def get(self, data, fan: Fan):
        html = dumps(fan.get_fan_speed() * 100)
        return html
    
class battery_voltage():

    def get(self, data, battery_monitor: Battery_Monitor):
        html = dumps(round(battery_monitor.read_battery_voltage(), 2))
        return html

class light_brightness():

    def get(self, data, light: Light):
        html = dumps(light.get_brightness_pc())
        return html
    
    def put(self, data, light: Light):
        html = {}
        brightness = int(data["value"])
        if brightness >=0 and brightness <=100:
            html["requested_brightness"] = brightness
            light.set_brightness_pc(brightness)
            brightness_set = light.get_brightness_pc()
            html["set_brightness"] = brightness_set
            html["message"] = "Light set to: " + str(brightness_set) +"%"
        else:
            html["message"] = "brightness percent not between 0 and 100. PUT data: " + data
        html["requested_brightness"] = brightness
        html = dumps(html)
        return html

class light_state():

    def get(self, data, light: Light, motion: Motion_Detector):
        html = dumps(light.get_state())
        return html
    
    def put(self, data, light: Light, motion: Motion_Detector):
        html = {}
        if data["state"] == "on":
            motion.disable()
            light.on()
            html["Message"] = "Light set on"
        elif data["state"] == "off":
            motion.disable()
            light.off()
            html["Message"] = "Light set off"
        elif data["state"] == "auto":
            motion.enable()
            html["Message"] = "Light set to auto"
        else:
            html["Message"] = "Unrecognised light state command"
        
        html["state"] = light.get_state()
        html = dumps(html)
        return html

class motion_state():

    def get(self, data, motion: Motion_Detector):
        html = dumps(motion.get_state())
        return html
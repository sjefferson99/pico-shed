from http.webserver import webserver
import config
from lib.fan import Fan
from lib.battery import Battery_Monitor
from json import dumps
from lib.light import Light
from lib.motion import Motion_Detector
from lib.ulogging import uLogger
import uasyncio

class Web_App:

    def __init__(self, log_level: int, module_list: dict) -> None: #TODO: module_list should probably be modules, named list of type dict is confusing.
        """
        module_list is a dictionary of required modules, this should take the structure:
        {'fan_module': Fan, 'battery_monitor': Battery_Monitor}
        """
        self.ulogger = uLogger("Web app", log_level)
        self.ulogger.info("Init webserver")
        self.app = webserver()
        self.all_modules = module_list
        self.environment = module_list['environment']
        self.fan = module_list['fan']
        self.battery_monitor = module_list['battery_monitor']
        self.motion = module_list['motion']
        self.light = module_list['light']
        self.wlan = module_list['wlan']
        self.display = module_list['display']
        self.running = False
        self.create_js()
        self.create_style_css()
        self.create_homepage()
        self.create_api()

    def init_service(self):
        network_access = uasyncio.run(self.wlan.check_network_access())

        if network_access == True:
            self.ulogger.info("Starting web server")
            self.app.run(host='0.0.0.0', port=config.web_port, loop_forever=False)
            self.running = True
            self.ulogger.info("Starting web monitor")
            uasyncio.create_task(self.status_monitor())
        else:
            self.ulogger.error("No network access - web server not started")
    
    async def status_monitor(self) -> None:
        while True:
            if self.wlan.dump_status() == 3 and self.running:
                self.display.update_main_display_values({"web_server": str(self.wlan.ip) + ":" + str(config.web_port)})
            else:
                self.display.update_main_display_values({"web_server": "Stopped"})
            await uasyncio.sleep(5)

    def create_js(self):
        @self.app.route('/js/api.js')
        async def index(request, response):
            await response.send_file('/http/html/js/api.js', content_type='application/javascript')
    
    def create_style_css(self):
        @self.app.route('/css/style.css')
        async def index(request, response):
            await response.send_file('/http/html/css/style.css', content_type='text/css')
    
    def create_homepage(self) -> None:
        @self.app.route('/')
        async def index(request, response):
            await response.send_file('/http/html/index.html')

    def create_api(self) -> None:
        @self.app.route('/api')
        async def api(request, response):
            await response.send_file('/http/html/api.html')
        
        self.app.add_resource(all_data, '/api/all_data', environment_modules = self.all_modules, ulogger = self.ulogger)
        self.app.add_resource(indoor_humidity, '/api/fan/indoor_humidity', fan = self.fan, ulogger = self.ulogger)
        self.app.add_resource(outdoor_humidity, '/api/fan/outdoor_humidity', fan = self.fan, ulogger = self.ulogger)
        self.app.add_resource(fan_speed, '/api/fan/speed', fan = self.fan, ulogger = self.ulogger)
        self.app.add_resource(battery_voltage, '/api/battery/voltage', battery_monitor = self.battery_monitor, ulogger = self.ulogger)
        self.app.add_resource(light_brightness, '/api/light/brightness', light = self.light, ulogger = self.ulogger)
        self.app.add_resource(light_state, '/api/light/state', light = self.light, motion = self.motion, ulogger = self.ulogger)
        self.app.add_resource(light_motion_detection, '/api/light/motion_detection', motion = self.motion, ulogger = self.ulogger)
        self.app.add_resource(motion_state, '/api/motion/state', motion = self.motion, ulogger = self.ulogger)
        self.app.add_resource(wlan_mac, '/api/wlan/mac', wlan = self.wlan, ulogger = self.ulogger)
        self.app.add_resource(version, '/api/version', environment = self.environment, ulogger = self.ulogger)

class all_data():

    def get(self, data, environment_modules: dict, ulogger: uLogger):
        ulogger.info("API request - all_data")
        all_data = {}

        for module in environment_modules:
            try:
                all_data[module] = environment_modules[module].get_all_data() #TODO: module class contains get_all_data and init_service and is extended
            except AttributeError as e:
                ulogger.warn(f"{module} has no get_all_data function. Error: {e}")
            except Exception as e:
                ulogger.warn(f"An error occurred while processing {module}: {e}")

        html = dumps(all_data)
        ulogger.info(f"Return value: {html}")
        return html

class indoor_humidity():

    def get(self, data, fan: Fan, ulogger: uLogger):
        ulogger.info("API request - fan/indoor_humidity")
        html = dumps(fan.get_latest_indoor_humidity())
        ulogger.info(f"Return value: {html}")
        return html

class outdoor_humidity():

    def get(self, data, fan: Fan, ulogger: uLogger):
        ulogger.info("API request - fan/outdoor_humidity")
        html = dumps(fan.get_latest_outdoor_humidity())
        ulogger.info(f"Return value: {html}")
        return html
    
class fan_speed():

    def get(self, data, fan: Fan, ulogger: uLogger):
        ulogger.info("API request - fan/speed")
        html = dumps(fan.get_fan_speed() * 100)
        ulogger.info(f"Return value: {html}")
        return html
    
class battery_voltage():

    def get(self, data, battery_monitor: Battery_Monitor, ulogger: uLogger):
        ulogger.info("API request - battery/voltage")
        html = dumps(round(battery_monitor.read_battery_voltage(), 2))
        ulogger.info(f"Return value: {html}")
        return html

class light_brightness():

    def get(self, data, light: Light, ulogger: uLogger):
        ulogger.info("API request - light/brightness")
        html = dumps(light.get_brightness_pc())
        ulogger.info(f"Return value: {html}")
        return html
    
    def put(self, data, light: Light, ulogger: uLogger):
        ulogger.info("API request - (PUT) fan/indoor_humidity")
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
        ulogger.info(f"Return value: {html}")
        return html

class light_state():

    def get(self, data, light: Light, motion: Motion_Detector, ulogger: uLogger):
        ulogger.info("API request - light/state")
        html = dumps(light.get_state())
        ulogger.info(f"Return value: {html}")
        return html
    
    def put(self, data, light: Light, motion: Motion_Detector, ulogger: uLogger):
        ulogger.info("API request - (PUT) light/state)")
        html = {}
        if data["state"] == "on":
            motion.disable()
            light.on()
            html["Message"] = "Light set on"
        elif data["state"] == "off":
            motion.disable()
            light.off()
            html["Message"] = "Light set off"
        else:
            html["Message"] = "Unrecognised light state command"
        
        html = dumps(light.get_state())
        ulogger.info(f"Return value: {html}")
        return html
    
class light_motion_detection():

    def get(self, data, motion: Motion_Detector, ulogger: uLogger):
        ulogger.info("API request - light/motion_detection")
        html = dumps(motion.get_enabled())
        ulogger.info(f"Return value: {html}")
        return html
    
    def put(self, data, motion: Motion_Detector, ulogger: uLogger):
        ulogger.info("API request - (PUT) light/motion_detection)")
        html = {}
        if data["state"] == "enabled":
            motion.enable()
            html["Message"] = "Light motion detection enabled"
        elif data["state"] == "disabled":
            motion.disable()
            html["Message"] = "Light motion detection disabled"
        else:
            html["Message"] = "Unrecognised light motion detection command"
        
        html = dumps(motion.get_enabled())
        ulogger.info(f"Return value: {html}")
        return html

class motion_state():

    def get(self, data, motion: Motion_Detector, ulogger: uLogger):
        ulogger.info("API request - motion/state")
        html = dumps(motion.get_state())
        ulogger.info(f"Return value: {html}")
        return html
    
class wlan_mac():

    def get(self, data, wlan, ulogger: uLogger):
        ulogger.info("API request - wlan/mac")
        html = dumps(wlan.get_mac())
        ulogger.info(f"Return value: {html}")
        return html
    
class version():

    def get(self, data, environment, ulogger: uLogger):
        ulogger.info("API request - all_data")
        html = dumps(environment.get_version())
        ulogger.info(f"Return value: {html}")
        return html
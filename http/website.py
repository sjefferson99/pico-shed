from http.webserver import webserver
import config
from lib.fan import Fan
from lib.battery import Battery_Monitor
from json import dumps

class Web_App:

    def __init__(self, module_list: dict) -> None:
        """
        module_list is a dictionary of required modules, this should take the structure:
        {'fan_module': Fan, 'battery_monitor': Battery_Monitor}
        """
        self.app = webserver()
        self.fan = module_list['fan_module']
        self.battery_monitor = module_list['battery_monitor']
        self.running = False
        self.create_homepage()
        self.create_api()

    def load_into_loop(self):
        self.app.run(host='0.0.0.0', port=config.web_port, loop_forever=False)
        self.running = True

    def create_homepage(self) -> None:
        @self.app.route('/')
        async def index(request, response):
            await response.start_html()
            ih = self.fan.get_latest_indoor_humidity()
            oh = self.fan.get_latest_outdoor_humidity()
            fs = self.fan.get_fan_speed() * 100
            bv = round(self.battery_monitor.read_battery_voltage(), 2)
            html = """
            <html>
                <body>
                    <h1>Pico environment control</h1>
                    <h2>Live values</h2>
                    <ul>
                        <li>Indoor humidity: {indoor_humidity}%</li>
                        <li>Outdoor humidity: {outdoor_humidity}%</li>
                        <li>Fan speed: {fan_speed}%</li>
                        <li>Battery voltage: {battery_voltage}%</li>
                    </ul>
                </body>
            </html>
            
            """.format(indoor_humidity = ih, outdoor_humidity = oh, fan_speed = fs, battery_voltage = bv)
            await response.send(html)

    def create_api(self) -> None:
        @self.app.route('/api')
        async def api(request, response):
            await response.start_html()
            html = """
            <html>
                <body>
                    <h1>Pico environment control - API</h1>
                    <h2>Endpoints</h2>
                    <ul>
                        <li>Indoor humidity: <a href="/api/fan/indoor_humidity">/api/fan/indoor_humidity</a></li>
                        <li>Outdoor humidity: <a href="/api/fan/outdoor_humidity">/api/fan/outdoor_humidity</a></li>
                        <li>Fan speed: <a href="/api/fan/speed">/api/fan/speed</a></li>
                        <li>Battery voltage: <a href="/api/battery/voltage">/api/battery/voltage</a></li>
                    </ul>
                </body>
            </html>
            
            """
            await response.send(html)
        
        self.app.add_resource(indoor_humidity, '/api/fan/indoor_humidity', fan = self.fan)
        self.app.add_resource(outdoor_humidity, '/api/fan/outdoor_humidity', fan = self.fan)
        self.app.add_resource(fan_speed, '/api/fan/speed', fan = self.fan)
        self.app.add_resource(battery_voltage, '/api/battery/voltage', battery_monitor = self.battery_monitor)

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
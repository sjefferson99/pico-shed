from http.webserver import webserver
import config
from lib.fan import Fan
from lib.battery import Battery_Monitor

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

    def load_into_loop(self):
        self.app.run(host='0.0.0.0', port=config.web_port, loop_forever=False)
        self.running = True

    def create_homepage(self) -> None: #TODO These values only load on startup and don't update
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


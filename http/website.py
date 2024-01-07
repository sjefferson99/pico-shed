from http.webserver import webserver
import config
from lib.fan import Fan

class Web_App:

    def __init__(self, fan_module: Fan) -> None:
        self.app = webserver()
        self.fan = fan_module
        self.running = False
        self.create_homepage()
        
    def load_into_loop(self):
        self.app.run(host='0.0.0.0', port=config.web_port, loop_forever=False)
        self.running = True

    def create_homepage(self) -> None:
        @self.app.route('/')
        async def index(request, response):
            await response.start_html()
            ih = self.fan.get_latest_indoor_humidity()
            html = """
            <html>
                <body>
                    <h1>Pico environment control</h1>
                    <h2>Live values</h2>
                    <ul>
                        <li>Indoor humidity: {indoor_humidity}%</li>
                    </ul>
                </body>
            </html>
            
            """.format(indoor_humidity = ih)
            await response.send(html)


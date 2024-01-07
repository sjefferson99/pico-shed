from http.webserver import webserver
import config

class Web_App:

    def __init__(self) -> None:
        self.app = webserver()
        self.running = False
        self.create_homepage()
        
    def load_into_loop(self):
        self.app.run(host='0.0.0.0', port=config.web_port, loop_forever=False)
        self.running = True

    def create_homepage(self) -> None:
        @self.app.route('/')
        async def index(request, response):
            await response.start_html()
            await response.send('<html><body><h1>Hello, world!</h1></html>\n')


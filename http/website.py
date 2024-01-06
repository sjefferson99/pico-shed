from lib.webserver import webserver
import config

app = webserver()

@app.route('/')
async def index(request, response):
    await response.start_html()
    await response.send('<html><body><h1>Hello, world!</h1></html>\n')

def run():
    app.run(host='0.0.0.0', port=config.web_port, loop_forever=False)
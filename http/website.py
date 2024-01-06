from webserver import webserver

app = webserver()

@app.route('/')
async def index(request, response):
    await response.start_html()
    await response.send('<html><body><h1>Hello, world! (<a href="/table">table</a>)</h1></html>\n')

def run():
    app.run(host='0.0.0.0', port=8081, loop_forever=False)
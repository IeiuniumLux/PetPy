# Pet Feeder - By: Al Bee - Sun Nov 28 2017

import sensor, image, network, usocket, ure, utime, uos, ubinascii, uhashlib, sys, ujson
from pyb import LED
from pyb import Servo

green_led = LED(2)
blue_led = LED(3)
servo = Servo(3)  # P9
servo.pulse_width(500)

SSID = 'YOUR_SSID'
KEY = 'YOUR_KEY'
LOG_FILE = 'time.log'
AUTH_FILE = '.htpasswd'
DAY_ABBR = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
SHAKES = 2

# Set sensor settings
sensor.reset()
sensor.set_framesize(sensor.QQVGA)  # 160x120 resolution
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.skip_frames()

# Init wlan module and connect to 2.4 GHz wifi
wlan = network.WINC()
wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)


class HTTPServer():

    def __init__(self):
        self.routes = []
        self.session_key = None

    @staticmethod
    def build_route_pattern(route):
        return ure.compile('^{}$'.format(route))

    def route(self, route_str):
        def decorator(f):
            route_pattern = self.build_route_pattern(route_str)
            self.routes.append((route_pattern, f))
            return f

        return decorator

    def get_route_match(self, path):
        for route_pattern, route_function in self.routes:
            m = route_pattern.match(path)
            if m:
                if m.group(0) is not None:
                    return dict([("key", m.group(0))]), route_function
                else:
                    return {}, route_function
        return None

    def run(self, host=None, port=None):
        server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        server.bind([host, port])
        server.listen(1)
        server.settimeout(0)  # Set server socket to non-blocking
        while True:
            try:
                blue_led.off()
                conn, addr = server.accept()
                blue_led.on()
                conn.settimeout(9.0)
                request = conn.recv(1024).decode('utf-8')

                path_info = request.splitlines()[0].split()[1]
                route_match = self.get_route_match(path_info)
                if route_match:
                    kwargs, route_function = route_match
                    route_function(**dict(kwargs, conn=conn, request=request))
                else:
                    print('Route "{}" has not been registered'.format(path_info))
                    error(conn, '404 Not Found', 'Error 404: Page not found')

            except OSError as err:
                pass
            except:
                blue_led.off()
                conn.close()
                raise

            conn.close()


app = HTTPServer()


@app.route('/')
@app.route('/login')
def index(key, conn, request):
    try:
        # HTTP headers are split from body by a \r\n\r\n sequence
        (headers, body) = request.split("\r\n\r\n")
        if body:
            data = ujson.loads(str(body))
            p = data["password"]
            v = read_value(AUTH_FILE)
            if (p != v):
                error(conn, '401 Unauthorized', 'Authentication failed.')
                return

        elif not hastoken(conn, headers):
           return

        with open('/static/index.html', 'r') as html:
            conn.send("HTTP/1.1 200 OK\r\n" \
                      "content-type: text/html; charset=utf-8\r\n" \
                      "access-control-allow-origin: http://petpy.net\r\n" \
                      "access-control-allow-methods: GET, POST, OPTIONS\r\n" \
                      "access-control-allow-credentials: true\r\n" \
                      "set-cookie: token="+str(app.session_key)+"; HttpOnly;\r\n" \
                      "vary: accept-encoding\r\n" \
                      "pragma: no-cache\r\n" \
                      "cache-control: no-cache\r\n\r\n")
            lf = utime.localtime(int(read_value(LOG_FILE)))
            ptag = '<p id="lastfeed">Last Feed: %s %d @ %02d:%02d</p>' % (DAY_ABBR[lf[6]], lf[2], lf[3], lf[4])
            response = html.read() % ptag
            conn.send(response.encode('utf-8'))
    except OSError:
        error(conn)


@app.route('/(\d+.)')
def stream(key, conn, request):
    # Send multipart header
    conn.send("HTTP/1.1 200 OK\r\n" \
              "content-type: multipart/x-mixed-replace;boundary=stream\r\n" \
              "vary: Accept-Encoding\r\n" \
              "cache-control: no-cache\r\n\r\n")
    frame = sensor.snapshot()
    cframe = frame.compressed(quality=50)
    conn.send("\r\n--stream\r\n" \
              "content-type: image/jpeg\r\n" \
              "content-length:" + str(cframe.size()) + "\r\n\r\n")
    conn.send(cframe)


@app.route('/feed/(\d+.)')
def feed(key, conn, request):
    (headers, body) = request.split("\r\n\r\n")
    if not hastoken(conn, headers):
       return

    green_led.on()
    counter = 0
    while counter < SHAKES:
        servo.pulse_width(2100)
        utime.sleep_ms(400)
        servo.pulse_width(500)
        counter = counter + 1
    green_led.off()
    save_value(LOG_FILE, str(key[6:]))
    conn.send("HTTP/1.1 200 OK\r\n" \
              "content-type: text/html\r\n" \
              "vary: Accept-Encoding\r\n" \
              "cache-control: no-cache\r\n\r\n")


@app.route('/static/(.+)')
def resource(key, conn, request):
    encoding = 'identity'
    if (key.endswith(".js")):
        mimetype = 'application/javascript; charset=utf-8'
        # encoding = 'gzip'
    elif (key.endswith(".css")):
        mimetype = 'text/css; charset=utf-8'
        encoding = 'gzip'
    elif (key.endswith(".ico")):
        mimetype = 'image/x-icon'
    elif (key.endswith(".svg")):
        mimetype = 'image/svg+xml'
    elif (key.endswith(".png")):
        mimetype = 'image/png'
    else:
        mimetype = 'text/html'

    filesize = get_size(key)

    conn.send("HTTP/1.1 200 OK\r\n" \
              "content-type:" + mimetype + "\r\n" \
              "access-control-allow-origin: http://petpy.net\r\n" \
              "content-length:" + str(filesize) + "\r\n" \
              "content-encoding:" + str(encoding) + "\r\n" \
              "accept-ranges: bytes\r\n" \
              "vary: Accept-Encoding\r\n" \
              "cache-control: max-age=604800\r\n\r\n")

    with open(key, 'rb') as f:
        conn.send(f.read())


def error(conn, code, message):
    conn.send("HTTP/1.1 " + str(code) + "\r\n" \
              "content-type: text/html\r\n" \
              "vary: Accept-Encoding\r\n" \
              "cache-control: no-cache\r\n\r\n")
    html = """<!DOCTYPE html>
        <html><head><meta charset="UTF-8"></meta></head><body>
        <center><h3>%s</h3></center>
        </body></html>"""
    response = html % str(message)
    conn.send(response.encode('utf-8'))

def hastoken(conn, headers):
    headers = parse_headers(headers)
    if not isset(headers, 'cookie'):
        with open('/static/login.html', 'r') as html:
            conn.send("HTTP/1.1 200 OK\r\n" \
                      "content-type: text/html; charset=utf-8\r\n" \
                      "access-control-allow-origin: http://petpy.net\r\n" \
                      "access-control-allow-methods: GET, POST, OPTIONS\r\n" \
                      "vary: Accept-Encoding\r\n" \
                      "cache-control: no-cache\r\n\r\n")
            conn.send(html.read().encode('utf-8'))
            return False

    return True

def parse_headers(request):
    headers = {}
    for line in request.split('\n')[1:]:
        # blank line separates headers from content
        if line == '\r':
            break
        header_line = line.partition(':')
        headers[header_line[0].lower()] = header_line[2].strip()

    return headers


def isset(headers, key):
    value = None
    if key in headers:
        value = headers[key]
    return value

def get_size(filename):
    info = uos.stat(filename)
    return info[6]

def read_value(filename):
    v = str(0)
    try:
        with open(filename) as f:
            v = f.read()
            if not v:
                v = str(0)
    except OSError:
        save_value(filename, v)

    return v

def save_value(filename, value):
    try:
        with open(filename, "w") as f:
            f.write(value)
    except OSError:
        pass

def hash(s):
    hash = uhashlib.sha256(s.encode()).digest()
    encoded = ubinascii.b2a_base64(hash)
    return encoded


if __name__ == '__main__':
    #app.session_key = ubinascii.b2a_base64(uos.urandom(16)).decode("ascii")
    app.session_key = ubinascii.hexlify(uos.urandom(16)).decode("ascii")
    app.run('', 8088)

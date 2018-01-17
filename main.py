# Pet Feeder - By: Al Bee - Sun Nov 28 2017

import gc
import sensor
import network
import usocket
import ure
import utime
import uos
import ubinascii
import uhashlib
from pyb import LED
from pyb import Servo

GREEN_LED = LED(2)
BLUE_LED = LED(3)
servo = Servo(3)  # P9
servo.pulse_width(500)

SSID = 'YOUR_SSID'
KEY = 'YOUR_KEY'
LOG_FILE = 'time.log'
AUTH_FILE = '.htpasswd'
DAY_ABBR = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
STATUS = {200:"200 OK", 404:"404 Not Found", 401:"401 Unauthorized", 501:"501 Server Error"}
TURNS = 1

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
        self.session_key = ubinascii.hexlify(uos.urandom(16)).decode("ascii")
        self.debug = False

    @staticmethod
    def build_route_pattern(route):
        return ure.compile('^{}$'.format(route))

    def route(self, route_str):
        def decorator(func):
            route_pattern = self.build_route_pattern(route_str)
            self.routes.append((route_pattern, func))
            return func

        return decorator

    def get_route_match(self, path):
        for route_pattern, route_function in self.routes:
            m = route_pattern.match(path)
            if m:
                if m.group(0) is not None:
                    return dict([("key", m.group(0))]), route_function
                return {}, route_function
        return None

    def run(self, host='', port=8088, debug=False):
        gc.collect()
        self.debug = debug
        server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        server.bind([host, port])
        server.listen(1)
        server.settimeout(0)  # Set server socket to non-blocking
        while True:
            try:
                BLUE_LED.off()
                conn, addr = server.accept()
                BLUE_LED.on()
                conn.settimeout(9.0)
                request = conn.recv(1024).decode('utf-8')

                path_info = request.splitlines()[0].split()[1]
                route_match = self.get_route_match(path_info)
                if route_match:
                    kwargs, route_function = route_match
                    route_function(**dict(kwargs, conn=conn, request=request))
                else:
                    if debug:
                        print('Route "{}" has not been registered'.format(path_info))
                    error(conn, STATUS[404], 'Error 404: Page not found')

            except OSError:
                pass
            except:
                BLUE_LED.off()
                conn.close()
                raise

            conn.close()


app = HTTPServer()


@app.route('/')
@app.route('/login')
def index(key, conn, request):
    try:
        if app.debug:
            print(request)

        # headers are split from body by a \r\n\r\n sequence
        (headers, body) = request.split("\r\n\r\n")
        if body:
            password = read_value(AUTH_FILE)
            if body != password:
                error(conn, STATUS[401], 'Authentication failed.')
                return

        elif not hastoken(conn, headers):
            return

        with open('/static/index.html', 'rb') as html:
            send_headers(conn, True)
            last_feed = utime.localtime(int(read_value(LOG_FILE)))
            ptag = '<p id="lastfeed">Last Feed: {} {:d} @ {:02d}:{:02d}</p>'.format( \
            DAY_ABBR[last_feed[6]], last_feed[2], last_feed[3], last_feed[4])
            nonce = ubinascii.hexlify(uos.urandom(16)).decode("ascii")
            conn.send(html.read() % ('\'nonce-{}{}'.format(nonce, '\''), ptag, \
            'nonce={}'.format(nonce)))
    except OSError:
        error(conn, STATUS[404], 'Error 404: Page not found')


@app.route('/(\d+.)')
def stream(key, conn, request):
    # Send multipart header
    conn.send("HTTP/1.1 200 OK\r\n" \
              "content-type: multipart/x-mixed-replace;boundary=stream\r\n" \
              "x-frame-options: deny\r\n" \
              "x-xss-protection: 1; mode=block\r\n" \
              "x-content-type-options: nosniff\r\n" \
              "vary: Accept-Encoding\r\n" \
              "cache-control: no-cache\r\n\r\n")
    frame = sensor.snapshot()
    cframe = frame.compressed(quality=50)
    conn.send("\r\n--stream\r\n" \
               "content-type: image/jpeg\r\n" \
               "content-length:{}\r\n\r\n".format(cframe.size()))
    conn.send(cframe)


@app.route('/feed/(\d+.)')
def feed(key, conn, request):
    (headers, body) = request.split("\r\n\r\n")
    if not hastoken(conn, headers):
        return

    GREEN_LED.on()
    counter = 0
    while counter < TURNS:
        servo.pulse_width(2100)
        utime.sleep_ms(400)
        servo.pulse_width(500)
        counter = counter + 1
    GREEN_LED.off()
    save_value(LOG_FILE, str(key[6:]))
    send_headers(conn)


@app.route('/static/(.+)')
def resource(key, conn, request):
    encoding = 'identity'
    if key.endswith(".js"):
        mimetype = 'application/javascript'
        # encoding = 'gzip'
    elif key.endswith(".css"):
        mimetype = 'text/css'
        #encoding = 'gzip'
    elif key.endswith(".ico"):
        mimetype = 'image/x-icon'
    elif key.endswith(".svg"):
        mimetype = 'image/svg+xml'
    elif key.endswith(".png"):
        mimetype = 'image/png'
    else:
        mimetype = 'text/html'

    #filesize = get_size(key)

    send_headers(conn, False, mimetype, encoding, 'max-age=604800')

    with open(key, 'rb') as f:
        conn.send(f.read())


def error(conn, status, message):
    conn.send("HTTP/1.1 {}\r\n" \
              "content-type: text/html\r\n" \
              "vary: Accept-Encoding\r\n" \
              "cache-control: no-cache\r\n\r\n" \
              "<center><h3>{}</h3></center>".format(status, message))


def hastoken(conn, headers):
    headers = parse_headers(headers)
    if not isset(headers, 'cookie'):
        with open('/static/login.html', 'rb') as html:
            send_headers(conn)
            nonce = ubinascii.hexlify(uos.urandom(16)).decode("ascii")
            conn.send(html.read() % ('\'nonce-{}{}'.format(nonce, '\''), \
            'nonce={}'.format(nonce)))
            return False
    return True


def send_headers(conn, cookie=False, mimetype='text/html', encoding='identity', cache='no-cache'):
    conn.send("HTTP/1.1 200 OK\r\n" \
              "content-type: {0}; charset=UTF-8\r\n" \
              "access-control-allow-origin: *\r\n" \
              "access-control-allow-methods: POST, GET, OPTIONS\r\n" \
              "access-control-allow-headers: Origin\r\n" \
              "x-frame-options: deny\r\n" \
              "x-xss-protection: 1; mode=block\r\n" \
              "x-content-type-options: nosniff\r\n" \
              "content-encoding: {1}\r\n" \
              "vary: Origin\r\n" \
              "cache-control: {2}\r\n{3}".format(mimetype, encoding, cache, \
              "set-cookie: token={}; HttpOnly;\r\n\r\n".format(app.session_key) \
              if cookie else "\r\n"))


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
        with open(filename, 'rb') as f:
            v = f.read()
            if not v:
                v = str(0)
    except OSError:
        save_value(filename, v)

    return v.decode('utf-8')


def save_value(filename, value):
    try:
        with open(filename, 'wb') as f:
            f.write(value)
    except OSError as err:
        if app.debug:
            print(err)


def hash_str(string_to_hash):
    hashed = uhashlib.sha256(string_to_hash.encode()).digest()
    encoded = ubinascii.b2a_base64(hashed)
    print(encoded.decode("ascii"))
    return encoded


if __name__ == '__main__':
    app.run(debug=True)

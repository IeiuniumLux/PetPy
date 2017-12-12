# Pet Feeder - By: Al Bee - Sun Nov 28 2017

import sensor, image, network, usocket, ure, utime, uos, ubinascii, uhashlib, sys
from pyb import LED
from pyb import Servo

green_led = LED(2)
blue_led = LED(3)
servo = Servo(3)  # P9
servo.pulse_width(500)

SSID = 'YOUR_2.4GHz_SSID'
KEY = 'YOUR_2.4GHz_KEY'
LOG_FILE = 'log.txt'
AUTH_FILE = 'auth.dat'
DAY_ABBR = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

# Set sensor settings
sensor.reset()
sensor.set_framesize(sensor.QQVGA)  # 160x120 resolution
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.skip_frames()

# Init wlan module and connect to 2.4 GHz wifi
wlan = network.WINC()
wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)

# Create server socket
server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server.bind(['', 8088])
server.listen(1)
server.settimeout(0)  # Set server socket to non-blocking

get_path_info = lambda x: x.split()[1]


class WSGIServer():
    def __init__(self):
        self.routes = []

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
        for route_pattern, view_function in self.routes:
            m = route_pattern.match(path)
            if m:
                if m.group(0) is not None:
                    return dict([("key", m.group(0))]), view_function
                else:
                    return {}, view_function
        return None

    def run(self):
        while True:
            try:
                blue_led.off()
                client, addr = server.accept()
                blue_led.on()
                client.settimeout(9.0)
                request = client.recv(1024).decode('utf-8')
                path_info = get_path_info(request.splitlines()[0])
                route_match = self.get_route_match(path_info)
                if route_match:
                    kwargs, view_function = route_match
                    view_function(**dict(kwargs, client=client))
                else:
                    print('Route "{}" has not been registered'.format(path_info))
                    client.send("HTTP/1.1 404 Not Found\r\n\r\n")
                    response = """<!DOCTYPE html>
                    <html><body>
                    <center><h3>Error 404: File not found</h3><p>PetPy HTTP Server</p></center>
                    </body></html>"""
                    client.send(response.encode('utf-8'))

            except OSError as err:
                pass
            except:
                raise
            client.close()


app = WSGIServer()


@app.route('/')
def index(key, client):
    client.send("HTTP/1.1 200 OK\r\n" \
                "server: PetPy.net\r\n" \
                "content-type: text/html; charset=utf-8\r\n" \
                "vary: Accept-Encoding\r\n" \
                "cache-control: no-cache\r\n\r\n")
    lf = utime.localtime(get_last_feed())
    ptag = '<p id="lastfeed">Last Feed: %s %d @ %02d:%02d</p>' % (DAY_ABBR[lf[6]], lf[2], lf[3], lf[4])
    with open('index.htm', 'r') as html:
        response = html.read() % ptag
        client.send(response.encode('utf-8'))


@app.route('/(\d+.)')
def stream(key, client):
    # Send multipart header
    client.send("HTTP/1.1 200 OK\r\n" \
                "server: PetPy.net\r\n" \
                "content-type: multipart/x-mixed-replace;boundary=stream\r\n" \
                "vary: Accept-Encoding\r\n" \
                "cache-control: no-cache\r\n\r\n")
    frame = sensor.snapshot()
    cframe = frame.compressed(quality=50)
    client.send("\r\n--stream\r\n" \
                "content-type: image/jpeg\r\n" \
                "content-length:" + str(cframe.size()) + "\r\n\r\n")
    client.send(cframe)


@app.route('/feed/(\d+.)')
def feed(key, client):
    green_led.on()
    servo.pulse_width(2100)
    utime.sleep_ms(500)
    servo.pulse_width(500)
    green_led.off()
    set_last_feed(key[6:])
    client.send("HTTP/1.1 200 OK\r\n" \
        "server: PetPy.net\r\n" \
        "content-type: text/html\r\n" \
        "vary: Accept-Encoding\r\n" \
        "cache-control: no-cache\r\n\r\n")


@app.route('/static/(.+)')
def resource(key, client):
    encoding = 'identity'
    if (key.endswith(".js")):
        mimetype = 'application/javascript; charset=utf-8'
        encoding = 'gzip'
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

    filesize = getsize(key)

    client.send("HTTP/1.1 200 OK\r\n" \
                "server: PetPy.net\r\n" \
                "content-type:" + mimetype + "\r\n" \
                "access-control-allow-origin: *\r\n" \
                "content-length:" + str(filesize) + "\r\n" \
                "content-encoding:" + str(encoding) + "\r\n" \
                "accept-ranges: bytes\r\n" \
                "vary: Accept-Encoding\r\n" \
                "cache-control: max-age=604800\r\n\r\n")

    with open(key, 'rb') as f:
        client.send(f.read())

def getsize(filename):
    info = uos.stat(filename)
    return info[6]

def get_last_feed():
    try:
        with open(LOG_FILE) as f:
            v = int(f.read())
    except OSError:
        v = 0
        try:
            with open(LOG_FILE, "w") as f:
                f.write(str(v))
        except OSError:
            pass
    except ValueError:
        v = 0
    return v

def set_last_feed(value):
    try:
        with open(LOG_FILE, "w") as f:
            f.write(str(value))
    except OSError:
        pass

def hash(s):
    hash = uhashlib.sha256(s.encode()).digest()
    encoded = ubinascii.b2a_base64(hash)
    return encoded

if __name__ == '__main__':
    app.run()

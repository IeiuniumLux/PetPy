# Pet Feeder - By: abencomo - Sun Oct 8 2017

import sensor, image, network, usocket, utime, ure, time
from pyb import LED
from pyb import Servo

green_led = LED(2)
blue_led  = LED(3)
servo = Servo(3) # P9
servo.calibration(900,2100,1500)
servo.pulse_width(900)

SSID ='AAGG-W24'     # Network SSID
KEY  ='Wireless4me'  # Network key
SERVER_ADDRESS = (HOST, PORT) = '', 8088
LOG_FILE = 'log.txt'

# Set sensor settings
sensor.reset()
sensor.set_framesize(sensor.QVGA)   # 320x240
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.skip_frames()

# Init wlan module and connect to network
wlan = network.WINC()
wlan.connect(SSID, key=KEY, security=wlan.WPA_PSK)

# Create server socket
server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server.bind([HOST, PORT])
server.listen(4)
server.settimeout(0) # Set server socket to non-blocking

html = """<!DOCTYPE html>
<html><head>
    <title>Pet Feeder</title>
    <link rel="stylesheet" href="http://ieiuniumlux.github.io/PetPy/style.css">
    </head>
    <body>
        <img id="openmv" style="display:block;margin-left:auto;margin-right:auto;" height="220" width="250" src="http://23.127.160.111:8088"/>
        <input type="button" id="feed" value="Feed Me!" onclick="feed(this);">
        %s
        <script src="http://ieiuniumlux.github.io/PetPy/script.js"></script>
</body></html>
"""

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
                    return dict([("epoch", m.group(0))]), view_function
                else:
                    return {}, view_function

        return None

    def run(self):
        while True:
            try:
                blue_led.on()
                client, addr = server.accept()
                blue_led.off()
                client.settimeout(9.0)
                request = client.recv(1024)
                path_info = get_path_info(request.decode('utf-8').splitlines()[0])
                route_match = self.get_route_match(path_info)
                if route_match:
                    kwargs, view_function = route_match
                    view_function(**dict(kwargs, client=client))
                else:
                    print('Route "{}" has not been registered'.format(path_info))

            except OSError as err:
                pass
            except:
                raise

            client.close()

app = WSGIServer()

@app.route('/')
def index(epoch, client):
    client.send("HTTP/1.1 200 OK\r\n" \
            "Server: OpenMV\r\n" \
            "Content-Type: text/html\r\n" \
            "Cache-Control: max-age=0,must-revalidate\r\n" \
            "Pragma: no-cache\r\n\r\n")
    ptag = '<p id="lastfeed">%s</p>' % 'Z'
    response = html % ptag
    client.send(response)

@app.route('/cam/(\d+.)')
def stream(epoch, client):
    # Send multipart header
    client.send("HTTP/1.1 200 OK\r\n" \
            "Server: OpenMV\r\n" \
            "Content-Type: multipart/x-mixed-replace;boundary=openmv\r\n" \
            "Cache-Control: no-cache\r\n" \
            "Pragma: no-cache\r\n\r\n")
    frame = sensor.snapshot()
    cframe = frame.compressed(quality=50)
    client.send("\r\n--openmv\r\n" \
         "Content-Type: image/jpeg\r\n"\
         "Content-Length:"+str(cframe.size())+"\r\n\r\n")
    client.send(cframe)

@app.route('/feed/(\d+.)')
def feed(epoch, client):
    green_led.on()
    servo.pulse_width(2100)
    time.sleep(300)
    servo.pulse_width(900)
    green_led.off()
    client.send("HTTP/1.1 200 OK\r\n" \
        "Server: OpenMV\r\n" \
        "Content-Type: text/html\r\n" \
        "Cache-Control: max-age=0,must-revalidate\r\n" \
        "Pragma: no-cache\r\n\r\n")

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

if __name__ == '__main__':
   app.run()

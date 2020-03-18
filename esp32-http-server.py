import os
import sys
import board
import busio
from digitalio import DigitalInOut
import neopixel
#from bs4 import BeautifulSoup

from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_wifimanager as wifimanager
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

# This example depends on the 'static' folder in the examples folder
# being copied to the root of the circuitpython filesystem.
# This is where our static assets like html, js, and css live.

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

try:
    import json as json_module
except ImportError:
    import ujson as json_module

print("ESP32 SPI simple web server test!")

# SAM32 board ESP32 Setup
dtr = DigitalInOut(board.DTR)
esp32_cs = DigitalInOut(board.TMS) #GPIO14
esp32_ready = DigitalInOut(board.TCK) #GPIO13
esp32_reset = DigitalInOut(board.RTS)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset, gpio0_pin=dtr, debug=False)
#esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset) # pylint: disable=line-too-long

status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)

## If you want to connect to wifi with secrets:
#wifi = wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
#wifi.connect()

# connect without secrets

#esp.connect_AP(b"Stanford Visitor", b"", timeout_s=20)
# ping google to test
#print("Pinging google.com: %d ms" % esp.ping(dest="www.google.com"))
#skt = esp.get_socket()
#while esp.socket_connected(skt):
#   print("Socket %d not yet connected" % skt)
#   esp.socket_open(skt, "www.example.com", port=80)
#print(esp.socket_status(skt))

#for ap in esp.scan_networks():
#   print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))

## If you want to create a WIFI hotspot to connect to with secrets:
secrets = {"ssid": "Hey Steve", "password": "notyourwifi"}
wifi = wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
wifi.create_ap()

## To you want to create an un-protected WIFI hotspot to connect to with secrets:"
#wifi = wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
#wifi.create_ap()

class SimpleWSGIApplication:
    """
    An example of a simple WSGI Application that supports
    basic route handling and static asset file serving for common file types
    """

    INDEX = "/index.html"
    CHUNK_SIZE = 8912 # max number of bytes to read at once when reading files

    def __init__(self, static_dir=None, debug=False):
        self._debug = debug
        self._listeners = {}
        self._start_response = None
        self._static = static_dir
        if self._static:
            self._static_files = ["/" + file for file in os.listdir(self._static)]

    def __call__(self, environ, start_response):
        """
        Called whenever the server gets a request.
        The environ dict has details about the request per wsgi specification.
        Call start_response with the response status string and headers as a list of tuples.
        Return a single item list with the item being your response data string.
        """
        if self._debug:
            self._log_environ(environ)

        self._start_response = start_response
        status = ""
        headers = []
        resp_data = []

        key = self._get_listener_key(environ["REQUEST_METHOD"].lower(), environ["PATH_INFO"])
        if key in self._listeners:
            status, headers, resp_data = self._listeners[key](environ)
        if environ["REQUEST_METHOD"].lower() == "get" and self._static:
            path = environ["PATH_INFO"]
            if path in self._static_files:
                status, headers, resp_data = self.serve_file(path, directory=self._static)
            elif path == "/" and self.INDEX in self._static_files:
                status, headers, resp_data = self.serve_file(self.INDEX, directory=self._static)

        self._start_response(status, headers)
        return resp_data

    def on(self, method, path, request_handler):
        """
        Register a Request Handler for a particular HTTP method and path.
        request_handler will be called whenever a matching HTTP request is received.

        request_handler should accept the following args:
            (Dict environ)
        request_handler should return a tuple in the shape of:
            (status, header_list, data_iterable)

        :param str method: the method of the HTTP request
        :param str path: the path of the HTTP request
        :param func request_handler: the function to call
        """
        self._listeners[self._get_listener_key(method, path)] = request_handler

    def serve_file(self, file_path, directory=None):
        status = "200 OK"
        headers = [("Content-Type", self._get_content_type(file_path))]

        full_path = file_path if not directory else directory + file_path
        def resp_iter():
            with open(full_path, 'rb') as file:
                while True:
                    chunk = file.read(self.CHUNK_SIZE)
                    if chunk:
                        yield chunk
                    else:
                        break

        return (status, headers, resp_iter())

    def _log_environ(self, environ): # pylint: disable=no-self-use
        print("environ map:")
        for name, value in environ.items():
            print(name, value)

    def _get_listener_key(self, method, path): # pylint: disable=no-self-use
        return "{0}|{1}".format(method.lower(), path)

    def _get_content_type(self, file): # pylint: disable=no-self-use
        ext = file.split('.')[-1]
        if ext in ("html", "htm"):
            return "text/html"
        if ext == "js":
            return "application/javascript"
        if ext == "css":
            return "text/css"
        if ext in ("jpg", "jpeg"):
            return "image/jpeg"
        if ext == "png":
            return "image/png"
        return "text/plain"

# Our HTTP Request handlers
def led_on(environ): # pylint: disable=unused-argument
    print("led on!")
    status_light.fill((0, 0, 100))
    return web_app.serve_file("static/index.html")

def led_off(environ): # pylint: disable=unused-argument
    print("led off!")
    status_light.fill(0)
    return web_app.serve_file("static/index.html")

def led_color(environ): # pylint: disable=unused-argument
    json = json_module.loads(environ["wsgi.input"].getvalue())
    print(json)
    rgb_tuple = (json.get("r"), json.get("g"), json.get("b"))
    status_light.fill(rgb_tuple)
    return ("200 OK", [], [])

# Here we create our application, setting the static directory location
# and registering the above request_handlers for specific HTTP requests
# we want to listen and respond to.
static = "/static"
try:
    static_files = os.listdir(static)
    if "index.html" not in static_files:
        raise RuntimeError("""
            This example depends on an index.html, but it isn't present.
            Please add it to the {0} directory""".format(static))
except (OSError) as e:
    raise RuntimeError("""
        This example depends on a static asset directory.
        Please create one named {0} in the root of the device filesystem.""".format(static))

web_app = SimpleWSGIApplication(static_dir=static)
web_app.on("GET", "/led_on", led_on)
web_app.on("GET", "/led_off", led_off)
web_app.on("POST", "/ajax/ledcolor", led_color)

# Here we setup our server, passing in our web_app as the application
server.set_interface(esp)
wsgiServer = server.WSGIServer(80, application=web_app)

print("open this IP in your browser: ", esp.pretty_ip(esp.ip_address))

# from s3ni0r on https://stackoverflow.com/questions/11329917/restart-python-script-from-within-itself
#import psutil
#import logging
import sys
def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """

    # try:
    #     #p = psutil.Process(os.getpid())
    #     for handler in p.get_open_files() + p.connections():
    #         os.close(handler.fd)
    # except Exception as e:
    #     logging.error(e)
    os.execl(sys.executable, sys.executable, * sys.argv)

# Start the server
wsgiServer.start()
while True:
    # Our main loop where we have the server poll for incoming requests
    try:
        wsgiServer.update_poll()
        # Could do any other background tasks here, like reading sensors
    except (ValueError, RuntimeError) as e:
        #print("Failed to update server, restarting ESP32\n", e)
        #wifi.reset()
        #continue
        print("Failed to update sever, restarting server script")
        restart_program()

import os
import sys
import board
import busio
from digitalio import DigitalInOut
import neopixel
import time

from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_wifimanager as wifimanager
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

from simpleWSGIApplication import SimpleWSGIApplication as webAppClass

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

#for ap in esp.scan_networks():
#   print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))

## If you want to create a WIFI hotspot to connect to with secrets:
secrets = {"ssid": "Hey Steve", "password": "notyourwifi"}
wifi = wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
wifi.create_ap()

## To you want to create an un-protected WIFI hotspot to connect to with secrets:"
#wifi = wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
#wifi.create_ap()

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

def relay(environ):
    json = json_module.loads(environ['wsgi.input'].getvalue())
    print("From relay function: ", json)
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

# Access the simpleWSGIApplication class
web_app = webAppClass(static_dir=static)
web_app.on("GET", "/led_on", led_on)
web_app.on("GET", "/led_off", led_off)
web_app.on("POST", "/ajax/ledcolor", led_color)
web_app.on("POST", "/relay", relay)

# Here we setup our server, passing in our web_app as the application
server.set_interface(esp)
wsgiServer = server.WSGIServer(80, application=web_app)

print("open this IP in your browser: ", esp.pretty_ip(esp.ip_address))

def restart_server():
    print("Failed to update server, restarting ESP32\n", e)
    wifi.reset()
    wifi = wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)
    wifi.create_ap()
    wsgiServer.start()

# Start the server
wsgiServer.start()
while True:
    # Our main loop where we have the server poll for incoming requests
    try:
        wsgiServer.update_poll()
        # Could do any other background tasks here, like reading sensors
    except (ValueError, RuntimeError) as e:
        restart_server()
        continue

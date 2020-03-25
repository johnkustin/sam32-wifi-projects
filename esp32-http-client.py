import os
import board
import busio
import digitalio
import analogio
from digitalio import DigitalInOut
import neopixel
import time
import pulseio
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_wifimanager as wifimanager
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_requests as requests


# SAM32 board ESP32 Setup
dtr = DigitalInOut(board.DTR)
esp32_cs = DigitalInOut(board.TMS) #GPIO14
esp32_ready = DigitalInOut(board.TCK) #GPIO13
esp32_reset = DigitalInOut(board.RTS)
print("Assigned ESP32 Pins")


pwmPin = pulseio.PWMOut(board.D31, frequency = 5000)
analogReadPin = analogio.AnalogIn(board.A9)
led = DigitalInOut(board.D59)
led.direction = digitalio.Direction.OUTPUT
led.value = False

print("Assigned SPI Module")
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

print("Assigned ESP SPI control")
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset, gpio0_pin=dtr, debug=False)

status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)

print("ESP--Socket Interface Set")
socket.set_interface(esp)
secrets = {"ssid": "Hey Steve", "password": "notyourwifi"}
wificonnection = wifimanager.ESPSPI_WiFiManager(esp, secrets)

wificonnection.connect()

sam32webserverip = "http://192.168.4.1"
sam32websererport = ":80"

rgbArr = [(255,0,0), (0,255,0), (0,0,255)]
duty_cycle_counter = 0

for i in range (0,3):
	try: resp = wificonnection.get(sam32webserverip + sam32websererport)
	except: 
		print("Failed on GET. continuing...")
		wificonnection.reset()
		continue
	print(resp.text)
	resp.close()
while True:
	try: resp = wificonnection.get(sam32webserverip + "/jsonData.json")
	except: 
		print("Failed on GET. continuing...")
		wificonnection.reset()
		continue
	try: jsonData = resp.json()
	except ValueError as e:
		print("Failed downloading JSON Data", e)

		wificonnection.reset()
		continue	
	print("JSON Data:", jsonData)

	resp.close()
	led.value = True
	time.sleep(2)
	led.value = False
	analogvalue = analogReadPin.value
	print("ADC value at pin A9: ", analogvalue) # 16 bit resolution
	print("Voltage at pin A9: ", analogvalue * 3.3 / (2**16))
	try: 
		duty_cycle_pair = jsonData['duty-cycle']
		pwmPin.duty_cycle = duty_cycle_pair[duty_cycle_counter % len(duty_cycle_pair)]
		duty_cycle_counter = duty_cycle_counter + 1
		#postResp = wificonnection.post(sam32webserverip + "/ajax/ledcolor",
		postResp = wificonnection.post(sam32webserverip + "/relay",
			json = {"r": rgbArr[duty_cycle_counter % len(rgbArr)][0], 
			"g": rgbArr[duty_cycle_counter % len(rgbArr)][1],
			"b":rgbArr[duty_cycle_counter % len(rgbArr)][2] })
		
		postResp.close()
	except (ValueError, RuntimeError) as e:
	    print("Failed to get data, retrying\n", e)
        wificonnection.reset()
        continue
	time.sleep(1)

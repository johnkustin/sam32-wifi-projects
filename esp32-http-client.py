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
print("Assigned ESP32 Pins")
# SAM32 board ESP32 Setup
dtr = DigitalInOut(board.DTR)
esp32_cs = DigitalInOut(board.TMS) #GPIO14
esp32_ready = DigitalInOut(board.TCK) #GPIO13
esp32_reset = DigitalInOut(board.RTS)

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

(r, g, b) = (1,1,1)
duty_cycle_counter = 0
#esp.set_pin_mode(5,1)#=output
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
	ledStatus = jsonData['led']
	motorStatus = jsonData['motor']
	colorStatus = jsonData['color']
	motorStatus = jsonData['speed']
	digitalWriteValue = jsonData['duty-cycle']
	print("Led Status:", ledStatus)
	print("Motor Status:", motorStatus)	
	print("Color Value:", colorStatus)
	print("Motor Speed:", ledStatus)
	led.value = True
	time.sleep(2)
	led.value = False
	print("Analog value read at pin:", analogReadPin.value) # 16 bit resolution
	print("Voltage at pin: ", analogReadPin.value * 3.3 / (2**16))
	print("PWM duty cycle", jsonData['duty-cycle'])
	try: 
		duty_cycle_pair = jsonData['duty-cycle']
		pwmPin.duty_cycle = duty_cycle_pair[duty_cycle_counter % len(duty_cycle_pair)]
		duty_cycle_counter = duty_cycle_counter + 1
		#postResp = wificonnection.post(sam32webserverip + "/ajax/ledcolor",
		postResp = wificonnection.post(sam32webserverip + "/relay",
			json = {"r": r % 255, "g": g % 255, "b": b % 255})
		r = (r + 10) * 2
		g = g + 10 * 3
		b = b + 10
		postResp.close()
	except (ValueError, RuntimeError) as e:
	    print("Failed to get data, retrying\n", e)
        wificonnection.reset()
        continue
	time.sleep(1)

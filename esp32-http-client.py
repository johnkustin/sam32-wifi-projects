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

pwmPin = pulseio.PWMOut(board.D31)
analogReadPin = analogio.AnalogIn(board.A9)
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

#esp.set_pin_mode(5,1)#=output
for i in range (0,3):
	try: resp = wificonnection.get(sam32webserverip + sam32websererport)
	except: 
		print("Failed on GET. Continuing...")
		time.sleep(1)
		continue
	print(resp.text)
while True:
	print("JSON Data:")
	try: resp = wificonnection.get(sam32webserverip + "/jsonData.json")
	except: 
		print("Failed on GET. Continuing...")
		time.sleep(1)
		continue
	try: jsonData = resp.json()
	except ValueError as e:
		print("Failed downloading JSON Data", e)
		continue	
	print(jsonData)
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
	#esp.set_digital_write(5, digitalWriteValue)
	print("Analog value read at pin:", analogReadPin.value) # 16 bit resolution
	print("Voltage at pin: ", analogReadPin.value * (((2**16 - 1) / analogReadPin.reference_voltage)**-1))
	print("PWM duty cycle", jsonData['duty-cycle'])
	pwmPin.duty_cycle = jsonData['duty-cycle']
	time.sleep(5)

import os, board, busio, digitalio, analogio
import neopixel, time, pulseio, io
from digitalio import DigitalInOut
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_esp32spi.adafruit_esp32spi_wifimanager as wifimanager
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server
import adafruit_esp32spi.adafruit_esp32spi_socket as socket


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

def pulseLED(led):
	led.value = True
	time.sleep(2)
	led.value = False
def readAnalogPin(pin):
	analogvalue = analogReadPin.value
	print("ADC value: ", analogvalue) # 16 bit resolution
	print("Voltage: ", analogvalue * 3.3 / (2**16))
def writePWMDutyCycle(pin, val):
	pin.duty_cycle = val

print("Testing connection\n\n")
for i in range (0,3):
	try: resp = wificonnection.get(sam32webserverip + sam32websererport)
	except: 
		print("Failed on GET. continuing...")
		wificonnection.reset()
		continue
	print(resp.text)
	resp.close()
while True: ## main client loop
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
	pulseLED(led)	
	readAnalogPin(analogReadPin)
	try: 
		duty_cycle_pair = jsonData['duty-cycle']
		duty_cycle_val = duty_cycle_pair[duty_cycle_counter % len(duty_cycle_pair)]
		writePWMDutyCycle(pwmPin, duty_cycle_val)
		duty_cycle_counter = duty_cycle_counter + 1
		#postResp = wificonnection.post(sam32webserverip + "/ajax/ledcolor",
		postResp = wificonnection.post(sam32webserverip + "/relay",
			json = {"r": rgbArr[duty_cycle_counter % len(rgbArr)][0], 
			"g": rgbArr[duty_cycle_counter % len(rgbArr)][1],
			"b":rgbArr[duty_cycle_counter % len(rgbArr)][2] })
		
		postResp.close()
		echoRequest = wificonnection.get(sam32webserverip + "/echoRequest")
		print(echoRequest.text)
		print(str(echoRequest.content, 'utf-8'))
		echoRequest.close()
	except (ValueError, RuntimeError) as e:
	    print("Failed to get data, retrying\n", e)
        wificonnection.reset()
        continue

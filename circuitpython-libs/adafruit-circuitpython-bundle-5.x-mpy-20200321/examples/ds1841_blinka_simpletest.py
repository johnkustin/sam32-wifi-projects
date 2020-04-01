from time import sleep
import board
import busio
import adafruit_ds3502

i2c = busio.I2C(board.SCL, board.SDA)
ds3502 = adafruit_ds3502.DS3502(i2c)

# WIRING:
# 1 Wire connecting  VCC to RH to make a voltage divider using the
#   internal resistor between RH and RW

# As this code runs, measure the voltage between ground and the RW (wiper) pin
# with a multimeter. You should see the voltage change with each print statement.
while True:
    ds3502.wiper = 127
    print("Wiper value set to 127")
    sleep(5.0)

    ds3502.wiper = 0
    print("Wiper value set to 0")
    sleep(5.0)

    ds3502.wiper = 63
    print("Wiper value set to 63")
    sleep(5.0)

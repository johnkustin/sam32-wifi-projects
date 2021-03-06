import board
import digitalio
import adafruit_sdcard
import storage
from adafruit_pyoa import PYOA_Graphics

try:
    sdcard = adafruit_sdcard.SDCard(board.SPI(), digitalio.DigitalInOut(board.SD_CS))
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    print("SD card found")  # no biggie
except OSError:
    print("No SD card found")  # no biggie

gfx = PYOA_Graphics()

gfx.load_game("/cyoa")
current_card = 0  # start with first card

while True:
    print("Current card:", current_card)
    current_card = gfx.display_card(current_card)

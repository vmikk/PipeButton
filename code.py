
import time
import board
import neopixel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# Built-in NeoPixel setup
n = 1  # Number of NeoPixels
pin = board.GP16  # Pin where NeoPixel is connected
np = neopixel.NeoPixel(pin, n)


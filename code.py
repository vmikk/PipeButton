
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

# HID keyboard setup
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

# Load the config
def read_config():
    """
    Reads the configuration from 'pipebutton.config' file.
    Returns a dictionary with configuration key-value pairs.
    """
    config = {}
    try:
        with open('pipebutton.config', 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip()] = value.strip()
    except OSError as e:
        print(f"Error reading config file: {e}")
    return config


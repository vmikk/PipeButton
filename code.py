
import time
import board
import neopixel
import random
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

## Initialize digital inputs for the 3-positional slide switch
switch_mode1 = digitalio.DigitalInOut(board.GP9)
switch_mode1.direction = digitalio.Direction.INPUT
switch_mode1.pull = digitalio.Pull.UP

switch_mode2 = digitalio.DigitalInOut(board.GP10)
switch_mode2.direction = digitalio.Direction.INPUT
switch_mode2.pull = digitalio.Pull.UP

switch_mode3 = digitalio.DigitalInOut(board.GP12)
switch_mode3.direction = digitalio.Direction.INPUT
switch_mode3.pull = digitalio.Pull.UP

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

def execute_script():
    """
    Executes a script based on the configuration read from 'pipebutton.config' file.
    """
    config = read_config()
    script_path = config.get('script_path')

    if script_path:
        # Press Win + R to open the Run dialog
        keyboard.press(Keycode.WINDOWS, Keycode.R)
        keyboard.release_all()
        time.sleep(1)

        # Type the command to run PowerShell script
        keyboard_layout.write(f'{script_path}\n')
    else:
        print("Script path not found in config file")

def send_keystroke(key_names):
    """
    Sends a keystroke by pressing and releasing the specified keys.
    """
    config = read_config()
    key_names = config.get('shortcut_keys')
    keycodes = [eval(key_name) for key_name in key_names]
    
    if keycodes:
        keyboard.press(*keycodes)
        keyboard.release_all()

def type_file_content():
    """
    Randomly selects a text file from the 'texts' directory and types its content.
    Mimics natural typing speed and random mistakes.
    """
    config = read_config()
    textdir = config.get('texts_dir')
    try:
        # Text files should be in the directory named 'texts'
        files = os.listdir(textdir)
        if not files:
            print("No text files found.")
            return
        
        file_path = textdir + '/' + random.choice(files)
        if verbose:
            print(f"Selected file: {file_path}")
        with open(file_path, 'r') as file:
            content = file.read()
            i = 0
            while i < len(content):
                char = content[i]
                keyboard_layout.write(char)  # Type the character
                i += 1
                
                # Random delay to mimic natural typing
                time.sleep(random.uniform(0.0001, 0.01))
                
                # Randomly simulate a typing mistake
                if random.randint(1, 100) > 98:  # About 2% chance of a mistake
                    # Simulate typing one wrong character then backspacing
                    keyboard_layout.write(random.choice('abcdefghijklmnopqrstuvwxyz'))
                    time.sleep(random.uniform(0.05, 0.3))
                    keyboard_layout.write('\b')  # Backspace character
                    time.sleep(random.uniform(0.05, 0.3))
    except OSError as e:
        print(f"Error opening or reading file: {e}")


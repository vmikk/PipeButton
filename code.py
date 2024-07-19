
import time
import digitalio
import board
import os
import neopixel
import random
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

## Verbose flag to control output of status messages
verbose = True
last_verbose_message = None  # Variable to store the last printed message

## Buit-in LED (NeoPixel)
np = neopixel.NeoPixel(board.GP16, 1)

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

## Setup the push button
button = digitalio.DigitalInOut(board.GP28)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP  # Use Pull.UP if the other side of the button is connected to GND

## Setup the button LED
led = digitalio.DigitalInOut(board.GP26)
led.direction = digitalio.Direction.OUTPUT

## HID keyboard setup
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

## Variable to monitor button press time
button_pressed_time = None

## Load the config
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

def is_button_pressed():
    """Check if the button is pressed with debouncing."""
    if not button.value:         # Button is pressed (pull-up means pressed is low/false)
        time.sleep(0.05)         # Debounce delay
        return not button.value  # Return the debounced button state
    return False

def verbose_print(message):
    """
    Prints the message only if it's different from the last printed message.
    """
    global last_verbose_message
    if message != last_verbose_message:
        print(message)
        last_verbose_message = message

def execute_script():
    """
    Executes a script based on the configuration read from 'pipebutton.config' file.
    """
    config = read_config()
    platform = config.get('platform', 'windows')  # Default to 'windows' if not specified
    script_path = config.get('script_path')

    if script_path:
        verbose_print(f"Executing script at: {script_path} on platform: {platform}")
        if platform == "windows":
            keyboard.press(Keycode.GUI, Keycode.R)
            keyboard.release_all()
            time.sleep(1)
            keyboard_layout.write(f'{script_path}\n')
        elif platform in ["linux", "mac"]:
            keyboard.press(Keycode.CONTROL, Keycode.ALT, Keycode.T)
            keyboard.release_all()
            time.sleep(1)
            keyboard_layout.write(f'{script_path}\n')
    else:
        verbose_print("Script path not found in config file")

def send_keystroke():
    """
    Sends a keystroke by pressing and releasing the specified keys from the config.
    """
    config = read_config()
    keys = config.get('shortcut_keys', '').split()
    # Using getattr to fetch the keycode from the Keycode class using the key string
    keycodes = [getattr(Keycode, key) for key in keys if hasattr(Keycode, key)]
    if keycodes:
        keyboard.press(*keycodes)  # Press all the keycodes
        keyboard.release_all()     # Then release them
    else:
        print("No valid keycodes found or provided.")

def type_file_content():
    """
    Randomly selects a text file from the 'texts' directory and types its content.
    Mimics natural typing speed and random mistakes.
    Allows interruption by pressing the button.
    """
    config = read_config()
    textdir = config.get('texts_dir')
    try:
        # Text files should be in the directory named 'texts'
        files = os.listdir(textdir)
        if not files:
            verbose_print("No text files found.")
            return
        
        file_path = textdir + '/' + random.choice(files)
        verbose_print(f"Selected file: {file_path}")
        with open(file_path, 'r') as file:
            content = file.read()
            i = 0
            while i < len(content):

                ## Check if the button is pressed again to interrupt typing
                if is_button_pressed():
                    verbose_print("Typing interrupted by button press.")
                    return
                
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

def main():
    """
    Main function
    """

    led.value = True
    button_was_pressed = False  # State to track button press
    active_mode = None
    active_pins = []

    # Check each switch and add active ones to the list
    if not switch_mode1.value:   # Inverted logic for pull-up
        np[0] = (0, 255, 0)      # Green
        active_pins.append("GP9")
        active_mode = "Mode 1: Typing text files"
    if not switch_mode2.value:   # Inverted logic for pull-up
        np[0] = (0, 0, 255)      # Blue
        active_pins.append("GP11")
        active_mode = "Mode 2: Sending shortcut"
    if not switch_mode3.value:   # Inverted logic for pull-up
        np[0] = (255, 0, 0)      # Red
        active_pins.append("GP13")
        active_mode = "Mode 3: Executing custom script"

    if verbose:
        if active_mode:
            verbose_print(f"{active_mode} active.")
            # verbose_print(f"Active pins: {', '.join(active_pins)}. Setting LED accordingly.")
        else:
            verbose_print("No active pins. LED turned off.")
            np[0] = (0, 0, 0)  # Turn off LED if no switches are active

    current_button_state = is_button_pressed()

    # Check if the button is pressed when a mode is active
    if active_mode and current_button_state and not button_was_pressed:
        led.value = False  # Turn off the LED when button is pressed
        verbose_print(f"Button pressed in {active_mode}.")
        if active_mode.startswith("Mode 1"):
            type_file_content()
        elif active_mode.startswith("Mode 2"):
            send_keystroke()
        elif active_mode.startswith("Mode 3"):
            ## Fetch the platform configuration from the config file
            ## If no platform is specified, it defaults to 'windows'
            execute_script()
        
        ## Pause for a second with the LED off
        time.sleep(0.5)
        led.value = True  # Turn the LED back on after the pause

    ## Update the last known button state
    button_was_pressed = current_button_state  

    ## Small delay for loop stability
    time.sleep(0.1)


## Run the main loop
while True:
    main()


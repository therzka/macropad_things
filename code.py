# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""Keypad and rotary encoder example for Adafruit MacroPad"""

from adafruit_display_text import bitmap_label as label
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_macropad import MacroPad
from rainbowio import colorwheel
import board
import digitalio
import displayio
import keypad
import neopixel
import rotaryio
import terminalio 
import time
import usb_hid

macropad = MacroPad()

pixels = macropad.pixels


kbd = Keyboard(usb_hid.devices)
right = Keycode.RIGHT_ARROW
left = Keycode.LEFT_ARROW
ctrl = Keycode.LEFT_CONTROL
cmd = Keycode.COMMAND
shift = Keycode.LEFT_SHIFT
opt = Keycode.OPTION

KEY_MAP = {
    # toggle zoom video
    9: [cmd, shift, Keycode.V],
    # toggle zoom audio
    10: [cmd, shift, Keycode.A], 
    # toggle meeting controls
    11: [ctrl, opt, cmd, Keycode.H]
}

encoder_last = 0
vol_state = False
video_state = False

while True:
    # Switch desktops via encoder rotation
    encoder_position = macropad.encoder
    if encoder_position > encoder_last:
        print(encoder_position)
        kbd.press(right, ctrl)
        kbd.release_all()
        encoder_last = encoder_position
    if encoder_position < encoder_last:
        print(encoder_position)
        kbd.press(left, ctrl)
        kbd.release_all()
        encoder_last = encoder_position


    # send keyboard events mapped to keypad
    key_event = macropad.keys.events.get()
    if key_event:
        print(key_event)
        
        if key_event.pressed:
            key_num = key_event.key_number
            keys_to_send = KEY_MAP.get(key_num)
            if keys_to_send:
                if key_num == 9:
                    video_state = not video_state
                if key_num == 10:
                    title.text = "you are {}muted".format("not " if vol_state else "")
                    vol_state = not vol_state
                print("sending keys: {}".format(str(keys_to_send)))
                kbd.press(*KEY_MAP[key_num])
                kbd.release_all()
        else:
            pass 

    # action when rotary switch is pressed
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.pressed:
        print("Pressed!")
    if macropad.encoder_switch_debounced.released:
        print("Released!")

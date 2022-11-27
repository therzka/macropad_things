# SPDX-FileCopyrightText: 2022 Tali Herzka
#
# SPDX-License-Identifier: MIT

"""Keypad and rotary encoder example for Adafruit MacroPad"""

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_macropad import MacroPad
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
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (204, 245, 2)

KEY_MAP = {
    # toggle zoom video
    9: ([cmd, shift, Keycode.V], RED),

    # toggle zoom audio
    10: ([cmd, shift, Keycode.A], RED), 
    
    # toggle zoom floating meeting controls
    11: ([ctrl, opt, cmd, Keycode.H], YELLOW)
}
    
# set initial key colors
for k, v in KEY_MAP.items():
    pixels[k] = v[1]
    pixels.brightness = 0.3
    pixels.show()

# WARNING: this will only be your initial state when you start a meeting if your Zoom settings are set to
# "mute my mic when joining a meeting" and "stop my video when joining a meeting"
vol_state = False
video_state = False

text = macropad.display_text(text_scale=2)
text[0].text = "MUTED"
text[1].text = "VIDEO OFF"

# set initial encoder position
encoder_last = 0

# Toggle LED from green to red or vice-versa
def toggle_led(key_num):
    pixels[key_num] = GREEN if pixels[key_num] == RED else RED

while True:
    # Switch desktops via encoder rotation
    encoder_position = macropad.encoder
    if encoder_position > encoder_last:
        kbd.press(right, ctrl)
        kbd.release_all()
        encoder_last = encoder_position
    if encoder_position < encoder_last:
        kbd.press(left, ctrl)
        kbd.release_all()
        encoder_last = encoder_position

    # send keyboard events mapped to keypad
    key_event = macropad.keys.events.get()
    if key_event and key_event.pressed:
        key_num = key_event.key_number
        keys_to_send = KEY_MAP.get(key_num)[0]
        if keys_to_send:
            if key_num == 9:
                video_state = not video_state
                text[1].text = "VIDEO {}".format("ON" if video_state else "OFF")
                toggle_led(key_num) 

            if key_num == 10:
                vol_state = not vol_state
                text[0].text = "{}MUTED".format("NOT " if vol_state else "")
                toggle_led(key_num)
            kbd.press(*KEY_MAP[key_num][0])
            kbd.release_all()

    # TODO: action when rotary switch is pressed
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.pressed:
        print("Pressed!")
    if macropad.encoder_switch_debounced.released:
        print("Released!")

    text.show()
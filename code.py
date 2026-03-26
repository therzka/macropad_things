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
grave = Keycode.GRAVE_ACCENT

RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (204, 245, 2)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
PURPLE = (150, 0, 255)
ORANGE = (255, 80, 0)

# maps the numeric macropad key number to a tuple containing a list of key(s) to send
# and the color to set the key to on the macropad
#
# Layout:
#   [0: CMD PALETTE]  [1: QUICK OPEN]  [2: TOGGLE TERM]   <- VSCode
#   [3: FIND FILES]   [4: FORMAT DOC]  [5: TOGGLE SIDE]   <- VSCode
#   [6: DEV TOOLS]    [7: SPLIT PANE]  [8: CLEAR BUFF]    <- Arc / iTerm2
#   [9: TEAMS AUDIO] [10: TEAMS VIDEO] [11: RAISE HAND]   <- Teams
KEY_MAP = {
    # VSCode
    0: ([cmd, shift, Keycode.P], BLUE),         # Command Palette
    1: ([cmd, Keycode.P], BLUE),                # Quick Open
    2: ([ctrl, grave], BLUE),                   # Toggle Terminal
    3: ([cmd, shift, Keycode.F], BLUE),         # Find in Files
    4: ([shift, opt, Keycode.F], BLUE),         # Format Document
    5: ([cmd, Keycode.B], BLUE),                # Toggle Sidebar

    # Arc Browser / iTerm2
    6: ([cmd, opt, Keycode.I], PURPLE),         # Open DevTools (Arc)
    7: ([cmd, Keycode.D], ORANGE),              # Split Pane Vertically (iTerm2)
    8: ([cmd, Keycode.K], ORANGE),              # Clear Buffer (iTerm2)

    # Teams
    # Zoom equivalents (commented out):
    #   9:  [cmd, shift, Keycode.A]             # Zoom: toggle audio
    #   10: [cmd, shift, Keycode.V]             # Zoom: toggle video
    #   11: [ctrl, opt, cmd, Keycode.H]         # Zoom: floating controls
    9:  ([cmd, shift, Keycode.M], RED),         # Teams: toggle audio
    10: ([cmd, shift, Keycode.O], RED),         # Teams: toggle video
    11: ([cmd, shift, Keycode.K], YELLOW),      # Teams: raise/lower hand
}

# set initial key colors and brightness
pixels.brightness = 0.2
for k, v in KEY_MAP.items():
    pixels[k] = v[1]
    pixels.show()

# WARNING: audio/video state will only be accurate if Teams is configured to
# mute mic and stop video on join, and you don't toggle them via the Teams UI.
vol_state = False
video_state = False

# display_mode: "status" shows Teams mute/video state; "labels" shows key group names
display_mode = "status"

# set initial display text
text = macropad.display_text(text_scale=2)
text[0].text = "MUTED"
text[1].text = "VIDEO OFF"

# set initial encoder position
encoder_last = 0

# Toggle LED from green to red or vice-versa
# uncomment the audio lines to play a sound when toggling
# (you must add the audio files to an audio directory and name the files accordingly)

# ON_AUDIO = "audio/on-tone.mp3"
# OFF_AUDIO = "audio/off-tone.mp3"

def toggle_led_and_sound(key_num):
    if pixels[key_num] not in [RED, GREEN]:
        return
    if pixels[key_num] == GREEN:
        # macropad.play_file(OFF_AUDIO)
        pixels[key_num] = RED
    else:
        # macropad.play_file(ON_AUDIO)
        pixels[key_num] = GREEN

def update_display():
    if display_mode == "labels":
        text[0].text = "VSCODE"
        text[1].text = "ARC/ITERM"
    else:
        text[0].text = "{}MUTED".format("NOT " if vol_state else "")
        text[1].text = "VIDEO {}".format("ON" if video_state else "OFF")

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
    if key_event:
        if key_event.pressed:
            key_num = key_event.key_number
            keys_to_send = KEY_MAP.get(key_num)[0]
            if keys_to_send:
                # track Teams audio toggle state
                if key_num == 9:
                    vol_state = not vol_state

                # track Teams video toggle state
                if key_num == 10:
                    video_state = not video_state

                toggle_led_and_sound(key_num)

                kbd.press(*keys_to_send)
                kbd.release_all()

                update_display()

    # Toggle display mode between key labels and Teams status when encoder is clicked
    macropad.encoder_switch_debounced.update()
    if macropad.encoder_switch_debounced.pressed:
        display_mode = "labels" if display_mode == "status" else "status"
        update_display()

    text.show()

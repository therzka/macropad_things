# SPDX-FileCopyrightText: 2022 Tali Herzka
#
# SPDX-License-Identifier: MIT

"""Keypad and rotary encoder example for Adafruit MacroPad"""

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_macropad import MacroPad
from rpc import RpcClient, RpcError
import usb_hid
import time
import asyncio
from rainbowio import colorwheel
# from adafruit_hid.consumer_control_code import ConsumerControlCode

macropad = MacroPad()
rpc = RpcClient()
hostname = "TEST"
username = ""

right = Keycode.RIGHT_ARROW
left = Keycode.LEFT_ARROW
ctrl = Keycode.LEFT_CONTROL
cmd = Keycode.COMMAND
shift = Keycode.LEFT_SHIFT
opt = Keycode.OPTION
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (204, 245, 2)
WHITE = (255, 255, 255)

# maps the numeric macropad key number to a tuple containing an list of key(s) to send
# and the color to set the key to on the macropad
TEN_KEY_MAP = {
    0: ([Keycode.SEVEN], RED),
    1: ([Keycode.EIGHT], RED),
    2: ([Keycode.NINE], RED),
    3: ([Keycode.FOUR], RED),
    4: ([Keycode.FIVE], RED),
    5: ([Keycode.SIX], RED),
    6: ([Keycode.ONE], RED),
    7: ([Keycode.TWO], RED),
    8: ([Keycode.THREE], RED),
    9: ([Keycode.ZERO], RED),
    10: ([Keycode.BACKSPACE], RED),   
    11: ([Keycode.ENTER], RED)
}
TEST_KEY_MAP = {
    0: ([Keycode.ONE], WHITE),
    1: ([Keycode.TWO], WHITE),
    2: ([Keycode.THREE], WHITE),
    3: ([Keycode.FOUR], WHITE),
    4: ([Keycode.FIVE], WHITE),
    5: ([Keycode.SIX], WHITE),
    6: ([Keycode.SEVEN], WHITE),
    7: ([Keycode.EIGHT], WHITE),
    8: ([Keycode.NINE], WHITE),
    # toggle zoom audio
    9: ([cmd, shift, Keycode.A], RED),

    # toggle zoom video
    10: ([cmd, shift, Keycode.V], RED), 
    
    # toggle zoom floating meeting controls
    11: ([ctrl, opt, cmd, Keycode.H], YELLOW)
}

TEN_KEY = {
    "KEYMAP": TEN_KEY_MAP,
    "NAME": "10-Key",
    "USE_RAINBOW": True
    }
TEST = {
    "KEYMAP": TEST_KEY_MAP,
    "NAME": "Test",
    "USE_RAINBOW": False
    }
HA = {
    "KEYMAP": TEN_KEY_MAP,
    "NAME": "Home Assistant",
    "USE_RAINBOW": False
    }

GLOBAL_STATES = { 0: TEN_KEY, 1: TEST, 2: HA }
pixels = macropad.pixels
text = macropad.display_text(text_scale=1)

def center_text(text, char=21):
    return f"{text : ^{char}}"
def right_text(text, char=21):
    return f"{text : >21}"
def left_text(text, char=21):
    return f"{text : <21}"

def set_global_state(state=0):
    pixels.brightness = 0.2
    for k, v in GLOBAL_STATES[state]["KEYMAP"].items():
        pixels[k] = v[1]
        pixels.show()
    text[2].text = right_text(GLOBAL_STATES[state]["NAME"])

def rainbow_scan(modifier, diff=10):
    for key in range(0,12):
        pixels[key] = colorwheel(modifier+(key*diff))
        pixels.show()

async def rpc_call(function, *args, **kwargs):
    responseTask = asyncio.create_task(rpc.call(function, *args, **kwargs))
    response = (await asyncio.gather(responseTask))[0]
    if response["error"]:
        raise RpcError(response["message"])
    return response["return_val"]

async def blink_led(sleep=0.3):
    while True:
        macropad.red_led = True
        await asyncio.sleep(sleep)
        macropad.red_led = False
        await asyncio.sleep(sleep)


async def connect_and_get_username():
    server_is_running = False
    start_time = time.time()
    LIMIT_ATTEMPTS = False
    ATTEMPTS = 100
    current_attempt = 0
    username = ""
    print("Waiting for HOST")
    while not server_is_running and (current_attempt < ATTEMPTS or not LIMIT_ATTEMPTS):
        try:
            if (LIMIT_ATTEMPTS):
                print("Waiting for HOST")
            await rpc_call("is_running")
            server_is_running = True
            print("Connected")
        except RpcError as e:
            if (LIMIT_ATTEMPTS):
                print(f"Attempt {current_attempt} of {ATTEMPTS}")
                current_attempt += 1
            pass

    if server_is_running:
        try:
            hostname = await rpc_call("get_hostname")
            username = await rpc_call("get_username")
            return hostname, username
        except:
            hostname = "ERROR"
            username = "ERROR"
            return hostname, username
    else:
        hostname = "Disconnected"
        username = "None"
        return hostname, username

async def main():
    hostname = "Disconnected"
    username = "None"
    host_user_task = asyncio.create_task(connect_and_get_username())
    blink_led_task = asyncio.create_task(blink_led())
    hostUserNameFuture = asyncio.gather(host_user_task)

    kbd = Keyboard(usb_hid.devices)
        
    # set initial key colors and brightness
    set_global_state()

    # WARNING: this will only be your initial state when you start a meeting if your Zoom settings are set to
    # "mute my mic when joining a meeting" and "stop my video when joining a meeting" and will only accurately
    # reflect your state if you don't toggle these manually via the zoom UI
    vol_state = False
    video_state = False

    ## set initial display text
    ## At a scale of 1m we just hit the 1 on the 13... so we have about 22 characters.

    text[0].text = center_text(f"{username}@{hostname}")
    text[1].text = right_text("BETA")

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

    hostnameSet = False
    ACTIVE_STATE = 0
    modifier = 1

    while True:
        if (not hostnameSet and host_user_task.done()):
            hostname, username = (await hostUserNameFuture)[0]
            text[0].text = center_text(f"{username}@{hostname}")
            hostnameSet = True
            try:
                blink_led_task.cancel()
            except CancelledError:
                pass
            macropad.red_led = False
        # hostname, username = asyncio.run(connect_and_get_username())
        # Switch desktops via encoder rotation
        encoder_position = macropad.encoder
        if encoder_position > encoder_last:
            macropad.consumer_control.send(
                macropad.ConsumerControlCode.VOLUME_INCREMENT
            )
            # kbd.press(right, ctrl)
            # kbd.release_all()
            encoder_last = encoder_position
        if encoder_position < encoder_last:
            macropad.consumer_control.send(
                macropad.ConsumerControlCode.VOLUME_DECREMENT
            )
            # kbd.press(left, ctrl)
            # kbd.release_all()
            encoder_last = encoder_position

        # send keyboard events mapped to keypad
        key_event = macropad.keys.events.get()
        if key_event:
            if key_event.pressed:
                key_num = key_event.key_number
                keys_to_send = GLOBAL_STATES[ACTIVE_STATE]["KEYMAP"].get(key_num)[0]
                if keys_to_send:
                    # toggle zoom video
                    if key_num == 9:
                        video_state = not video_state
                        # text[1].text = "VIDEO {}".format("ON" if video_state else "OFF")

                    # toggle zoom audio
                    if key_num == 10:
                        vol_state = not vol_state
                        # text[0].text = "{}MUTED".format("NOT " if vol_state else "")
                    
                    toggle_led_and_sound(key_num)

                    keys_to_press = GLOBAL_STATES[ACTIVE_STATE]["KEYMAP"][key_num][0]
                    if keys_to_press:
                        kbd.press(*keys_to_press)
                    kbd.release_all()

        # TODO: action when rotary switch is pressed
        macropad.encoder_switch_debounced.update()
        if macropad.encoder_switch_debounced.pressed:
            print(ACTIVE_STATE)
            if (ACTIVE_STATE + 1 == len(GLOBAL_STATES)):
                ACTIVE_STATE = 0
                set_global_state(0)
            else:
                ACTIVE_STATE += 1
                set_global_state(ACTIVE_STATE)
        # if macropad.encoder_switch_debounced.released:
        #     text[2].text = "Released!"

        text.show()
        if (GLOBAL_STATES[ACTIVE_STATE]["USE_RAINBOW"]):
            rainbow_scan(modifier, diff=20)
        modifier += 1
        await asyncio.sleep(0.01)

asyncio.run(main())
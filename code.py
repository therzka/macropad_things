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

macropad = MacroPad()
rpc = RpcClient()
hostname = "TEST"
username = ""

async def rpc_call(function, *args, **kwargs):
    responseTask = asyncio.create_task(rpc.call(function, *args, **kwargs))
    response = (await asyncio.gather(responseTask))[0]
    print(response)
    if response["error"]:
        raise RpcError(response["message"])
    return response["return_val"]


async def connect_and_get_username():
    server_is_running = False
    start_time = time.time()
    ATTEMPTS = 2
    current_attempt = 0
    username = ""
    while not server_is_running and current_attempt < ATTEMPTS:
        try:
            print("Waiting for HOST")
            await rpc_call("is_running")
            server_is_running = True
            print("Connected")
        except RpcError as e:
            current_attempt += 1
            print(f"Attempt {current_attempt} of {ATTEMPTS}")
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
        hostname = "RPI Macropad"
        username = "A"
        return hostname, username

async def main():
    hostname = "RPI Macropad"
    username = "A"
    host_user_task = asyncio.create_task(connect_and_get_username())
    hostUserNameFuture = asyncio.gather(host_user_task)
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
    WHITE = (255, 255, 255)

    # maps the numeric macropad key number to a tuple containing an list of key(s) to send
    # and the color to set the key to on the macropad
    KEY_MAP = {
        0: ([Keycode.SEVEN], WHITE),
        1: ([Keycode.EIGHT], WHITE),
        2: ([Keycode.NINE], WHITE),
        3: ([Keycode.FOUR], WHITE),
        4: ([Keycode.FIVE], WHITE),
        5: ([Keycode.SIX], WHITE),
        6: ([Keycode.ONE], WHITE),
        7: ([Keycode.TWO], WHITE),
        8: ([Keycode.THREE], WHITE),
        # toggle zoom audio
        9: ([cmd, shift, Keycode.A], RED),

        # toggle zoom video
        10: ([cmd, shift, Keycode.V], RED), 
        
        # toggle zoom floating meeting controls
        11: ([ctrl, opt, cmd, Keycode.H], YELLOW)
    }
        
    # set initial key colors and brightness
    pixels.brightness = 0.2
    for k, v in KEY_MAP.items():
        pixels[k] = v[1]
        pixels.show()

    # WARNING: this will only be your initial state when you start a meeting if your Zoom settings are set to
    # "mute my mic when joining a meeting" and "stop my video when joining a meeting" and will only accurately
    # reflect your state if you don't toggle these manually via the zoom UI
    vol_state = False
    video_state = False

    ## set initial display text
    ## At a scale of 1m we just hit the 1 on the 13... so we have about 22 characters.

    def center_text(text, char=21):
        return f"{text : ^{char}}"
    def right_text(text, char=21):
        return f"{text : >21}"
    def left_text(text, char=21):
        return f"{text : <21}"

    text = macropad.display_text(text_scale=1)
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
    while True:
        if (not hostnameSet and host_user_task.done()):
            hostname, username = (await hostUserNameFuture)[0]
            text[0].text = center_text(f"{username}@{hostname}")
            hostnameSet = True
        # hostname, username = asyncio.run(connect_and_get_username())
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
                    # toggle zoom video
                    if key_num == 9:
                        video_state = not video_state
                        text[1].text = "VIDEO {}".format("ON" if video_state else "OFF")

                    # toggle zoom audio
                    if key_num == 10:
                        vol_state = not vol_state
                        text[0].text = "{}MUTED".format("NOT " if vol_state else "")
                    
                    toggle_led_and_sound(key_num)

                    keys_to_press = KEY_MAP[key_num][0]
                    if keys_to_press:
                        kbd.press(*keys_to_press)
                    kbd.release_all()

        # TODO: action when rotary switch is pressed
        macropad.encoder_switch_debounced.update()
        if macropad.encoder_switch_debounced.pressed:
            text[2].text = "Pressed!"
        if macropad.encoder_switch_debounced.released:
            text[2].text = "Released!"

        text.show()
        await asyncio.sleep(0.01)

asyncio.run(main())
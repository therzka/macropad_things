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


class Runner:
    def __init__(self):
        hostname = "Disconnected"
        username = "None"
        os = "UNKNOWN"
        futures = None
        macropad = MacroPad()
        rpc = RpcClient()
        kbd = Keyboard(usb_hid.devices)
        LIMIT_ATTEMPTS = False
        ATTEMPTS = 100

        # text[0].text = center_text(f"{username}@{hostname}")
        # set initial encoder position
        encoder_last = 0
        _states = {}
        _state = 0 # -1 is a special mode
        text = macropad.display_text(text_scale=1)
        pixels = macropad.pixels
        set_global_state()
    
    @property
    def state(self):
      return self._states[self._state]
    
    @state.setter
    def state(self, index):
      self._state = index
    
    @property
    def globalStates(self):
      return self._states

    @property
    def configState(self):
      return self._states[-1]

    @configState.setter
    def configState(self, stateDictionary):
      self.AddState(stateDictionary)
    
    def AddState(self, stateDictionary):
      if stateDictionary.isConfig:
        self._states[-1] = stateDictionary
      else:
        state_count = len(self._states)
        self._states[state_count+1] = stateDictionary
        self.configState.add_label(stateDictionary.name)

    def center_text(text, char=21):
      return f"{text : ^{char}}"

    def right_text(text, char=21):
      return f"{text : >21}"

    def left_text(text, char=21):
      return f"{text : <21}"

    def update_pixels_with_keymap(self, keymap=None):
      this.pixels.brightness = 0.2 # TODO: put this elsewhere
      if keymap is not None:
        for k, v in keymap.items():
          self.pixels[k] = v[1]
      else:
        for k, v in self.state.keymap.items():
          self.pixels[k] = v[1]
      self.pixels.show()
    
    def update_state_labels_and_name(self, name, rotary_label, name_col=1, rot_col=2, wrap_func=None):
      if wrap_func is None:
        self.text[name_col] = name
        self.text[rot_col] = rotary_label
      else:
        self.text[name_col] = wrap_func(name)
        self.text[rot_col] = wrap_func(rotary_label)

    def set_global_state(self, state=0):
      self.state = state # Update our current state
      self.update_pixels_with_keymap() # Don't need to send anything in
      self.update_state_labels_and_name(name=self.state.name, rotary_label=self.state.rotary_label, wrap_func=self.right_text)

    def rainbow_scan(self, modifier, diff=10):
      for key in range(0, 12):
        self.pixels[key] = colorwheel(modifier+(key*diff))
        self.pixels.show()

    async def rpc_call(self, function, *args, **kwargs):
      responseTask = asyncio.create_task(self.rpc.call(function, *args, **kwargs))
      response = (await asyncio.gather(responseTask))[0]
      if response["error"]:
        raise RpcError(response["message"])
      return response["return_val"]

    async def blink_led(self, sleep=0.3):
      while True:
        self.macropad.red_led = True
        await asyncio.sleep(sleep)
        self.macropad.red_led = False
        await asyncio.sleep(sleep)

    def toggle_led_and_sound(self, key_num):
      if self.pixels[key_num] not in [RED, GREEN]:
        return
      if self.pixels[key_num] == GREEN:
        # macropad.play_file(OFF_AUDIO)
        self.pixels[key_num] = RED
      else:
        # macropad.play_file(ON_AUDIO)
        self.pixels[key_num] = GREEN

    async def connect_and_get_username(self):
      server_is_running = False
      start_time = time.time()
      current_attempt = 0
      username = ""
      print("Waiting for HOST")
      while not server_is_running and (current_attempt < ATTEMPTS or not LIMIT_ATTEMPTS):
        try:
          if (self.LIMIT_ATTEMPTS):
            print("Waiting for HOST")
          await self.rpc_call("is_running")
          server_is_running = True
          print("Connected")
        except RpcError as e:
          if (self.LIMIT_ATTEMPTS):
            print(f"Attempt {current_attempt} of {self.ATTEMPTS}")
            current_attempt += 1
          pass

      if server_is_running:
        try:
          hostname = await self.rpc_call("get_hostname")
          username = await self.rpc_call("get_username")
          os = await self.rpc_call("get_os")
          return hostname, username, os
        except:
          hostname = "ERROR"
          username = "ERROR"
          os = "ERROR"
          return hostname, username, os
      else:
        hostname = "Disconnected"
        username = "None"
        os = "UNKNOWN"
        return hostname, username, os

    def update_mode(self):
      self.macropad.encoder_switch_debounced.update()
      if self.macropad.encoder_switch_debounced.pressed:
        if self._state != -1:
          self.set_global_state(-1) # -1 is a "config" mode
        else:
          self.set_global_state(self.state.get_selected_state()) # if we're in config mode, get the selected highlighted state.

    async def update_os_hostname_username(self):
      if (host_user_task.done()):
        hostname, username, os = (await self.futures)[0]
        self.text[0].text = center_text(f"{username}@{hostname}")
        self.text[3].text = center_text(f":: {os}  ::")
        try:
          blink_led_task.cancel()
        except CancelledError:
          pass
        self.macropad.red_led = False
        return True
      return False

    async def main(self):
      # initial setup stuff.
      host_user_task = asyncio.create_task(self.connect_and_get_username())
      blink_led_task = asyncio.create_task(self.blink_led())
      self.futures = asyncio.gather(host_user_task)
      hostNameSet = False
      modifier += 1
      while true:
        if (not hostNameSet):
          hostNameSet = self.update_os_hostname_username()
        self.update_mode() # check if we clicked.
        self.global_states[self.active_state].loop(self.macropad, self.text)
        if (global_states[self.active_state].use_rainbow):
          this.rainbow_scan(modifier, diff=20)
        modifier += 1
        if modifier == 256:
          modifier = 0
        await asyncio.sleep(global_states[self.active_state].update_frequency)

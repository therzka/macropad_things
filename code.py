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
from states import State, Config
from runner import Runner

runner = Runner()
config = Config()
ten_key = State()
test = State()
off = State()
runner.AddState(config)
runner.AddState(ten_key)
runner.AddState(test)
runner.AddState(off)
asyncio.run(runner.main())
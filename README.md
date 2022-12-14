This repo has code I use to personalize my [Adafruit MacroPad RP2040](https://learn.adafruit.com/adafruit-macropad-rp2040) using [CircuitPython](https://docs.circuitpython.org/en/latest/README.html).

currently it allows for
- switching between Mac OS desktops by turning the encoder (knob) right or left
- toggle Zoom audio
- toggle Zoom video
- toggle Zoom floating meeting controls

(along with some LED and screen fanciness)

## Prerequisite packages to run my code

**Update**: I've included a `lib` directory containing the packages below but have left the instructions

You'll need to download the latest [CircuitPython bundle](https://circuitpython.org/libraries) and drag the appropriate packages from the `lib/` directory in the bundle to the `lib/` directory on your mounted macropad (`CIRCUITPY`). [More info here](https://learn.adafruit.com/adafruit-macropad-rp2040/macropad-circuitpython-library)

specifically, you'll need:
- adafruit_debouncer.mpy
- adafruit_display_text/ 
- adafruit_hid/ 
- adafruit_macropad.mpy 
- adafruit_midi/
- adafruit_simple_text_display.mpy
- adafruit_ticks.mpy
- neopixel.mpy 


## Adafruit/CircuitPython Resources
- https://learn.adafruit.com/circuitpython-essentials
- https://github.com/adafruit/awesome-circuitpython


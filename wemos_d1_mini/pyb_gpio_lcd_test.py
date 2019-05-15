"""Implements a HD44780 character LCD connected via pyboard GPIO pins."""

import machine
from machine import Pin
import time
from pyb_gpio_lcd import GpioLcd
from machine import RTC
import encoderLib

# Wiring used for this example:
#
#  1 - Vss (aka Ground) - Connect to one of the ground pins on you pyboard.
#  2 - VDD - I connected to VIN which is 5 volts when your pyboard is powered via USB
#  3 - VE (Contrast voltage) - I'll discuss this below
#  4 - RS (Register Select) connect to Y12 (as per call to GpioLcd)
#  5 - RW (Read/Write) - connect to ground
#  6 - EN (Enable) connect to Y11 (as per call to GpioLcd)
#  7 - D0 - leave unconnected
#  8 - D1 - leave unconnected
#  9 - D2 - leave unconnected
# 10 - D3 - leave unconnected
# 11 - D4 - connect to Y5 (as per call to GpioLcd)
# 12 - D5 - connect to Y6 (as per call to GpioLcd)
# 13 - D6 - connect to Y7 (as per call to GpioLcd)
# 14 - D7 - connect to Y8 (as per call to GpioLcd)
# 15 - A (BackLight Anode) - Connect to VIN
# 16 - K (Backlight Cathode) - Connect to Ground
#
# On 14-pin LCDs, there is no backlight, so pins 15 & 16 don't exist.
#
# The Contrast line (pin 3) typically connects to the center tap of a
# 10K potentiometer, and the other 2 legs of the 10K potentiometer are
# connected to pins 1 and 2 (Ground and VDD)
#
# The wiring diagram on the following page shows a typical "base" wiring:
# http://www.instructables.com/id/How-to-drive-a-character-LCD-displays-using-DIP-sw/step2/HD44780-pinout/
# Add to that the EN, RS, and D4-D7 lines.

def millis():
    return rtc.datetime()[5]*3600 + rtc.datetime()[6]*1000 + rtc.datetime()[7]

if __name__ == "builtins":
    last = 0

    # Initializes the library with pin CLK on 12 and pin DT on 13
    e = encoderLib.encoder(2, 0)

    rtc = RTC()
    machine.freq(160000000)
    """Test function for verifying basic functionality."""
    print("Running test_main")
    lcd = GpioLcd(rs_pin=Pin(13, Pin.OUT),
                  enable_pin=Pin(15, Pin.OUT),
                  d4_pin=Pin(12, Pin.OUT),
                  d5_pin=Pin(14, Pin.OUT),
                  d6_pin=Pin(16, Pin.OUT),
                  d7_pin=Pin(5, Pin.OUT),
                  num_lines=4, num_columns=20)
    lcd.putstr("It Works!\nSecond Line\nThird Line\nFourth Line")
    time.sleep_ms(3000)
    lcd.clear()
    count = 0
    while True:
        lcd.move_to(0, 0)
        lcd.putstr("%02d : %02d : %02d\n" % (rtc.datetime()[4], rtc.datetime()[5], rtc.datetime()[6]))
        value = e.getValue()  # Get rotary encoder value
        if value != last:  # If there is a new value do
            last = value
        lcd.putstr("%7d" % value)
        time.sleep_ms(100)
        count += 1

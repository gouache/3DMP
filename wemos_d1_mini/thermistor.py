from machine import ADC
from machine import Timer

import math
import time

CelsiusToKelvin = 273.15

Vcc = 3.3
R0 = 100000
T0 = 25
Beta = 4092
R1 = 112000

NumSamples = 20
adc = ADC(0)

tval = 0
Rinf = R0 * math.exp(-Beta / (T0 + CelsiusToKelvin))

def getValue(ttim):
    global tval

    val = 0
    for i in range(0, NumSamples):
        val = val + adc.read()
        time.sleep_ms(1)

    tval = val

def getTemperature():
    if tval == 0:
        return

    average = tval / NumSamples
    v = (Vcc * average)/1024

    if v >= Vcc:
        raise OSError("Thermistor not connected")
    if v <= 0:
        raise OSError("Short circuit")

    r = (v * R1) / (Vcc - v)
    t = (Beta / math.log(r / Rinf)) - CelsiusToKelvin

    return t

tim = Timer(-1)
tim.init(period=1000, mode=Timer.PERIODIC, callback=getValue)

if __name__ == 'builtins':
    try:
        print("-- start thermistor --")
        while True:
            print(getTemperature())
            time.sleep(1)
            pass
    except:
        print("-- Failed to start thermistor --")

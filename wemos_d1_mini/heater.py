from machine import Pin, PWM
import utime
import thermistor
import Pid
import time

######################################################
#
# this is workaround for using L298N as 3.3V PWM
# wemos d1 mini 13 : D7
# wemos d1 mini 15 : D8
# wemos d1 mini 2 : D4
# fixed on: (D7 = HIGH, D8 = LOW)
# fixed off: (D7 = LOW, D8 = LOW)
# duty range : 0 ~ 1023

p13 = Pin(13, Pin.OUT)
p15 = Pin(15, Pin.OUT)
p13.off()  # on
p15.off()  # off

pwm0 = PWM(Pin(2))
pwm0.duty(0)
######################################################

targetT = 195
p = Pid.Pid(targetT, {"P": 22.2, "I": 1.09, "D": 114}, 0)

if __name__ == 'builtins':
    while 1:
        temperature = thermistor.getTemperature()

        if (temperature is None):
            continue

        targetPwm = p.update(temperature)

        print("[fixed : %d] Target: %.1f C | Current: %.1f C | PWM: %s %%"
            %(p.is_fixed(), targetT, temperature, targetPwm*100))

        pwm0.duty(int(targetPwm*1023))
        time.sleep(0.5)

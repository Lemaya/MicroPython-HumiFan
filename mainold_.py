import time
from machine import Pin
from rotary import Rotary


#led: object = Pin(3, Pin.OUT)

# parameter order is Pin19, Pin18, Pin20 ---> dt, clk, sw 
rotary = Rotary(19, 18, 20)

led_pwm = machine.pwm(machine.Pin(3), freq=1000)

def rotary_changed(change):
    global val_pwm
    if change == Rotary.ROT_CW:
        led_pwm += 1
        print(led_pwm)
    elif change == Rotary.ROT_CCW:
        led_pwm -= 1
        print(led_pwm)
    elif change == Rotary.SW_PRESS:
        #print('PRESSED')
        pass
    elif change == Rotary.SW_RELEASE:
        #print('RELEASED')
        pass

try:
    rotary.add_handler(rotary_changed)
except RuntimeError:
    pass

while True:
    time.sleep(0.1)


while True:
    led.high()
    time.sleep(0.5)
  
    


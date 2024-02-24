import machine
import time
from machine import Timer
from machine import Pin

def tachometer (timer_numer=0,pin_number=22, pulses_per_rev_=2):
    
    num_samples = 16

    rpm_timer = Timer(timer_numer)
    pin_number = pin_number

    print("test1")
    rpm_timer.init(mode=Timer.PERIODIC, freq=1000, callback=rising_edge)
    print("test2")






def rising_edge(pin_number):
    edge = Pin(pin_number, Pin.IN)
    edge.IRQ_RISING
    print ("test_edge")

    return



tachometer()
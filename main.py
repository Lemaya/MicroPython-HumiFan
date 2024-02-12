from machine import Pin, PWM
import time, math, gc
from dht import DHT11, InvalidChecksum
from math import log

def dew_point(temp, humidity):
    a = 17.27
    b = 237.7
    alpha = ((a * temp) / (b + temp)) + log(humidity / 100.0)
    return (b * alpha) / (a - alpha)

#PWM Steuerungsgerade a = min, b = max
def duty_pwm (target):
    # Kann angepasst werden Min Humidity
    a_pwm = 40.0
    # Kann angepasst werden Max Humidity
    b_pwm = 80.0
    m = 65356/(b_pwm - a_pwm)
    n = (65356 * a_pwm)/(a_pwm - b_pwm)
    
    if target < a_pwm:
        y = 0
    elif target > b_pwm:
        y = 65356
    else:
        y = (m * target + n)
       
    return y

#Init Feuchtigkeitssensor
DHTPin = Pin(20, Pin.OUT, Pin.PULL_DOWN)

# Initialisiere PWM-Pin
fan_pin = Pin(3)
fan_pwm = PWM(fan_pin, freq=1000, duty_u16=512)
fan_pwm.duty_u16(500)

# Init Statusled
status = Pin(25,Pin.OUT)
status.on()

while True:
    time.sleep(1)
    sensor = DHT11(DHTPin)
    status.toggle()
    
    temp = (sensor.temperature)
    humidity = (sensor.humidity)
    dew_point_temp = dew_point(temp, humidity)
    pwmperc = 100*(fan_pwm.duty_u16()/(65356))
          
    # Zeige alle interessanten Werte an      
    print("Temperature: " + str(temp))
    print("Humidity: " + str(humidity))
    print("DewPoint: " + str(dew_point_temp))
    print("PWMduty: " + str(fan_pwm.duty_u16()))
    print("PWM: " + str(pwmperc)+"%")
    print("Speicherverbrauch:", gc.mem_alloc() / 1024, "KiB")
    
    
    # Regle Lüftergeschwindigkeit basierend auf Feuchtigkeitswert
    
    duty = int(duty_pwm(humidity))
         
    fan_pwm.duty_u16(duty)
    
    # Garbage Collection
    if gc.mem_alloc() > 1000000:
        gc.collect()






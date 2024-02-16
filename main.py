import time, math, gc, dht, machine, network
from machine import Pin, PWM
from math import log
from network_script import do_connect
#from update_time import update_time_ntp #funktioniert noch nicht
import umqtt

def print_stuff():
    # Zeige alle interessanten Werte an      
    print("Local time：%s" %str(time.localtime()))
    print("Counter " + str(counter))
    print("Temperature: " + str(temp))
    print("Humidity: " + str(humidity))
    print("DewPoint: " + str(dew_point_temp))
    print("PWMduty: " + str(fan_pwm.duty_u16()))
    print("PWM: " + str(pwmperc)+"%")
    print("Speicherverbrauch:", gc.mem_alloc() / 1024, "KiB")
    print("StatusLED " + str(status.value()))
    print("Network connection " +str(wlan.isconnected()))
    
    print()
    
    return

def toggle_esp32(PinOUT):
    
    #toggle pinout
    if PinOUT.value() == 1:
        PinOUT.off()
    else:
        PinOUT.on()
    
    
    return


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
       
    return int(y)

#Init Network variablen
wlan = network.WLAN(network.STA_IF)

#Init Feuchtigkeitssensor
sensor = dht.DHT22(machine.Pin(23))

# Initialisiere PWM-Pin
fan_pin = Pin(25)
fan_pwm = PWM(fan_pin, freq=25000, duty_u16=512)
fan_pwm.duty_u16(500)

# Init Statusled
status = Pin(14, Pin.OUT)
status.on()

counter = 0

do_connect()

#update_time_ntp() #(funktioniert noch nicht)

while True:
    time.sleep(1)
    
    toggle_esp32(status)
    
    try: 
        sensor.measure()
        temp = sensor.temperature()
        humidity = sensor.humidity()
                   
        dew_point_temp = dew_point(temp, humidity)
    
    
        # Regle Lüftergeschwindigkeit basierend auf Feuchtigkeitswert
                   
        fan_pwm.duty_u16(duty_pwm(humidity))
    
        #Berechne pwm als Prozentwert
        pwmperc = 100*(fan_pwm.duty_u16()/(65356))
          
    except OSError as e:
            print("DHT Error")
    
    #Print
    print_stuff()
    
    # Garbage Collection
    if gc.mem_alloc() > 1000000:
        gc.collect()
        
    counter = counter + 1






import dht
import gc
import machine
import network
import time
from math import log

from machine import Pin, PWM

from config import *
from network_script import do_connect
from update_time import update_time_ntp, lokalzeit


def print_stuff():
    # Zeige alle interessanten Werte an      
    print("Local time：%s" %str(lokalzeit()))
    print("Counter " + str(counter))
    print("Temperature: " + str(temp) + "°C")
    print("Humidity: " + str(humidity) + "%")
    print("DewPoint: " + str(dew_point_temp) + "°C")
    print("PWM duty: " + str(fan_pwm.duty_u16()))
    print("PWM: " + str(pwm_perc) + "%")
    print("Speicherverbrauch:", gc.mem_alloc() / 1024, "KiB")
    print("StatusLED " + str(status.value()))
    print("Network connection " +str(wlan.isconnected()))
    
    print()
    
    return

def toggle_esp32(pin_out):
    
    #toggle pinout
    if pin_out.value() == 1:
        pin_out.off()
    else:
        pin_out.on()
    
    
    return


def dew_point(dew_temp, dew_humidity):
    a = 17.27
    b = 237.7
    alpha = ((a * dew_temp) / (b + dew_temp)) + log(dew_humidity / 100.0)
    return (b * alpha) / (a - alpha)



def duty_pwm (target):
    # PWM Steuerungsgerade a = min, b = max

    a_pwm = hum_min
    b_pwm = hum_max
    m = 65356/(b_pwm - a_pwm)
    n = (65356 * a_pwm)/(a_pwm - b_pwm)
    
    if target < a_pwm:
        y = 0
    elif target > b_pwm:
        y = 65356
    else:
        y = (m * target + n)
       
    return int(y)

def read_dht (pin,last_t,last_h):
    # Lese DHT 22 Sensor an angegeben Pin aus
    
    sensor_read = dht.DHT22(machine.Pin(pin))

    temp_read = last_t
    humidity_read = last_h
        
    try: 
        sensor_read.measure()
        temp_read = sensor_read.temperature()
        humidity_read = sensor_read.humidity()
        
        # print("Temperature: " + str(pin) + " " + str(temp_read) + "°C")
        # print("Humidity: " + str(pin) + " " + str(humidity_read) + "°C")    
                                   
    except OSError as e:
            print("DHT Error")
            
    
    return temp_read, humidity_read

      

# Hier beginnt die Main Loop

# Init Network variablen
wlan = network.WLAN(network.STA_IF)

# Initialisiere PWM-Pin
fan_pin = Pin(25)
fan_pwm = PWM(fan_pin, freq=25000, duty_u16=512)
fan_pwm.duty_u16(500)

# Init Status Led
status = Pin(14, Pin.OUT)
status.on()

counter = 0
last_temp = 20
last_hum = 60

do_connect()

update_time_ntp()

while True:
    time.sleep(1)
    
    toggle_esp32(status)
      
    try: 
        
        temp, humidity = read_dht(23, last_temp, last_hum)
        last_temp = temp
        last_hum = humidity
                   
        dew_point_temp = dew_point(temp, humidity)

        
        # Regle Lüftergeschwindigkeit basierend auf Feuchtigkeitswert
                   
        fan_pwm.duty_u16(duty_pwm(humidity))
    
        #Berechne pwm als Prozentwert
        pwm_perc = 100 * (fan_pwm.duty_u16() / 65356)
          
    except Exception:
            print("DHT Error")
                        
    if not wlan.isconnected():
        do_connect()
    
    #Print
    print_stuff()
    
    # Garbage Collection
    if gc.mem_alloc() > 1000000:
        gc.collect()
        
    counter = counter + 1






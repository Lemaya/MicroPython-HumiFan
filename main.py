import dht
import gc
import machine
import network
import time
import asyncio
from math import log

from machine import Pin, PWM

from config import *
from network_script import do_connect
from update_time import update_time_ntp, lokalzeit
try:
  import usocket as socket
except:
  import socket

# Init Network variablen
wlan = network.WLAN(network.STA_IF)

# Initialisiere PWM-Pin
fan_pin = Pin(12)
fan_pwm = PWM(fan_pin, freq=25000, duty_u16=512)
fan_pwm.duty_u16(500)

# Init Status Led
status = Pin(STATUS_LED, Pin.OUT)
status.on()


counter = 0
last_temp = 20
last_hum = 60


def print_stuff():
    # Zeige alle interessanten Werte an      
    print("Local time：%s" %str(lokalzeit()))
    print("Counter " + str(counter))
    print("Temperature: " + str(temp) + " °C")
    print("Humidity: " + str(humidity) + " %")
    print("DewPoint: " + str(dew_point_temp) + " °C")
    print("PWM duty: " + str(fan_pwm.duty_u16()))
    print("PWM: " + str(pwm_perc) + "%")
    print("Speicherverbrauch:", gc.mem_alloc() / 1024, " KiB")
    print("StatusLED " + str(status.value()))
    print("Network connection " +str(wlan.isconnected()))
    print('network config:', wlan.ifconfig())
    
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
            print("DHT Error internal")
            
    
    return temp_read, humidity_read
  
def web_page_py():
    
    html = """
      <html>
    <head> 
        <title>ESP Web Server</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head>
  
  <body>
    <h1>ESP Web Server</h1> 
  
  <p>Local time: <strong>""" + str(lokalzeit()) + """</strong>  </p>
  <p>Counter: <strong>""" + str(counter) + """</strong></p>
  <p>Temperature:  <strong>""" + str(temp) + """</strong>  C</p>
  <p>Humidity: <strong>""" + str(humidity) + """</strong> %</p>
  <p>DewPoint: <strong>""" + str(dew_point_temp) + """</strong> C</p>
  <p>PWM duty: <strong>""" + str(fan_pwm.duty_u16()) +  """</strong></p>
  <p>PWM: <strong>""" + str(pwm_perc) + """</strong> %</p>
  <p>Speicherverbrauch:""" + str(gc.mem_alloc() / 1024) + """ KiB"</p>
  <p><a href="/?led=on"><button class="button">reload</button></a>
    </p>
  <p><a href="/?led=off"><button class="button button2">OFF</button></a>
    </p>
    </body>
  </html>"""

    return html
  

async def pwm_function(last_temp, last_hum):
    global state

    #try:
    temp, humidity = read_dht(23, last_temp, last_hum)
    last_temp = temp
    last_hum = humidity
                   
    dew_point_temp = dew_point(temp, humidity)

    # Regle Lüftergeschwindigkeit basierend auf Feuchtigkeitswert
                   
    fan_pwm.duty_u16(duty_pwm(humidity))
    
        #Berechne pwm als Prozentwert
    pwm_perc = 100 * (fan_pwm.duty_u16() / 65356)

        #Print
    print_stuff()
    
        # Garbage Collection
    if gc.mem_alloc() > 1000000:
        gc.collect()
        
    counter = counter + 1

    await asyncio.sleep(1)

    toggle_esp32(status)
          
    #except Exception:
        #print("DHT Error")

    return last_hum, last_hum, fan_pwm, pwm_perc, counter, dew_point

async def live_webserver():
        global state
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        request = str(request)
        print('Content = %s' % request)
        response = web_page_py()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
        await asyncio.sleep(0.5)
        return 

# Hier beginnt die Main Loop


do_connect()

update_time_ntp()

#start listening to html request
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

async def main():

    asyncio.create_task(pwm_function(last_temp, last_hum))
    asyncio.create_task(live_webserver())

    if not wlan.isconnected():
        do_connect()
    return

# Create an Event Loop
loop = asyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    print('Error occured: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')


    



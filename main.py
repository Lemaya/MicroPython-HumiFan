import uasyncio as asyncio
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

#Init Prozess

<<<<<<< Updated upstream
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
=======
# Init Network variablen
wlan = network.WLAN(network.STA_IF)

# Initialisiere PWM-Pin
fan_pin = Pin(PWM_OUTPUT)
fan_pwm = PWM(fan_pin, freq=25000, duty_u16=512)
fan_pwm.duty_u16(500)

# Init Status Led
#status = Pin(STATUS_LED, Pin.OUT)
#status.on()

#Init Sensor
sensor_read = dht.DHT22(dht_pin)
latest_readings = {"temp": None, "humidity": None, "dewPoint" : None}
pwm_perc = None
manual_override = False

counter = 0
last_temp = 20
last_hum = 60

do_connect()

update_time_ntp()

async def print_stuff():
    # Zeige alle interessanten Werte an
    global latest_readings, pwm_perc
    while True:
        try:
            print("Local time：%s" %str(lokalzeit()))
            #print("Counter " + str(counter))
            print("Temperature: " + str(latest_readings['temp']) + " °C")
            print("Humidity: " + str(latest_readings["humidity"]) + " %")
            print("DewPoint: " + str(latest_readings["dewPoint"]) + " °C")
            print("PWM duty: " + str(fan_pwm.duty_u16()))
            print("PWM: " + str(pwm_perc) + "%")
            print("Speicherverbrauch:", gc.mem_alloc() / 1024, " KiB") # type: ignore
            #print("StatusLED " + str(status.value()))
            print("Network connection " +str(wlan.isconnected()))
        
            print()
        
        except OSError as e:
            print ("Printing error:", e)
            
        await asyncio.sleep(1)
>>>>>>> Stashed changes
    
    

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


async def read_dht ():
    # Lese DHT 22 Sensor an angegeben Pin aus
    
<<<<<<< Updated upstream
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
=======
    global latest_readings, pwm_perc, manual_override
    
    while True:
            
        try: 
            sensor_read.measure()
            latest_readings['temp'] = sensor_read.temperature()
            latest_readings['humidity'] = sensor_read.humidity()
            
            # print("Temperature: " + str(pin) + " " + str(temp_read) + "°C")
            # print("Humidity: " + str(pin) + " " + str(humidity_read) + "°C")
            
            latest_readings["dewPoint"] = dew_point(latest_readings['temp'], latest_readings['humidity'])

            
            # Regle Lüftergeschwindigkeit basierend auf Feuchtigkeitswert
            if not manual_override:
                fan_pwm.duty_u16(duty_pwm(latest_readings['humidity']))
        
            #Berechne pwm als Prozentwert
            pwm_perc = 100 * (fan_pwm.duty_u16() / 65356)
            #print(pwm_perc)
                                       
        except OSError as e:
                print("DHT Error")
                
        await asyncio.sleep(1)
        
            
# Async function to handle HTTP requests
async def serve_client(reader, writer):
    global manual_override, pwm_perc
    
    request_line = await reader.readline()
    request = str(request_line)
    print("Request:", request)

    # Read and discard headers
    while await reader.readline() != b"\r\n":
        pass

    if "GET /set_pwm" in request:
        try:
            # Extract value from query
            import ure
            match = ure.search(r"value=(\d+)", request)
            if match:
                value = int(match.group(1))
                value = max(0, min(100, value))  # Clamp between 0 and 100
                pwm_val = int((value / 100) * 65356)
                fan_pwm.duty_u16(pwm_val)
                pwm_perc = value  # Optional: reflect manual value
                response = "HTTP/1.0 200 OK\r\n\r\nPWM set to {}%".format(value)
                manual_override = True
            else:
                response = "HTTP/1.0 400 Bad Request\r\n\r\nInvalid value"
        except Exception as e:
            response = "HTTP/1.0 500 Internal Server Error\r\n\r\nError: {}".format(e)
    
    elif "GET /reset_pwm" in request:
        manual_override = False
        response = "HTTP/1.0 200 OK\r\n\r\nManual override reset"
    
    
    elif "GET /data" in request:
        
        lt = lokalzeit()  # Assuming this returns a tuple like (year, month, day, hour, minute, second, wday, yday)
        time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        lt[0], lt[1], lt[2], lt[3], lt[4], lt[5]
        )

        # Return JSON
        response = (
            "HTTP/1.0 200 OK\r\n"
            "Content-Type: application/json\r\n\r\n"
            '{{"time": "{}","temperature": {:.2f}, "humidity": {:.2f}, "dewPoint": {:.2f},"pwm_perc": {:.2f},"ram_load": {:.2f},"manual_override": {}}}\r\n'.format(
                time_str,
                latest_readings["temp"] or 0.0,
                latest_readings["humidity"] or 0.0,
                latest_readings["dewPoint"] or 0.0,
                pwm_perc,
                gc.mem_alloc() / 1024,
                "true" if manual_override else "false"
            )
        )
    else:
        # Return HTML page with JavaScript
        response = """\
HTTP/1.0 200 OK
Content-Type: text/html

<!DOCTYPE html>
  <html>
    <head> 
        <meta charset="UTF-8">
>>>>>>> Stashed changes
        <title>ESP Web Server</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head>
<<<<<<< Updated upstream
  
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
=======
<body>
  <h1>ESP Web Server - DHT22 Sensor Readings</h1>
  <p>Local time: <strong><span id="time">--</span></strong></p>
  <p>Temperature: <strong><span id="temp">--</span> °C</strong></p>
  <p>Humidity: <strong><span id="hum">--</span> %</strong></p>
  <p>DewPoint: <strong> <span id="dew">--</span> °C</strong></p>
  <p>PWM: <strong> <span id="pwm">--</span> %</strong></p>
  <p>Speicherverbrauch: <strong> <span id="ram">--</span>  KiB</strong></p>
  <p>
  Set Fan PWM (%):
  <input type="number" id="pwmInput" min="0" max="100" value="0">
  <button onclick="setPWM()">Set</button></p>
  
  <p>
  Mode: <strong id="mode" style="color:red">Manual</strong>
  <button onclick="resetPWM()">Switch to Auto</button></p>
  
  <script>
    async function updateData() {
      try {
        const res = await fetch('/data');
        const data = await res.json();
        document.getElementById('time').textContent = data.time;
        document.getElementById('temp').textContent = data.temperature;
        document.getElementById('hum').textContent = data.humidity;
        document.getElementById('dew').textContent = data.dewPoint;
        document.getElementById('pwm').textContent = data.pwm_perc;
        document.getElementById('ram').textContent = data.ram_load
        
        // Update mode
      const modeEl = document.getElementById('mode');
      if (data.manual_override) {
        modeEl.textContent = "Manual";
        modeEl.style.color = "red";
      } else {
        modeEl.textContent = "Auto";
        modeEl.style.color = "green";
      }
    
      } catch (e) {
        console.error('Fetch error:', e);
      }
    }

    setInterval(updateData, 1000); // Update every second
    updateData(); // Initial load
    
    async function setPWM() {
    const val = document.getElementById("pwmInput").value;
    try {
      await fetch(`/set_pwm?value=${val}`);
    } catch (e) {
      console.error('Failed to set PWM:', e);
    }
  }
    async function resetPWM() {
    try {
      await fetch('/reset_pwm');
    } catch (e) {
      console.error('Failed to reset override:', e);
    }
  }
  
  
  </script>
</body>
</html>
"""
    await writer.awrite(response)
    await writer.aclose()


# Start web server
async def start_server():
    print("Web server running...")
    await asyncio.start_server(serve_client, "0.0.0.0", 80)
    
# Garbage Collection
async def garbage():   
    
    while True:
        if gc.mem_alloc() > 1000000: #1 MB
            print("Running garbage collection...")
            print("Before GC: free =", gc.mem_free(), "alloc =", gc.mem_alloc())
            gc.collect()
            print("After GC: free =", gc.mem_free(), "alloc =", gc.mem_alloc())
    
        await asyncio.sleep(10)
    

# Hier beginnt die Main Loop
async def main():
    asyncio.create_task(read_dht())  # Start sensor task
    asyncio.create_task(start_server())
    asyncio.create_task(garbage())
    asyncio.create_task(print_stuff())
    #print("Web server running...")
    while True:
        await asyncio.sleep(1)  # Keep main loop alive
        
# Run
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Server stopped")


>>>>>>> Stashed changes

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


    



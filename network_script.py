import network
import time
from config import *
from umqtt.robust2 import MQTTClient

ssid = SSID
key = KEY


def do_connect(timeout = 30000):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, key)
        t = time.ticks_ms()    
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), t) > timeout:
                wlan.disconnect()
                print("WLAN connection timeout")
            
    print('network config:', wlan.ifconfig())


    
if __name__ == "__main__":
    do_connect()
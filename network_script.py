import network
from config import *

ssid = SSID
key = KEY


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, key)
               
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    
if __name__ == "__main__":
    do_connect()
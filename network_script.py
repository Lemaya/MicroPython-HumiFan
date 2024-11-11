import network
import time
from config import *
from umqtt.robust2 import MQTTClient
try:
  import usocket as socket
except:
  import socket

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
            
    print("Network connection successfull")
    print('network config:', wlan.ifconfig())
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #s.bind(('', 80))
    #s.listen(5)
    return

def web_page_html():
    if network.WLAN(network.STA_IF).isconnected():
        fname = "webpage.html"
        html_file = open(fname, 'r', encoding='utf-8')
        source_code = html_file.read() 
        #print(source_code)


        html = source_code
        return html
    
if __name__ == "__main__":
    do_connect()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        request = str(request)
        print('Content = %s' % request)
        response = web_page_html()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
    
from config import *
import ntptime, network, time, utime, machine
from network_script import do_connect

timezone = TIMEZONE

def update_time_ntp():
    #print("Zeit in sec seit epoch " + str (time.time()))
    wlan = network.WLAN(network.STA_IF)
    print("UTC time before synchronization：%s" %str(time.localtime()))
    if wlan.isconnected():
        ntptime.settime()

        #machine.RTC.datetime(*localzeit)
        print("UTC after synchronization：%s" %str(time.localtime()))
        #print("Zeit in sec seit epoch " + str (time.time()))
    else:
        print ("Zeitupdate nicht möglich, Keine WLAN Verbindung")
        
    return

def lokalzeit(tz = timezone):
    # rechne die Lokale Zeit anhand von geg. UTC aus
    
    add_timetupel = (0, 0, 0, tz, 0, 0, 0, 0)
    
    localzeit = tuple ( map ( sum, zip(time.localtime(), add_timetupel)))
        
    return localzeit

        
if __name__ == "__main__":
    do_connect()
    update_time_ntp()
    
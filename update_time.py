#from mpython import *
import ntptime, network, time


timezone = 1
npt_server = "de.pool.ntp.org"

def update_time_ntp():
    
    wlan = network.WLAN(network.STA_IF)
    print("Local time before synchronization：%s" %str(time.localtime()))
    if wlan.isconnected():
        ntptime.settime(timezone, ntp_server)
        print("Local time after synchronization：%s" %str(time.localtime()))
    else:
        print ("Zeitupdate nicht möglich, Keine WLAN Verbindung")
        
if __name__ == "__main__":
    update_time_ntp()
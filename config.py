from secrets_wifi import *

# Network Variablen aus Secrets
SSID = secret_SSID
KEY = secret_KEY
IPSETTINGS = secret_IPSETTINGS

# Einstellungen zur Steuerungsgerade

# Wert Humidity Wert für 0% PWM
hum_min = 50

# Wert Humidity Wert für 100% PWM
hum_max = 80

TIMEZONE = 1

# Pinout

PWM_OUTPUT = 25

STATUS_LED = 14

# Pin Input

dht_pin = 23
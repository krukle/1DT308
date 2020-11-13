
from network import WLAN
from mqtt import MQTTClient
import machine
import time

def settimeout(duration):
    pass

wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.EXT_ANT)
wlan.connect("LNU-iot", auth=(WLAN.WPA2, "modermodemet"), timeout=5000)

while not wlan.isconnected():
     machine.idle()

print("Connected to Wifi\n")
client = MQTTClient("abda03c2-9f4b-43f9-be51-3dc3e126b80a", "iot-edu-lab.lnu.se",user="king", password="arthur", port=1883)
client.settimeout = settimeout
client.connect()

while True:
     print("Sending ON")
     client.publish("/lights", "ON")
     time.sleep(1)
     print("Sending OFF")
     client.publish("/lights", "OFF")
     time.sleep(1)

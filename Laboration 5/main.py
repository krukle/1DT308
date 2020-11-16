from mqtt import MQTTClient
from network import WLAN
import machine
import time
from machine import Pin
from machine import PWM
from _thread import start_new_thread
from machine import Timer

def mqtt_peds_green():
    """
    Turns green led on for peds and sends information to MQTT-server.
    """
    ledpedgreen.value(1)
    client.publish(topic="cowboys/christoffer/peds", msg="GREEN")

def mqtt_peds_red():
    """
    Turns red led on for peds and sends information to MQTT-server.
    """
    ledpedred.value(1)
    client.publish(topic="cowboys/christoffer/peds", msg="RED")

def mqtt_cars_green():
    """
    Turns green LED on for traffic on and sends information to MQTT-server.
    """
    ledcargreen.value(1)
    client.publish(topic="cowboys/christoffer/cars", msg="GREEN")

def mqtt_cars_red():
    """
    Turns red LED on for traffic on and sends information to MQTT-server
    """
    ledcarred.value(1)
    client.publish(topic="cowboys/christoffer/cars", msg="RED")

def buttonEventCallback(argument):
    """
    When button is pressed, 'ledpedbutton' turns on and traffic
    light loop will begin when 'ledcargreen' has been on for
    atleast four seconds.
    """
    global buttonCanBePressed
    if buttonCanBePressed is True:
        ledpedbutton.value(1)
        buttonCanBePressed = False
        start_new_thread(is_timer_4, tuple('0'))

def is_timer_4(argument):
    """
    Checks if 'ledcargreen' has been on for atleast four
    seconds, if so, start traffic light loop, if not, wait
    until it has, then start traffic light loop.
    """
    if timer.read() > 4:
        start_new_thread(car_soon_stop, tuple('0'))
    else:
        time.sleep(4-timer.read())
        start_new_thread(car_soon_stop, tuple('0'))


def car_go(argument):
    """
    This is the start of the traffic loop.
    Cars can go: 'ledcargreen' is on, 'ledpedred' is on.
    Timer for 'ledcargreen' is reset.
    buttonCanBePressed is set to True.
    """
    global buttonCanBePressed
    #Timer for car_go starts.
    timer.start()
    timer.reset()
    ledcargreen.value(1)
    client.publish(topic="cowboys/christoffer/cars", msg="GREEN")
    ledpedred.value(1)

    client.publish(topic="cowboys/christoffer/peds", msg="RED")
    buttonCanBePressed = True

def car_soon_stop(argument):
    """
    from: car_go
    to: all_stop
    Cars can go for two more seconds: 'ledcaryellow' is on.
    """
    ledcargreen.value(0)
    ledcaryellow.value(1)
    time.sleep(2)
    start_new_thread(all_stop, tuple('0'))

def all_stop(argument):
    """
    from: car_soon_stop
    to: ped_go
    Cars and pedestrians have to stop: 'ledcarred' is on,
    'ledpedred' is on.
    """
    ledcaryellow.value(0)
    ledcarred.value(1)
    client.publish(topic="cowboys/christoffer/cars", msg="RED")
    time.sleep(1)
    start_new_thread(ped_go, tuple('0'))

def ped_go(argument):
    """
    from: all_stop
    to: ped_soon_stop

    Pedestrians can go: 'ledpedgreen' and 'ledcarred' is
    on, buzzer ticks fast.
    """
    ledpedbutton.value(0)
    ledpedred.value(0)
    ledpedgreen.value(1)
    client.publish(topic="cowboys/christoffer/peds", msg="GREEN")
    for i in range(20):#20 times (0.1 + 0.1) = 4 seconds
        ch.duty_cycle(0.5)
        time.sleep(0.1)
        ch.duty_cycle(0)
        time.sleep(0.1)
    start_new_thread(ped_soon_stop, tuple('0'))

def ped_soon_stop(argument):
    """
    from: ped_go
    to: car_get_ready

    Pedestrians can go for 1.8 more seconds: 'ledpedgreen' and
    'ledcarred' is on, buzzer ticks slowly.
    """
    for i in range(3):#3 times (0.3+0.3) = 1.8 seconds
        ch.duty_cycle(0.5)
        time.sleep(0.3)
        ch.duty_cycle(0)
        time.sleep(0.3)
    start_new_thread(car_get_ready, tuple('0'))

def car_get_ready(argument):
    """
    from: ped_soon_stop
    to: car_go

    Noone can go. Cars can go in 1 second: 'ledcarred',
    'ledcaryellow' and 'ledpedred' is on.
    """
    ledcaryellow.value(1)
    ledpedred.value(1)

    client.publish(topic="cowboys/christoffer/peds", msg="RED")
    ledpedgreen.value(0)
    time.sleep(1)
    ledcarred.value(0)
    ledcaryellow.value(0)
    ledpedbutton.value(0)
    start_new_thread(car_go, tuple('0'))

def sub_cb(topic, msg):
    global MSG
    MSG = (msg, topic)

def wifi_connect():
    wlan.connect("LNU-iot", auth=(WLAN.WPA2, "modermodemet"), timeout=5000)

    while not wlan.isconnected():
        machine.idle()
    print("Connected to WiFi\n")


#If button can be pressed;
#buttonCanBePressed is set to True
buttonCanBePressed = True

#Timer for car_go. We want cars to have a green
#light for atleast 4 seconds.
timer = Timer.Chrono()

#Lights for pedestrians
ledpedbutton = Pin('P7', mode=Pin.OUT)
ledpedgreen = Pin('P8', mode=Pin.OUT)
ledpedred = Pin('P9', mode=Pin.OUT)

#Lights for cars/traffic
ledcargreen = Pin('P10', mode=Pin.OUT)
ledcaryellow = Pin('P11', mode=Pin.OUT)
ledcarred = Pin('P12', mode=Pin.OUT)

#Buzzer
buzzer = Pin('P5')
tim = PWM(0, frequency=2900)
ch = tim.channel(2, duty_cycle=0, pin=buzzer)

#Button
buttonPin = Pin('P6', mode=Pin.IN, pull=None)
buttonPin.callback(Pin.IRQ_FALLING, buttonEventCallback)

#Global variable for messages in MQTT server.
MSG = (None, None)

#Global variable to check if connected to mqtt server.
mqtt_connected = False

#Wlan
wlan = WLAN(mode=WLAN.STA)
wifi_connect()
client = MQTTClient("abda03c2-9f4b-43f9-be51-3dc3e126b80a", "iot-edu-lab.lnu.se",user="king", password="arthur", port=1883)
mqtt_connected = True
client.set_callback(sub_cb)
client.connect()
client.subscribe(topic="cowboys/olof/cars")
client.subscribe(topic="cowboys/olof/peds")
print("Connected to MQTT\n")
start_new_thread(car_go, tuple("0"))

while True:
    try:
        if not wlan.isconnected():
            wifi_connect()
        elif mqtt_connected is False:
            mqtt_connected = True
            client.connect()


        else:
            client.check_msg()
            print(MSG)
        time.sleep(1)
    except OSError as er:
        print("failed: " + str(er)) # give us some idea on what went wrong
        client.disconnect() # disconnect from adafruit IO to free resources
        mqtt_connected = False # mark us disconnected so we know that we should connect again

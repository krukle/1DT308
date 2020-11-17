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
    Turns green led on for pedestrians and sends information to MQTT-server.
    """
    print("My pedestrians: green")
    ledpedbutton.value(0)
    ledpedred.value(0)
    ledpedgreen.value(1)
    client.publish(topic="cowboys/christoffer/peds", msg="GREEN")

def mqtt_peds_red():
    """
    Turns red led on for pedestrians and sends information to MQTT-server.
    """
    print("My pedestrians: red")
    ledpedgreen.value(0)
    ledpedred.value(1)
    client.publish(topic="cowboys/christoffer/peds", msg="RED")

def mqtt_cars_green():
    """
    Turns green LED on for traffic and sends information to mqtt-server.
    """
    print("My cars: green")

    #Turns on yellow light for a second before passing to green
    ledcaryellow.value(1)
    client.publish(topic="cowboys/christoffer/cars", msg="GREEN")
    time.sleep(1)

    #Turns on green light
    ledcarred.value(0)
    ledcaryellow.value(0)
    ledcargreen.value(1)

def mqtt_cars_red():
    """
    Turns red LED on for traffic on and sends information to MQTT-server
    """
    print("My cars: red")

    #Turns on yellow light for a second before passing to red
    ledcaryellow.value(1)
    ledcargreen.value(0)
    time.sleep(1)

    #Turns on red light
    ledcaryellow.value(0)
    ledcarred.value(1)
    client.publish(topic="cowboys/christoffer/cars", msg="RED")

def buttonEventCallback(argument):
    """
    When button is pressed; ifButtonCanBePressed is True,
    start the pedestrian crossing loop in at most 4 seconds.
    """
    global buttonCanBePressed
    if buttonCanBePressed is True:
        ledpedbutton.value(1)
        buttonCanBePressed = False
        start_new_thread(is_timer_4, ())

def is_timer_4():
    """
    Checks if timer has been on for atleast 4
    seconds, if so, start function, if not, wait
    until it has, then start function.
    """
    while timer.read() < 4 or peds == "green":
        machine.idle()
    ped_loop()

def car_green():
    """
    Part of 'standard traffic loop'.
    Plays for 9s, then goes to car_red.
    """
    #Resets timer for pedestrians and green light
    timer.reset()
    mqtt_cars_green()
    mqtt_peds_red()
    while peds == "green" or timer.read() < 9:
        machine.idle()
    while buttonCanBePressed is False:
        machine.idle()
    car_red()

def car_red():
    """
    Part of 'standard traffic loop'.
    Plays for 9s, then goes to car_green.
    """
    timer.reset()
    mqtt_cars_red()
    mqtt_peds_red()

    while timer.read() < 9:
        machine.idle()

    #Keeps the loop from playing while the pedestrian crossing
    #loop is ongoing.
    while buttonCanBePressed is False:
        machine.idle()
    car_green()

def ped_loop():
    """
    When button is presssed:
    Loop for pedestrians to cross.
    """
    global buttonCanBePressed
    client.publish(topic="cowboys/christoffer/peds", msg="GREEN")

    #If traffic light was green when pedestrian Crossing
    #loop began, turn the traffic light, red.
    if ledcargreen.value() == 1:
        mqtt_cars_red()

    #1 second later green light for pedestrians is on.
    time.sleep(1)
    mqtt_peds_green()

    #Ticking noise
    #20 times (0.1 + 0.1) = 4 seconds
    for i in range(20):
        ch.duty_cycle(0.5)
        time.sleep(0.1)
        ch.duty_cycle(0)
        time.sleep(0.1)
    #3 times (0.3+0.3) = 1.8 seconds
    for i in range(3):
        ch.duty_cycle(0.5)
        time.sleep(0.3)
        ch.duty_cycle(0)
        time.sleep(0.3)

    #Turns pedestrian crossing red and returns to regular
    #crossing loop.
    mqtt_peds_red()
    ledpedbutton.value(0)
    buttonCanBePressed = True

def sub_cb(topic, msg):
    """
    Takes the values recieved from the MQTT subscription
    and translates them into variables cars and peds.
    """
    global cars, peds
    topic = topic.decode('utf-8').lower()
    msg = msg.decode('utf-8').lower()
    if topic == topic1:
        cars = msg
    elif topic == topic2:
        peds = msg

def wifi_connect(wifi, password):
    """
    Connects to WIFI.
    """
    wlan.connect(wifi, auth=(WLAN.WPA2, password), timeout=5000)

    while not wlan.isconnected():
        machine.idle()
    print("Connected to WiFi\n")

def mqtt_connect(topic1, topic2):
    """
    Connects to MQTT-server and subscribes to topics 1 and 2.
    """
    global mqtt_connected
    mqtt_connected = True
    client = MQTTClient("abda03c2-9f4b-43f9-be51-3dc3e126b80a", "iot-edu-lab.lnu.se",user="king", password="arthur", port=1883)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic=topic1)
    client.subscribe(topic=topic2)
    print("Connected to MQTT\n")
    return client

#If button can be pressed;
#buttonCanBePressed is set to True
buttonCanBePressed = True

#Timer
timer = Timer.Chrono()
timer.start()

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

#Global variable to check if connected to mqtt server.
mqtt_connected = False

#Global variables for MQTT subscription topics
topic1 = "cowboys/olof/cars"
topic2 = "cowboys/olof/peds"

#Global variables for MQTT subscription messages
cars = "green"
peds = "red"

#Wlan
wlan = WLAN(mode=WLAN.STA)
wifi_connect("ChristofferLisen", "EidPetersson")

#MQTTClient
client = mqtt_connect(topic1, topic2)

#Traffic light begins
start_new_thread(car_red, ())

#Makes sure everything works as should.
#If so, checks for messages on MQTT-server.
while True:
    try:
        if not wlan.isconnected():
            wifi_connect("ChristofferLisen", "EidPetersson")

        elif not mqtt_connected:
            client = mqtt_connect(topic1, topic2)

        else:
            client.wait_msg()

            print("Crossing cars:", cars)
            print("Crossing pedestrians:", peds, "\n")

    except OSError as er:
        print("failed: " + str(er)) # give us some idea on what went wrong
        client.disconnect() # disconnect from MQTT server to free resources
        mqtt_connected = False # mark us disconnected so we know that we should connect again

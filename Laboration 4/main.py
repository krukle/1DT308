from machine import Pin
from machine import PWM
import time
from _thread import start_new_thread
from machine import Timer

value = True
timer = Timer.Chrono()
timer.start()


def buttonEventCallback(argument):
    """When button is pressed, traffic light start."""
    global value
    ledpedbutton.value(1)
    if value is True:
        value = False
        start_new_thread(is_timer_4, tuple('0'))

def is_timer_4(argument):
    if timer.read() > 4:
        start_new_thread(car_soon_stop, tuple('0'))
    else:
        time.sleep(4-timer.read())
        start_new_thread(car_soon_stop, tuple('0'))


def car_go(argument):
    global value
    timer.reset()
    ledcargreen.value(1)
    ledpedred.value(1)
    value = True


def car_soon_stop(argument):
    ledcargreen.value(0)
    ledcaryellow.value(1)
    time.sleep(2)
    start_new_thread(all_stop, tuple('0'))

def all_stop(argment):
    ledcaryellow.value(0)
    ledcarred.value(1)
    time.sleep(1)
    start_new_thread(ped_go, tuple('0'))

def ped_go(argument):
    ledpedred.value(0)
    ledpedgreen.value(1)
    for i in range(20):#20 times (0.1 + 0.1) = 4 seconds
        ch.duty_cycle(0.5)
        time.sleep(0.1)
        ch.duty_cycle(0)
        time.sleep(0.1)
    start_new_thread(ped_soon_stop, tuple('0'))

def ped_soon_stop(argument):
    for i in range(3):#3 times (0.3+0.3) = 1.8 seconds
        ch.duty_cycle(0.5)
        time.sleep(0.3)
        ch.duty_cycle(0)
        time.sleep(0.3)
    start_new_thread(car_get_ready, tuple('0'))

def car_get_ready(argument):
    ledcaryellow.value(1)
    ledpedgreen.value(0)
    time.sleep(1)
    ledcaryellow.value(0)
    ledcarred.value(0)
    ledpedbutton.value(0)
    start_new_thread(car_go, tuple('0'))

ledpedbutton = Pin('P7', mode=Pin.OUT)
ledpedgreen = Pin('P8', mode=Pin.OUT)
ledpedred = Pin('P9', mode=Pin.OUT)

ledcargreen = Pin('P10', mode=Pin.OUT)
ledcaryellow = Pin('P11', mode=Pin.OUT)
ledcarred = Pin('P12', mode=Pin.OUT)

buzzer = Pin('P5')
tim = PWM(0, frequency=2900)
ch = tim.channel(2, duty_cycle=0, pin=buzzer)

ledcargreen.value(1)
ledpedred.value(1)

buttonPin = Pin('P6', mode=Pin.IN, pull=None)
buttonPin.callback(Pin.IRQ_FALLING, buttonEventCallback)

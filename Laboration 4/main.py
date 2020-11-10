from machine import Pin
from machine import PWM
import time
from _thread import start_new_thread
from machine import Timer

#If button can be pressed;
#buttonCanBePressed is set to True
buttonCanBePressed = True

#Timer for car_go. We want cars to have a green
#light for atleast 4 seconds.
timer = Timer.Chrono()

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
    timer.reset()
    ledcargreen.value(1)
    ledpedred.value(1)
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
    ledpedgreen.value(0)
    time.sleep(1)
    ledcarred.value(0)
    ledcaryellow.value(0)
    ledpedbutton.value(0)
    start_new_thread(car_go, tuple('0'))

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

#Traffic light starts. Timer for car_go starts.
timer.start()
car_go('argument')

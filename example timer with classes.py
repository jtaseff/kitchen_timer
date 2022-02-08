import touchio
import board
import adafruit_dotstar
import time
import pulseio
# import alarm # alarm currently works only on the ESP32-S2 chip,
# e.g., AdaFruit's Metro ESP32-S2 and FeatherS2

sleep_time = 5 * 60  # in seconds
addl_time = 60  # in seconds
BLUE = (0, 0, 10)
GREEN = (0, 10, 0)
BRIGHT_GREEN = (0, 255, 0)
OFF = (0, 0, 0)
YELLOW = (10, 10, 0)
LOW_YELLOW = (2, 2, 0)
RED = (255, 0, 0)
# see http://electronic-setup.blogspot.com/2010/11/nokia-rttl-frequencies-hz.html
A5 = 440   # Octave 5 in RTTTL
C5 = 523 
C6 = 1046
A6 = 880
A7 = 1760
E6 = 1175


class Kitchen_Timer():
    def calc_asleep_time(self):
        return time.monotonic() + sleep_time

    def __init__(self, dotstar, piezo):
        # a kitchen timer consists of light (the dotstar) and sound (the piezo)
        # it has touch sensors for input. Those are passed in do_check()
        self.alarm_time = 0
        self.asleep_time = self.calc_asleep_time()
        self.is_asleep = False
        self.alarmed = False
        self.alarming = False
        self.dotstar = dotstar
        self.piezo = piezo
        self.dotstar.brightness = 1
        self.dotstar.fill(BLUE)

    def play_note(self, note):
        if note[0] != 0:
            pwm = pulseio.PWMOut(self.piezo, duty_cycle=0x7FFF, frequency=note[0])
            # 0x7FFF is 50% duty cycle
            # pwm.frequency = math.floor(note[0] * 1.25)
        time.sleep(note[1])
        if note[0] != 0:
            pwm.deinit()

    def play_touch(self):
        self.dotstar.brightness = 8
        self.dotstar.fill(BRIGHT_GREEN)
        self.play_note((E6, 0.125))
        time.sleep(0.2)
        self.dotstar.brightness = 1
        self.dotstar.fill(GREEN)
        time.sleep(0.2)

    def play_beep(self):
        self.play_note((A7, 0.125))

    def play_alarm(self):
        self.dotstar.brightness = 8
        self.dotstar.fill(RED)
        self.play_note((C5, 0.5))
        time.sleep(0.2)
        self.dotstar.fill(OFF)
        time.sleep(0.2)

    def trigger_alarm(self):
        self.alarming = True
        self.alarmed = False
        self.asleep_time = self.calc_asleep_time()
        # reset when we'll go to sleep

    def turn_off(self):
        self.alarming = False
        self.dotstar.brightness = 1
        self.dotstar.fill(BLUE)
        self.play_beep()

    def wake_up(self):
        global loop_sleep
        self.dotstar.fill(BLUE)
        self.play_beep()
        self.is_asleep = False
        loop_sleep = 0.2
        self.asleep_time = self.calc_asleep_time()  # reset our asleep time

    def start(self):
        self.alarm_time = time.monotonic()
        self.alarmed = True

    def cancel(self):
        self.alarmed = False
        self.dotstar.brightness = 1
        self.dotstar.fill(BLUE)
        self.play_beep()

    def add_time(self):
        self.alarm_time += addl_time
        self.play_touch()
        self.dotstar.brightness = 1
        self.dotstar.fill(GREEN)

    def go_to_sleep(self):
        # time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 20)
        self.alarming = False
        self.is_asleep = True
        self.dotstar.fill(LOW_YELLOW)
        # alarm.exit_and_deep_sleep_until_alarms(time_alarm)
        
    def do_check(self, touch1, touch2):
        loop_sleep = 0.2
        if self.alarmed and touch1.value and touch2.value:  # touch both to cancel a pending alarm
            self.cancel()
            time.sleep(0.5)
        if touch1.value or touch2.value:  # touch will either turn off the alarm, reawaken the loop, or add minutes
            if self.alarming:
                self.turn_off()
                time.sleep(0.5)           # gives the user some time to take finger off pad
            elif self.is_asleep:
                self.wake_up()
                time.sleep(0.5)           # just to give some delay before the next touch
            else:                         # we start alarm and add time
                if not self.alarmed:
                    self.start()
                self.add_time()
                time.sleep(0.25)          # delay before the next touch to add time
        if self.alarmed and time.monotonic() > self.alarm_time:
            self.trigger_alarm()
        if self.alarming:
            self.play_alarm()
        if not self.alarmed and not self.is_asleep and time.monotonic() > self.asleep_time:
            loop_sleep = 2.0               # slow down the loop. Not sure if this matters to power management
            self.go_to_sleep()
        return loop_sleep    

touch1 = touchio.TouchIn(board.D1)
touch2 = touchio.TouchIn(board.D2)
dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
alarm = Kitchen_Timer(dotstar=dotstar, piezo=board.D0)

while True:
    loop_time = alarm.do_check(touch1,touch2)    
    time.sleep(loop_time)
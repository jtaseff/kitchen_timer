



CFG_BTN1_DURATION = 5
CFG_BTN2_DURATION = 15
CFG_BTN3_DURATION = 30










import board
import displayio
import terminalio
import digitalio
import time
from adafruit_display_text import label     # circuitpython library
import adafruit_displayio_ssd1305           # circuitpython library
from math import ceil




selected = -1	# the currently selected timer
lastbtnpress = 0






######################
#  DISPLAY HARDWARE  #
######################


# pins and defines
oled_reset = board.D4
spi = board.SPI()		# this picks default SCK and MOSI
oled_dc = board.RX	    # data/cmd pin, idk what this does
oled_cs = board.TX		# chip select
WIDTH = 64
HEIGHT = 128
ROTATION = 270


# create display objects
displayio.release_displays()
display_bus = displayio.FourWire(spi, command=oled_dc, chip_select=oled_cs, reset=oled_reset, baudrate=12000000)
# display = adafruit_displayio_ssd1305.SSD1305(display_bus, width=WIDTH, height=HEIGHT, rotation=ROTATION, auto_refresh=False)
display = adafruit_displayio_ssd1305.SSD1305(display_bus, width=WIDTH, height=HEIGHT, rotation=ROTATION, auto_refresh=False)

# print(display_bus.frequency)








######################
#  DISPLAY GRAPHICS  #
######################


CFG_SHOW_STATE = True


# Make the display context
main_timer_disp_group = displayio.Group()
display.show(main_timer_disp_group)

# lists to hold stuff
timelabels = []
durationlabels = []
boxes = []

# other settings
zerotime = "0:00"
FONTSCALE = 2
white = 0xFFFFFF
black = 0x00

# scale2 text seems padded by 6 top, 6 right
from adafruit_display_shapes.rect import Rect

for ii in range(3):
	
	# timelabels.append(label.Label(terminalio.FONT, text=zerotime, color=white, scale=2, anchor_point=(0,0), anchored_position=(3,ii*42-5)))
	timelabels.append(label.Label(terminalio.FONT, text=zerotime, color=white, scale=2, anchor_point=(1,0), anchored_position=(62,ii*42-5)))
	durationlabels.append(label.Label(terminalio.FONT, text=zerotime, color=white, scale=1, anchor_point=(1,0), anchored_position=(61,ii*42+20)))
	boxes.append(Rect(x=0, y=0+ii*42, width=64, height=38, outline=white, fill=None, stroke=1))
	
	
	main_timer_disp_group.append(timelabels[ii])
	main_timer_disp_group.append(durationlabels[ii])
	main_timer_disp_group.append(boxes[ii])
	
	
# rect = Rect(20, 30, 21, 41, fill=0x0, outline=0xFFFFFF)


MAIN_UPDATE_INTERVAL = 0.1
last_main_update = 0


def StateToString(state):
	if state == 1:
		return "Idle"
	elif state == 2:
		return "Timing"
	elif state == 3:
		return "Alarm!"
	elif state == 4:
		return "Long alarm!"
	elif state == 5:
		return "Silenced"
	elif state == 6:
		return "Counting"
	else:
		return "Unknown"


def Updatetimelabels():
	for ii in range(3):
		remmin, remsec = divmod(ceil(timers[ii].GetRemainingSec()), 60)
		durmin, dursec = divmod(ceil(timers[ii].GetDurationSec()), 60)
		state = timers[ii].GetState()
		# timelabels[ii].text = "{}\n{}".format(StateToString(timers[ii].GetState()), ceil(timers[ii].GetRemainingSec()))
		# timelabels[ii].text = "{}:{}".format(min, sec)
		timelabels[ii].text = "%2d:%02d" % (remmin, remsec)
		durationlabels[ii].text = "%2d:%02d" % (durmin, dursec)
		if selected == ii:
			boxes[ii].outline = white
		else:
			boxes[ii].outline = black
	
	
	display.refresh()





#################
#  TIMER SETUP  #
#################

# create the list of timers
from jtimer import jtimer
timers = []
for ii in range(3):
	timers.append(jtimer())


# AUTO TEST ON STARTUP
timers[0].SetDurationSec(7)
timers[2].SetDurationSec(60)
Updatetimelabels()
time.sleep(1)
timers[0].Start()
timers[2].Start()
# END AUTO TEST







###################
#  BUTTONS SETUP  #
###################

# pins are 5, 6, 9, 10, 11, 12, 13

# KEYPAD METHOD
import keypad

# define key order being used
KEY_PINS = (
    board.D5,
    board.D6,
    board.D9,
    board.D10,
    board.D11,
    board.D12,
    board.D13
)

T1event = keypad.Event(0, True)   # Button T1 pressed
T2event = keypad.Event(1, True)   # Button T2 pressed
T3event = keypad.Event(2, True)   # Button T3 pressed
SRevent = keypad.Event(3, True)   # Button SR pressed
A1event = keypad.Event(4, True)   # Button A1 pressed
A2event = keypad.Event(5, True)   # Button A2 pressed
A3event = keypad.Event(6, True)   # Button A3 pressed

# create keypad object to read the pins
keys = keypad.Keys(KEY_PINS, value_when_pressed=True, pull=True)

# create a blank event - we will always get key events into this to avoid allocating new ones every time
event = keypad.Event()

# END KEYPAD METHOD






#################
#  LOGIC SETUP  #
#################



def AnyButtonPressed():
	global lastbtnpress
	lastbtnpress = time.monotonic()
	
def NoBounce():
	global lastbtnpress
	return time.monotonic() > lastbtnpress + 0.25
	
	
def TimeSinceLastButtonPress():
	return time.monotonic() - lastbtnpress



def AddToSelected(sec):
	global selected
	
	# if none selected, pick the first idle one
	if selected == -1:
		for ii in range(3):
			if timers[ii].GetIsIdle():
				Select(ii)
				break
		print("Auto selected T{}".format(selected+1))

	sel = timers[selected]
	if sel.IsTimeUp():
		# clear and restart alarming timer
		sel.Clear()
		sel.AddDurationSec(sec)
		sel.Start()
		print("Cleared T{} and started with new time {}".format(selected+1, sec))
	elif sel.state == sel.IDLE:
		# start idle timer
		sel.AddDurationSec(sec)
		sel.Start()
		print("Started T{} with new time {}".format(selected+1, sec))
	else:
		# add to running timer
		sel.AddDurationSec(sec)
	
	print("{} added to T{}".format(sec, selected+1))


def ClearSelected():
	timers[selected].Clear()
	print("T{} reset".format(selected+1))


def Select(which):
	global selected
	if selected != which:
		selected = which
		print("T{} selected".format(which+1))
		return True
	else:
		print("T{} already selected".format(which+1))
		return False
	
def Deselect():
	global selected
	selected = -1
	print("Deselected")


def ClearBtnCounters():
	btnT1ctr.reset()
	btnT2ctr.reset()
	btnT3ctr.reset()
	btnSRctr.reset()
	btnA1ctr.reset()



#############
#  LOOPING  #
#############


while True:
	
	
	
    
    # event will be None if nothing has happened.
	if keys.events.get_into(event):
		print(event)
		
		if event.pressed:
			# record that something pressed, track timing for some logic
			AnyButtonPressed()
		
		
		if event == T1event:
			Select(0)
			print("T1 button")
			
		if event == T2event:
			Select(1)
			print("T2 button")
			
		if event == T3event:
			Select(2)
			print("T3 button")
			
		if event == A1event:
			print("A1 button")
			AddToSelected(CFG_BTN1_DURATION)
		
		if event == A2event:
			print("A2 button")
			AddToSelected(CFG_BTN2_DURATION)
		
		if event == A3event:
			print("A3 button")
			AddToSelected(CFG_BTN3_DURATION)
		
		if event == SRevent:
			print("SR button")
			ClearSelected()
		
		
		
		
	else:
		
		# update the displays only after we have handled button events, since it will block for a 
		
		# update the timer data
		timers[0].Update()
		timers[1].Update()
		timers[2].Update()
		
		profstart = time.monotonic()
		
		# update the display
		Updatetimelabels()
		
		profend = time.monotonic()
		
		proftime = profend - profstart
		# print(proftime)






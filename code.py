



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


MAIN_UPDATE_INTERVAL = 0.2
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
timers.append(jtimer())
timers.append(jtimer())
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



# DEBOUNCER METHOD
# from adafruit_debouncer import Debouncer
# def make_pin_reader(pin):
    # io = digitalio.DigitalInOut(pin)
    # io.direction = digitalio.Direction.INPUT
    # io.pull = digitalio.Pull.UP
    # return lambda: io.value
	
# btnT1 = Debouncer(make_pin_reader(board.D5))
# btnT2 = Debouncer(make_pin_reader(board.D6))
# btnT3 = Debouncer(make_pin_reader(board.D9))
# btnS = Debouncer(make_pin_reader(board.D10))
# btn30sec = Debouncer(make_pin_reader(board.D11))
# btn1min = Debouncer(make_pin_reader(board.D12))
# btn5min = Debouncer(make_pin_reader(board.D13))
# END DEBOUNCER METHOD


# RAW PIN VALUE METHOD
# def make_pin_io(pin):
    # io = digitalio.DigitalInOut(pin)
    # io.direction = digitalio.Direction.INPUT
    # io.pull = digitalio.Pull.UP
    # return io
	

# btnT1 = make_pin_io(board.D5)
# btnT2 = make_pin_io(board.D6)
# btnT3 = make_pin_io(board.D9)
# btnS = make_pin_io(board.D10)
# btn30sec = make_pin_io(board.D11)
# btn1min = make_pin_io(board.D12)
# btn5min = make_pin_io(board.D13)
# END RAW PIN VALUE METHOD


# COUNTIO METHOD
# class countio.Counter(pin: microcontroller.Pin, *, edge: Edge = countio.Edge.FALL, pull: Optional[digitalio.Pull])
import countio
btnT1ctr = countio.Counter(pin=board.D5, edge=countio.Edge.FALL, pull=digitalio.Pull.UP)
btnT2ctr = countio.Counter(pin=board.D6, edge=countio.Edge.FALL, pull=digitalio.Pull.UP)
btnT3ctr = countio.Counter(pin=board.D9, edge=countio.Edge.FALL, pull=digitalio.Pull.UP)
btnSRctr = countio.Counter(pin=board.D10, edge=countio.Edge.FALL, pull=digitalio.Pull.UP)
btnA1ctr = countio.Counter(pin=board.D11, edge=countio.Edge.FALL, pull=digitalio.Pull.UP)
btnA2ctr = countio.Counter(pin=board.D12, edge=countio.Edge.FALL, pull=digitalio.Pull.UP)
btnA3ctr = countio.Counter(pin=board.D13, edge=countio.Edge.FALL, pull=digitalio.Pull.UP)
# END COUNTIO METHOD








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
		print("Auto selected T{}".format(selected))

	sel = timers[selected]
	if sel.IsTimeUp():
		# clear and restart alarming timer
		sel.Clear()
		sel.AddDurationSec(sec)
		sel.Start()
		print("Cleared T{} and started with new time {}".format(selected, sec))
	elif sel.state == sel.IDLE:
		# start idle timer
		sel.AddDurationSec(sec)
		sel.Start()
		print("Started T{} with new time {}".format(selected, sec))
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





#############
#  LOOPING  #
#############


while True:
	
	# update all the button states
	# btnT1.update()
	# btnT2.update()
	# btnT3.update()
	# btnS.update()
	# btn30sec.update()
	# btn1min.update()
	# btn5min.update()
	
	didselect = 0
	
	
	# react to buttons
	# if btnT1.fell:
	# if btnT1.value == 0 and NoBounce():
	if btnT1ctr.count > 0 and NoBounce():
		btnT1ctr.reset()
		AnyButtonPressed()
		didselect = Select(0)
	
	# if btnT2.fell:
	# if btnT2.value == 0 and NoBounce():
	if btnT2ctr.count > 0 and NoBounce():
		btnT2ctr.reset()
		AnyButtonPressed()
		didselect = Select(1)
	
	# if btnT3.fell:
	# if btnT3.value == 0 and NoBounce():
	if btnT3ctr.count > 0 and NoBounce():
		btnT3ctr.reset()
		AnyButtonPressed()
		didselect = Select(2)
	
	# if btn30sec.fell:
	# if btn30sec.value == 0 and NoBounce():
	if btnA1ctr.count > 0 and NoBounce():
		btnA1ctr.reset()
		AnyButtonPressed()
		AddToSelected(CFG_BTN1_DURATION)
	
	# if btn1min.fell:
	# if btn1min.value == 0 and NoBounce():
	if btnA2ctr.count > 0 and NoBounce():
		btnA2ctr.reset()
		AnyButtonPressed()
		AddToSelected(CFG_BTN2_DURATION)
	
	# if btn5min.fell:
	# if btn5min.value == 0 and NoBounce():
	if btnA3ctr.count > 0 and NoBounce():
		btnA3ctr.reset()
		AnyButtonPressed()
		AddToSelected(CFG_BTN3_DURATION)
		
	# if btnS.fell:
	# if btnS.value == 0 and NoBounce():
	if btnSRctr.count > 0 and NoBounce():
		btnSRctr.reset()
		AnyButtonPressed()
		ClearSelected()
		didselect = True
	
	
	
	
	# update the timers and displays every 200ms
	if time.monotonic() > last_main_update + MAIN_UPDATE_INTERVAL:
		last_main_update = time.monotonic()
	
		# update the timer data
		# timer1.Update()
		# timer2.Update()
		# timer3.Update()
		timers[0].Update()
		timers[1].Update()
		timers[2].Update()
		
		profstart = time.monotonic()
		
		# update the display
		Updatetimelabels()
		
		profend = time.monotonic()
		
		proftime = profend - profstart
		print(proftime)






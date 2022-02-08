
import time



class jtimer:
	# my custom timer class

	# global class vars
	NS_TO_SEC = 1000000000
	NS_TO_MILLI = 1000000
	
	CFG_ALARM_TIME_TO_CHILL = 30
	
	# static vars to represent state
	IDLE = 1
	TIMING = 2
	ALARMED = 3
	LONGALARM = 4
	SILENCED = 5
	COUNTUP = 6		# starting with duration 0 will make it count up instead
	# paused?
	
	
	# init function
	def __init__(self):
		self.Clear()
		
	
	def GetState(self):
		return self.state
		
	
	
	def Clear(self):
		self.state = self.IDLE
		self.durationSec = 0
		self.durationNS = 0
		self.startNS = 0
		self.endNS = 0
		self.elapsedNS = 0
		self.elapsedSec = 0
		self.elapsedSinceAlarmNS = 0
		self.elapsedSinceAlarmSec =  0
		
		
	def _CalcEndTime(self):
		self.endNS = self.startNS + self.durationNS
		
		
	def GetDurationSec(self):
		return self.durationSec
		
		
	def GetDurationNS(self):
		return self.durationNS
		
		
	def SetDurationSec(self, NewDurationSec):
		self.durationSec = NewDurationSec
		self.durationNS = int(NewDurationSec * self.NS_TO_SEC)
		if self.state == self.TIMING:
			self._CalcEndTime()
		
	
	def AddDurationSec(self, NewDurationSec):
		current = self.GetDurationSec()
		new = current + NewDurationSec
		self.SetDurationSec(new)
	
	
	def _CalcElapsed(self):
		# calculate the elapsed time
		self.elapsedNS = time.monotonic_ns() - self.startNS
		self.elapsedMsec = self.elapsedNS // self.NS_TO_MILLI		# gives an int
		self.elapsedSec = self.elapsedNS / self.NS_TO_SEC			# gives a float, which can lose reolution for large values
		if self.IsTimeUp():
			self.elapsedSinceAlarmNS = time.monotonic_ns() - self.endNS
			self.elapsedSinceAlarmSec = self.elapsedSinceAlarmNS / self.NS_TO_SEC
		
		if self.state == self.IDLE:
			self.elapsedNS = 0
			self.elapsedSec = 0
		return self.elapsedSec
		
		
	def GetElapsedSec(self):
		self._CalcElapsed()
		return self.elapsedSec
		
		
	def GetElapsedSinceAlarmSec(self):
		self._CalcElapsed()
		return self.elapsedSinceAlarmSec
		
	
	def GetRemainingNS(self):
		remain = self.endNS - time.monotonic_ns()
		if remain > 0 and self.GetIsTiming():
			return remain
		elif self.state == self.IDLE:
			return self.durationNS
		else:
			return 0
	
	
	def GetRemainingSec(self):
		return self.GetRemainingNS() / self.NS_TO_SEC
		
	
	def IsTimeUp(self):
		# return whether we're past the end time
		return time.monotonic_ns() > self.endNS and self.GetIsTiming()
	

	def Start(self):
		# start timing
		
		if self.state == self.IDLE:
			
			# record the start time
			self.startNS = time.monotonic_ns()
			
			if self.durationNS > 0:
				# if a duration has been defined, start counting down
				self._CalcEndTime()
				self.state = self.TIMING
			
			else:
				# if no duration, start counting up
				self.durationSec = 0
				self.durationNS = 0
				self.elapsedNS = 0
				self.elapsedSec = 0
				self.endNS = 0
				self.state = self.COUNTUP
		
		else:
			print("wrong state {} to start timing".format(self.state))
	
	
	def Silence(self):
		if self.state == self.ALARMED or self.state == self.LONGALARM:
			self.state = self.SILENCED
			
			
	def GetIsAlarm(self):
		# get whether alarm is active
		return self.state == self.ALARMED
		
		
	def GetIsLongAlarm(self):
		# get whether alarm has been going off for a while
		return self.state == self.LONGALARM
		
		
	def GetIsSilenced(self):
		# get whether alarm has been silenced
		return self.state == self.SILENCED
		
	
	def GetIsTiming(self):
		# get whether timer is going, including alarmed/silenced/whatever
		return self.state == self.TIMING or self.state == self.ALARMED or self.state == self.LONGALARM or self.state == self.SILENCED
		
		
	def GetIsCountingUp(self):
		return self.state == self.COUNTUP
		
	
	def GetIsIdle(self):
		return self.state == self.IDLE
	
	
	def Update(self):

		# branch through any the states we need to act on
		
		if self.state == self.TIMING:
			# timer is running, check elapsed
			
			if self.IsTimeUp():
				self.state = self.ALARMED
			
		elif self.state == self.ALARMED:
			# check if it has been going off for a while
			if self.GetElapsedSinceAlarmSec() > self.CFG_ALARM_TIME_TO_CHILL:
				self.state = self.LONGALARM
				
			
		# elif self.state == self.COUNTUP:
			# calculate the elapsed time so it can be displayed
			# actually don't think we need to do anything here
			# self._CalcElapsed()
	

	# IDLE = 1
	# TIMING = 2
	# ALARMED = 3
	# LONGALARM = 4
	# SILENCED = 5
	# COUNTUP = 6		# starting with duration 0 will make it count up instead
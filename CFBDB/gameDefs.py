EVENT_NULL = -1
EVENT_KICKOFF = 0
EVENT_ONSIDE_KICK = 1
EVENT_RUSH = 2
EVENT_FUMBLE = 3
EVENT_RECOVERY = 4
EVENT_RECOVERY_OFFENSE = 5
EVENT_RECOVERY_DEFENSE = 6 # for turnovers, not necessariy the team originally on defense
EVENT_PASS = 7
EVENT_INCOMPLETE_PASS = 8
EVENT_INTERCEPTION = 9
EVENT_SACK = 10
EVENT_LATERAL = 11
EVENT_FIELD_GOAL_ATTEMPT = 12
EVENT_BLOCKED_FIELD_GOAL = 13
EVENT_PUNT = 14
EVENT_BLOCKED_PUNT = 15
EVENT_ADVANCE = 16
EVENT_RETURN = 17
EVENT_PENALTY = 18

def eventString(event):
	if event == EVENT_KICKOFF:
		return 'Kickoff'
	elif event == EVENT_ONSIDE_KICK:
		return 'Onside Kick'
	elif event == EVENT_RUSH:
		return 'Rush'
	elif event == EVENT_FUMBLE:
		return 'Fumble'
	elif event == EVENT_RECOVERY:
		return 'Recovery'
	elif event == EVENT_RECOVERY_OFFENSE:
		return 'Offensive recovery'
	elif event == EVENT_RECOVERY_DEFENSE:
		return 'Defensive recovery'
	elif event == EVENT_PASS:
		return 'Pass'
	elif event == EVENT_INCOMPLETE_PASS:
		return 'Pass incomplete'
	elif event == EVENT_INTERCEPTION:
		return 'Pass intercepted'
	elif event == EVENT_SACK:
		return 'Sack'
	elif event == EVENT_LATERAL:
		return 'Lateral'
	elif event == EVENT_FIELD_GOAL_ATTEMPT:
		return 'Field Goal Attempt'
	elif event == EVENT_BLOCKED_FIELD_GOAL:
		return 'Blocked Field Goal'
	elif event == EVENT_PUNT:
		return 'Punt'
	elif event == EVENT_BLOCKED_PUNT:
		return 'Blocked Punt'
	elif event == EVENT_ADVANCE:
		return 'Advanced'
	elif event == EVENT_RETURN:
		return 'Returned'
	elif event == EVENT_PENALTY:
		return 'Penalty'
	else:
		return 'NO PLAY'

RESULT_NONE = -1
RESULT_REPEAT_DOWN = 0 # same team, same drive
RESULT_ADVANCE_DOWN = 1 # same team, same drive (except for onside kicks)
RESULT_FIRST_DOWN = 2 # same team, same drive
RESULT_TURNOVER_ON_DOWNS = 3 # other team
RESULT_KICK_RECEIVED = 4 # other team
RESULT_FIELD_GOAL = 5 # same team, same drive (kickoff)
RESULT_MISSED_FIELD_GOAL = 6 # other team
RESULT_TOUCHDOWN = 7 # same team, same drive (try down)
RESULT_DEFENSIVE_TOUCHDOWN = 8 # other team
RESULT_SAFETY = 9 # same team, same drive (kickoff)
RESULT_DEFENSIVE_SAFETY = 10 # other team
RESULT_TOUCHBACK = 11 # other team
RESULT_DEFENSIVE_TOUCHBACK = 12 # same team, new drive
RESULT_TURNOVER = 13 # other team
RESULT_DEFENSIVE_TURNOVER = 14 # same team, new drive

def resultString(result):
	if result == RESULT_REPEAT_DOWN:
		return 'Repeat Down'
	elif result == RESULT_ADVANCE_DOWN:
		return 'Advance Down'
	elif result == RESULT_FIRST_DOWN:
		return 'First Down'
	elif result == RESULT_TURNOVER_ON_DOWNS:
		return 'Turnover On Downs'
	elif result == RESULT_KICK_RECEIVED:
		return 'Kick Received'
	elif result == RESULT_FIELD_GOAL:
		return 'Field Goal'
	elif result == RESULT_MISSED_FIELD_GOAL:
		return 'Missed Field Goal'
	elif result == RESULT_TOUCHDOWN:
		return 'Touchdown'
	elif result == RESULT_DEFENSIVE_TOUCHDOWN:
		return 'Defensive Touchdown'
	elif result == RESULT_SAFETY:
		return 'Safety'
	elif result == RESULT_DEFENSIVE_SAFETY:
		return 'Defensive Safety'
	elif result == RESULT_TOUCHBACK:
		return 'Touchback'
	elif result == RESULT_DEFENSIVE_TOUCHBACK:
		return 'Defensive Touchback'
	elif result == RESULT_TURNOVER:
		return 'Turnover'
	elif result == RESULT_DEFENSIVE_TURNOVER:
		return 'Defensive Turnover'
	else:
		return 'NO RESULT'

# all PARSER_ values will == 2^n, where n is some number.
# this is done so that we can OR all of the values, bitwise,
# to come up with a single code that tells us where the data
# came from, and if it has been verified yet.
# the PARSER_VERIFIED bit will be set by the cfbdb.verifyGame()
# function (when it finds no errors to report), and each
# particular parser will set its own bit.
# a game may be parsed by more than one parser, with the results
# merged by a function yet to be written.  in that case, multiple
# parser bits may be set.
PARSER_VERIFIED = 1
PARSER_ESPN = 2
PARSER_ASB = 4

class Game:
	
	def __init__(self):
		self.drives = []
	
	def setNames(self, homeName, awayName):
		self.homeName = homeName.replace(' St', ' State')
		self.awayName = awayName.replace(' St', ' State')
	
	def setGameID(self):
		self.gameID = teamCode(self.homeName)
		self.gameID += self.day*1000
		self.gameID += self.month*100000
		self.gameID += (self.year - 2000)*10000000
	
	def eliminateEmptyDrives(self):
		numDrives = len(self.drives)
		i = 0
		while i < numDrives:
			drive = self.drives[i]
			drive.eliminateEmptyPlays()
			if len(drive.plays) == 0:
				del self.drives[i]
				numDrives -= 1
			else:
				i += 1
	
	def calcResults(self):
		hmScore = 0
		awScore = 0
		
		self.eliminateEmptyDrives()
		
		numDrives = len(self.drives)
		i = 0
		while i < numDrives:
			drive = self.drives[i]
			if i+1 < numDrives:
				nextDrive = self.drives[i+1]
				merged = True
				drive.calcResults(nextDrive.homePoss)
				# check and see if we had a drive erroneously split in
				# two (or more) pieces.  if so, merge them back together
				while drive.homePoss == nextDrive.homePoss and merged:
					merged = drive.mergeDrives(nextDrive)
					if merged:
						del self.drives[i+1]
						numDrives -= 1
						if i+1 < numDrives:
							nextDrive = self.drives[i+1]
							drive.calcResults(nextDrive.homePoss)
						else:
							merged = False
							drive.calcResults(drive.homePoss)
						
			else:
				drive.calcResults(drive.homePoss)
			
			drive.homeScore = hmScore
			drive.awayScore = awScore
			
			if drive.pointsThisDrive and drive.defensivePointsThisDrive:
				points = drive.pointsThisDrive
				defPoints = drive.defensivePointsThisDrive
				if drive.homePoss:
					hmScore += points
					awScore += defPoints
				else:
					hmScore += defPoints
					awScore += points
			i += 1

class Team:

	def __init__(self, longName, medName):
		self.code = -1
		self.names = [longName, medName]
	
	def addName(name):
		self.names.append(name)

class Venue:

	def __init__(self, name, city, state):
		self.name = name
		self.city = city
		self.state = state
		self.code = venueCode(self.name, self.city)
		#if self.code == -1:
		#	cfbdb.getVenueID(self)

class Drive:
	
	def __init__(self, hmPoss, teamName, defTeamName, medName, defMedName):
		self.homePoss = hmPoss
		self.teamPoss = teamName.replace('State','St')
		self.teamDef = defTeamName.replace('State','St')
		self.medPoss = medName
		self.medDef = defMedName
		self.plays = []
		self.homeScore = None
		self.awayScore = None
		self.firstDownsThisDrive = None
		self.pointsThisDrive = None
		self.defensivePointsThisDrive = None
	
	def eventDuringReturn(self, event):
		numPlays = len(self.plays)
		if numPlays == 0:
			return False
		lastPlay = self.plays[numPlays-1]
		if event in lastPlay.events:
			return lastPlay.duringReturn(event)
		else:
			return False
	
	def eliminateEmptyPlays(self):
		numPlays = len(self.plays)
		i = 0
		while i < numPlays:
			play = self.plays[i]
			play.eliminateNullEvents()
			if len(play.events) == 0:
				del self.plays[i]
				numPlays -= 1
			else:
				i += 1
	
	def calcResults(self, nextHomePoss):
		numPlays = len(self.plays)
		if numPlays == 0:
			return
		self.firstDownsThisDrive = 0
		self.pointsThisDrive = 0
		self.defensivePointsThisDrive = 0
		prevDown = 0
		prevResult = RESULT_NONE
		i = 0
		while i < numPlays:
			play = self.plays[i]
			if i+1 == numPlays:
				play.calcResults(self.homePoss == nextHomePoss)
				#print 'end of drive'
				#if self.homePoss:
				#	print 'self.homePoss'
				#if nextHomePoss:
				#	print 'nextHomePoss'
			else:
				play.calcResults(True)
				#print 'not end of drive'
			if play.result == RESULT_FIRST_DOWN:
				self.firstDownsThisDrive += 1
			if play.result == RESULT_DEFENSIVE_TOUCHDOWN or play.result == RESULT_SAFETY:
				self.defensivePointsThisDrive += play.pointsThisPlay
			elif play.pointsThisPlay:
				self.pointsThisDrive += play.pointsThisPlay
			# some play-by-play systems will label penalties that occur
			# during or after the try down (to be enforced on the kickoff)
			# as occuring on 1st down -- not necessarily incorrect, but
			# incompatible with the system I've set up.  we'll simply
			# re-label those plays as occuring on 0th down.
			#if prevDown == -1 and prevResult != RESULT_REPEAT_DOWN:
			#	print 'here - ' + play.body
			#	print play.down
			#	print play.result
			#	if play.down != 0 and play.result == RESULT_REPEAT_DOWN:
			#		play.down = 0
			#prevDown = play.down
			#prevResult = play.result
			
			i += 1
	
	def mergeDrives(self, nextDrive):
		if self.homePoss != nextDrive.homePoss:
			return False
		numPlays = len(self.plays)
		if numPlays == 0:
			# we shouldn't get here -- we should have already deleted this drive
			return False
		lastPlay = self.plays[numPlays-1]
		firstPlay = nextDrive.plays[0]
		lastQuarter = lastPlay.quarter
		nextQuarter = firstPlay.quarter
		if lastQuarter != nextQuarter:
			if lastQuarter+1 != nextQuarter:
				return False
			if lastQuarter != 1 and lastQuarter != 3:
				return False
		lastResult = lastPlay.result
		if lastResult == RESULT_TURNOVER_ON_DOWNS:
			return False
		if lastResult == RESULT_KICK_RECEIVED:
			return False
		if lastResult == RESULT_MISSED_FIELD_GOAL:
			return False
		if lastResult == RESULT_DEFENSIVE_TOUCHDOWN:
			return False
		if lastResult == RESULT_DEFENSIVE_SAFETY:
			return False
		if lastResult == RESULT_TOUCHBACK:
			return False
		if lastResult == RESULT_DEFENSIVE_TOUCHBACK:
			return False
		if lastResult == RESULT_TURNOVER:
			return False
		if lastResult == RESULT_DEFENSIVE_TURNOVER:
			return False
		if lastResult == RESULT_ADVANCE_DOWN:
			if lastPlay.events[0].eventType == EVENT_ONSIDE_KICK:
				return False
		# if we get here, we've weeded out all of the conditions
		# under which we shouldn't merge the drives,
		# so now it's ok to proceed
		self.plays.extend(nextDrive.plays)
		return True
	
	def printSelf(self):
		score = '[Score] ' + str(self.awayScore) + '-' + str(self.homeScore)
		print score
		summary = '[Drive] ' + self.teamPoss + ' : '
		if self.pointsThisDrive and self.defensivePointsThisDrive:
			summary += str(self.pointsThisDrive - self.defensivePointsThisDrive) + ' points, and '
		summary += str(self.firstDownsThisDrive) + ' first downs.'
		print summary

class Play:
	
	def __init__(self, qtr, dn, dist, yd):
		self.quarter = qtr
		self.down = dn
		self.distance = dist
		self.startingYard = yd
		self.endingYard = None
		self.body = None
		self.events = []
		self.pointsThisPlay = None
		self.result = RESULT_NONE
	
	def didChangePoss(self, event = None):
		defensivePoss = False
		numEvents = len(self.events)
		if numEvents == 0:
			return defensivePoss
		if event == None:
			event = self.events[numEvents-1]
		justChanged = False
		i = 0
		while i < numEvents:
			e = self.events[i]
			if (e.eventType == EVENT_RETURN) and not justChanged:
				defensivePoss = not defensivePoss
			justChanged = False
			if e.eventType == EVENT_KICKOFF:
				defensivePoss = True
				justChanged = True
			elif e.eventType == EVENT_PUNT:
				defensivePoss = True
				justChanged = True
			elif e.eventType == EVENT_INTERCEPTION:
				defensivePoss = True
				justChanged = True
			elif e.eventType == EVENT_RECOVERY_DEFENSE:
				defensivePoss = not defensivePoss
				justChanged = True
			if e == event:
				return defensivePoss
			i += 1
		return defensivePoss
	
	def duringReturn(self, event):
		defensivePoss = False
		numEvents = len(self.events)
		i = 0
		while i < numEvents:
			e = self.events[i]
			if e.eventType == EVENT_RETURN:
				defensivePoss = True
			if e == event:
				return defensivePoss
			if e.eventType == EVENT_KICKOFF:
				defensivePoss = True
			elif e.eventType == EVENT_PUNT:
				defensivePoss = True
			elif e.eventType == EVENT_INTERCEPTION:
				defensivePoss = True
			elif e.eventType == EVENT_RECOVERY_DEFENSE:
				defensivePoss = True
			i += 1
		return defensivePoss
	
	def fieldReversed(self, event):
		fieldReversed = False
		changedPoss = False
		numEvents = len(self.events)
		i = 0
		while i < numEvents:
			e = self.events[i]
			if e.eventType == EVENT_RETURN:
				fieldReversed = not fieldReversed
				changedPoss = False
			if e == event:
				break
			changedPoss = False
			if e.eventType == EVENT_KICKOFF:
				changedPoss = True
			elif e.eventType == EVENT_PUNT:
				changedPoss = True
			elif e.eventType == EVENT_INTERCEPTION:
				changedPoss = True
			elif e.eventType == EVENT_RECOVERY_DEFENSE:
				changedPoss = True
			i += 1
		if changedPoss:
			fieldReversed = not fieldReversed
		return fieldReversed
	
	def eliminateNullEvents(self):
		numEvents = len(self.events)
		i = 0
		while i < numEvents:
			event = self.events[i]
			if event.eventType == EVENT_NULL:
				del self.events[i]
				numEvents -= 1
			else:
				i += 1
	
	def calcResults(self, nextPlaySamePoss):
		numEvents = len(self.events)
		lastRecovery = -1
		onsideKick = False
		i = 0
		while i < numEvents:
			event = self.events[i]
			event.formatNames()
			if event.eventType == EVENT_RECOVERY:
				lastRecovery = i
				print 'unknown recovery = ' + self.body
			elif event.eventType == EVENT_ONSIDE_KICK:
				onsideKick = True
			i += 1
		
		if lastRecovery > -1:
			event = self.events[lastRecovery]
			if nextPlaySamePoss is self.didChangePoss():
				print 'found our way here; result = ' + resultString(self.result)
				#if nextPlaySamePoss:
				#	print 'next play same poss'
				#print 'numReturns = ' + str(numReturns)
				#print 'body = ' + self.body
				#print resultString(self.result)
				# defensive team recovers
				if self.result == RESULT_TOUCHDOWN:
					self.result = RESULT_DEFENSIVE_TOUCHDOWN
				elif self.result == RESULT_DEFENSIVE_TOUCHDOWN:
					self.result = RESULT_TOUCHDOWN
				elif self.result == RESULT_SAFETY:
					self.result = RESULT_DEFENSIVE_SAFETY
				elif self.result == RESULT_DEFENSIVE_SAFETY:
					self.result = RESULT_SAFETY
				elif self.result == RESULT_TOUCHBACK:
					self.result = RESULT_DEFENSIVE_TOUCHBACK
				elif self.result == RESULT_DEFENSIVE_TOUCHBACK:
					self.result = RESULT_TOUCHBACK
				elif self.result == RESULT_TURNOVER:
					self.result = RESULT_DEFENSIVE_TURNOVER
				elif self.result == RESULT_KICK_RECEIVED:
					self.result = RESULT_DEFENSIVE_TURNOVER
				elif self.result == RESULT_ADVANCE_DOWN and onsideKick:
					self.result = RESULT_KICK_RECEIVED
				else:
					self.result = RESULT_TURNOVER
				print 'new result = ' + resultString(self.result)
				#print resultString(self.result)
				event.eventType = EVENT_RECOVERY_DEFENSE
			else:
				event.eventType = EVENT_RECOVERY_OFFENSE
		
		# don't allow non-numerical distances
		if self.distance == 'Goal' and self.startingYard != None:
			self.distance = 100 - self.startingYard
		
		# set the number of points for this play
		if self.result == RESULT_TOUCHDOWN or self.result == RESULT_DEFENSIVE_TOUCHDOWN:
			if self.down == -1:
				self.pointsThisPlay = 2
			else:
				self.pointsThisPlay = 6
			if self.result == RESULT_TOUCHDOWN:
				self.endingYard = 100
			else:
				self.endingYard = 0
		elif self.result == RESULT_FIELD_GOAL:
			if self.down == -1:
				self.pointsThisPlay = 1
			else:
				self.pointsThisPlay = 3
			self.endingYard = 100
		elif self.result == RESULT_SAFETY or self.result == RESULT_DEFENSIVE_SAFETY:
			if self.down == -1:
				self.pointsThisPlay = 1
			else:
				self.pointsThisPlay = 2
			if self.result == RESULT_SAFETY:
				self.endingYard = 0
			else:
				self.endingYard = 100
		else:
			self.pointsThisPlay = 0
		
		if numEvents > 0:
			firstEvent = self.events[0]
			if firstEvent.startingYard:
				self.startingYard = firstEvent.startingYard
				if self.pointsThisPlay == 0:
					lastEvent = self.events[numEvents-1]
					if self.fieldReversed(lastEvent) and lastEvent.endingYard:
						self.endingYard = 100 - lastEvent.endingYard
					else:
						self.endingYard = lastEvent.endingYard
		
		if self.endingYard == 100 and self.down != -1:
			if self.result != RESULT_TOUCHDOWN and self.result != RESULT_DEFENSIVE_SAFETY and self.result != RESULT_FIELD_GOAL:
				#self.printSelf()
				self.result = RESULT_TOUCHBACK
		if self.endingYard == 0 and self.down != -1:
			if self.result != RESULT_DEFENSIVE_TOUCHDOWN and self.result != RESULT_SAFETY:
				#self.printSelf()
				self.result = RESULT_DEFENSIVE_TOUCHBACK
	
	def playResult(self):
		return resultString(self.result)
	
	def printSelf(self):
   		string = '[Play] Q' + str(self.quarter) + ', Dn ' + str(self.down) + ', Dist ' + str(self.distance)
   		string2 = ' @ ' + str(self.startingYard) + 'Y to ' + str(self.endingYard) + 'Y - '
   		string3 = resultString(self.result) + ' scoring ' + str(self.pointsThisPlay) + ' points'
   		print string + string2 + string3
		#situation = '[Play] Dn: ' + str(self.down) + ', Dist: ' + str(self.distance) + ', Yd: ' + str(self.startingYard)
		#play = self.playResult() + ' for ' + str(self.endingYard - self.startingYard) + ' yards and ' + str(self.pointsThisPlay) + ' points.'
		#print situation + ' ' + play
	
	def outputSelf(self, f, i):
		if self.playType == EVENT_NULL:
			return
		kickingPlay = False
		if self.playType == EVENT_KICKOFF or self.playType == EVENT_FIELD_GOAL_ATTEMPT or self.playType == EVENT_PUNT:
			kickingPlay = True
		nextPlay = self.nextPlay
		# ID
		# play num
		f.write(str(i) + "\t")
		# quarter
		f.write(str(self.quarter) + "\t")
		# road team name
		if self.homePoss:
			f.write(self.teamDef + "\t")
		else:
			f.write(self.teamPoss + "\t")
		# road score
		f.write(str(self.awayScore) + "\t")
		# road team off/def
		if self.homePoss:
			f.write("Def\t")
		else:
			f.write("Off\t")
		# home team name
		if self.homePoss:
			f.write(self.teamPoss + "\t")
		else:
			f.write(self.teamDef + "\t")
		# home score
		f.write(str(self.homeScore) + "\t")
		# home team off/def
		if self.homePoss:
			f.write("Off\t")
		else:
			f.write("Def\t")
		# offense team name
		f.write(self.teamPoss + "\t")
		# defense team name
		f.write(self.teamDef + "\t")
		# leading team name
		# trailing team name
		if self.homeScore > self.awayScore:
			if self.homePoss:
				f.write(self.teamPoss + "\t" + self.teamDef + "\t")
			else:
				f.write(self.teamDef + "\t" + self.teamPoss + "\t")
		elif self.homeScore < self.awayScore:
			if self.homePoss:
				f.write(self.teamDef + "\t" + self.teamPoss + "\t")
			else:
				f.write(self.teamPoss + "\t" + self.teamDef + "\t")
		else:
			f.write("Tie\tTie\t")
		# possible points
		f.write(str(self.pointsThisDrive) + "\t")
		# QB name
		if not kickingPlay:
			f.write(self.offense1 + "\t")
		else:
			f.write("\t")
		# down
		f.write(str(self.down) + "\t")
		# distance
		f.write(str(self.distance) + "\t")
		# yardline
		f.write(str(self.startingYard) + "\t")
		# run/pass
		if self.playType == EVENT_KICKOFF:
			f.write("KICKOFF\t")
		elif self.playType == EVENT_RUSH:
			f.write("Run\t")
		elif self.playType == EVENT_PASS:
			f.write("Pass\t")
		elif self.playType == EVENT_FIELD_GOAL_ATTEMPT:
			if self.tryDown:
				f.write("EP\t")
			else:
				f.write("FG\t")
		elif self.playType == EVENT_PUNT:
			f.write("PUNT\t")
		elif self.playType == EVENT_SACK:
			f.write("Sack\t")
		elif self.playType == EVENT_PENALTY:
			f.write("PENALTY\t")
		# player name
		if not kickingPlay:
			f.write(self.offense2 + "\t")
		else:
			f.write("\t")
		# yards
		if not kickingPlay:
			f.write(str(self.endingYard - self.startingYard) + "\t")
		else:
			f.write("\t")
		# tackler name 1
		# tackler name 2
		if not (kickingPlay or self.fumble or self.interception):
			f.write(self.defense1 + "\t" + self.defense2 + "\t")
		else:
			f.write("\t\t")
		# result
		if self.tryDown:
			if self.playType == EVENT_FIELD_GOAL_ATTEMPT:
				if self.fieldGoal:
					f.write("EP\t")
				elif self.block:
					if nextPlay and nextPlay.playType == EVENT_RETURN and nextPlay.touchdown:
						f.write("EP BLOCKED RETURN TD\t")
					else:
						f.write("EP BLOCKED\t")
				else:
					f.write("EP MISSED\t")
			elif self.touchdown:
				f.write("2 PT CONVERSION\t")
			else:
				f.write("2 PT CONVERSION FAILED\t")
		if self.interception:
			if nextPlay and nextPlay.playType == EVENT_RETURN and nextPlay.touchdown:
				f.write("INTERCEPTION RETURN TD\t")
			else:
				f.write("INTERCEPTION\t")
		elif self.fumble:
			if nextPlay and nextPlay.playType == EVENT_RETURN and nextPlay.touchdown:
				f.write("FUMBLE RETURN TD\t")
			else:
				f.write("FUMBLE\t")
		elif self.touchdown:
			f.write("TOUCHDOWN\t")
		elif self.safety:
			f.write("SAFETY\t")
		elif self.touchback:
			f.write("TOUCHBACK\t")
		elif self.playType == EVENT_FIELD_GOAL_ATTEMPT:
			if self.fieldGoal:
				f.write("FG\t")
			elif self.block:
				if nextPlay and nextPlay.playType == EVENT_RETURN and nextPlay.touchdown:
					f.write("FG BLOCKED RETURN TD\t")
				else:
					f.write("FG BLOCKED\t")
			else:
				f.write("FG MISSED\t")
		elif self.playType == EVENT_PUNT:
			if self.block:
				if nextPlay and nextPlay.playType == EVENT_RETURN and nextPlay.touchdown:
					f.write("PUNT BLOCKED RETURN TD\t")
				else:
					f.write("PUNT BLOCKED\t")
			else:
				f.write("PUNT\t")
		else:
			f.write("\t")
		# kicker
		if kickingPlay:
			f.write(self.offense1 + "\t")
		else:
			f.write("\t")
		# kick yards
		if self.playType == EVENT_KICKOFF or self.playType == EVENT_PUNT:
			f.write(str(self.endingYard - self.startingYard) + "\t")
		else:
			f.write("\t")
		# returner
		if kickingPlay and nextPlay and nextPlay.playType == EVENT_RETURN:
			f.write(nextPlay.offense2 + "\t")
		else:
			f.write("\t")
		# return yards
		if kickingPlay and nextPlay and nextPlay.playType == EVENT_RETURN:
			f.write(str(nextPlay.endingYard - nextPlay.startingYard) + "\t")
		else:
			f.write("\t")
		# net kick yards
		if kickingPlay:
			kickYards = self.endingYard - self.startingYard
			if nextPlay and nextPlay.playType == EVENT_RETURN:
				returnYards = nextPlay.endingYard - nextPlay.startingYard
			elif self.touchback:
				returnYards = 20
			else:
				returnYards = 0
			if self.playType == EVENT_KICKOFF or self.playType == EVENT_PUNT or returnYards != 0:
				f.write(str(kickYards - returnYards) + "\t")
			else:
				f.write("\t")
		else:
			f.write("\t")
		# fumble forced name
		# fumble return name
		if self.fumble:
			f.write(self.defense1 + "\t" + self.defense2 + "\t")
		else:
			f.write("\t\t")
		# interception name
		if self.interception:
			f.write(self.defense1 + "\t")
		else:
			f.write("\t")
		# game margin
		# close?
		margin = abs(self.homeScore - self.awayScore)
		f.write(str(margin) + "\t")
		if margin < 17:
			f.write("Close\t")
		else:
			f.write("\t")
		# success?
		# line yards
		# pressure?
		# down yardage
		# passing down
		# red zone
		# special teams?
		# special team points
		# turnover?
		# point value
		# conference game?
		# date
		# month
		
		f.write("\n")

class Event:
	
	def __init__(self):
		self.startingYard = None
		self.endingYard = None
		self.offense1 = None
		self.offense2 = None
		self.defense1 = None
		self.defense2 = None
		self.eventType = EVENT_NULL
	
	def formatNames(self):
		if self.offense1:
			commaLoc = self.offense1.find(',')
			if commaLoc != -1:
				self.offense1 = self.offense1[commaLoc+1:].strip() + ' ' + self.offense1[0:commaLoc].strip()
			#if self.offense1 != '':
			#	print self.offense1
		if self.offense2:
			commaLoc = self.offense2.find(',')
			if commaLoc != -1:
				self.offense2 = self.offense2[commaLoc+1:].strip() + ' ' + self.offense2[0:commaLoc].strip()
			#if self.offense2 != '':
			#	print self.offense2
		if self.defense1:
			commaLoc = self.defense1.find(',')
			if commaLoc != -1:
				self.defense1 = self.defense1[commaLoc+1:].strip() + ' ' + self.defense1[0:commaLoc].strip()
			#if self.defense1 != '':
			#	print self.defense1
		if self.defense2:
			commaLoc = self.defense2.find(',')
			if commaLoc != -1:
				self.defense2 = self.defense2[commaLoc+1:].strip() + ' ' + self.defense2[0:commaLoc].strip()
			#if self.defense2 != '':
			#	print self.defense2
	
	def eventString(self):
		return eventString(self.eventType)
	
	def printSelf(self):
		if self.eventType == EVENT_NULL:
			print 'Null event.'
			return
		if self.startingYard and self.endingYard:
			event = '[Event] ' + self.eventString() + ' for ' + str(self.endingYard - self.startingYard) + ' yards'
			print event
			#print str(self.endingYard) + ' - ' + str(self.startingYard)

def teamCodeOld(teamName):
	if teamName == 'Air Force':
		return 1
	elif teamName == 'Akron':
		return 2
	elif teamName == 'Alabama':
		return 3
	elif teamName == 'Arizona':
		return 4
	elif teamName == 'Arizona St' or teamName == 'Arizona State':
		return 5
	elif teamName == 'Arkansas':
		return 6
	elif teamName == 'Arkansas St' or teamName == 'Arkansas State':
		return 7
	elif teamName == 'Army':
		return 8
	elif teamName == 'Auburn':
		return 9
	elif teamName == 'Ball St' or teamName == 'Ball State':
		return 10
	elif teamName == 'Baylor':
		return 11
	elif teamName == 'Boise St' or teamName == 'Boise State':
		return 12
	elif teamName == 'Boston College':
		return 13
	elif teamName == 'Bowling Green':
		return 14
	elif teamName == 'Buffalo':
		return 15
	elif teamName == 'Brigham Young' or teamName == 'BYU':
		return 16
	elif teamName == 'California' or teamName == 'Cal':
		return 17
	elif teamName == 'Central Michigan':
		return 18
	elif teamName == 'Cincinnati':
		return 19
	elif teamName == 'Clemson':
		return 20
	elif teamName == 'Colorado':
		return 21
	elif teamName == 'Colorado St' or teamName == 'Colorado State':
		return 22
	elif teamName == 'Connecticut':
		return 23
	elif teamName == 'Duke':
		return 24
	elif teamName == 'East Carolina':
		return 25
	elif teamName == 'Eastern Michigan':
		return 26
	elif teamName == 'FAU' or teamName == 'Florida Atlantic':
		return 27
	elif teamName == 'Florida':
		return 28
	elif teamName == 'FIU' or teamName == 'Florida International':
		return 29
	elif teamName == 'Florida St' or teamName == 'Florida State':
		return 30
	elif teamName == 'Fresno St' or teamName == 'Fresno State':
		return 31
	elif teamName == 'Georgia':
		return 32
	elif teamName == 'Georgia Tech':
		return 33
	elif teamName == 'Hawaii':
		return 34
	elif teamName == 'Houston':
		return 35
	elif teamName == 'Idaho':
		return 36
	elif teamName == 'Illinois':
		return 37
	elif teamName == 'Indiana':
		return 38
	elif teamName == 'Iowa':
		return 39
	elif teamName == 'Iowa St' or teamName == 'Iowa State':
		return 40
	elif teamName == 'Kansas':
		return 41
	elif teamName == 'Kansas St' or teamName == 'Kansas State':
		return 42
	elif teamName == 'Kent St' or teamName == 'Kent State':
		return 43
	elif teamName == 'Kentucky':
		return 44
	elif teamName == 'Louisiana-Lafayette' or teamName == 'UL Lafayette':
		return 45
	elif teamName == 'Louisiana-Monroe' or teamName == 'UL Monroe':
		return 46
	elif teamName == 'Louisiana Tech':
		return 47
	elif teamName == 'Louisville':
		return 48
	elif teamName == 'LSU' or teamName == 'Louisiana St' or teamName == 'Louisiana State':
		return 49
	elif teamName == 'Marshall':
		return 50
	elif teamName == 'Maryland':
		return 51
	elif teamName == 'Memphis':
		return 52
	elif teamName == 'Miami (FL)':
		return 53
	elif teamName == 'Miami (OH)':
		return 54
	elif teamName == 'Michigan':
		return 55
	elif teamName == 'Michigan St' or teamName == 'Michigan State':
		return 56
	elif teamName == 'Middle Tennessee St' or teamName == 'Middle Tennessee State':
		return 57
	elif teamName == 'Minnesota':
		return 58
	elif teamName == 'Mississippi':
		return 59
	elif teamName == 'Mississippi St' or teamName == 'Mississippi State':
		return 60
	elif teamName == 'Missouri':
		return 61
	elif teamName == 'Navy':
		return 62
	elif teamName == 'Nebraska':
		return 63
	elif teamName == 'Nevada':
		return 64
	elif teamName == 'New Mexico':
		return 65
	elif teamName == 'New Mexico St' or teamName == 'New Mexico State':
		return 66
	elif teamName == 'North Carolina':
		return 67
	elif teamName == 'North Carolina St' or teamName == 'North Carolina State':
		return 68
	elif teamName == 'North Texas':
		return 69
	elif teamName == 'Northern Illinois':
		return 70
	elif teamName == 'Northwestern':
		return 71
	elif teamName == 'Notre Dame':
		return 72
	elif teamName == 'Ohio':
		return 73
	elif teamName == 'Ohio St' or teamName == 'Ohio State':
		return 74
	elif teamName == 'Oklahoma':
		return 75
	elif teamName == 'Oklahoma St' or teamName == 'Oklahoma State':
		return 76
	elif teamName == 'Oregon':
		return 77
	elif teamName == 'Oregon St' or teamName == 'Oregon State':
		return 78
	elif teamName == 'Penn St' or teamName == 'Penn State':
		return 79
	elif teamName == 'Pittsburgh':
		return 80
	elif teamName == 'Purdue':
		return 81
	elif teamName == 'Rice':
		return 82
	elif teamName == 'Rutgers':
		return 83
	elif teamName == 'San Diego St' or teamName == 'San Diego State':
		return 84
	elif teamName == 'San Jose St' or teamName == 'San Jose State':
		return 85
	elif teamName == 'SMU' or teamName == 'Southern Methodist':
		return 86
	elif teamName == 'South Carolina':
		return 87
	elif teamName == 'South Florida':
		return 88
	elif teamName == 'USC' or teamName == 'Southern California':
		return 89
	elif teamName == 'Southern Miss':
		return 90
	elif teamName == 'Stanford':
		return 91
	elif teamName == 'Syracuse':
		return 92
	elif teamName == 'TCU' or teamName == 'Texas Christian':
		return 93
	elif teamName == 'Temple':
		return 94
	elif teamName == 'Tennessee':
		return 95
	elif teamName == 'Texas':
		return 96
	elif teamName == 'Texas A&M':
		return 97
	elif teamName == 'Texas Tech':
		return 98
	elif teamName == 'Toledo':
		return 99
	elif teamName == 'Troy':
		return 100
	elif teamName == 'Tulane':
		return 101
	elif teamName == 'Tulsa':
		return 102
	elif teamName == 'UAB':
		return 103
	elif teamName == 'UCF':
		return 104
	elif teamName == 'UCLA':
		return 105
	elif teamName == 'UNLV':
		return 106
	elif teamName == 'Utah':
		return 107
	elif teamName == 'Utah St' or teamName == 'Utah State':
		return 108
	elif teamName == 'UTEP':
		return 109
	elif teamName == 'Vanderbilt':
		return 110
	elif teamName == 'Virginia':
		return 111
	elif teamName == 'Virginia Tech':
		return 112
	elif teamName == 'Wake Forest':
		return 113
	elif teamName == 'Washington':
		return 114
	elif teamName == 'Washington St' or teamName == 'Washington State':
		return 115
	elif teamName == 'West Virginia':
		return 116
	elif teamName == 'Western Kentucky':
		return 117
	elif teamName == 'Western Michigan':
		return 118
	elif teamName == 'Wisconsin':
		return 119
	elif teamName == 'Wyoming':
		return 120
	else:
		print 'Team name = ' + teamName
		return -1

TEAMS = {
	1 : ['Air Force'],
	2 : ['Akron'],
	3 : ['Alabama'],
	4 : ['Arizona'],
	5 : ['Arizona State', 'Arizona St'],
	6 : ['Arkansas'],
	7 : ['Arkansas State', 'Arkansas St'],
	8 : ['Army'],
	9 : ['Auburn'],
	10 : ['Ball State', 'Ball St'],
	11 : ['Baylor'],
	12 : ['Boise State', 'Boise St'],
	13 : ['Boston College'],
	14 : ['Bowling Green'],
	15 : ['Buffalo'],
	16 : ['Brigham Young', 'BYU'],
	17 : ['California', 'Cal'],
	18 : ['Central Michigan'],
	19 : ['Cincinnati'],
	20 : ['Clemson'],
	21 : ['Colorado'],
	22 : ['Colorado State', 'Colorado St'],
	23 : ['Connecticut'],
	24 : ['Duke'],
	25 : ['East Carolina'],
	26 : ['Eastern Michigan'],
	27 : ['Florida Atlantic', 'FAU'],
	28 : ['Florida'],
	29 : ['Florida International', 'FIU'],
	30 : ['Florida State', 'Florida St'],
	31 : ['Fresno State', 'Fresno St'],
	32 : ['Georgia'],
	33 : ['Georgia Tech'],
	34 : ['Hawaii'],
	35 : ['Houston'],
	36 : ['Idaho'],
	37 : ['Illinois'],
	38 : ['Indiana'],
	39 : ['Iowa'],
	40 : ['Iowa State', 'Iowa St'],
	41 : ['Kansas'],
	42 : ['Kansas State', 'Kansas St'],
	43 : ['Kent State', 'Kent St'],
	44 : ['Kentucky'],
	45 : ['Louisiana-Lafayette', 'UL Lafayette'],
	46 : ['Louisiana-Monroe', 'UL Monroe'],
	47 : ['Louisiana Tech'],
	48 : ['Louisville'],
	49 : ['Louisiana State', 'LSU'],
	50 : ['Marshall'],
	51 : ['Maryland'],
	52 : ['Memphis'],
	53 : ['Miami (FL)', 'Miami'],
	54 : ['Miami (OH)'],
	55 : ['Michigan'],
	56 : ['Michigan State', 'Michigan St'],
	57 : ['Middle Tennessee State', 'Middle Tennessee St'],
	58 : ['Minnesota'],
	59 : ['Mississippi', 'Ole Miss'],
	60 : ['Mississippi State', 'Mississippi St'],
	61 : ['Missouri'],
	62 : ['Navy'],
	63 : ['Nebraska'],
	64 : ['Nevada'],
	65 : ['New Mexico'],
	66 : ['New Mexico State', 'New Mexico St'],
	67 : ['North Carolina'],
	68 : ['North Carolina State', 'North Carolina St', 'N.C. State', 'NC State'],
	69 : ['North Texas'],
	70 : ['Northern Illinois'],
	71 : ['Northwestern'],
	72 : ['Notre Dame'],
	73 : ['Ohio'],
	74 : ['Ohio State', 'Ohio St'],
	75 : ['Oklahoma'],
	76 : ['Oklahoma State', 'Oklahoma St'],
	77 : ['Oregon'],
	78 : ['Oregon State', 'Oregon St'],
	79 : ['Penn State', 'Penn St'],
	80 : ['Pittsburgh'],
	81 : ['Purdue'],
	82 : ['Rice'],
	83 : ['Rutgers'],
	84 : ['San Diego State', 'San Diego St'],
	85 : ['San Jose State', 'San Jose St'],
	86 : ['Southern Methodist'],
	87 : ['South Carolina'],
	88 : ['South Florida'],
	89 : ['Southern California', 'USC'],
	90 : ['Southern Miss'],
	91 : ['Stanford'],
	92 : ['Syracuse'],
	93 : ['Texas Christian', 'TCU'],
	94 : ['Temple'],
	95 : ['Tennessee'],
	96 : ['Texas'],
	97 : ['Texas A&M', 'Texas A+M'],
	98 : ['Texas Tech'],
	99 : ['Toledo'],
	100 : ['Troy'],
	101 : ['Tulane'],
	102 : ['Tulsa'],
	103 : ['UAB'],
	104 : ['UCF', 'Central Florida'],
	105 : ['UCLA'],
	106 : ['UNLV'],
	107 : ['Utah'],
	108 : ['Utah State', 'Utah St'],
	109 : ['UTEP'],
	110 : ['Vanderbilt'],
	111 : ['Virginia'],
	112 : ['Virginia Tech'],
	113 : ['Wake Forest'],
	114 : ['Washington'],
	115 : ['Washington State', 'Washington St'],
	116 : ['West Virginia'],
	117 : ['Western Kentucky'],
	118 : ['Western Michigan'],
	119 : ['Wisconsin'],
	120 : ['Wyoming']
}


def teamCode(teamName):
	teamName = teamName.strip('.')
	for code, names in TEAMS.items():
		if teamName in names:
			return code
	return -1

def teamName(teamCode):
	return TEAMS[teamCode][0]

def venueCode(venueName, cityName):
	if venueName == 'Falcon Stadium' and cityName == 'UNITED STATES AF ACA, CO':
		return 1
	elif venueName == 'Rubber Bowl' and cityName == 'AKRON, OH':
		return 2
	elif venueName == 'Bryant-Denny Stadium' and cityName == 'TUSCALOOSA, AL':
		return 3
	elif venueName == 'Arizona Stadium' and cityName == 'TUCSON, AZ':
		return 4
	elif venueName == 'Sun Devil Stadium' and cityName == 'TEMPE, AZ':
		return 5
	elif venueName == 'Razorback Stadium' and cityName == 'FAYETTEVILLE, AR':
		return 6
	elif venueName == 'ASU STADIUM' and cityName == 'JONESBORO, AR':
		return 7
	elif venueName == 'Michie Stadium' and cityName == 'WEST POINT, NY':
		return 8
	elif venueName == 'Jordan-Hare Stadium' and cityName == 'AUBURN, AL':
		return 9
	elif venueName == 'Scheumann Stadium' and cityName == 'MUNCIE, IN':
		return 10
	elif venueName == 'Floyd Casey Stadium' and cityName == 'WACO, TX':
		return 11
	elif venueName == 'Bronco Stadium' and cityName == 'BOISE, ID':
		return 12
	elif venueName == 'Alumni Stadium' and cityName == 'CHESTNUT HILL, MA':
		return 13
	elif venueName == 'Perry Stadium' and cityName == 'BOWLING GREEN, OH':
		return 14
	elif venueName == 'UB Stadium' and cityName == 'BUFFALO, NY':
		return 15
	elif venueName == 'LaVell Edwards Stadium' and cityName == 'PROVO, UT':
		return 16
	elif venueName == 'Memorial Stadium' and cityName == 'BERKELEY, CA':
		return 17
	elif venueName == 'Kelly/Shorts Stadium' and cityName == 'MOUNT PLEASANT, MI':
		return 18
	elif venueName == 'Nippert Stadium' and cityName == 'CINCINNATI, OH':
		return 19
	elif venueName == 'Memorial Stadium' and cityName == 'CLEMSON, SC':
		return 20
	elif venueName == 'Folsom Field' and cityName == 'BOULDER, CO':
		return 21
	elif venueName == 'Hughes Stadium' and cityName == 'FORT COLLINS, CO':
		return 22
	elif venueName == 'Rentschler Field' and cityName == 'EAST HARTFORD, CT':
		return 23
	elif venueName == 'Wallace Wade Stadium' and cityName == 'DURHAM, NC':
		return 24
	elif venueName == 'Dowdy-Ficklen Stadium' and cityName == 'GREENVILLE, NC':
		return 25
	elif venueName == 'Rynearson Stadium' and cityName == 'YPSILANTI, MI':
		return 26
	elif venueName == 'Lockhart Stadium' and cityName == 'FORT LAUDERDALE, FL':
		return 27
	elif venueName == 'BEN HILL GRIFFIN STADIUM' and cityName == 'GAINESVILLE, FL':
		return 28
	elif venueName == 'FIU Stadium' and cityName == 'MIAMI, FL':
		return 29
	elif venueName == 'Doak Campbell Stadium' and cityName == 'TALLAHASSEE, FL':
		return 30
	elif venueName == 'Bulldog Stadium' and cityName == 'FRESNO, CA':
		return 31
	elif venueName == 'Sanford Stadium' and cityName == 'ATHENS, GA':
		return 32
	elif venueName == 'Bobby Dodd Stadium' and cityName == 'ATLANTA, GA':
		return 33
	elif venueName == 'Aloha Stadium' and cityName == 'HONOLULU, HI':
		return 34
	elif venueName == 'Robertson Stadium' and cityName == 'HOUSTON, TX':
		return 35
	elif venueName == 'Kibbie Dome' and cityName == 'MOSCOW, ID':
		return 36
	elif venueName == 'Memorial Stadium' and cityName == 'CHAMPAIGN, IL':
		return 37
	elif venueName == 'Memorial Stadium' and cityName == 'BLOOMINGTON, IN':
		return 38
	elif venueName == 'Jack Trice Stadium' and cityName == 'AMES, IA':
		return 39
	elif venueName == 'Kinnick Stadium' and cityName == 'IOWA CITY, IA':
		return 40
	elif venueName == 'Memorial Stadium' and cityName == 'LAWRENCE, KS':
		return 41
	elif venueName == 'Bill Snyder Stadium' and cityName == 'MANHATTAN, KS':
		return 42
	elif venueName == 'Dix Stadium' and cityName == 'KENT, OH':
		return 43
	elif venueName == 'Commonwealth Stadium' and cityName == 'LEXINGTON, KY':
		return 44
	elif venueName == 'Cajun Field' and cityName == 'LAFAYETTE, LA':
		return 45
	elif venueName == 'Malone Stadium' and cityName == 'MONROE, LA':
		return 46
	elif venueName == 'Joe Aillet Stadium' and cityName == 'RUSTON, LA':
		return 47
	elif venueName == "Papa John's Cardinal Stadium' and cityName == 'LOUISVILLE, KY":
		return 48
	elif venueName == 'Tiger Stadium' and cityName == 'BATON ROUGE, LA':
		return 49
	elif venueName == 'Edwards Stadium' and cityName == 'HUNTINGTON, WV':
		return 50
	elif venueName == 'Byrd Stadium' and cityName == 'COLLEGE PARK, MD':
		return 51
	elif venueName == 'Liberty Bowl' and cityName == 'MEMPHIS, TN':
		return 52
	elif venueName == 'Sun Life Stadium' and cityName == 'MIAMI, FL':
		return 53
	elif venueName == 'Yager Stadium' and cityName == 'OXFORD, OH':
		return 54
	elif venueName == 'Michigan Stadium' and cityName == 'ANN ARBOR, MI':
		return 55
	elif venueName == 'Spartan Stadium' and cityName == 'EAST LANSING, MI':
		return 56
	elif venueName == 'Floyd Stadium' and cityName == 'MURFREESBORO, TN':
		return 57
	elif venueName == 'The Metrodome' and cityName == 'MINNEAPOLIS, MN':
		return 58
	elif venueName == 'Vaught-Hemingway Stadium' and cityName == 'OXFORD, MS':
		return 59
	elif venueName == 'Davis Wade Stadium' and cityName == 'STARKVILLE, MS':
		return 60
	elif venueName == 'Faurot Field' and cityName == 'COLUMBIA, MO':
		return 61
	elif venueName == 'Navy Memorial Stadium' and cityName == 'ANNAPOLIS, MD':
		return 62
	elif venueName == 'Memorial Stadium' and cityName == 'LINCOLN, NE':
		return 63
	elif venueName == 'Mackay Stadium' and cityName == 'RENO, NV':
		return 64
	elif venueName == 'University Stadium' and cityName == 'ALBUQUERQUE, NM':
		return 65
	elif venueName == 'Aggie Memorial Stadium' and cityName == 'LAS CRUCES, NM':
		return 66
	elif venueName == 'Kenan Stadium' and cityName == 'CHAPEL HILL, NC':
		return 67
	elif venueName == 'Carter-Finley Stadium' and cityName == 'RALEIGH, NC':
		return 68
	elif venueName == 'Fouts Field' and cityName == 'DENTON, TX':
		return 69
	elif venueName == 'Huskie Stadium' and cityName == 'DEKALB, IL':
		return 70
	elif venueName == 'Ryan Field' and cityName == 'EVANSTON, IL':
		return 71
	elif venueName == 'Notre Dame Stadium' and cityName == 'NOTRE DAME, IN':
		return 72
	elif venueName == 'Peden Stadium' and cityName == 'ATHENS, OH':
		return 73
	elif venueName == 'Ohio Stadium' and cityName == 'COLUMBUS, OH':
		return 74
	elif venueName == 'Oklahoma Memorial Stadium' and cityName == 'NORMAN, OK':
		return 75
	elif venueName == 'Boone Pickens Stadium' and cityName == 'STILLWATER, OK':
		return 76
	elif venueName == 'Autzen Stadium' and cityName == 'EUGENE, OR':
		return 77
	elif venueName == 'Reser Stadium' and cityName == 'CORVALLIS, OR':
		return 78
	elif venueName == 'Beaver Stadium' and cityName == 'UNIVERSITY PARK, PA':
		return 79
	elif venueName == 'Heinz Field' and cityName == 'PITTSBURGH, PA':
		return 80
	elif venueName == 'Ross-Ade Stadium' and cityName == 'WEST LAFAYETTE, IN':
		return 81
	elif venueName == 'Rice Stadium' and cityName == 'HOUSTON, TX':
		return 82
	elif venueName == 'Rutgers Stadium' and cityName == 'PISCATAWAY, NJ':
		return 83
	elif venueName == 'Qualcomm Stadium' and cityName == 'SAN DIEGO, CA':
		return 84
	elif venueName == 'SPARTAN STADIUM' and cityName == 'CA' and cityName == 'SAN JOSE, CA':
		return 85
	elif venueName == 'Gerald Ford Stadium' and cityName == 'DALLAS, TX':
		return 86
	elif venueName == 'Williams-Brice Stadium' and cityName == 'COLUMBIA, SC':
		return 87
	elif venueName == 'Raymond James Stadium' and cityName == 'TAMPA, FL':
		return 88
	elif venueName == 'Los Angeles Coliseum' and cityName == 'LOS ANGELES, CA':
		return 89
	elif venueName == 'M.M. Roberts Stadium' and cityName == 'HATTIESBURG, MS':
		return 90
	elif venueName == 'Stanford Stadium' and cityName == 'STANFORD, CA':
		return 91
	elif venueName == 'Carrier Dome' and cityName == 'SYRACUSE, NY':
		return 92
	elif venueName == 'Amon Carter Stadium' and cityName == 'FORT WORTH, TX':
		return 93
	elif venueName == 'Lincoln Financial Field' and cityName == 'PHILADELPHIA, PA':
		return 94
	elif venueName == 'Neyland Stadium' and cityName == 'KNOXVILLE, TN':
		return 95
	elif venueName == 'Royal-Texas Memorial Stadium' and cityName == 'AUSTIN, TX':
		return 96
	elif venueName == 'Kyle Field' and cityName == 'COLLEGE STATION, TX':
		return 97
	elif venueName == 'Jones AT&T Stadium' and cityName == 'LUBBOCK, TX':
		return 98
	elif venueName == 'Glass Bowl' and cityName == 'TOLEDO, OH':
		return 99
	elif venueName == 'Movie Gallery Veterans Stadium' and cityName == 'TROY, AL':
		return 100
	elif venueName == 'Superdome' and cityName == 'NEW ORLEANS, LA':
		return 101
	elif venueName == 'CHAPMAN STADIUM' and cityName == 'TULSA, OK':
		return 102
	elif venueName == 'Legion Field' and cityName == 'BIRMINGHAM, AL':
		return 103
	elif venueName == 'BH Networks Stadium' and cityName == 'ORLANDO, FL':
		return 104
	elif venueName == 'Rose Bowl' and cityName == 'PASADENA, CA':
		return 105
	elif venueName == 'Sam Boyd Stadium' and cityName == 'LAS VEGAS, NV':
		return 106
	elif venueName == 'Rice-Eccles Stadium' and cityName == 'SALT LAKE CITY, UT':
		return 107
	elif venueName == 'Romney Stadium' and cityName == 'LOGAN, UT':
		return 108
	elif venueName == 'Sun Bowl' and cityName == 'EL PASO, TX':
		return 109
	elif venueName == 'Vanderbilt Stadium' and cityName == 'NASHVILLE, TN':
		return 110
	elif venueName == 'Scott Stadium' and cityName == 'CHARLOTTESVILLE, VA':
		return 111
	elif venueName == 'Lane Stadium' and cityName == 'BLACKSBURG, VA':
		return 112
	elif venueName == 'GROVES STADIUM' and cityName == 'WINSTON-SALEM, NC':
		return 113
	elif venueName == 'Husky Stadium' and cityName == 'SEATTLE, WA':
		return 114
	elif venueName == 'Martin Stadium' and cityName == 'PULLMAN, WA':
		return 115
	elif venueName == 'Mountaineer Field' and cityName == 'MORGANTOWN, WV':
		return 116
	elif venueName == 'Smith Stadium' and cityName == 'BOWLING GREEN, KY':
		return 117
	elif venueName == 'Waldo Stadium' and cityName == 'KALAMAZOO, MI':
		return 118
	elif venueName == 'Camp Randall Stadium' and cityName == 'MADISON, WI':
		return 119
	elif venueName == 'War Memorial Stadium' and cityName == 'LARAMIE, WY':
		return 120
	else:
		print 'Team name = ' + venueName
		return -1
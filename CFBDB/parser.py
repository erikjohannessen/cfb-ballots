import gameDefs

Game = gameDefs.Game
Drive = gameDefs.Drive
Play = gameDefs.Play
Event = gameDefs.Event

def getPlay(game, drive, play, item, itemWNames):
	play.body = itemWNames
	gain = 0
	
	kickoffLoc = item.find(' kickoff')
	onsideLoc = item.find('on-side kick')
	fieldGoalLoc = item.find(' field goal')
	extraPointLoc = item.find(' extra point')
	if extraPointLoc == -1:
		extraPointLoc = item.find('blocked pat')
	
	##### parser2 changes #####
	
	if extraPointLoc == -1:
		extraPointLoc = item.find(' kick attempt')
	
	##### end parser2 changes #####
	
	puntLoc = item.find(' punt ')
	rushLoc = item.find(' rush ')
	sackLoc = item.find(' sacked')
	scrambleLoc = item.find(' scramble')
	passLoc = item.find(' pass ')
	recoverLoc = item.find(' recover')
	
	advanceLoc = -1
	returnLoc = item.find(' return')
	fumbleLoc = item.find(' fumble')
	lateralLoc = item.find(' lateral')
	penaltyLoc = item.find(' penalty')
	nextPlayLoc = len(item)
	if returnLoc != -1 and returnLoc < nextPlayLoc:
		nextPlayLoc = returnLoc
	if fumbleLoc != -1 and fumbleLoc < nextPlayLoc:
		nextPlayLoc = fumbleLoc
	if lateralLoc != -1 and lateralLoc < nextPlayLoc:
		nextPlayLoc = lateralLoc
	if penaltyLoc != -1 and penaltyLoc < nextPlayLoc:
		nextPlayLoc = penaltyLoc
	
	event = Event()
	event.startingYard = play.startingYard
	play.events.append(event)
	# extra point
	if extraPointLoc != -1:
		event.eventType = gameDefs.EVENT_FIELD_GOAL_ATTEMPT
		play.down = -1
		play.distance = 3
		play.startingYard = 97
		event.startingYard = 97
		kickerName = itemWNames[0:extraPointLoc]
		event.offense1 = kickerName.strip()
		if item.find('missed', extraPointLoc, nextPlayLoc) != -1:
			play.result = gameDefs.RESULT_MISSED_FIELD_GOAL
			event.endingYard = event.startingYard
		elif item.find('good', 0, nextPlayLoc) != -1:
			play.result = gameDefs.RESULT_FIELD_GOAL
			event.endingYard = 100
		elif item.find('blocked', extraPointLoc, nextPlayLoc) != -1:
			#print "EP BLOCKED - " + item
			play.result = gameDefs.RESULT_TURNOVER_ON_DOWNS
			getDefenderNames(event, item, itemWNames, extraPointLoc, len(item), 'blocked by ')
			# recovery
			nextEvent = getRecovery(drive, play, event, item, itemWNames, recoverLoc, nextPlayLoc)
			if nextEvent:
				event = nextEvent
			else:			
				event.endingYard = event.startingYard
	# two-point conversion
	elif item.find('conversion', 0, nextPlayLoc) != -1 or play.down == -1:
		#print "2PC - " + item
		play.down = -1
		play.distance = 3
		play.startingYard = 97
		event.startingYard = 97
		attemptLoc = item.find(' attempt,', 0, nextPlayLoc)
		passLoc = item.find(' pass ', 0, nextPlayLoc)
		rushLoc = item.find(' rush ', 0, nextPlayLoc)
		if item.find(' failed', 0, nextPlayLoc) != -1:
			play.result = gameDefs.RESULT_ADVANCE_DOWN
			if passLoc != -1:
				event.eventType = gameDefs.EVENT_PASS
				qbName = itemWNames[attemptLoc+9:passLoc]
				event.offense1 = qbName.strip()
			elif rushLoc != -1:
				event.eventType = gameDefs.EVENT_RUSH
				rusherName = itemWNames[attemptLoc+9:rushLoc]
				event.offense1 = rusherName.strip()
			play.endingYard = play.startingYard
		elif item.find(' good', 0, nextPlayLoc) != -1:
			play.result = gameDefs.RESULT_TOUCHDOWN
			if passLoc != -1:
				event.eventType = gameDefs.EVENT_PASS
				qbName = itemWNames[attemptLoc+9:passLoc]
				event.offense1 = qbName.strip()
				toLoc = item.find(' to ', attemptLoc, nextPlayLoc)
				goodLoc = item.find(' good', attemptLoc, nextPlayLoc)
				if toLoc != -1:
					receiverName = itemWNames[toLoc+4:goodLoc]
					event.offense2 = receiverName.strip()
			elif rushLoc != -1:
				event.eventType = gameDefs.EVENT_RUSH
				rusherName = itemWNames[attemptLoc+9:rushLoc]
				event.offense1 = rusherName.strip()
			event.endingYard = 100
	# field goal
	elif fieldGoalLoc != -1:
		event.eventType = gameDefs.EVENT_FIELD_GOAL_ATTEMPT
		i = 0
		while i <= fieldGoalLoc and not item[i].isdigit():
			i += 1
		kickerName = itemWNames[0:i-1]
		event.offense1 = kickerName.strip()
		if item.find('missed', fieldGoalLoc, nextPlayLoc) != -1:
			play.result = gameDefs.RESULT_MISSED_FIELD_GOAL
			if event.startingYard > 80:
				event.endingYard = 80
			else:
				event.endingYard = event.startingYard
		elif item.find('good', fieldGoalLoc, nextPlayLoc) != -1:
			play.result = gameDefs.RESULT_FIELD_GOAL
			event.endingYard = 100
		elif item.find('blocked', fieldGoalLoc, nextPlayLoc) != -1:
			play.result = gameDefs.RESULT_MISSED_FIELD_GOAL
			getDefenderNames(event, item, itemWNames, fieldGoalLoc, len(item), 'blocked by ')
			# recovery
			nextEvent = getRecovery(drive, play, event, item, itemWNames, recoverLoc, nextPlayLoc)
			if nextEvent:
				event = nextEvent
			else:			
				event.endingYard = event.startingYard
	# kickoff
	elif kickoffLoc != -1:
		event.eventType = gameDefs.EVENT_KICKOFF
		play.down = 0
		kickerName = itemWNames[0:kickoffLoc]
		event.offense1 = kickerName.strip()
		kickLength = getGain(drive, event, item[kickoffLoc+8:nextPlayLoc])
		if item.find('out-of-bounds', kickoffLoc, nextPlayLoc) != -1:
			if game.year == 2007:
				# except during 2007, when this number was 35
				event.endingYard = event.startingYard + 35 # usually 65
			else:
				event.endingYard = event.startingYard + 30 # usually 60 now, though was 65 before 2007
		else:
			event.endingYard = event.startingYard + kickLength
		play.result = gameDefs.RESULT_KICK_RECEIVED
	# on-side kick
	elif onsideLoc != -1:
		event.eventType = gameDefs.EVENT_ONSIDE_KICK
		play.down = 0
		kickerName = itemWNames[0:onsideLoc]
		event.offense1 = kickerName.strip()
		
		play.result = gameDefs.RESULT_ADVANCE_DOWN
		# recovery
		nextEvent = getRecovery(drive, play, event, item, itemWNames, recoverLoc, nextPlayLoc)
		if nextEvent:
			event = nextEvent
		else:
			kickLength = getGain(drive, event, item[onsideLoc+13:nextPlayLoc])
			event.endingYard = event.startingYard + kickLength
	# punt
	elif puntLoc != -1:
		event.eventType = gameDefs.EVENT_PUNT
		kickerName = itemWNames[0:puntLoc]
		event.offense1 = kickerName.strip()
		if item.find('blocked', puntLoc, nextPlayLoc) != -1:
			event.eventType = gameDefs.EVENT_BLOCKED_PUNT
			getDefenderNames(event, item, itemWNames, puntLoc, len(item), 'blocked by ')
			play.result = gameDefs.RESULT_ADVANCE_DOWN
			# recovery
			nextEvent = getRecovery(drive, play, event, item, itemWNames, recoverLoc, nextPlayLoc)
			if nextEvent:
				event = nextEvent
			else:			
				event.endingYard = event.startingYard
		else:
			getDefenderNames(event, item, itemWNames, puntLoc, nextPlayLoc, ' fair catch by ')
			puntLength = getGain(drive, event, item[puntLoc+5:nextPlayLoc])
			event.endingYard = event.startingYard + puntLength
			play.result = gameDefs.RESULT_KICK_RECEIVED
	# rush
	elif rushLoc != -1:
		event.eventType = gameDefs.EVENT_RUSH
		rusherName = itemWNames[0:rushLoc]
		event.offense1 = rusherName.strip()
		getDefenderNames(event, item, itemWNames, rushLoc, nextPlayLoc, ' tackled by ')
		gain = getGain(drive, event, item[rushLoc+5:nextPlayLoc])
		event.endingYard = event.startingYard + gain
		play.result = gameDefs.RESULT_ADVANCE_DOWN
	# sack
	elif sackLoc != -1:
		event.eventType = gameDefs.EVENT_SACK
		qbName = itemWNames[0:sackLoc]
		event.offense1 = qbName.strip()
		getDefenderNames(event, item, itemWNames, sackLoc, nextPlayLoc, ' by ')
		gain = getGain(drive, event, item[sackLoc+7:nextPlayLoc])
		if gain > 0:
			gain = -gain
		event.endingYard = event.startingYard + gain
		play.result = gameDefs.RESULT_ADVANCE_DOWN
	# scramble
	elif scrambleLoc != -1:
		event.eventType = gameDefs.EVENT_RUSH
		qbName = itemWNames[0:scrambleLoc]
		event.offense1 = qbName.strip()
		getDefenderNames(event, item, itemWNames, scrambleLoc, nextPlayLoc, ' tackled by ')
		gain = getGain(drive, event, item[rushLoc+9:nextPlayLoc])
		event.endingYard = event.startingYard + gain
		play.result = gameDefs.RESULT_ADVANCE_DOWN
	# pass
	elif passLoc != -1 and (penaltyLoc == -1 or passLoc < penaltyLoc):
		event.eventType = gameDefs.EVENT_PASS
		qbName = itemWNames[0:passLoc]
		event.offense1 = qbName.strip()
		getOffensiveNames(event, item, itemWNames, passLoc, nextPlayLoc, ' to ')
		if item.find('incomplete', passLoc, nextPlayLoc) != -1:
			event.eventType = gameDefs.EVENT_INCOMPLETE_PASS
			gain = 0
			# for other plays, it's obvious from the type of play how to credit the defenders
			# listed.  however, for an incomplete pass, there's no distinction between a
			# defender hurring the quarterback and a defender breaking up the pass.
			# if this becomes an issue, we'll have to modify our database.
			getDefenderNames(event, item, itemWNames, passLoc, nextPlayLoc, ' hurry by ')
			getDefenderNames(event, item, itemWNames, passLoc, nextPlayLoc, ' hurried by ')
			getDefenderNames(event, item, itemWNames, passLoc, nextPlayLoc, ' broken up by ')
		else:
			gain = getGain(drive, event, item[passLoc+5:nextPlayLoc])
		event.endingYard = event.startingYard + gain
		interceptionLoc = item.find('intercepted', passLoc, nextPlayLoc)
		if interceptionLoc != -1:
			event.eventType = gameDefs.EVENT_INTERCEPTION
			play.result = gameDefs.RESULT_TURNOVER
			event.offense2 = ''
			getDefenderNames(event, item, itemWNames, interceptionLoc, nextPlayLoc, ' by ')
		else:
			getDefenderNames(event, item, itemWNames, passLoc, nextPlayLoc, ' tackled by ')
			play.result = gameDefs.RESULT_ADVANCE_DOWN
	# timeout
	elif item.find('timeout') != -1:
		event.eventType = gameDefs.EVENT_NULL
		event.endingYard = event.startingYard
	# end of quarter
	elif item.find('end of ') != -1 and (item.find(' quarter') != -1 or item.find(' ot') != -1):
		event.eventType = gameDefs.EVENT_NULL
		event.endingYard = event.startingYard
	# nothing listed
	elif len(item) == 0:
		event.eventType = gameDefs.EVENT_NULL
		event.endingYard = event.startingYard
	# has a next play
	if nextPlayLoc != len(item):
		# don't worry
		pass
	# unknown play
	#else:
	#	if item != '&nbsp; &nbsp;':
	#		print '[unknown] ' + item
	
	if nextPlayLoc != len(item):
		getNextEvent(drive, play, event, item, itemWNames, advanceLoc, returnLoc, fumbleLoc, lateralLoc, penaltyLoc, nextPlayLoc)
	
	if event.eventType == gameDefs.EVENT_NULL:
		tackledLoc = item.find(' tackled ')
		if tackledLoc != -1:
			event.eventType = gameDefs.EVENT_RUSH
			name = itemWNames[0:tackledLoc]
			event.offense1 = name
			getDefenderNames(event, item, itemWNames, tackledLoc, nextPlayLoc, ' by ')
			gain = getGain(drive, event, item[tackledLoc+9:nextPlayLoc])
			event.endingYard = event.startingYard + gain
			play.result = gameDefs.RESULT_ADVANCE_DOWN
	
	resolveResult(play, event, item, 0, nextPlayLoc)
	
	if play.down == 4 and play.result == gameDefs.RESULT_ADVANCE_DOWN:
		play.result = gameDefs.RESULT_TURNOVER_ON_DOWNS
	return 0

# get stats for a recovery, if there is one
# return the recovery event, or None
def getRecovery(drive, play, event, item, itemWNames, recoverLoc, nextPlayLoc):
	if recoverLoc != -1:
		recovery = item[recoverLoc+7:nextPlayLoc]
		
		gain = getGain(drive, event, recovery)
		event.endingYard = event.startingYard + gain
		
		prevEvent = event
		event = Event()
		event.startingYard = prevEvent.endingYard
		play.events.append(event)
		
		event.eventType = gameDefs.EVENT_RECOVERY
		event.endingYard = event.startingYard
		
		duringReturn = play.duringReturn(event)
					
		byLoc = item.find(' by ', recoverLoc+7, nextPlayLoc)
		if byLoc != -1:
			str = item[byLoc+4:nextPlayLoc]
			strWNames = itemWNames[byLoc+4:nextPlayLoc]
			recovererName = findName(str, strWNames, drive)
			# look for which team recovered
			spaceLoc = recovererName.find(' ')
			if spaceLoc == -1:
				spaceLoc = len(recovererName)
			teamID = recovererName[0:spaceLoc].lower()
			if teamID == drive.medPoss.lower() or teamID == drive.teamPoss.lower():
				recovererName = recovererName[spaceLoc+1:]
				if duringReturn:
					# offense (now defense) got it back
					event.eventType = gameDefs.EVENT_RECOVERY_DEFENSE
					event.defense1 = recovererName
					play.result = gameDefs.RESULT_DEFENSIVE_TURNOVER
				else:
					# offense retained it
					event.eventType = gameDefs.EVENT_RECOVERY_OFFENSE
					event.offense1 = recovererName
			elif teamID == drive.medDef.lower() or teamID == drive.teamDef.lower():
				recovererName = recovererName[spaceLoc+1:]
				if duringReturn:
					# defense (now offense) retained it
					event.eventType = gameDefs.EVENT_RECOVERY_OFFENSE
					event.offense1 = recovererName
				else:
					# defense recovered it
					event.eventType = gameDefs.EVENT_RECOVERY_DEFENSE
					event.defense1 = recovererName
					play.result = gameDefs.RESULT_TURNOVER
			elif recovererName == prevEvent.offense1 or recovererName == prevEvent.offense2:
				# recovered by kicker/fumbler
				if duringReturn:
					# offense (now defense) got it back
					event.eventType = gameDefs.EVENT_RECOVERY_DEFENSE
					event.defense1 = recovererName
					play.result = gameDefs.RESULT_DEFENSIVE_TURNOVER
				else:
					# offense retained it
					event.eventType = gameDefs.EVENT_RECOVERY_OFFENSE
					event.offense1 = recovererName
			elif recovererName == prevEvent.defense1 or recovererName == prevEvent.defense1:
				# recovered by player who blocked the kick/forced the fumble
				if duringReturn:
					# defense (now offense) retained it
					event.eventType = gameDefs.EVENT_RECOVERY_OFFENSE
					event.offense1 = recovererName
				else:
					# defense recovered it
					event.eventType = gameDefs.EVENT_RECOVERY_DEFENSE
					event.defense1 = recovererName
					play.result = gameDefs.RESULT_TURNOVER
				
			else:
				# unknown recovery
				event.offense1 = recovererName
			getDefenderNames(event, item, itemWNames, byLoc, nextPlayLoc, ' tackled by ')
		return event
	else:
		return None

def getNextEvent(drive, play, prevEvent, item, itemWNames, advanceLoc, returnLoc, fumbleLoc, lateralLoc, penaltyLoc, nextPlayLoc):
	if prevEvent.eventType != gameDefs.EVENT_NULL:
		event = Event()
		event.startingYard = prevEvent.endingYard
		if prevEvent.eventType == gameDefs.EVENT_RUSH or prevEvent.eventType == gameDefs.EVENT_SACK or prevEvent.eventType == gameDefs.EVENT_RETURN:
			event.offense1 = prevEvent.offense1
		elif prevEvent.eventType == gameDefs.EVENT_RECOVERY_OFFENSE or prevEvent.eventType == gameDefs.EVENT_RECOVERY:
			event.offense1 = prevEvent.offense1
		elif prevEvent.eventType == gameDefs.EVENT_RECOVERY_DEFENSE:
			event.offense1 = prevEvent.defense1
		elif prevEvent.eventType == gameDefs.EVENT_PASS or prevEvent.eventType == gameDefs.EVENT_LATERAL:
			event.offense1 = prevEvent.offense2
		elif prevEvent.eventType == gameDefs.EVENT_INTERCEPTION:
			event.offense1 = prevEvent.defense1
		play.events.append(event)
	else:
		event = prevEvent
	if advanceLoc == nextPlayLoc:
		event.eventType = gameDefs.EVENT_ADVANCE
		getAdvance(drive, play, event, item, itemWNames, advanceLoc)
	elif returnLoc == nextPlayLoc:
		event.eventType = gameDefs.EVENT_RETURN
		event.startingYard = 100 - prevEvent.endingYard
		getReturn(drive, play, event, item, itemWNames, returnLoc)
	elif fumbleLoc == nextPlayLoc:
		event.eventType = gameDefs.EVENT_FUMBLE
		getFumble(drive, play, event, item, itemWNames, fumbleLoc)
	elif lateralLoc == nextPlayLoc:
		event.eventType = gameDefs.EVENT_LATERAL
		getLateral(drive, play, event, item, itemWNames, lateralLoc)
	else:
		event.offense1 = ''
		if play.result == gameDefs.RESULT_NONE:
			play.result = gameDefs.RESULT_REPEAT_DOWN
		changePoss = False
		if prevEvent.eventType == gameDefs.EVENT_KICKOFF or prevEvent.eventType == gameDefs.EVENT_PUNT:
			changePoss = True
		elif prevEvent.eventType == gameDefs.EVENT_INTERCEPTION or prevEvent.eventType == gameDefs.EVENT_RECOVERY_DEFENSE:
			changePoss = True
		event.eventType = gameDefs.EVENT_PENALTY
		if changePoss:
			event.startingYard = 100 - prevEvent.endingYard
		getPenalty(drive, play, event, item, itemWNames, penaltyLoc)

def getAdvance(drive, play, event, item, itemWNames, advanceLoc):
	advanceLoc2 = -1
	returnLoc = item.find(' return', advanceLoc)
	fumbleLoc = item.find(' fumble', advanceLoc)
	lateralLoc = item.find(' lateral', advanceLoc)
	penaltyLoc = item.find(' penalty', advanceLoc)
	nextPlayLoc = len(item)
	if returnLoc != -1 and returnLoc < nextPlayLoc:
		nextPlayLoc = returnLoc
	if fumbleLoc != -1 and fumbleLoc < nextPlayLoc:
		nextPlayLoc = fumbleLoc
	if lateralLoc != -1 and lateralLoc < nextPlayLoc:
		nextPlayLoc = lateralLoc
	if penaltyLoc != -1 and penaltyLoc < nextPlayLoc:
		nextPlayLoc = penaltyLoc
	
	gain = getGain(drive, event, item[advanceLoc+8:nextPlayLoc])
	event.endingYard = event.startingYard + gain
	getDefenderNames(event, item, itemWNames, advanceLoc, nextPlayLoc, ' tackled by ')
	if nextPlayLoc != len(item):
		getNextEvent(drive, play, event, item, itemWNames, advanceLoc2, returnLoc, fumbleLoc, lateralLoc, penaltyLoc, nextPlayLoc)
	resolveResult(play, event, item, advanceLoc, nextPlayLoc)

def getReturn(drive, play, event, item, itemWNames, returnLoc):
	advanceLoc = -1
	returnLoc2 = item.find(' return', returnLoc+1)
	fumbleLoc = item.find(' fumble', returnLoc)
	lateralLoc = item.find(' lateral', returnLoc)
	penaltyLoc = item.find(' penalty', returnLoc)
	nextPlayLoc = len(item)
	if returnLoc2 != -1 and returnLoc2 < nextPlayLoc:
		nextPlayLoc = returnLoc2
	if fumbleLoc != -1 and fumbleLoc < nextPlayLoc:
		nextPlayLoc = fumbleLoc
	if lateralLoc != -1 and lateralLoc < nextPlayLoc:
		nextPlayLoc = lateralLoc
	if penaltyLoc != -1 and penaltyLoc < nextPlayLoc:
		nextPlayLoc = penaltyLoc
	
	if event.offense1 == '':
		getOffensiveNames(event, item, itemWNames, returnLoc, nextPlayLoc, ' by ')
		#spaceLoc = item.rfind(' ', 0, returnLoc)
		#commaLoc = item.rfind(',', 0, returnLoc)
		#periodLoc = item.rfind('.', 0, returnLoc)
		#if commaLoc != -1 and commaLoc+1 == spaceLoc:
		#	commaLoc = item.rfind(',', 0, commaLoc-1)
		#	periodLoc = item.rfind('.', 0, commaLoc)
		#elif periodLoc != -1 and periodLoc+1 == spaceLoc:
		#	periodLoc = item.rfind(',', 0, periodLoc-1)
		#if commaLoc > periodLoc:
		#	returnerName = itemWNames[commaLoc+1:returnLoc]
		#elif periodLoc > commaLoc:
		#	returnerName = itemWNames[periodLoc+1:returnLoc]
		#else:
			# periodLoc can't equal commaLoc unless they both equal -1
		#	returnerName = ''
		#event.offense1 = returnerName.strip()
	spaceLoc = item.find(' ', returnLoc+1, nextPlayLoc)
	returnLength = getGain(drive, event, item[spaceLoc:nextPlayLoc])
	event.endingYard = event.startingYard + returnLength
	
	#print 'return: ' + item[returnLoc:nextPlayLoc]
	#print event.startingYard
	#print event.endingYard
	#print returnLength
	
	getDefenderNames(event, item, itemWNames, returnLoc, nextPlayLoc, ' tackled by ')
	
	if nextPlayLoc != len(item):
		getNextEvent(drive, play, event, item, itemWNames, advanceLoc, returnLoc2, fumbleLoc, lateralLoc, penaltyLoc, nextPlayLoc)
	resolveResult(play, event, item, returnLoc, nextPlayLoc)

def getFumble(drive, play, event, item, itemWNames, fumbleLoc):
	advanceLoc = -1
	returnLoc = item.find(' return', fumbleLoc)
	fumbleLoc2 = item.find(' fumble', fumbleLoc+1)
	lateralLoc = item.find(' lateral', fumbleLoc)
	penaltyLoc = item.find(' penalty', fumbleLoc)
	nextPlayLoc = len(item)
	if returnLoc != -1 and returnLoc < nextPlayLoc:
		nextPlayLoc = returnLoc
	if fumbleLoc2 != -1 and fumbleLoc2 < nextPlayLoc:
		nextPlayLoc = fumbleLoc2
	if lateralLoc != -1 and lateralLoc < nextPlayLoc:
		nextPlayLoc = lateralLoc
	if penaltyLoc != -1 and penaltyLoc < nextPlayLoc:
		nextPlayLoc = penaltyLoc
	
	getDefenderNames(event, item, itemWNames, fumbleLoc, nextPlayLoc, ' forced by ')
	
	recoverLoc = item.find(' recover', fumbleLoc, nextPlayLoc)
	# recovery
	nextEvent = getRecovery(drive, play, event, item, itemWNames, recoverLoc, nextPlayLoc)
	if nextEvent:
		if nextEvent.eventType == gameDefs.EVENT_RECOVERY_OFFENSE:
			recovererName = nextEvent.offense1
		elif nextEvent.eventType == gameDefs.EVENT_RECOVERY_DEFENSE:
			recovererName = nextEvent.defense1
		
		commaLoc = item.find(',', recoverLoc, nextPlayLoc)
		if commaLoc != -1:
			name = recovererName.lower() + ' for '
			nameLoc = item.find(name, commaLoc, nextPlayLoc)
			if nameLoc != -1 and nameLoc < nextPlayLoc:
				if nextEvent.eventType == gameDefs.EVENT_RECOVERY_DEFENSE:
					returnLoc = nameLoc
				else:
					advanceLoc = nameLoc
				nextPlayLoc = nameLoc
				
				gain = getGain(drive, event, item[recoverLoc+7:nextPlayLoc])
				event.endingYard = event.startingYard + gain
				nextEvent.startingYard = event.endingYard
				nextEvent.endingYard = nextEvent.startingYard
		
		event = nextEvent
	
	if nextPlayLoc != len(item):
		getNextEvent(drive, play, event, item, itemWNames, advanceLoc, returnLoc, fumbleLoc2, lateralLoc, penaltyLoc, nextPlayLoc)
	resolveResult(play, event, item, fumbleLoc, nextPlayLoc)

def getLateral(drive, play, event, item, itemWNames, lateralLoc):
	advanceLoc = -1
	returnLoc = item.find(' return', lateralLoc)
	fumbleLoc = item.find(' fumble', lateralLoc)
	lateralLoc2 = item.find(' lateral', lateralLoc+1)
	penaltyLoc = item.find(' penalty', lateralLoc)
	nextPlayLoc = len(item)
	if returnLoc != -1 and returnLoc < nextPlayLoc:
		nextPlayLoc = returnLoc
	if fumbleLoc != -1 and fumbleLoc < nextPlayLoc:
		nextPlayLoc = fumbleLoc
	if lateralLoc2 != -1 and lateralLoc2 < nextPlayLoc:
		nextPlayLoc = lateralLoc2
	if penaltyLoc != -1 and penaltyLoc < nextPlayLoc:
		nextPlayLoc = penaltyLoc
	
	getOffensiveNames(event, item, itemWNames, lateralLoc, nextPlayLoc, ' to ')
	gain = getGain(drive, event, item[lateralLoc+8:nextPlayLoc])
	event.endingYard = event.startingYard + gain
	getDefenderNames(event, item, itemWNames, lateralLoc, nextPlayLoc, ' tackled by ')
	if nextPlayLoc != len(item):
		getNextEvent(drive, play, event, item, itemWNames, advanceLoc, returnLoc, fumbleLoc, lateralLoc2, penaltyLoc, nextPlayLoc)
	resolveResult(play, event, item, lateralLoc, nextPlayLoc)

def getPenalty(drive, play, event, item, itemWNames, penaltyLoc):
	penaltyLoc2 = item.find(' penalty', penaltyLoc+1)
	if penaltyLoc2 == -1:
		penaltyLoc2 = len(item)
	acceptedLoc = item.find(' accepted', penaltyLoc, penaltyLoc2)
	declinedLoc = item.find(' declined', penaltyLoc, penaltyLoc2)
	offsettingLoc = item.find('off-setting', penaltyLoc, penaltyLoc2)
	
	if item.find(' no play', penaltyLoc, penaltyLoc2) != -1:
		play.events = []
		event.startingYard = play.startingYard
		play.events.append(event)
		play.result = gameDefs.RESULT_REPEAT_DOWN
	
	i = penaltyLoc+9
	while i < len(item) and not item[i].isdigit():
		i += 1
	gain = getGain(drive, event, item[i:penaltyLoc2], True)
	
	# look for which team committed the penalty
	spaceLoc = item.find(' ', penaltyLoc+9)
	if spaceLoc == -1:
		spaceLoc = len(item)
	teamID = itemWNames[penaltyLoc+9:spaceLoc]
	if teamID == drive.medPoss:
		# offense did it
		offensivePenalty = True
	elif teamID == drive.medDef:
		# defense did it
		offensivePenalty = False
	else:
		searchLoc = i - 25
		if searchLoc < 0:
			searchLoc = 0
		penaltyString = item[searchLoc:penaltyLoc]
		commaLoc = penaltyString.find(',')
		if commaLoc != -1:
			penaltyString = penaltyString[commaLoc+1:]
		periodLoc = penaltyString.find('.')
		if periodLoc != -1:
			penaltyString = penaltyString[periodLoc+1:]
		offensivePenalty = whichTeam(drive.teamPoss.lower(), drive.teamDef.lower(), penaltyString)
	
	duringReturn = play.duringReturn(event)
	
	if declinedLoc != -1:
		gain = 0
	elif offsettingLoc != -1:
		gain = 0
		#if play.result == gameDefs.RESULT_ADVANCE_DOWN:
		#	play.result = gameDefs.RESULT_REPEAT_DOWN
	else:
		#print 'PENALTY - ' + item[i:]
		# check if there's a loss of down
		lossOfDown = False
		if item.find('intentional grounding', penaltyLoc, penaltyLoc2) != -1:
			lossOfDown = True
		elif item.find('illegal forward pass', penaltyLoc, penaltyLoc2) != -1:
			lossOfDown = True
		# check if there's an automatic first down
		automaticFirstDown = False
		if not (offensivePenalty or duringReturn):
			if item.find('personal foul', penaltyLoc, penaltyLoc2) != -1:
				automaticFirstDown = True
			elif item.find('pass interference', penaltyLoc, penaltyLoc2) != -1:
				automaticFirstDown = True
			elif item.find('roughing the kicker', penaltyLoc, penaltyLoc2) != -1:
				automaticFirstDown = True
		if offensivePenalty:
			#print "Offensive Penalty"
			gain = -gain
		if duringReturn:
			#print "During Return"
			gain = -gain
		if item.find('1st down', penaltyLoc, penaltyLoc2) != -1:
			if play.result < gameDefs.RESULT_FIRST_DOWN:
				play.result = gameDefs.RESULT_FIRST_DOWN
		elif play.result == gameDefs.RESULT_ADVANCE_DOWN:
			if not lossOfDown:
				play.result = gameDefs.RESULT_REPEAT_DOWN
			if automaticFirstDown and play.down != 0:
				play.result = gameDefs.RESULT_FIRST_DOWN
		elif play.result == gameDefs.RESULT_REPEAT_DOWN:
			if lossOfDown:
				play.result = gameDefs.RESULT_ADVANCE_DOWN
			if automaticFirstDown and play.down != 0:
				play.result = gameDefs.RESULT_FIRST_DOWN
	loc = penaltyLoc2
	if acceptedLoc != -1 and acceptedLoc < loc:
		loc = acceptedLoc
	if declinedLoc != -1 and declinedLoc < loc:
		loc = declinedLoc
	if offsettingLoc != -1 and offsettingLoc < loc:
		loc = offsettingLoc
	getDefenderNames(event, item, itemWNames, penaltyLoc, loc, ' on ')
	if offensivePenalty is not duringReturn:
		event.offense1 = event.defense1
		event.defense1 = ''
	event.endingYard = event.startingYard + gain
	# check to see if the penalty will result in a first down
	if play.startingYard + int(play.distance) <= event.endingYard:
		if play.result < gameDefs.RESULT_FIRST_DOWN and play.down != 0:
			play.result = gameDefs.RESULT_FIRST_DOWN
	if penaltyLoc2 < len(item):
		nextEvent = Event()
		nextEvent.startingYard = event.endingYard
		play.events.append(nextEvent)
		nextEvent.eventType = gameDefs.EVENT_PENALTY
		getPenalty(drive, play, nextEvent, item, itemWNames, penaltyLoc2)

def resolveResult(play, event, item, playLoc, nextPlayLoc):
	if item.find('1st down', playLoc, nextPlayLoc) != -1:
		if play.result < gameDefs.RESULT_FIRST_DOWN:
			play.result = gameDefs.RESULT_FIRST_DOWN
	if item.find('touchdown', playLoc, nextPlayLoc) != -1:
		event.endingYard = 100
		if play.didChangePoss(event):
			play.result = gameDefs.RESULT_DEFENSIVE_TOUCHDOWN
		else:
			play.result = gameDefs.RESULT_TOUCHDOWN
	if (item.find('conversion', playLoc, nextPlayLoc) != -1) and (item.find('failed', playLoc, nextPlayLoc) == -1):
		event.endingYard = 100
		if play.didChangePoss(event):
			play.result = gameDefs.RESULT_DEFENSIVE_TOUCHDOWN
		else:
			play.result = gameDefs.RESULT_TOUCHDOWN
	if item.find('safety', playLoc, nextPlayLoc) != -1:
		event.endingYard = 0
		if play.didChangePoss(event):
			play.result = gameDefs.RESULT_DEFENSIVE_SAFETY
		else:
			play.result = gameDefs.RESULT_SAFETY
	if item.find('touchback', playLoc, nextPlayLoc) != -1:
		if play.duringReturn(event):
			if event.endingYard == 0:
				play.result = gameDefs.RESULT_TOUCHBACK
			else:
				play.result = gameDefs.RESULT_DEFENSIVE_TOUCHBACK
				event.endingYard = 100
		else:
			play.result = gameDefs.RESULT_TOUCHBACK
			event.endingYard = 100

def getGain(drive, event, item, forPenalty = False):
	#print 'GAIN - ' + item
	gain = 0
	penaltyLoc = item.find(' penalty')
	if penaltyLoc == -1:
		penaltyLoc = len(item)
	forLoc = item.find(' for ')
	if forPenalty:
		yardLoc = item.find(' yard', 0, penaltyLoc)
		if yardLoc == -1:
			yardLoc = item.find(' yds ', 0, penaltyLoc)
		forLoc = -1
		#print 'penalty yardLoc = ' + str(yardLoc)
	elif forLoc == -1:
		yardLoc = item.find(' yard', 0, penaltyLoc)
		if yardLoc == -1:
			yardLoc = item.find(' yds ', 0, penaltyLoc)
	elif forLoc == item.find(' for a touch') or forLoc == item.find(' for a safety') or forLoc == item.find(' for a 1st down'):
		forLoc = -1
		yardLoc = item.find(' yard', 0, penaltyLoc)
		if yardLoc == -1:
			yardLoc = item.find(' yds ', 0, penaltyLoc)
	else:
		yardLoc = item.find(' yard', forLoc, penaltyLoc)
		if yardLoc == -1:
			yardLoc = item.find(' yds ', forLoc, penaltyLoc)
	fiftyYardLoc = item.find(' the 50 yard ')
	if fiftyYardLoc != -1 and (fiftyYardLoc+7) == yardLoc:
		yardLoc = -1
	lossLoc = item.find('loss of', forLoc, yardLoc)
	#print str(forLoc) + ' ' + str(yardLoc) + ' ' + str(lossLoc)
	noGainLoc = item.find('no gain')
	toTheLoc = item.find(' to the ')
	atTheLoc = item.find(' at the ')
	atLoc = item.find(' at ')
	ballOnLoc = item.find(' ball on ')
	endZoneLoc = item.find(' in the endzone')
	if endZoneLoc == -1:
		endZoneLoc = item.find(' in the end zone')
	if toTheLoc != -1 and atTheLoc != -1:
		if toTheLoc < atTheLoc:
			atTheLoc = -1
		else:
			toTheLoc = -1
	if yardLoc != -1 and (noGainLoc == -1 or yardLoc < noGainLoc):
		if lossLoc != -1:
			gainStr = item[lossLoc+8:yardLoc]
			if gainStr.strip('- ').isdigit():
				gain = -int(gainStr)
			else:
				print '[loss err] ' + item + ' - ' + gainStr
		else:
			if forLoc != -1:
				gainStr = item[forLoc+5:yardLoc]
			else:
				gainStr = item[0:yardLoc]
			parenLoc = gainStr.find(')')
			if parenLoc != -1:
				gainStr = gainStr[parenLoc+1:]
			if gainStr.strip('- ').isdigit():
				gain = int(gainStr)
			else:
				print '[gain err] ' + item + ' - ' + gainStr
	#elif noGainLoc != -1:
	#	gain = 0
	elif toTheLoc != -1:
		if fiftyYardLoc == toTheLoc+3:
			yardLine = 50
		else:
			yardLine = getYardLine(drive, event, item[toTheLoc+8:])
		event.endingYard = yardLine
		gain = event.endingYard - event.startingYard
	elif atTheLoc != -1:
		if fiftyYardLoc == atTheLoc+3:
			yardLine = 50
		else:
			yardLine = getYardLine(drive, event, item[atTheLoc+8:])
		event.endingYard = yardLine
		gain = event.endingYard - event.startingYard
	elif atLoc != -1:
		yardLine = getYardLine(drive, event, item[atLoc+4:])
		event.endingYard = yardLine
		gain = event.endingYard - event.startingYard
	elif ballOnLoc != -1:
	#	print 'ball on'
	#	print item[ballOnLoc+9:]
		yardLine = getYardLine(drive, event, item[ballOnLoc+9:])
	#	print 'yardline = ' + str(yardline)
		event.endingYard = yardLine
		gain = event.endingYard - event.startingYard
	elif endZoneLoc != -1:
		# now, we know the ball ended up in the end zone
		# but we don't know which end zone
		# so, we guess.  an educated guess, though:
		# since the ball is unlikely to travel the distance
		# of the field on a single play, we pick the closer endzone
		if event.startingYard > 50:
			event.endingYard = 100
		else:
			event.endingYard = 0
		gain = event.endingYard - event.startingYard
	if noGainLoc != -1 and not forPenalty:
		gain = 0
	#else:
		#print '[lossorgain err] ' + item
	#print 'gain = ' + str(gain) + ', item = ' + str(item)
	return gain

def getYardLine(drive, event, item):
	# decide team
	ownSide = True
	if drive.eventDuringReturn(event):
		offense = drive.medDef.lower()
		defense = drive.medPoss.lower()
	else:
		offense = drive.medPoss.lower()
		defense = drive.medDef.lower()
	spaceLoc = item.find(' ')
	sideName = item[0:spaceLoc]
	if sideName == offense:
		ownSide = True
	elif sideName == defense:
		ownSide = False
	if item[0] == offense[0] and item[0] != defense[0]:
		ownSide = True
	elif item[0] != offense[0] and item[0] == defense[0]:
		ownSide = False
	else:
		i = 1
		while i < 5:
			letter = item[i]
			offLoc = offense.find(letter)
			defLoc = defense.find(letter)
			if offLoc != -1 and defLoc == -1:
				ownSide = True
				break
			elif offLoc == -1 and defLoc != -1:
				ownSide = False
				break
			elif offLoc < defLoc:
				ownSide = True
				break
			elif offLoc > defLoc:
				ownSide = False
				break
			else:
				i += 1
	# get yardline
	i = 1
	while i < len(item) and not item[i].isdigit():
		i += 1
	numStart = i
	while i < len(item) and item[i].isdigit():
		i += 1
	numEnd = i
	numerals = item[numStart:numEnd]
	if numerals.isdigit():
		yardLine = int(numerals)
	else:
		print '[yardline err:' + str(numStart) + ':' + str(numEnd) + '] ' + item
		yardLine = 50
	if not ownSide:
		yardLine = 100 - yardLine
	return yardLine

def getOffensiveNames(event, item, itemWNames, playLoc, nextPlayLoc, phrase):
	phraseLoc = item.find(phrase, playLoc, nextPlayLoc)
	if phraseLoc != -1:
		phraseLoc += len(phrase)
		str = item[phraseLoc:nextPlayLoc]
		strWNames = itemWNames[phraseLoc:nextPlayLoc]
		offensiveName = findName(str, strWNames)
		if event.offense1 != '':
			event.offense2 = offensiveName
		else:
			event.offense1 = offensiveName

def getDefenderNames(event, item, itemWNames, playLoc, nextPlayLoc, phrase):
	#print itemWNames
	phraseLoc = item.find(phrase, playLoc, nextPlayLoc)
	# in the case of finding names for penalties, make an extra check
	ballOnLoc = item.find(' ball on ', playLoc, nextPlayLoc)
	while phraseLoc == ballOnLoc+5:
		phraseLoc = item.find(phrase, phraseLoc+1, nextPlayLoc)
		ballOnLoc = item.find(' ball on ', ballOnLoc+1, nextPlayLoc)
	openParenLoc = item.find('(', playLoc, nextPlayLoc)
	if phraseLoc != -1:
		phraseLoc += len(phrase)
		str = item[phraseLoc:nextPlayLoc]
		strWNames = itemWNames[phraseLoc:nextPlayLoc]
		defenderName = findName(str, strWNames)
	elif openParenLoc != -1:	
		closeParenLoc = item.find(')', openParenLoc, nextPlayLoc)
		defenderName = itemWNames[openParenLoc+1:closeParenLoc]
		# we've already gotten these names earlier; don't worry about it
		if defenderName.find('blocked by ') == 0:
			return
	else:
		return
	#print defenderName
	andLoc = defenderName.find(' and ')
	semicolonLoc = defenderName.find(';')
	if andLoc != -1:
		defenderName1 = defenderName[0:andLoc]
		defenderName2 = defenderName[andLoc+5:]
		event.defense1 = defenderName1.strip()
		event.defense2 = defenderName2.strip()
	elif semicolonLoc != -1:
		defenderName1 = defenderName[0:semicolonLoc]
		defenderName2 = defenderName[semicolonLoc+1:]
		event.defense1 = defenderName1.strip()
		event.defense2 = defenderName2.strip()
	else:
		event.defense1 = defenderName.strip()

def findName(str, strWNames, drive = None):
	atLoc = str.find(' at ')
	inLoc = str.find(' in ')
	forLoc = str.find(' for ')
	#andLoc = str.find(' and ')
	outOfBoundsLoc = str.find(' out-of-bounds')
	openParenLoc = str.find('(')
	closeParenLoc = str.find(')')
	
	loc = len(str)
	if atLoc != -1 and atLoc < loc:
		loc = atLoc
	if inLoc != -1 and inLoc < loc:
		loc = inLoc
	if forLoc != -1 and forLoc < loc:
		loc = forLoc
	#if andLoc != -1 and andLoc < loc:
	#	loc = andLoc
	if outOfBoundsLoc != -1 and outOfBoundsLoc < loc:
		loc = outOfBoundsLoc
	if openParenLoc != -1 and openParenLoc < loc:
		loc = openParenLoc
	if closeParenLoc != -1 and closeParenLoc < loc:
		loc = closeParenLoc
	
	name = strWNames[0:loc].strip()
	if name[0:3].lower() == 'n/a':
		# don't return n/a, just assume name is unknown, return nothing
		return ''
	if name[0:4].lower() == 'team':
		# don't go looking for anything else, just return 'team'
		return name[0:4]
	spaceLoc = name.find(' ')
	if spaceLoc != -1:
		if drive:
			teamID = name[0:spaceLoc]
			if teamID == drive.medPoss or teamID == drive.teamPoss:
				spaceLoc = name.find(' ', spaceLoc+1)
			elif teamID == drive.medDef or teamID == drive.teamDef:
				spaceLoc = name.find(' ', spaceLoc+1)
		if spaceLoc != -1:
			commaLoc = name.find(',', spaceLoc)
			if commaLoc > spaceLoc:
				name = name[0:commaLoc].strip()
			periodLoc = name.rfind('.')
			length = len(name)
			if periodLoc == length-1 and spaceLoc != length-3:
				name = name[0:periodLoc].strip()
	#print name
	return name

def whichTeam(teamName, otherTeamName, string):
	if string.find(teamName) != -1:
		return True
	elif string.find(otherTeamName) != -1:
		return False
	else:
		str = string.strip()
		i = len(str) - 1
		while i >= 0:
			letter = str[i]
			teamLoc = teamName.rfind(letter)
			otherLoc = otherTeamName.rfind(letter)
			if teamLoc != -1 and otherLoc == -1:
				return True
			elif teamLoc == -1 and otherLoc != -1:
				return False
			elif teamLoc > otherLoc:
				return True
			elif teamLoc < otherLoc:
				return False
			else:
				i -= 1
		return True

if __name__ == '__main__':
    import sys
    print geturlstring(sys.argv[1])
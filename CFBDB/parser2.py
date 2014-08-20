import urllib
import MySQLdb
import gameDefs
import cfbdb

Game = gameDefs.Game
Drive = gameDefs.Drive
Play = gameDefs.Play
Event = gameDefs.Event

def geturlstring(page):
	sock = urllib.urlopen(page)
	htmlSource = sock.read()
	sock.close()
	return htmlSource

def test():
	f = file('driveSummary2.html')
	urlstring = f.read()
	game = parsePlayByPlay2(urlstring)
	if game:
		game.gameID = 1
		game.calcResults()
		
		conn = MySQLdb.connect(host = "localhost", db = "test")
		cursor = conn.cursor()
		cfbdb.createTables(cursor)
		cfbdb.insertGame(game, cursor)
		cfbdb.verifyGame(game.gameID, cursor)
		cursor.close()
		conn.close()
	
def parsePlayByPlay2(urlstring):
	# get full names and Ids
	# get visiting team full name
	loc = urlstring.find('<body>')
	loc2 = urlstring.find('(', loc)
	teamName1 = urlstring[loc+6:loc2].strip()
	loc3 = urlstring.find(')', loc2)
	teamScore1 = int(urlstring[loc2+1:loc3])
	# get home team full name
	loc = urlstring.find('vs.', loc)
	loc2 = urlstring.find('(', loc)
	teamName2 = urlstring[loc+3:loc2].strip()
	loc3 = urlstring.find(')', loc2)
	teamScore2 = int(urlstring[loc2+1:loc3])
	#print teamName1 + ' ' + str(teamScore1) + ' @ ' + teamName2 + ' ' + str(teamScore2)
	
	# find date
	loc = urlstring.find('<br>', loc3)
	date = urlstring[loc3+1:loc]
	# find venue
	loc = urlstring.find('at ', loc)
	loc2 = urlstring.find('<br>', loc)
	venue = urlstring[loc+3:loc2].strip()
	
	year, month, day = convertDate2(date)
	
	g = Game(0, year, month, day, venue, '', teamName1, teamName2, teamScore1, teamScore2)
	
	# set up variables
	qtr = 0
	homePoss = False
	teamPoss = teamName1
	teamDef = teamName2
	
	# placeholders
	shortName1 = ''
	shortName2 = ''
	shortPoss = ''
	shortDef = ''
	
	eof = len(urlstring)
	
	# figure out shortNames
	toTheLoc = 0
	while shortName1 == '' or shortName2 == '':
		toTheLoc = urlstring.find(' to the ', toTheLoc+1)
		if toTheLoc != -1:
			nameLoc = toTheLoc+8
			i = nameLoc
			while i < eof and not urlstring[i].isdigit():
				i += 1
			digitLoc = i
			shortName = urlstring[nameLoc:digitLoc]
			
			if shortName == '50':
				pass
			elif shortName[0] == teamName1[0] and shortName[0] != teamName2[0]:
				shortName1 = shortName
				#print 'teamName1 = ' + teamName1 + ', shortName1 = ' + shortName1
			elif shortName[0] != teamName1[0] and shortName[0] == teamName2[0]:
				shortName2 = shortName
				#print 'teamName2 = ' + teamName2 + ', shortName2 = ' + shortName2
			elif (shortName1 == '') and (shortName2 != '') and (shortName != shortName2):
				shortName1 = shortName
				#print 'teamName1 = ' + teamName1 + ', shortName1 = ' + shortName1
			elif (shortName2 == '') and (shortName1 != '') and (shortName != shortName1):
				shortName2 = shortName
				#print 'teamName2 = ' + teamName2 + ', shortName2 = ' + shortName2
			else:
				j = 1
				while j < len(shortName):
					letter = shortName[j]
					oneLoc = teamName1.find(letter)
					twoLoc = teamName2.find(letter)
					if oneLoc != -1 and twoLoc == -1:
						shortName1 = shortName
						#print 'teamName1 = ' + teamName1 + ', shortName1 = ' + shortName1
						break
					elif oneLoc == -1 and twoLoc != -1:
						shortName2 = shortName
						#print 'teamName2 = ' + teamName2 + ', shortName2 = ' + shortName2
						break
					elif oneLoc < twoLoc:
						shortName1 = shortName
						#print 'teamName1 = ' + teamName1 + ', shortName1 = ' + shortName1
						break
					elif oneLoc > twoLoc:
						shortName2 = shortName
						#print 'teamName2 = ' + teamName2 + ', shortName2 = ' + shortName2
						break
					else:
						j += 1
		#i += 1
	
	driveLoc = urlstring.find('<tr><td><a href="driveSummary.jsp?')
	while driveLoc < eof:
		# get various info related to the drive
		# get quarter
		tdLoc = urlstring.find('<td>', driveLoc+8)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		qtr = int(urlstring[tdLoc+4:tdLoc2])
		# get the team in possession
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		teamPoss = urlstring[tdLoc+4:tdLoc2].strip()
		# get how the possession started
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		possStart = urlstring[tdLoc+4:tdLoc2].strip()
		# get the starting clock time
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		clockStart = urlstring[tdLoc+4:tdLoc2].strip()
		# get the starting yard
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		startingYard = urlstring[tdLoc+4:tdLoc2].strip()
		# get how the possession ended
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		possEnd = urlstring[tdLoc+4:tdLoc2].strip()
		# get the ending clock time
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		clockEnd = urlstring[tdLoc+4:tdLoc2].strip()
		# get the ending yard
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		endingYard = urlstring[tdLoc+4:tdLoc2].strip()
		# get the number of plays
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		numPlays = int(urlstring[tdLoc+4:tdLoc2])
		# get the number of yards
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		numYards = int(urlstring[tdLoc+4:tdLoc2])
		# get the time of possession
		tdLoc = urlstring.find('<td>', tdLoc2)
		tdLoc2 = urlstring.find('</td>', tdLoc)
		timeOfPoss = urlstring[tdLoc+4:tdLoc2].strip()
		
		if teamPoss == teamName1:
			homePoss = False
			teamDef = teamName2
			shortPoss = shortName1
			shortDef = shortName2
		elif teamPoss == teamName2:
			homePoss = True
			teamDef = teamName1
			shortPoss = shortName2
			shortDef = shortName1
		else:
			print 'what the fuck?'
			
		d = Drive(homePoss, teamPoss, teamDef, shortPoss, shortDef)
		#print teamPoss + ' (' + shortPoss + ') / ' + teamDef + ' (' + shortDef + ')'
		g.drives.append(d)
		
		if startingYard.find('opp') != -1:
			yardline = 100 - int(startingYard[4:])
		elif startingYard != '':
			yardline = int(startingYard)
		else:
			yardline = 97
			#print 'whaaa?'
		#print yardline
		
		dn = 0
		dist = 0
		
		playLoc = urlstring.find('<li>', driveLoc)
		driveLoc = urlstring.find('<tr><td><a href="driveSummary.jsp?', driveLoc+1)
		
		if driveLoc == -1:
			driveLoc = eof
		
		while playLoc != -1:
			eol = urlstring.find("\n", playLoc)
			playString = urlstring[playLoc+4:eol]
			if playString.find('Start of 2nd quarter') != -1:
				qtr = 2
				pass
			elif playString.find('Start of 3rd quarter') != -1:
				qtr = 3
				d = Drive(homePoss, teamPoss, teamDef, shortPoss, shortDef)
				g.drives.append(d)
				yardline = 30
				pass
			elif playString.find('Start of 4th quarter') != -1:
				qtr = 4
				pass
			down, distance, rest = downAndDist(playString)
			if distance == '0':
				# check for special situations
				if dn > 0:
					distance = str(100 - yardline)
				else:
					down = dn
					if down == -1:
						distance = str(100 - yardline)
				print playString
				print down
				print distance
			p = Play(qtr, down, distance, yardline)
			d.plays.append(p)			
			getPlay(g, d, p, rest.lower(), rest)
			playLoc = urlstring.find('<li>', playLoc+1, driveLoc)
			if playLoc == -1:
				p.calcResults(False)
			else:
				p.calcResults(True)
			if p.result == gameDefs.RESULT_NONE:
				pass
			elif p.down == -1 and p.result != gameDefs.RESULT_REPEAT_DOWN:
				# kickoffs got moved back in 2007
				if g.year > 2006:
					yardline = 30
				else:
					yardline = 35
				dn = 0
			elif p.result == gameDefs.RESULT_TOUCHDOWN or p.result == gameDefs.RESULT_DEFENSIVE_TOUCHDOWN:
				yardline = 97
				dn = -1
			elif p.result == gameDefs.RESULT_FIELD_GOAL:
				# kickoffs got moved back in 2007
				if g.year > 2006:
					yardline = 30
				else:
					yardline = 35
				dn = 0
			elif p.result == gameDefs.RESULT_SAFETY or p.result == gameDefs.RESULT_DEFENSIVE_SAFETY:
				yardline = 20
				dn = 0
			elif p.result == gameDefs.RESULT_REPEAT_DOWN:
				yardline = p.endingYard
				dn = p.down
			elif p.result == gameDefs.RESULT_ADVANCE_DOWN:
				yardline = p.endingYard
				dn = p.down + 1
			elif p.result == gameDefs.RESULT_FIRST_DOWN:
				yardline = p.endingYard
				dn = 1
			else:
				yardline = p.endingYard
				
			#print rest
			#print p.playResult()
			#print yardline
	
	return g

# for a given play, get the down and distance
def downAndDist(item):
	down = 0
	if item.find('1st') != -1:
		down = 1
	elif item.find('2nd') != -1:
		down = 2
	elif item.find('3rd') != -1:
		down = 3
	elif item.find('4th') != -1:
		down = 4
	andLoc = item.find('and')
	closeParenLoc = item.find(')')
	distance = item[andLoc+4:closeParenLoc]
	rest = item[closeParenLoc+1:]
	return [down, distance, rest]

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
			#item, itemWNames = removeBlockers(event, item, itemWNames, extraPointLoc, recoverLoc, nextPlayLoc)
			# recovery
			nextEvent = getRecovery(drive, play, event, item, itemWNames, recoverLoc, nextPlayLoc)
			if nextEvent:
				if nextEvent.recoveryType == gameDefs.RECOVERY_DEFENSE:
					play.result = gameDefs.RESULT_TURNOVER
				event = nextEvent
			else:			
				event.endingYard = event.startingYard
			#if item.find('two-point') != -1:
			#	if event.recoveryType == gameDefs.RECOVERY_DEFENSE:
			#		play.result = gameDefs.RESULT_DEFENSIVE_TOUCHDOWN
			#	else:
			#		play.result = gameDefs.RESULT_TOUCHDOWN
			#if item.find('2 defensive point conversion') != -1:
			#	play.result = gameDefs.RESULT_DEFENSIVE_TOUCHDOWN
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
			#item, itemWNames = removeBlockers(event, item, itemWNames, fieldGoalLoc, recoverLoc, nextPlayLoc)
			# recovery
			nextEvent = getRecovery(drive, play, event, item, itemWNames, recoverLoc, nextPlayLoc)
			if nextEvent:
				if nextEvent.recoveryType == gameDefs.RECOVERY_DEFENSE:
					play.result = gameDefs.RESULT_TURNOVER
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
			if nextEvent.recoveryType == gameDefs.RECOVERY_DEFENSE:
				play.result = gameDefs.RESULT_KICK_RECEIVED
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
			#item, itemWNames = removeBlockers(event, item, itemWNames, puntLoc, recoverLoc, nextPlayLoc)
			play.result = gameDefs.RESULT_ADVANCE_DOWN
			# recovery
			nextEvent = getRecovery(drive, play, event, item, itemWNames, recoverLoc, nextPlayLoc)
			if nextEvent:
				if nextEvent.recoveryType == gameDefs.RECOVERY_DEFENSE:
					play.result = gameDefs.RESULT_TURNOVER
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
			gain = 0
			getDefenderNames(event, item, itemWNames, passLoc, nextPlayLoc, ' broken up by ')
			getDefenderNames(event, item, itemWNames, passLoc, nextPlayLoc, ' qb hurry by ')
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
					
		byLoc = item.find(' by ', recoverLoc+7, nextPlayLoc)
		if byLoc != -1:
			str = item[byLoc+4:nextPlayLoc]
			strWNames = itemWNames[byLoc+4:nextPlayLoc]
			recovererName = findName(str, strWNames, drive)
			# look for which team recovered
			spaceLoc = recovererName.find(' ')
			if spaceLoc == -1:
				spaceLoc = len(recovererName)
			teamID = recovererName[0:spaceLoc]
			recovererName = recovererName[spaceLoc+1:]
			if teamID == drive.medPoss or teamID == drive.teamPoss:
				# offense got it
				event.recoveryType = gameDefs.RECOVERY_OFFENSE
				event.offense1 = recovererName
			elif teamID == drive.medDef or teamID == drive.teamDef:
				# defense got it
				event.recoveryType = gameDefs.RECOVERY_DEFENSE
				event.defense1 = recovererName
				play.result = gameDefs.RESULT_TURNOVER
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
		elif prevEvent.eventType == gameDefs.EVENT_RECOVERY:
			if prevEvent.recoveryType == gameDefs.RECOVERY_DEFENSE:
				event.offense1 = prevEvent.defense1
			else:
				event.offense1 = prevEvent.offense1
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
		elif prevEvent.eventType == gameDefs.EVENT_INTERCEPTION:
			changePoss = True
		elif prevEvent.eventType == gameDefs.EVENT_RECOVERY and prevEvent.recoveryType == gameDefs.RECOVERY_DEFENSE:
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
	
	getOffensiveNames(event, item, itemWNames, returnLoc, nextPlayLoc, ' by ')
	if event.offense1 == '':
		spaceLoc = item.rfind(' ', 0, returnLoc)
		commaLoc = item.rfind(',', 0, returnLoc)
		periodLoc = item.rfind('.', 0, returnLoc)
		if commaLoc != -1 and commaLoc+1 == spaceLoc:
			commaLoc = item.rfind(',', 0, commaLoc-1)
			periodLoc = item.rfind('.', 0, commaLoc)
		elif periodLoc != -1 and periodLoc+1 == spaceLoc:
			periodLoc = item.rfind(',', 0, periodLoc-1)
		if commaLoc > periodLoc:
			returnerName = itemWNames[commaLoc+1:returnLoc]
		elif periodLoc > commaLoc:
			returnerName = itemWNames[periodLoc+1:returnLoc]
		else:
			# periodLoc can't equal commaLoc unless they both equal -1
			returnerName = ''
		event.offense1 = returnerName.strip()
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
		if nextEvent.recoveryType == gameDefs.RECOVERY_OFFENSE:
			if play.result == gameDefs.RESULT_TURNOVER:
				play.result = gameDefs.RESULT_DEFENSIVE_TURNOVER
			elif play.result == gameDefs.RESULT_KICK_RECEIVED:
				play.result = gameDefs.RESULT_DEFENSIVE_TURNOVER
			recovererName = event.offense1
		elif nextEvent.recoveryType == gameDefs.RECOVERY_DEFENSE:
			if play.result == gameDefs.RESULT_ADVANCE_DOWN:
				play.result = gameDefs.RESULT_TURNOVER
			recovererName = event.defense1
			
		commaLoc = item.find(',', recoverLoc, nextPlayLoc)
		if commaLoc != -1:
			name = recovererName.lower() + ' for '
			nameLoc = item.find(name, commaLoc, nextPlayLoc)
			if nameLoc != -1 and nameLoc < nextPlayLoc:
				if play.didChangePoss(event) is not (nextEvent.recoveryType == gameDefs.RECOVERY_OFFENSE):
					advanceLoc = nameLoc
				else:
					returnLoc = nameLoc
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
	
	##### parser2 changes #####
	
	if item.find(' no play', penaltyLoc, penaltyLoc2) != -1:
		play.events = []
		event.startingYard = play.startingYard
		play.events.append(event)
		play.result = gameDefs.RESULT_REPEAT_DOWN
	
	##### end parser2 changes #####
	
	i = penaltyLoc+9
	while i < len(item) and not item[i].isdigit():
		i += 1
	gain = getGain(drive, event, item[i:penaltyLoc2], True)
	
	##### parser2 changes #####
	
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
	
	##### end parser2 changes #####
	
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
			if automaticFirstDown:
				play.result = gameDefs.RESULT_FIRST_DOWN
		elif play.result == gameDefs.RESULT_REPEAT_DOWN:
			if lossOfDown:
				play.result = gameDefs.RESULT_ADVANCE_DOWN
			if automaticFirstDown:
				play.result = gameDefs.RESULT_FIRST_DOWN
	loc = penaltyLoc2
	if acceptedLoc != -1 and acceptedLoc < loc:
		loc = acceptedLoc
	if declinedLoc != -1 and declinedLoc < loc:
		loc = declinedLoc
	if offsettingLoc != -1 and offsettingLoc < loc:
		loc = offsettingLoc
	getDefenderNames(event, item, itemWNames, penaltyLoc, loc, ' on ')
	if offensivePenalty:
		event.offense1 = event.defense1
		event.defense1 = ''
	event.endingYard = event.startingYard + gain
	# check to see if the penalty will result in a first down
	if play.startingYard + int(play.distance) <= event.endingYard:
		if play.result < gameDefs.RESULT_FIRST_DOWN:
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
			play.result = gameDefs.RESULT_DEFENSIVE_TOUCHBACK
			event.endingYard = 0
			play.endingYard = 0
		else:
			play.result = gameDefs.RESULT_TOUCHBACK
			event.endingYard = 100
			play.endingYard = 100

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

def removeBlockers(event, item, itemWNames, playLoc, recoverLoc, nextPlayLoc):
	# check to see if this is beyond the next play location
	# if so, remove it to avoid double names
	blockedByLoc = item.find('blocked by ', playLoc)
	if blockedByLoc > recoverLoc or blockedByLoc > nextPlayLoc:
		defenderName = event.defense1
		before = item[0:blockedByLoc]
		beforeWNames = itemWNames[0:blockedByLoc]
		# 11 is the length of 'blocked by '
		endNameLoc = blockedByLoc+11+len(defenderName)
		if endNameLoc < len(item):
			after = item[endNameLoc:]
			afterWNames = itemWNames[endNameLoc:]
			item = before + after
			itemWNames = beforeWNames + afterWNames
		else:
			item = before
			itemWNames = beforeWNames
	return [item, itemWNames]

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
	andLoc = str.find(' and ')
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
	if andLoc != -1 and andLoc < loc:
		loc = andLoc
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

def convertDate2(dateString):
	dashLoc = dateString.find('-')
	dashLoc2 = dateString.find('-', dashLoc+1)
	
	day = int(dateString[:dashLoc])
	monthStr = dateString[dashLoc+1:dashLoc2]
	year = int(dateString[dashLoc2+1:])
	year += 2000
	
	if monthStr == 'AUG':
		month = 8
	elif monthStr == 'SEP':
		month = 9
	elif monthStr == 'OCT':
		month = 10
	elif monthStr == 'NOV':
		month = 11
	elif monthStr == 'DEC':
		month = 12
	elif monthStr == 'JAN':
		month = 1
	return year, month, day

if __name__ == '__main__':
    import sys
    print geturlstring(sys.argv[1])
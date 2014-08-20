import urllib
import MySQLdb
import gameDefs
import cfbdb
import parser2

Game = gameDefs.Game
Drive = gameDefs.Drive
Play = gameDefs.Play
Event = gameDefs.Event

def geturlstring(page):
	sock = urllib.urlopen(page)
	htmlSource = sock.read()
	sock.close()
	return htmlSource

def getsked(numWeeks = 17, numGames = 20000):
	gameIds = []
	
	year = 2008
	week = 0
	if numWeeks > 17:
		numWeeks = 17
	while week < numWeeks:
		page = 'http://sports.espn.go.com/ncf/schedules'
		page += '?year=' + str(year) + '&week=' + str(week+1) + '&season=2&groupId=80'
		urlstring = geturlstring(page)
		ids = getgameids(urlstring)
		gameIds.extend(ids)
		week += 1
	
	#conn = MySQLdb.connect(host = "localhost", user = "erik", passwd = "erj007", db = "test")
	conn = MySQLdb.connect(host = "localhost", db = "test")
	cursor = conn.cursor()
	#cursor.execute("SELECT VERSION()")
	#row = cursor.fetchone()
	#print "server version:", row[0]
	
	cfbdb.createTables(cursor)
	
	#leads = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	
	i = 0
	numGameIds = len(gameIds)
	if numGames > numGameIds:
		numGames = numGameIds
	while i < numGames:
		gameId = gameIds[i]
		page = 'http://sports.espn.go.com/ncf/playbyplay?gameId=' + gameId + '&period=0'
		urlstring = geturlstring(page)
		game = parsePlayByPlay(urlstring)
		if game:
			game.gameID = i
			game.calcResults()
			#readOne(game, leads)
			cfbdb.insertGame(game, cursor)
			cfbdb.verifyGame(game.gameID, cursor)
		i += 1
	
	cursor.close()
	conn.close()
	
	#print leads

def getgame(weekNum, gameNum):
	if weekNum > 17:
		weekNum = 17
	page = 'http://sports.espn.go.com/ncf/schedules'
	page += '?year=2008&week=' + str(weekNum) + '&season=2&groupId=80'
	urlstring = geturlstring(page)
	gameIds = getgameids(urlstring)
	
	conn = MySQLdb.connect(host = "localhost", db = "test")
	cursor = conn.cursor()
	
	cfbdb.createTables(cursor)
	
	numGameIds = len(gameIds)
	if gameNum > numGameIds:
		gameNum = numGameIds
	gameId = gameIds[gameNum]
	page = 'http://sports.espn.go.com/ncf/playbyplay?gameId=' + gameId + '&period=0'
	urlstring = geturlstring(page)
	game = parsePlayByPlay(urlstring)
	if game:
		game.gameID = gameNum
		game.calcResults()
		cfbdb.insertGame(game, cursor)
		cfbdb.verifyGame(game.gameID, cursor)
	
	cursor.close()
	conn.close()

def getgameids(urlstring):
	gameIds = []
	loc = urlstring.find('boxscore?gameId=')
	while loc != -1:
		start = loc + 16
		loc = start
		while urlstring[loc].isdigit():
			loc += 1
		gameId = urlstring[start:loc]
		gameIds.append(gameId)
		loc = urlstring.find('boxscore?gameId=', loc)
	return gameIds

def test():
	#url = 'http://sports.espn.go.com/ncf/playbyplay?gameId=272440235&period=0'
	#urlstring = geturlstring(url)
	f = file('playbyplay.htm')
	urlstring = f.read()
	game = parsePlayByPlay(urlstring)
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

#def t(url):
def t():
	url = 'http://www.calbears.com/sports/m-footbl/stats/2008-2009/msucal.html#GAME.PLY'
	urlstring = geturlstring(url)
	readTwo(urlstring)

def readOne(game, leads):
	if len(game.drives) <= 1:
		return
	
	f = open('test.txt', 'w')
		
	homeScore = 0
	awayScore = 0
	
	quarter = 1
	homeScore3Q = 0
	awayScore3Q = 0
	
	i = 0
	while i < len(game.drives):
		drive = drives[i]
		
		j = 0
		while j < len(drive.plays):
			play = drive.plays[j]
		
			if play.quarter != quarter:
				quarter = play.quarter
				if quarter == 4:
					homeScore3Q = homeScore
					awayScore3Q = awayScore
			
			j += 1
		
		points = drive.pointsThisDrive
		if drive.homePoss:
			homeScore += points
		else:
			awayScore += points
		
		i += 1
	
	#p = plays[0]
	#if p.homeScore != homeScore:
	#	print p.teamPoss + ' @ ' + p.teamDef
	#	print "Home Score doesn't add up : " + str(p.homeScore) + " vs. " + str(homeScore)
	#if p.awayScore != awayScore:
	#	print p.teamPoss + ' @ ' + p.teamDef
	#	print "Away Score doesn't add up : " + str(p.awayScore) + " vs. " + str(awayScore)
	#print "Home Score : " + str(p.homeScore) + " vs. " + str(homeScore)
	#print "Away Score : " + str(p.awayScore) + " vs. " + str(awayScore)
	
	if True:
	#if p.homeScore == homeScore and p.awayScore == awayScore:
		homeLead3Q = homeScore3Q - awayScore3Q
		homeMargin = homeScore - awayScore
		leads[0] += 1
		if homeMargin > 0:
			if homeLead3Q > 17:
				leads[1] += 1
			elif homeLead3Q > 9:
				leads[2] += 1
			elif homeLead3Q > 4:
				leads[3] += 1
			elif homeLead3Q > 0:
				leads[4] += 1
			elif homeLead3Q == 0:
				leads[5] += 1
			elif homeLead3Q > -4:
				leads[6] += 1
			elif homeLead3Q > -9:
				leads[7] += 1
			elif homeLead3Q > -17:
				leads[8] += 1
			else:
				leads[9] += 1
			if leads[10] < -homeLead3Q:
				leads[10] = -homeLead3Q
		if homeMargin < 0:
			if homeLead3Q < -17:
				leads[1] += 1
			elif homeLead3Q < -9:
				leads[2] += 1
			elif homeLead3Q < -4:
				leads[3] += 1
			elif homeLead3Q < 0:
				leads[4] += 1
			elif homeLead3Q == 0:
				leads[5] += 1
			elif homeLead3Q < 4:
				leads[6] += 1
			elif homeLead3Q < 9:
				leads[7] += 1
			elif homeLead3Q < 17:
				leads[8] += 1
			else:
				leads[9] += 1
			if leads[10] < homeLead3Q:
				leads[10] = homeLead3Q
	
	#f.write("Play\tQ\tAway\tAway Score\tAway O/D\tHome\tHome Score\tHome O/D\t")
	#f.write("Offense\tDefense\tLEADER\tTRAILER\tPOSS PTS\tQB\tDown\tDistance\tYdLine\t")
	#f.write("Run/Pass\tPlayer\tYards\tTackler 1\tTackler 2\tRESULT\tKicker\tKickYds\t")
	#f.write("Returner\tKickRet\tNetKick\tFF\tFR\tINT\tGameMargin\tClose?")
	
	#i = 1
	#while i < len(plays):
	#	play = plays[i]
		
		#play.outputSelf(f, i)
	#	i += 1
		
	#	if i < len(plays):
			#print str(play.startingYard)
			#play.printSelf()
			#print play.body
			#print str(play.nextStartingYard())
			#play.printSelf()
			#if play.didChangePoss():
			#	print 'Change of Possession'
	#		nextPlay = plays[i]
	#		if play.nextStartingYard() != nextPlay.startingYard:
	#			if play.quarter == 2 and nextPlay.quarter == 3:
	#				continue
	#			elif play.touchdown or play.fieldGoal or play.tryDown or play.safety:
	#				continue
	#			if abs(play.nextStartingYard() - nextPlay.startingYard) <= 1:
	#				continue
				#print 'Play ends at ' + str(play.nextStartingYard())
				#if play.didChangePoss():
				#	print 'Change of Possession'
				#print play.body
				#play.printSelf()
				#print 'Next play starts at ' + str(nextPlay.startingYard)
				#print nextPlay.body
				#nextPlay.printSelf()
	
def parsePlayByPlay(urlstring):
	# get full names and Ids
	# get visiting teamId
	loc = urlstring.find('teamId=')
	loc2 = urlstring.find('"', loc)
	if loc == -1 or loc2 == -1:
		return []
	teamId1 = int(urlstring[loc+7:loc2])
	# get visiting team full name
	loc = urlstring.find('</a>', loc)
	if urlstring[loc+4:loc+9] == '<span':
		loc = urlstring.find('</span>', loc) + 4
	loc2 = loc
	while not urlstring[loc2].isdigit():
		loc2 += 1
	teamName1 = urlstring[loc+4:loc2-1]
	loc3 = loc2
	while urlstring[loc3].isdigit():
		loc3 += 1
	teamScore1 = int(urlstring[loc2:loc3])
	# get second teamId
	loc = urlstring.find('teamId=', loc)
	loc2 = urlstring.find('"', loc)
	teamId2 = int(urlstring[loc+7:loc2])
	# get home team full name
	loc = urlstring.find('</a>', loc)
	if urlstring[loc+4:loc+9] == '<span':
		loc = urlstring.find('</span>', loc) + 4
	loc2 = loc
	while not urlstring[loc2].isdigit():
		loc2 += 1
	teamName2 = urlstring[loc+4:loc2-1]
	loc3 = loc2
	while urlstring[loc3].isdigit():
		loc3 += 1
	teamScore2 = int(urlstring[loc2:loc3])
	#print teamName1 + ' @ ' + teamName2
	
	# find time and date
	loc2 = urlstring.find('ET, ', loc)
	loc = urlstring.rfind('<div>', 0, loc2)
	time = urlstring[loc+5:loc2]
	loc3 = urlstring.find('</div>', loc2)
	date = urlstring[loc2+4:loc3]
	# find venue
	loc = urlstring.find('<div>', loc3)
	loc2 = urlstring.find('</div>', loc)
	venue = urlstring[loc+5:loc2]
	# find city
	loc = urlstring.find('<div>', loc2)
	loc2 = urlstring.find('</div>', loc)
	city = urlstring[loc+5:loc2]
	
	time = convertTime(time)
	year, month, day = convertDate(date)
	
	# find play by play
	loc = urlstring.find('gp-body', loc)
	loc2 = urlstring.find('gp-body', loc+1)
	playByPlay = urlstring[loc:loc2]
	# separate lines
	rows = []
	loc = playByPlay.find('<tr')
	while loc != -1:
		loc2 = playByPlay.find('</tr>', loc)
		row = playByPlay[loc:loc2]
		#print row
		rowList = parseRow2(row)
		rows.append(rowList)
		loc = playByPlay.find('<tr', loc2)
		
	if len(rows) == 0:
		print 'No Play By Play'
		return None
	
	# placeholders
	medName1 = ''
	medName2 = ''
	shortName1 = teamName1
	shortName2 = teamName2
	
	# figure out medNames
	i = 0
	while medName1 == '' or medName2 == '':
		rowList = rows[i]
		rest = ' '.join(rowList[1:])
		rest = rest.replace('(','')
		rest = rest.replace(')','')
		rest = rest.replace('  ', ' ')
		restLower = rest.lower()
		toTheLoc = rest.find(' to the ')
		if toTheLoc != -1:
			space1 = toTheLoc+7
			space2 = rest.find(' ', space1+1)
			medName = rest[space1+1:space2]
			
			if medName == '50':
				pass
			elif medName[0] == teamName1[0] and medName[0] != teamName2[0]:
				medName1 = medName
				#print 'teamName1 = ' + teamName1 + ', medName1 = ' + medName1
			elif medName[0] != teamName1[0] and medName[0] == teamName2[0]:
				medName2 = medName
				#print 'teamName2 = ' + teamName2 + ', medName2 = ' + medName2
			elif (medName1 == '') and (medName2 != '') and (medName != medName2):
				medName1 = medName
				#print 'teamName1 = ' + teamName1 + ', medName1 = ' + medName1
			elif (medName2 == '') and (medName1 != '') and (medName != medName1):
				medName2 = medName
				#print 'teamName2 = ' + teamName2 + ', medName2 = ' + medName2
			else:
				j = 1
				while j < len(medName):
					letter = medName[j]
					oneLoc = teamName1.find(letter)
					twoLoc = teamName2.find(letter)
					if oneLoc != -1 and twoLoc == -1:
						medName1 = medName
						#print 'teamName1 = ' + teamName1 + ', medName1 = ' + medName1
						break
					elif oneLoc == -1 and twoLoc != -1:
						medName2 = medName
						#print 'teamName2 = ' + teamName2 + ', medName2 = ' + medName2
						break
					elif oneLoc < twoLoc:
						medName1 = medName
						#print 'teamName1 = ' + teamName1 + ', medName1 = ' + medName1
						break
					elif oneLoc > twoLoc:
						medName2 = medName
						#print 'teamName2 = ' + teamName2 + ', medName2 = ' + medName2
						break
					else:
						j += 1
		i += 1
	
	g = Game(time, year, month, day, venue, city, teamName1, teamName2, teamScore1, teamScore2)
	
	# set up variables
	qtr = 0
	homePoss = False
	teamPoss = teamName1
	teamDef = teamName2
	
	quarterTurn = False
	
	# flag for printing rows -- for testing purposes only
	flag = False
	p = Play(0, 0, 0, 0)
	
	# process rows
	i = 0
	while i < len(rows):
		rowList = rows[i]
		first = rowList[0]
		#print '#first# : ' + first
		#print ' '.join(rowList)
		#rest = ' '.join(rowList[1:]).strip(' &nbsp;')
		if len(rowList) > 1:
			rest = rowList[1]
		else:
			rest = ''
		rest = rest.replace('(','')
		rest = rest.replace(')','')
		rest = rest.replace('  ', ' ')
		restLower = rest.lower()
		if first.find('Quarter') != -1:
			if first.find('1st') != -1:
				qtr = 1
				shortName1 = rowList[2]
				shortName2 = rowList[3]
			elif first.find('2nd') != -1:
				qtr = 2
				quarterTurn = True
			elif first.find('3rd') != -1:
				qtr = 3
			elif first.find('4th') != -1:
				qtr = 4
				quarterTurn = True
			elif first.find('5th') != -1:
				qtr = 5
			elif first.find('6th') != -1:
				qtr = 6
			elif first.find('7th') != -1:
				qtr = 7
			elif first.find('8th') != -1:
				qtr = 8
			elif first.find('9th') != -1:
				qtr = 9
			elif first.find('10th') != -1:
				qtr = 10
			elif first.find('11th') != -1:
				qtr = 11
			#print '>> [quarter ' + str(qtr) + '] ' + ' '.join(rowList)
		elif first.find('DRIVE TOTALS') != -1:
			pass
			#print '>> [drive totals] ' + ' '.join(rowList)
		elif first.find(teamName1 + ' at ') != -1:
			if quarterTurn and not homePoss:
				quarterTurn = False
			else:
				homePoss = False
				teamPoss = teamName1
				teamDef = teamName2
				d = Drive(homePoss, teamName1, teamName2, medName1, medName2)
				g.drives.append(d)
				#print '>> [visitor] ' + ' '.join(rowList)
			if quarterTurn:
				quarterTurn = False
		elif first.find(teamName2 + ' at ') != -1:
			if quarterTurn and homePoss:
				quarterTurn = False
			else:
				homePoss = True
				teamPoss = teamName2
				teamDef = teamName1
				d = Drive(homePoss, teamName2, teamName1, medName2, medName1)
				g.drives.append(d)
				#print '>> [home] ' + ' '.join(rowList)
			if quarterTurn:
				quarterTurn = False
		elif first.find(shortName1) != -1:
			down, distance, yardline = ddy(first, shortName1, homePoss)
			p = Play(qtr, down, distance, yardline)
			touchLoc = restLower.find('touchdown')
			if touchLoc != -1 and (restLower.find('extra point') != -1 or restLower.find('two-point') != -1):
				touchRest = rest[0:touchLoc+10]
				touchRestLower = restLower[0:touchLoc+10]
				d.plays.append(p)
				#getPlay(p, d, touchRestLower, touchRest)
				parser2.getPlay(g, d, p, touchRestLower, touchRest)
				p = Play(qtr, -1, 3, 97)
				rest = rest[touchLoc+10:]
				restLower = restLower[touchLoc+10:]
			d.plays.append(p)			
			#getPlay(p, d, restLower, rest)
			parser2.getPlay(g, d, p, restLower, rest)
			#print ' '.join(rowList)
			#p.printSelf()
			#print '>> [' + teamPoss + ' - Dn: ' + str(down) + ', Dist: ' + str(distance) + ', Yd: ' + str(yardline) + ' ] ' + ' '.join(rowList)
		elif first.find(shortName2) != -1:
			down, distance, yardline = ddy(first, shortName2, not homePoss)
			p = Play(qtr, down, distance, yardline)
			touchLoc = restLower.find('touchdown')
			if touchLoc != -1 and (restLower.find('extra point') != -1 or restLower.find('two-point') != -1):
				touchRest = rest[0:touchLoc+10]
				touchRestLower = restLower[0:touchLoc+10]
				d.plays.append(p)
				#getPlay(p, d, touchRestLower, touchRest)
				parser2.getPlay(g, d, p, touchRestLower, touchRest)
				if p.result == gameDefs.RESULT_DEFENSIVE_TOUCHDOWN:
					homePoss = not homePoss
					if homePoss:
						d = Drive(homePoss, teamName2, teamName1, medName2, medName1)
					else:
						d = Drive(homePoss, teamName1, teamName2, medName1, medName2)
					g.drives.append(d)
				p = Play(qtr, -1, 3, 97)
				rest = rest[touchLoc+10:]
				restLower = restLower[touchLoc+10:]
			d.plays.append(p)
			#getPlay(p, d, restLower, rest)
			parser2.getPlay(g, d, p, restLower, rest)
			#print ' '.join(rowList)
			#p.printSelf()
			#print '>> [' + teamPoss + ' - Dn: ' + str(down) + ', Dist: ' + str(distance) + ', Yd: ' + str(yardline) + ' ] ' + ' '.join(rowList)
		elif first.find('&nbsp;') != -1 and rest != '':
			down = 0
			distance = 0
			yardline = 0
			if len(d.plays) > 0:
				prevPlay = d.plays[len(d.plays)-1]
				prevPlay.calcResults(True)
				if prevPlay.result == gameDefs.RESULT_NONE:
					playsBack = 1
					while len(d.plays) > playsBack and (prevPlay.result == gameDefs.RESULT_NONE):
						prevPlay = d.plays[len(d.plays)-(playsBack+1)]
						prevPlay.calcResults(True)
						playsBack += 1
				if (prevPlay.down == -1) or (prevPlay.result == gameDefs.RESULT_FIELD_GOAL):
					yardline = 30
				elif (prevPlay.result == gameDefs.RESULT_SAFETY) or (prevPlay.result == gameDefs.RESULT_DEFENSIVE_SAFETY):
					yardline = 20
				else:
					down = prevPlay.down
					#if prevPlay.result != gameDefs.RESULT_PENALTY:
					#	down += 1
					distance = int(prevPlay.distance) - (prevPlay.endingYard - prevPlay.startingYard)
					if distance <= 0:
						distance = 10
					yardline = prevPlay.endingYard
					if yardline + distance > 100:
						distance = 100 - yardline
			else:
				yardline = 30
			p = Play(qtr, down, distance, yardline)
			touchLoc = restLower.find('touchdown')
			if touchLoc != -1 and (restLower.find('extra point') != -1 or restLower.find('two-point') != -1):
				touchRest = rest[0:touchLoc+10]
				touchRestLower = restLower[0:touchLoc+10]
				d.plays.append(p)
				#getPlay(p, d, touchRestLower, touchRest)
				parser2.getPlay(g, d, p, touchRestLower, touchRest)
				if p.result == gameDefs.RESULT_DEFENSIVE_TOUCHDOWN:
					homePoss = not homePoss
					if homePoss:
						d = Drive(homePoss, teamName2, teamName1, medName2, medName1)
					else:
						d = Drive(homePoss, teamName1, teamName2, medName1, medName2)
					g.drives.append(d)
				p = Play(qtr, -1, 3, 97)
				rest = rest[touchLoc+10:]
				restLower = restLower[touchLoc+10:]
			d.plays.append(p)
			#getPlay(p, d, restLower, rest)
			parser2.getPlay(g, d, p, restLower, rest)
			
			#print ' '.join(rowList)
			#p.printSelf()
			#print '>> [nothing] ' + ' '.join(rowList)
		else:
			pass
			#print '>> [???] ' + ' '.join(rowList)
		
		# look for previous off-setting fouls
		#if flag:
		#	p.printSelf()
		#	flag = False
		#elif p.body.find('off-setting') != -1:
		#	print 'Off-setting : ' + p.body
		#	p.printSelf()
		#	flag = True
		#elif p.body.find('blocked') != -1:
		#	print 'Blocked : ' + p.body
		#	p.printSelf()
		#	flag = True
		
		i += 1
	
	return g

def parseRow(row):
	loc = row.find('<')
	while loc != -1:
		loc2 = row.find('>', loc)
		row = row[:loc] + '#' + row[loc2+1:]
		loc = row.find('<')
	row.strip('#')
	rowList = row.split('#')
	rowList = filter(notEmpty, rowList)
	return rowList

def notEmpty(item):
	return item != ''

def parseRow2(row):
	items = []
	loc = row.find('<td')
	while loc != -1:
		loc2 = row.find('>', loc)
		loc3 = row.find('</td>', loc2)
		item = row[loc2+1:loc3]
		loc4 = item.find('<')
		while loc4 != -1:
			loc5 = item.find('>', loc4)
			item = item[0:loc4] + item[loc5+1:]
			loc4 = item.find('<')
		items.append(item)
		loc = row.find('<td', loc3)
		#print len(items)
		#print item
	return items

# for a give play, get the down, distance, and yardline
def ddy(item, name, oppSide):
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
	atLoc = item.find('at')
	distance = item[andLoc+4:atLoc-1]
	nameLoc = item.find(name)
	yardline = int(item[nameLoc+len(name)+1:])
	if oppSide:
		yardline = 100 - yardline
	if distance == 'Goal':
		distance = 100 - yardline
	return [down, distance, yardline]

def getPlay(play, drive, item, itemWNames):
	play.body = itemWNames
	gain = 0
	
	kickoffLoc = item.find(' kickoff')
	onsideLoc = item.find('on-side kick')
	fieldGoalLoc = item.find(' field goal')
	extraPointLoc = item.find(' extra point')
	if extraPointLoc == -1:
		extraPointLoc = item.find('blocked pat')
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
		event.offense1 = kickerName
		if item.find('missed', extraPointLoc, nextPlayLoc) != -1:
			play.result = gameDefs.RESULT_MISSED_FIELD_GOAL
			event.endingYard = event.startingYard
		elif item.find('good', 0, nextPlayLoc) != -1:
			play.result = gameDefs.RESULT_FIELD_GOAL
			event.endingYard = 100
		elif item.find('blocked', extraPointLoc, nextPlayLoc) != -1:
			#print "EP BLOCKED - " + item
			play.result = gameDefs.RESULT_TURNOVER_ON_DOWNS
			# recovery
			if recoverLoc != -1:
				if returnLoc != -1:
					recovery = item[recoverLoc+7:returnLoc]
				else:
					recovery = item[recoverLoc+7:]
				
				kickLength = getGain(drive, event, recovery)
				event.endingYard = event.startingYard + kickLength
				
				prevEvent = event
				event = Event()
				event.startingYard = prevEvent.endingYard
				play.events.append(event)
				
				event.eventType = gameDefs.EVENT_RECOVERY
							
				byLoc = item.find(' by ', recoverLoc+7, nextPlayLoc)
				if byLoc != -1:
					str = item[byLoc+4:nextPlayLoc]
					strWNames = itemWNames[byLoc+4:nextPlayLoc]
					recovererName = findName(str, strWNames)
					# look for which team recovered
					spaceLoc = recovererName.find(' ')
					if spaceLoc == -1:
						spaceLoc = len(recovererName)
					teamID = recovererName[0:spaceLoc]
					if teamID == drive.medPoss:
						# offense got it
						event.recoveryType = gameDefs.RECOVERY_OFFENSE
						recovererName = recovererName[spaceLoc+1:]
					elif teamID == drive.medDef:
						# defense got it
						event.recoveryType = gameDefs.RECOVERY_DEFENSE
						recovererName = recovererName[spaceLoc+1:]
						play.result = gameDefs.RESULT_TURNOVER
					event.offense1 = recovererName
					tackledLoc = item.find(' tackled by ', byLoc, nextPlayLoc)
					if tackledLoc != -1:
						getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
				
			event.endingYard = event.startingYard
			#if item.find('two-point') != -1:
			#	if event.recoveryType == gameDefs.RECOVERY_DEFENSE:
			#		play.result = gameDefs.RESULT_DEFENSIVE_TOUCHDOWN
			#	else:
			#		play.result = gameDefs.RESULT_TOUCHDOWN
			#if item.find('2 defensive point conversion') != -1:
			#	play.result = gameDefs.RESULT_DEFENSIVE_TOUCHDOWN
	# two-point conversion
	elif item.find('conversion', 0, nextPlayLoc) != -1:
		#print "2PC - " + item
		play.down = -1
		play.distance = 3
		play.startingYard = 97
		event.startingYard = 97
		attemptLoc = item.find(' attempt,', 0, nextPlayLoc)
		passLoc = item.find(' pass ', attemptLoc, nextPlayLoc)
		rushLoc = item.find(' rush ', attemptLoc, nextPlayLoc)
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
		event.offense1 = kickerName
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
			#play.result = gameDefs.RESULT_ADVANCE_DOWN
			play.result = gameDefs.RESULT_MISSED_FIELD_GOAL
			# recovery
			if recoverLoc != -1:
				if returnLoc != -1:
					recovery = item[recoverLoc+7:returnLoc]
				else:
					recovery = item[recoverLoc+7:]
				
				kickLength = getGain(drive, event, recovery)
				event.endingYard = event.startingYard + kickLength
				
				prevEvent = event
				event = Event()
				event.startingYard = prevEvent.endingYard
				play.events.append(event)
				
				event.eventType = gameDefs.EVENT_RECOVERY
							
				byLoc = item.find(' by ', recoverLoc+7, nextPlayLoc)
				if byLoc != -1:
					str = item[byLoc+4:nextPlayLoc]
					strWNames = itemWNames[byLoc+4:nextPlayLoc]
					recovererName = findName(str, strWNames)
					# look for which team recovered
					spaceLoc = recovererName.find(' ')
					if spaceLoc == -1:
						spaceLoc = len(recovererName)
					teamID = recovererName[0:spaceLoc]
					if teamID == drive.medPoss:
						# offense got it
						event.recoveryType = gameDefs.RECOVERY_OFFENSE
						recovererName = recovererName[spaceLoc+1:]
					elif teamID == drive.medDef:
						# defense got it
						event.recoveryType = gameDefs.RECOVERY_DEFENSE
						recovererName = recovererName[spaceLoc+1:]
						play.result = gameDefs.RESULT_TURNOVER
					event.offense1 = recovererName
					tackledLoc = item.find(' tackled by ', byLoc, nextPlayLoc)
					if tackledLoc != -1:
						getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
			
			event.endingYard = event.startingYard
	# kickoff
	elif kickoffLoc != -1:
		event.eventType = gameDefs.EVENT_KICKOFF
		play.down = 0
		kickerName = itemWNames[0:kickoffLoc]
		event.offense1 = kickerName
		kickLength = getGain(drive, event, item[kickoffLoc+8:nextPlayLoc])
		if item.find('out-of-bounds', kickoffLoc, nextPlayLoc) != -1:
			# except during 2007, when this number was 35
			event.endingYard = event.startingYard + 30 # usually 60
		else:
			event.endingYard = event.startingYard + kickLength
		play.result = gameDefs.RESULT_KICK_RECEIVED
	# on-side kick
	elif onsideLoc != -1:
		event.eventType = gameDefs.EVENT_ONSIDE_KICK
		play.down = 0
		kickerName = itemWNames[0:onsideLoc]
		event.offense1 = kickerName
		
		# recovery
		if recoverLoc != -1:
			if returnLoc != -1:
				recovery = item[recoverLoc+7:returnLoc]
			else:
				recovery = item[recoverLoc+7:]
				
			kickLength = getGain(drive, event, recovery)
			event.endingYard = event.startingYard + kickLength
			
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
				recovererName = findName(str, strWNames)
				# look for which team recovered
				spaceLoc = recovererName.find(' ')
				if spaceLoc == -1:
					spaceLoc = len(recovererName)
				teamID = recovererName[0:spaceLoc]
				if teamID == drive.medPoss or teamID == drive.teamPoss:
					# offense got it
					event.recoveryType = gameDefs.RECOVERY_OFFENSE
					recovererName = recovererName[spaceLoc+1:]
					play.result = gameDefs.RESULT_ADVANCE_DOWN
				elif teamID == drive.medDef or teamID == drive.teamDef:
					# defense got it
					event.recoveryType = gameDefs.RECOVERY_DEFENSE
					recovererName = recovererName[spaceLoc+1:]
					play.result = gameDefs.RESULT_KICK_RECEIVED
				else:
					# no idea who recovered it
					play.result = gameDefs.RESULT_ADVANCE_DOWN
				event.offense1 = recovererName
				tackledLoc = item.find(' tackled by ', byLoc, nextPlayLoc)
				if tackledLoc != -1:
					getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
			else:
				play.result = gameDefs.RESULT_ADVANCE_DOWN
		else:
			kickLength = getGain(drive, event, item[onsideLoc+13:nextPlayLoc])
			event.endingYard = event.startingYard + kickLength
			play.result = gameDefs.RESULT_ADVANCE_DOWN
	# punt
	elif puntLoc != -1:
		event.eventType = gameDefs.EVENT_PUNT
		kickerName = itemWNames[0:puntLoc]
		event.offense1 = kickerName
		if item.find('blocked', puntLoc, nextPlayLoc) != -1:
			event.eventType = gameDefs.EVENT_BLOCKED_PUNT
			play.result = gameDefs.RESULT_ADVANCE_DOWN
			# recovery
			if recoverLoc != -1:
				if returnLoc != -1:
					recovery = item[recoverLoc+7:returnLoc]
				else:
					recovery = item[recoverLoc+7:]
					
				puntLength = getGain(drive, event, recovery)
				event.endingYard = event.startingYard + puntLength
				
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
					recovererName = findName(str, strWNames)
					# look for which team recovered
					spaceLoc = recovererName.find(' ')
					if spaceLoc == -1:
						spaceLoc = len(recovererName)
					teamID = recovererName[0:spaceLoc]
					if teamID == drive.medPoss:
						# offense got it
						event.recoveryType = gameDefs.RECOVERY_OFFENSE
						recovererName = recovererName[spaceLoc+1:]
					elif teamID == drive.medDef:
						# defense got it
						event.recoveryType = gameDefs.RECOVERY_DEFENSE
						play.result = gameDefs.RESULT_TURNOVER
						recovererName = recovererName[spaceLoc+1:]
					event.offense1 = recovererName
					tackledLoc = item.find(' tackled by ', byLoc, nextPlayLoc)
					if tackledLoc != -1:
						getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
			else:
				event.endingYard = event.startingYard
		else:
			fairCatchLoc = item.find(' fair catch by ', puntLoc, nextPlayLoc)
			if fairCatchLoc != -1:
				getDefenderNames(event, item, itemWNames, fairCatchLoc+15, nextPlayLoc)
			puntLength = getGain(drive, event, item[puntLoc+5:nextPlayLoc])
			event.endingYard = event.startingYard + puntLength
			play.result = gameDefs.RESULT_KICK_RECEIVED
	# rush
	elif rushLoc != -1:
		event.eventType = gameDefs.EVENT_RUSH
		rusherName = itemWNames[0:rushLoc]
		event.offense1 = rusherName
		gain = getGain(drive, event, item[rushLoc+5:nextPlayLoc])
		event.endingYard = event.startingYard + gain
		tackledLoc = item.find(' tackled by ', rushLoc, nextPlayLoc)
		if tackledLoc != -1:
			getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
		play.result = gameDefs.RESULT_ADVANCE_DOWN
	# sack
	elif sackLoc != -1:
		event.eventType = gameDefs.EVENT_SACK
		qbName = itemWNames[0:sackLoc]
		event.offense1 = qbName
		byLoc = item.find(' by ', sackLoc, nextPlayLoc)
		if byLoc != -1:
			getDefenderNames(event, item, itemWNames, byLoc+4, nextPlayLoc)
		gain = getGain(drive, event, item[sackLoc+7:nextPlayLoc])
		if gain > 0:
			gain = -gain
		event.endingYard = event.startingYard + gain
		play.result = gameDefs.RESULT_ADVANCE_DOWN
	# scramble
	elif scrambleLoc != -1:
		event.eventType = gameDefs.EVENT_RUSH
		qbName = itemWNames[0:scrambleLoc]
		event.offense1 = qbName
		gain = getGain(drive, event, item[rushLoc+9:nextPlayLoc])
		event.endingYard = event.startingYard + gain
		tackledLoc = item.find(' tackled by ', scrambleLoc, nextPlayLoc)
		if tackledLoc != -1:
			getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
		play.result = gameDefs.RESULT_ADVANCE_DOWN
	# pass
	elif passLoc != -1 and (penaltyLoc == -1 or passLoc < penaltyLoc):
		event.eventType = gameDefs.EVENT_PASS
		qbName = itemWNames[0:passLoc]
		event.offense1 = qbName
		toLoc = item.find(' to ', passLoc, nextPlayLoc)
		if toLoc != -1:
			forLoc = item.find(' for ', toLoc, nextPlayLoc)
			commaLoc = item.find(',', toLoc, nextPlayLoc)
			periodLoc = item.find('.', toLoc, nextPlayLoc)
			if periodLoc == toLoc+5:
				periodLoc = len(itemWNames)
				periodLoc = item.find('.', toLoc+8, nextPlayLoc)
			if periodLoc == toLoc+6:
				periodLoc = len(itemWNames)
				periodLoc = item.find('.', toLoc+9, nextPlayLoc)
			loc = len(itemWNames)
			if forLoc != -1 and forLoc < loc:
				loc = forLoc
			if commaLoc != -1 and commaLoc < loc:
				loc = commaLoc
			if periodLoc != -1 and periodLoc < loc:
				loc = periodLoc
			receiverName = itemWNames[toLoc+4:loc]
			event.offense2 = receiverName.strip()
		if item.find('incomplete', passLoc, nextPlayLoc) != -1:
			gain = 0
			brokenLoc = item.find(' broken up by ', passLoc, nextPlayLoc)
			if brokenLoc != -1:
				getDefenderNames(event, item, itemWNames, brokenLoc+14, nextPlayLoc)
		else:
			gain = getGain(drive, event, item[passLoc+5:nextPlayLoc])
		event.endingYard = event.startingYard + gain
		interceptionLoc = item.find('intercepted', passLoc, nextPlayLoc)
		if interceptionLoc != -1:
			event.eventType = gameDefs.EVENT_INTERCEPTION
			play.result = gameDefs.RESULT_TURNOVER
			event.offense2 = ''
			byLoc = item.find(' by ', interceptionLoc, nextPlayLoc)
			if byLoc != -1:
				getDefenderNames(event, item, itemWNames, byLoc+4, nextPlayLoc)
		else:
			tackledLoc = item.find(' tackled by ', passLoc, nextPlayLoc)
			if tackledLoc != -1:
				getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
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
			gain = getGain(drive, event, item[tackledLoc+9:nextPlayLoc])
			event.endingYard = event.startingYard + gain
			byLoc = item.find(' by ', tackledLoc, nextPlayLoc)
			if byLoc != -1:
				getDefenderNames(event, item, itemWNames, byLoc+4, nextPlayLoc)
			play.result = gameDefs.RESULT_ADVANCE_DOWN
	
	resolveResult(play, event, item, 0, nextPlayLoc)
	
	if play.down == 4 and play.result == gameDefs.RESULT_ADVANCE_DOWN:
		play.result = gameDefs.RESULT_TURNOVER_ON_DOWNS
	return 0

def getNextEvent(drive, play, prevEvent, item, itemWNames, advanceLoc, returnLoc, fumbleLoc, lateralLoc, penaltyLoc, nextPlayLoc):
	if prevEvent.eventType != gameDefs.EVENT_NULL:
		event = Event()
		event.startingYard = prevEvent.endingYard
		if prevEvent.eventType == gameDefs.EVENT_RUSH or prevEvent.eventType == gameDefs.EVENT_SACK:
			event.offense1 = prevEvent.offense1
		elif prevEvent.eventType == gameDefs.EVENT_RECOVERY or prevEvent.eventType == gameDefs.EVENT_RETURN:
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
	tackledLoc = item.find(' tackled by ', advanceLoc, nextPlayLoc)
	if tackledLoc != -1:
		getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
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
	
	byLoc = item.find(' by ', returnLoc, nextPlayLoc)
	if byLoc != -1:
		forLoc = item.find(' for ', byLoc, nextPlayLoc)
		commaLoc = item.find(',', byLoc, nextPlayLoc)
		periodLoc = item.find('.', byLoc, nextPlayLoc)
		if periodLoc == byLoc+5:
			periodLoc = len(itemWNames)
			periodLoc = item.find('.', byLoc+8, nextPlayLoc)
		if periodLoc == byLoc+6:
			periodLoc = len(itemWNames)
			periodLoc = item.find('.', byLoc+9, nextPlayLoc)
		loc = len(itemWNames)
		if forLoc != -1 and forLoc < loc:
			loc = forLoc
		if commaLoc != -1 and commaLoc < loc:
			loc = commaLoc
		if periodLoc != -1 and periodLoc < loc:
			loc = periodLoc
		returnerName = itemWNames[byLoc+4:loc]
		event.offense1 = returnerName.strip()
	spaceLoc = item.find(' ', returnLoc+1, nextPlayLoc)
	returnLength = getGain(drive, event, item[spaceLoc:nextPlayLoc])
	event.endingYard = event.startingYard + returnLength
	
	#print 'return: ' + item[returnLoc:nextPlayLoc]
	#print event.startingYard
	#print event.endingYard
	#print returnLength
	
	tackledLoc = item.find(' tackled by ', returnLoc, nextPlayLoc)
	if tackledLoc != -1:
		getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
	
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
	
	forcedLoc = item.find(' forced ', fumbleLoc, nextPlayLoc)
	recoverLoc = item.find(' recover', fumbleLoc, nextPlayLoc)
	# forcing
	if forcedLoc != -1:
		if recoverLoc != -1:
			forcing = item[forcedLoc+7:recoverLoc]
		elif returnLoc != -1:
			forcing = item[forcedLoc+7:returnLoc]
		else:
			forcing = item[forcedLoc+7:]
		nxtPlyLoc = nextPlayLoc - (forcedLoc+7)
		byLoc = forcing.find(' by ', 0, nxtPlyLoc)
		if byLoc != -1:
			atLoc = forcing.find(' at ', byLoc, nxtPlyLoc)
			commaLoc = forcing.find(',', byLoc, nxtPlyLoc)
			periodLoc = forcing.find('.', byLoc, nxtPlyLoc)
			if periodLoc == byLoc+5:
				periodLoc = len(forcing)
				periodLoc = forcing.find('.', byLoc+8, nxtPlyLoc)
			elif periodLoc == byLoc+6:
				periodLoc = len(forcing)
				periodLoc = forcing.find('.', byLoc+9, nxtPlyLoc)
			loc = len(forcing)
			if atLoc != -1 and atLoc < loc:
				loc = atLoc
			if commaLoc != -1 and commaLoc < loc:
				loc = commaLoc
			if periodLoc != -1 and periodLoc < loc:
				loc = periodLoc
			forcerName = itemWNames[forcedLoc+byLoc+11:forcedLoc+7+loc]
			event.defense1 = forcerName.strip()
	# recovery
	recovery = ''
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
			recovererName = findName(str, strWNames)
			# look for which team recovered
			spaceLoc = recovererName.find(' ')
			if spaceLoc == -1:
				spaceLoc = len(recovererName)
			teamID = recovererName[0:spaceLoc]
			if teamID == drive.medPoss:
				# offense got it
				event.recoveryType = gameDefs.RECOVERY_OFFENSE
				recovererName = recovererName[spaceLoc+1:]
				if play.result == gameDefs.RESULT_TURNOVER:
					play.result = gameDefs.RESULT_DEFENSIVE_TURNOVER
				elif play.result == gameDefs.RESULT_KICK_RECEIVED:
					play.result = gameDefs.RESULT_DEFENSIVE_TURNOVER
			elif teamID == drive.medDef:
				# defense got it
				event.recoveryType = gameDefs.RECOVERY_DEFENSE
				recovererName = recovererName[spaceLoc+1:]
				if play.result == gameDefs.RESULT_ADVANCE_DOWN:
					play.result = gameDefs.RESULT_TURNOVER
			event.offense1 = recovererName
			tackledLoc = item.find(' tackled by ', byLoc, nextPlayLoc)
			if tackledLoc != -1:
				getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
	
		commaLoc = item.find(',', recoverLoc, nextPlayLoc)
		if commaLoc != -1:
			name = event.offense1.lower() + ' for '
			nameLoc = item.find(name, commaLoc, nextPlayLoc)
			if nameLoc != -1 and nameLoc < nextPlayLoc:
				#if play.didChangePoss(prevEvent):
				#	print 'play.didChangePoss(prevEvent)'
				#if event.recoveryType == gameDefs.RECOVERY_OFFENSE:
				#	print 'event.recoveryType == gameDefs.RECOVERY_OFFENSE'
				if play.didChangePoss(prevEvent) is not (event.recoveryType == gameDefs.RECOVERY_OFFENSE):
					advanceLoc = nameLoc
				else:
					returnLoc = nameLoc
				nextPlayLoc = nameLoc
				#print 'Found one, at '
				#print nameLoc
				#print item
				#print advanceLoc
				#print returnLoc
				#print nextPlayLoc
				
				gain = getGain(drive, prevEvent, item[recoverLoc+7:nextPlayLoc])
				prevEvent.endingYard = prevEvent.startingYard + gain
				event.startingYard = prevEvent.endingYard
				event.endingYard = event.startingYard
	
	#elif returnLoc != -1:
	#	gain = getGain(drive, event, recovery)
	#	event.endingYard = event.startingYard + gain
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
	
	toLoc = item.find(' to ', lateralLoc, nextPlayLoc)
	if toLoc != -1:
		forLoc = item.find(' for ', toLoc, nextPlayLoc)
		commaLoc = item.find(',', toLoc, nextPlayLoc)
		periodLoc = item.find('.', toLoc, nextPlayLoc)
		if periodLoc == toLoc+5:
			periodLoc = len(itemWNames)
			periodLoc = item.find('.', toLoc+8, nextPlayLoc)
		if periodLoc == toLoc+6:
			periodLoc = len(itemWNames)
			periodLoc = item.find('.', toLoc+9, nextPlayLoc)
		loc = len(itemWNames)
		if forLoc != -1 and forLoc < loc:
			loc = forLoc
		if commaLoc != -1 and commaLoc < loc:
			loc = commaLoc
		if periodLoc != -1 and periodLoc < loc:
			loc = periodLoc
		receiverName = itemWNames[toLoc+4:loc]
		event.offense2 = receiverName.strip()
	gain = getGain(drive, event, item[lateralLoc+8:nextPlayLoc])
	event.endingYard = event.startingYard + gain
	tackledLoc = item.find(' tackled by ', lateralLoc, nextPlayLoc)
	if tackledLoc != -1:
		getDefenderNames(event, item, itemWNames, tackledLoc+12, nextPlayLoc)
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
	
	i = penaltyLoc+9
	while i < len(item) and not item[i].isdigit():
		i += 1
	gain = getGain(drive, event, item[i:penaltyLoc2], True)
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
			if automaticFirstDown:
				play.result = gameDefs.RESULT_FIRST_DOWN
		elif play.result == gameDefs.RESULT_REPEAT_DOWN:
			if lossOfDown:
				play.result = gameDefs.RESULT_ADVANCE_DOWN
			if automaticFirstDown:
				play.result = gameDefs.RESULT_FIRST_DOWN
	onLoc = item.find(' on ', penaltyLoc, penaltyLoc2)
	if onLoc != -1:
		commaLoc = item.find(',', onLoc, penaltyLoc2)
		periodLoc = item.find('.', onLoc, penaltyLoc2)
		if periodLoc == onLoc+5:
			periodLoc = len(itemWNames)
			periodLoc = item.find('.', onLoc+8)
		if periodLoc == onLoc+6:
			periodLoc = len(itemWNames)
			periodLoc = item.find('.', onLoc+9)
		loc = len(itemWNames)
		if acceptedLoc != -1 and acceptedLoc < loc:
			loc = acceptedLoc
		if declinedLoc != -1 and declinedLoc < loc:
			loc = declinedLoc
		if offsettingLoc != -1 and offsettingLoc < loc:
			loc = offsettingLoc
		if commaLoc != -1 and commaLoc < loc:
			loc = commaLoc
		if periodLoc != -1 and periodLoc < loc:
			loc = periodLoc
		penalizedName = itemWNames[onLoc+4:loc]
		if offensivePenalty:
			event.offense1 = penalizedName.strip()
		else:
			event.defense1 = penalizedName.strip()
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

def getDefenderNames(event, item, itemWNames, tackledLoc, nextPlayLoc):
	atLoc = item.find(' at ', tackledLoc, nextPlayLoc)
	forLoc = item.find(' for ', tackledLoc, nextPlayLoc)
	commaLoc = item.find(',', tackledLoc, nextPlayLoc)
	periodLoc = item.find('.', tackledLoc, nextPlayLoc)
	if periodLoc == tackledLoc+1:
		periodLoc = len(itemWNames)
		periodLoc = item.find('.', tackledLoc+4, nextPlayLoc)
	if periodLoc == tackledLoc+2:
		periodLoc = len(itemWNames)
		periodLoc = item.find('.', tackledLoc+5, nextPlayLoc)
	loc = len(itemWNames)
	if atLoc != -1 and atLoc < loc:
		loc = atLoc
	if forLoc != -1 and forLoc < loc:
		loc = forLoc
	if commaLoc != -1 and commaLoc < loc:
		loc = commaLoc
	if periodLoc != -1 and periodLoc < loc:
		loc = periodLoc
	tacklerName = itemWNames[tackledLoc:loc]
	andLoc = tacklerName.find(' and ')
	if andLoc != -1:
		tacklerName1 = tacklerName[0:andLoc]
		tacklerName2 = tacklerName[andLoc+5:]
		event.defense1 = tacklerName1.strip()
		event.defense2 = tacklerName2.strip()
	else:
		event.defense1 = tacklerName.strip()

def findName(str, strWNames):
	atLoc = str.find(' at ')
	inLoc = str.find(' in ')
	forLoc = str.find(' for ')
	andLoc = str.find(' and ')
	outOfBoundsLoc = str.find(' out-of-bounds')
	commaLoc = str.find(',')
	periodLoc = str.find('.')
	if periodLoc == 1:
		periodLoc = len(str)
		periodLoc = str.find('.', 3)
	elif periodLoc == 2:
		periodLoc = len(str)
		periodLoc = str.find('.', 5)
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
	if commaLoc != -1 and commaLoc < loc:
		loc = commaLoc
	if periodLoc != -1 and periodLoc < loc:
		loc = periodLoc
	return strWNames[0:loc].strip()

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

def convertTime(timeString):
	pm = timeString.find('PM')
	colonLoc = timeString.find(':')
	hour = int(timeString[0:colonLoc])
	if pm != -1:
		minute = int(timeString[colonLoc+1:pm])
		return (hour+12)*100+minute
	else:
		am = timeString.find('AM')
		minute = int(timeString[colonLoc+1:am])
		return hour*100+minute

def convertDate(dateString):
	commaLoc = dateString.find(',')
	augustLoc = dateString.find('August')
	septemberLoc = dateString.find('September')
	octoberLoc = dateString.find('October')
	novemberLoc = dateString.find('November')
	decemberLoc = dateString.find('December')
	januaryLoc = dateString.find('January')
	if augustLoc != -1:
		month = 8
		day = int(dateString[augustLoc+7:commaLoc])
		year = int(dateString[commaLoc+2:])
	elif septemberLoc != -1:
		month = 9
		day = int(dateString[septemberLoc+10:commaLoc])
		year = int(dateString[commaLoc+2:])
	elif octoberLoc != -1:
		month = 10
		day = int(dateString[octoberLoc+8:commaLoc])
		year = int(dateString[commaLoc+2:])
	elif novemberLoc != -1:
		month = 11
		day = int(dateString[novemberLoc+9:commaLoc])
		year = int(dateString[commaLoc+2:])
	elif decemberLoc != -1:
		month = 12
		day = int(dateString[decemberLoc+9:commaLoc])
		year = int(dateString[commaLoc+2:])
	elif januaryLoc != -1:
		month = 1
		day = int(dateString[januaryLoc+8:commaLoc])
		year = int(dateString[commaLoc+2:])
	return year, month, day

if __name__ == '__main__':
    import sys
    print geturlstring(sys.argv[1])
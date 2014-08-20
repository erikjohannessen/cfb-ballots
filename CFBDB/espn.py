import urllib
import MySQLdb
import gameDefs
import cfbdb
import parser

parsingDatabase = "parsingdb"
parsingHost = "localhost"
parsingUser = "root"

def getHtmlSource(page):
	sock = urllib.urlopen(page)
	htmlSource = sock.read()
	sock.close()
	return htmlSource

def test():
	game = getTestGame()
	if game:
		#game.gameID = 1
		
		conn = MySQLdb.connect(host = "localhost", db = "test")
		cursor = conn.cursor()
		cfbdb.createTables(cursor)
		cfbdb.insertGame(game, gameDefs.PARSER_ESPN, cursor)
		#cfbdb.verifyGame(game.gameID, cursor)
		cursor.close()
		conn.close()
		
def t():
	return getTestGame()

def getTestGame():
	f = file('uclacal.html')
	fileContents = f.read()
	game = gameDefs.Game()
	getTeams(game, fileContents)
	getDateTimeVenue(game, fileContents)
	rows = getRows(fileContents)
	if rows:
		parseRows(game, rows)
		game.calcResults()
		return game

def getSked(numWeeks = 17, numGames = 20000):
	if numWeeks > 17:
		numWeeks = 17
	week = 0
	while week < numWeeks:
		getWeek(week, numGames)
		week += 1

def getWeek(week = 0, numGames = 20000):
	gameIds = []
	
	year = 2008
	page = 'http://sports.espn.go.com/ncf/schedules'
	page += '?year=' + str(year) + '&week=' + str(week+1) + '&season=2&groupId=80'
	urlString = getHtmlSource(page)
	gameIds = getGameIds(urlString)
	
	#conn = MySQLdb.connect(host = "localhost", user = "erik", passwd = "erj007", db = "test")
	conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
	cursor = conn.cursor()
	#cursor.execute("SELECT VERSION()")
	#row = cursor.fetchone()
	#print "server version:", row[0]
	
	cfbdb.createTables(cursor)
	
	i = 0
	numGameIds = len(gameIds)
	if numGames > numGameIds:
		numGames = numGameIds
	while i < numGames:
		gameId = gameIds[i]
		url = 'http://sports.espn.go.com/ncf/playbyplay?gameId=' + gameId + '&period=0'
		game = getGame(url)
		if game:
			#game.gameID = i
			cfbdb.insertGame(game, gameDefs.PARSER_ESPN, cursor)
			#cfbdb.verifyGame(game.gameID, cursor)
		i += 1
	
	cursor.close()
	conn.close()

def getGame(url):
	htmlSource = getHtmlSource(url)
	game = gameDefs.Game()
	getTeams(game, htmlSource)
	getDateTimeVenue(game, htmlSource)
	rows = getRows(htmlSource)
	if rows:
		parseRows(game, rows)
		game.calcResults()
		return game

def insertGame(weekNum, gameNum):
	if weekNum > 17:
		weekNum = 17
	page = 'http://sports.espn.go.com/ncf/schedules'
	page += '?year=2008&week=' + str(weekNum) + '&season=2&groupId=80'
	urlstring = getHtmlSource(page)
	gameIds = getGameIds(urlstring)
	
	conn = MySQLdb.connect(host = "localhost", db = "test")
	cursor = conn.cursor()
	
	#cfbdb.createTables(cursor)
	
	numGameIds = len(gameIds)
	if gameNum > numGameIds:
		gameNum = numGameIds
	gameId = gameIds[gameNum]
	url = 'http://sports.espn.go.com/ncf/playbyplay?gameId=' + gameId + '&period=0'
	game = getGame(url)
	if game:
		#game.gameID = gameNum
		game.calcResults()
		cfbdb.deleteGame(game.gameID, cursor)
		cfbdb.insertGame(game, gameDefs.PARSER_ESPN, cursor)
		#cfbdb.verifyGame(game.gameID, cursor)
	
	cursor.close()
	conn.close()

def getGameIds(htmlSource):
	gameIds = []
	loc = htmlSource.find('boxscore?gameId=')
	while loc != -1:
		start = loc + 16
		loc = start
		while htmlSource[loc].isdigit():
			loc += 1
		gameId = htmlSource[start:loc]
		gameIds.append(gameId)
		loc = htmlSource.find('boxscore?gameId=', loc)
	return gameIds

def getTeams(game, fileContents):
	content = HtmlContent(fileContents)
	# get away team full name and score
	content.advance('class="team away"')
	awayName = content.getTagContents('a')
	game.awayScore = content.getTagContents('span')
	# get home team full name and score
	content.advance('class="team home"')
	homeName = content.getTagContents('a')
	game.homeScore = content.getTagContents('span')
	game.setNames(homeName, awayName)
	print game.awayName + ' (' + game.awayScore + ') @ ' + game.homeName + ' (' + game.homeScore + ')'

def getDateTimeVenue(game, fileContents):
	content = HtmlContent(fileContents)
	# get time and date
	content.advance('class="game-time-location"')
	timeAndDate = content.getTagContents('p')
	commaLoc = timeAndDate.find(',')
	time = timeAndDate[:commaLoc]
	game.time = convertTime(time)
	date = timeAndDate[commaLoc+2:]
	game.year, game.month, game.day = convertDate(date)
	# get venue
	venueInfo = content.getTagContents('p')
	commaLoc = venueInfo.find(',')
	venueName = venueInfo[:commaLoc]
	cityAndState = venueInfo[commaLoc+2:]
	commaLoc = cityAndState.find(',')
	city = cityAndState[:commaLoc]
	state = cityAndState[commaLoc+2:]
	game.venue = gameDefs.Venue(venueName, city, state)
	
def getRows(fileContents):
	# find play by play
	gpBodyLoc = fileContents.find('class="gp-body"')
	gpBodyEndLoc = fileContents.find('nd gp-body')
	playByPlay = HtmlContent(fileContents[gpBodyLoc:gpBodyEndLoc])
	# separate lines
	rows = []
	pointer = 0
	row = playByPlay.getTagContents('tr')
	while row:
		rowList = []
		row = HtmlContent(row)
		data = row.getTagContents('td')
		while data:
			rowList.append(data)
			data = row.getTagContents('td')
		if len(rowList) == 0:
			header = row.getTagContents('th')
			# mark the header rows
			if header:
				rowList.append('header')
			while header:
				rowList.append(header)
				header = row.getTagContents('th')
		rows.append(rowList)
		row = playByPlay.getTagContents('tr')
	
	if len(rows) == 0:
		print 'No Play By Play'
		return None
	
	return rows

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
	print teamName1 + ' @ ' + teamName2
	
	# find time and date
	loc2 = urlstring.find('ET, ', loc)
	loc = urlstring.rfind('<div>', 0, loc2)
	time = urlstring[loc+5:loc2]
	loc3 = urlstring.find('</div>', loc2)
	date = urlstring[loc2+4:loc3]
	
	time = convertTime(time)
	year, month, day = convertDate(date)
	
	# find venue
	loc = urlstring.find('<div>', loc3)
	loc2 = urlstring.find('</div>', loc)
	venueName = urlstring[loc+5:loc2]
	# find city & state
	loc = urlstring.find('<div>', loc2)
	loc2 = urlstring.find('</div>', loc)
	commaLoc = urlstring.find(',', loc, loc2)
	city = urlstring[loc+5:commaLoc]
	state = urlstring[commaLoc+2:loc2]
	
	venue = gameDefs.Venue(venueName, city, state)
	
	g = Game(time, year, month, day, venue, teamName1, teamName2, teamScore1, teamScore2)
	
def oldFindRows(urlstring, loc):
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
		rowList = parseRow(row)
		rows.append(rowList)
		loc = playByPlay.find('<tr', loc2)
		
	if len(rows) == 0:
		print 'No Play By Play'
		return None
	
	return rows

def getAltTeamNames(rows, teamName1, teamName2):
	# placeholders
	medName1 = ''
	medName2 = ''
	
	# figure out medNames
	i = 0
	while medName1 == '' or medName2 == '':
		rowList = rows[i]
		if rowList[0] == 'header':
			rowList.remove('header')
		rest = ' '.join(rowList[1:])
		rest = stripTags(rest)
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
	return medName1, medName2

def parseRows(game, rows):
	teamName1 = game.awayName
	teamName2 = game.homeName
	medName1, medName2 = getAltTeamNames(rows, teamName1, teamName2)
	# placeholders
	shortName1 = ''
	shortName2 = ''
	
	# set up variables
	qtr = 0
	homePoss = False
	teamPoss = teamName1
	teamDef = teamName2
	
	quarterTurn = False
	
	# flag for printing rows -- for testing purposes only
	flag = False
	play = gameDefs.Play(0, 0, 0, 0)
	
	# process rows
	i = 0
	while i < len(rows):
		rowList = rows[i]
		#if len(rowList) == 0:
		#	i += 1
		#	continue
		first = rowList[0]
		if first == 'header':
			header = True
			rowList.remove('header')
			first = rowList[0]
		#print '#first# : ' + first
		#print ' '.join(rowList)
		#rest = ' '.join(rowList[1:]).strip(' &nbsp;')
		if len(rowList) > 1:
			rest = rowList[1]
		else:
			rest = ''
		rest = stripTags(rest)
		rest = rest.replace('(','')
		rest = rest.replace(')','')
		rest = rest.replace('  ', ' ')
		restLower = rest.lower()
		if first.find('Quarter') != -1:
			if first.find('1st') != -1:
				qtr = 1
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
		elif first.find(teamName1 + ' at ') != -1 or first == teamName1:
			if shortName1 == '':
				shortName1 = rowList[1]
			if shortName2 == '':
				shortName2 = rowList[2]
			if quarterTurn and not homePoss:
				quarterTurn = False
			else:
				homePoss = False
				teamPoss = teamName1
				teamDef = teamName2
				drive = gameDefs.Drive(homePoss, teamName1, teamName2, medName1, medName2)
				game.drives.append(drive)
				#print '>> [visitor] ' + ' '.join(rowList)
			if quarterTurn:
				quarterTurn = False
		elif first.find(teamName2 + ' at ') != -1 or first == teamName2:
			if quarterTurn and homePoss:
				quarterTurn = False
			else:
				homePoss = True
				teamPoss = teamName2
				teamDef = teamName1
				drive = gameDefs.Drive(homePoss, teamName2, teamName1, medName2, medName1)
				game.drives.append(drive)
				#print '>> [home] ' + ' '.join(rowList)
			if quarterTurn:
				quarterTurn = False
		elif first.find(shortName1) != -1:
			down, distance, yardline = ddy(first, shortName1, homePoss)
			# some play-by-play systems will label penalties that occur
			# during or after the try down (to be enforced on the kickoff)
			# as occuring on 1st down -- not necessarily incorrect, but
			# incompatible with the system I've set up.  we'll simply
			# re-label those plays as occuring on 0th down.
			if down == 1 and distance == 70:
				down = 0
				distance = 0
			play = gameDefs.Play(qtr, down, distance, yardline)
			touchLoc = restLower.find('touchdown')
			if touchLoc != -1 and (restLower.find('extra point') != -1 or restLower.find('two-point') != -1):
				touchRest = rest[0:touchLoc+10]
				touchRestLower = restLower[0:touchLoc+10]
				drive.plays.append(play)
				parser.getPlay(game, drive, play, touchRestLower, touchRest)
				play = gameDefs.Play(qtr, -1, 3, 97)
				rest = rest[touchLoc+10:]
				restLower = restLower[touchLoc+10:]
			drive.plays.append(play)
			parser.getPlay(game, drive, play, restLower, rest)
			#print ' '.join(rowList)
			#play.printSelf()
			#print '>> [' + teamPoss + ' - Dn: ' + str(down) + ', Dist: ' + str(distance) + ', Yd: ' + str(yardline) + ' ] ' + ' '.join(rowList)
		elif first.find(shortName2) != -1:
			down, distance, yardline = ddy(first, shortName2, not homePoss)
			# some play-by-play systems will label penalties that occur
			# during or after the try down (to be enforced on the kickoff)
			# as occuring on 1st down -- not necessarily incorrect, but
			# incompatible with the system I've set up.  we'll simply
			# re-label those plays as occuring on 0th down.
			if down == 1 and distance == 70:
				down = 0
				distance = 0
			play = gameDefs.Play(qtr, down, distance, yardline)
			touchLoc = restLower.find('touchdown')
			if touchLoc != -1 and (restLower.find('extra point') != -1 or restLower.find('two-point') != -1):
				touchRest = rest[0:touchLoc+10]
				touchRestLower = restLower[0:touchLoc+10]
				drive.plays.append(play)
				parser.getPlay(game, drive, play, touchRestLower, touchRest)
				if play.result == gameDefs.RESULT_DEFENSIVE_TOUCHDOWN:
					homePoss = not homePoss
					if homePoss:
						drive = gameDefs.Drive(homePoss, teamName2, teamName1, medName2, medName1)
					else:
						drive = gameDefs.Drive(homePoss, teamName1, teamName2, medName1, medName2)
					game.drives.append(drive)
				play = gameDefs.Play(qtr, -1, 3, 97)
				rest = rest[touchLoc+10:]
				restLower = restLower[touchLoc+10:]
			drive.plays.append(play)
			parser.getPlay(game, drive, play, restLower, rest)
			#print ' '.join(rowList)
			#play.printSelf()
			#print '>> [' + teamPoss + ' - Dn: ' + str(down) + ', Dist: ' + str(distance) + ', Yd: ' + str(yardline) + ' ] ' + ' '.join(rowList)
		elif first.find('&nbsp;') != -1 and rest != '':
			down = 0
			distance = 0
			yardline = 0
			if len(drive.plays) > 0:
				prevPlay = drive.plays[len(drive.plays)-1]
				prevPlay.calcResults(True)
				if prevPlay.result == gameDefs.RESULT_NONE:
					playsBack = 1
					while len(drive.plays) > playsBack and (prevPlay.result == gameDefs.RESULT_NONE):
						prevPlay = drive.plays[len(drive.plays)-(playsBack+1)]
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
					if prevPlay.endingYard and prevPlay.startingYard:
						distance = int(prevPlay.distance) - (prevPlay.endingYard - prevPlay.startingYard)
						if distance <= 0:
							distance = 10
						yardline = prevPlay.endingYard
						if yardline + distance > 100:
							distance = 100 - yardline
					else:
						distance = prevPlay.distance
			else:
				yardline = 30
			play = gameDefs.Play(qtr, down, distance, yardline)
			touchLoc = restLower.find('touchdown')
			if touchLoc != -1 and (restLower.find('extra point') != -1 or restLower.find('two-point') != -1):
				touchRest = rest[0:touchLoc+10]
				touchRestLower = restLower[0:touchLoc+10]
				drive.plays.append(play)
				parser.getPlay(game, drive, play, touchRestLower, touchRest)
				if play.result == gameDefs.RESULT_DEFENSIVE_TOUCHDOWN:
					homePoss = not homePoss
					if homePoss:
						drive = gameDefs.Drive(homePoss, teamName2, teamName1, medName2, medName1)
					else:
						drive = gameDefs.Drive(homePoss, teamName1, teamName2, medName1, medName2)
					game.drives.append(drive)
				play = gameDefs.Play(qtr, -1, 3, 97)
				rest = rest[touchLoc+10:]
				restLower = restLower[touchLoc+10:]
			drive.plays.append(play)
			parser.getPlay(game, drive, play, restLower, rest)
			
			#print ' '.join(rowList)
			#play.printSelf()
			#print '>> [nothing] ' + ' '.join(rowList)
		else:
			pass
		
		i += 1

def parseRow(row):
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

# for a given play, get the down, distance, and yardline
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


class HtmlContent:
	
	def __init__(self, html):
		self.html = html
		self.pointer = 0
	
	def advance(self, stringToFind):
		loc = self.html.find(stringToFind, self.pointer)
		if loc == -1:
			loc = self.html.find(stringToFind)
			if loc == -1:
				return None
		self.pointer = loc
	
	def getTagContents(self, tagName):
		openStartLoc = self.html.find('<' + tagName, self.pointer)
		if openStartLoc != -1:
			openEndLoc = self.html.find('>', openStartLoc)
			closeTag = self.html.find('</' + tagName + '>', openEndLoc)
			contents = self.html[openEndLoc+1:closeTag]
			self.pointer = closeTag + len(tagName) + 3
			return contents

def stripTags(html):
	openLoc = html.find('<')
	while openLoc != -1:
		closeLoc = html.find('>', openLoc)
		html = html[:openLoc] + html[closeLoc+1:]
		openLoc = html.find('<')
	return html

if __name__ == '__main__':
    import sys
    print getHtmlSource(sys.argv[1])
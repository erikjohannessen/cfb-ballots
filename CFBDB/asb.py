import urllib
import MySQLdb
import gameDefs
import cfbdb
import parser

Game = gameDefs.Game
Drive = gameDefs.Drive
Play = gameDefs.Play

parsingDatabase = "parsingdb"
parsingHost = "localhost"
parsingUser = "root"

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
		
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		cfbdb.createTables(cursor)
		cfbdb.insertGame(game, gameDefs.PARSER_ASB, cursor)
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
	
	year, month, day = convertDate(date)
	
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
			parser.getPlay(g, d, p, rest.lower(), rest)
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

def convertDate(dateString):
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
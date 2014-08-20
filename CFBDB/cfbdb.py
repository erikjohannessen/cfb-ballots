import MySQLdb
import gameDefs

Game = gameDefs.Game
Drive = gameDefs.Drive
Play = gameDefs.Play
Event = gameDefs.Event

parsingDatabase = "parsingdb"
parsingHost = "localhost"
parsingUser = "root"
storageDatabase = "storagedb"
storageHost = "localhost"
storageUser = "root"

def initiateAllDatabases():
	parsingConn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
	parsingCursor = parsingConn.cursor()
	createTables(parsingCursor)
	parsingCursor.close()
	parsingConn.close()
	
	storageConn = MySQLdb.connect(host = storageHost, user = storageUser, db = storageDatabase)
	storageCursor = storageConn.cursor()
	createTables(storageCursor)
	storageCursor.close()
	storageConn.close()

def createTables(cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	try:
		cursor.execute("DROP TABLE IF EXISTS teams")
		cursor.execute("DROP TABLE IF EXISTS venues")
		cursor.execute("DROP TABLE IF EXISTS games")
		cursor.execute("DROP TABLE IF EXISTS drives")
		cursor.execute("DROP TABLE IF EXISTS plays")
		cursor.execute("DROP TABLE IF EXISTS events")
	except MySQLdb.Error, e:
		print "Error dropping table %d: %s" % (e.args[0], e.args[1])
	
	createTeams = """
		CREATE TABLE teams
      	(
      		teamID				MEDIUMINT(10),
     		teamName			CHAR(40)
      	)
      	"""
	
	createVenues = """
		CREATE TABLE venues
      	(
      		venueID				MEDIUMINT(10),
      		name				CHAR(40),
      		city				CHAR(40)
      		state				CHAR(2)
      	)
      	"""
	
	createGames = """
		CREATE TABLE games
      	(
      		gameID				INT(10),
      		time				MEDIUMINT(10),
      		year				MEDIUMINT(10),
      		month				MEDIUMINT(10),
      		day					MEDIUMINT(10),
      		venueID				INT(10),
     		homeTeamID			MEDIUMINT(10),
     		awayTeamID			MEDIUMINT(10),
      		homeScore			MEDIUMINT(10),
      		awayScore			MEDIUMINT(10),
      		numDrives			MEDIUMINT(10),
      		parserCode			MEDIUMINT(10)
      	)
      	"""
	
	createDrives = """
		CREATE TABLE drives
      	(
      		gameID				INT(10),
      		driveID				INT(10),
      		teamPossID			MEDIUMINT(10),
      		pointsThisDrive		MEDIUMINT(10),
      		defPointsThisDrive	MEDIUMINT(10),
      		homeScore			MEDIUMINT(10),
      		awayScore			MEDIUMINT(10),
      		numFirstDowns		MEDIUMINT(10),
      		numPlays			MEDIUMINT(10)
      	)
      	"""
	
	createPlays = """
    	CREATE TABLE plays
    	(
      		gameID				INT(10),
    	  	driveID				INT(10),
    	  	playID				INT(10),
     		playText			CHAR(250),
    	  	pointsThisPlay		MEDIUMINT(10),
    	  	quarter				MEDIUMINT(10),
    	  	down				MEDIUMINT(10),
    	  	distance			MEDIUMINT(10),
    	  	startingYard		MEDIUMINT(10),
    	  	endingYard			MEDIUMINT(10),
    	  	direction			MEDIUMINT(10),
    	  	result				MEDIUMINT(10),
    	  	numEvents			MEDIUMINT(10)
		)
    	"""
	
	createEvents = """
    	CREATE TABLE events
    	(
      		gameID				INT(10),
    	  	driveID				INT(10),
    	  	playID				INT(10),
    	  	eventID				INT(10),
    	  	eventType			MEDIUMINT(10),
    	  	startingYard		MEDIUMINT(10),
    	  	endingYard			MEDIUMINT(10),
    	  	offense1			CHAR(40),
    	  	offense2			CHAR(40),
    	  	defense1			CHAR(40),
    	  	defense2			CHAR(40)
    	)
    	"""
	
	try:
		cursor.execute(createTeams)
		cursor.execute(createVenues)
		cursor.execute(createGames)
		cursor.execute(createDrives)
   		cursor.execute(createPlays)
   		cursor.execute(createEvents)
    	except MySQLdb.Error, e:
			print "Error creating table %d: %s" % (e.args[0], e.args[1])
	
	if closeConnection:
		cursor.close()
		conn.close()

def getVenueID(venue, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cursor.execute("SELECT venueID FROM venues WHERE name = \"" + venue.name + "\" AND city = \"" + venue.city + "\"")
	rows = cursor.fetchall()
	if len(rows) > 0:
	   	venue.code = rows[0][0]
	else:
		venue.code = 1
		cursor.execute("SELECT name FROM venues WHERE venueID = \"" + str(venue.code) + "\"")
   		rows = cursor.fetchall()
		while len(rows) > 0:
			venue.code += 1
			cursor.execute("SELECT name FROM venues WHERE venueID = \"" + str(venue.code) + "\"")
   			rows = cursor.fetchall()
   		print venue.name + ' (' + venue.city + ', ' + venue.state + ') has a new ID : ' + str(venue.code)
   		try:
			cursor.execute("INSERT INTO venues (venueID, name, city, state) VALUES ('" + str(venue.code) + "', \"" + venue.name + "\", '" + venue.city + "', '" + venue.state + "')\n")
			cursor.execute("INSERT INTO storagedb.venues (venueID, name, city, state) VALUES ('" + str(venue.code) + "', \"" + venue.name + "\", '" + venue.city + "', '" + venue.state + "')\n")
   		except MySQLdb.Error, e:
			print "Error inserting data into venues/storagedb.venues %d: %s" % (e.args[0], e.args[1])
			print venue.code
			print venue.name
			print venue.city
			print venue.state
	
	if closeConnection:
		cursor.close()
		conn.close()

def insertGame(game, parserCode, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cursor.execute("SELECT teamID FROM teams WHERE teamName = \"" + game.homeName + "\"")
   	rows = cursor.fetchall()
   	if len(rows) > 0:
	   	homeTeamID = rows[0][0]
	else:
		homeTeamID = gameDefs.teamCode(game.homeName)
		if homeTeamID == -1:
			homeTeamID = 121
			cursor.execute("SELECT teamName FROM teams WHERE teamID = \"" + str(homeTeamID) + "\"")
   			rows = cursor.fetchall()
			while len(rows) > 0:
				homeTeamID += 1
				cursor.execute("SELECT teamName FROM teams WHERE teamID = \"" + str(homeTeamID) + "\"")
   				rows = cursor.fetchall()
   			print game.homeName + ' has a new ID : ' + str(homeTeamID)
   		try:
	   		cursor.execute("INSERT INTO teams (teamID, teamName) VALUES ('" + str(homeTeamID) + "', '" + game.homeName + "')\n")
   			cursor.execute("INSERT INTO storagedb.teams (teamID, teamName) VALUES ('" + str(homeTeamID) + "', '" + game.homeName + "')\n")
   		except MySQLdb.Error, e:
			print "Error inserting data into teams/storagedb.teams %d: %s" % (e.args[0], e.args[1])
			print homeTeamID
			print game.homeName
	cursor.execute("SELECT teamID FROM teams WHERE teamName = \"" + game.awayName + "\"")
   	rows = cursor.fetchall()
   	if len(rows) > 0:
	   	awayTeamID = rows[0][0]
	else:
		awayTeamID = gameDefs.teamCode(game.awayName)
		if awayTeamID == -1:
			awayTeamID = 121
			cursor.execute("SELECT teamName FROM teams WHERE teamID = \"" + str(awayTeamID) + "\"")
   			rows = cursor.fetchall()
			while len(rows) > 0:
				awayTeamID += 1
				cursor.execute("SELECT teamName FROM teams WHERE teamID = \"" + str(awayTeamID) + "\"")
   				rows = cursor.fetchall()
   			print game.awayName + ' has a new ID : ' + str(awayTeamID)
   		try:
	   		cursor.execute("INSERT INTO teams (teamID, teamName) VALUES ('" + str(awayTeamID) + "', '" + game.awayName + "')\n")
   			cursor.execute("INSERT INTO storagedb.teams (teamID, teamName) VALUES ('" + str(awayTeamID) + "', '" + game.awayName + "')\n")
   		except MySQLdb.Error, e:
			print "Error inserting data into teams/storagedb.teams %d: %s" % (e.args[0], e.args[1])
			print awayTeamID
			print game.awayName
	
	venueID = None
	if game.venue:
		cursor.execute("SELECT venueID FROM venues WHERE name = \"" + game.venue.name + "\" AND city = \"" + game.venue.city + "\"")
		rows = cursor.fetchall()
	   	if len(rows) > 0:
		   	venueID = rows[0][0]
		else:
			venueID = 1
			cursor.execute("SELECT name FROM venues WHERE venueID = \"" + str(venueID) + "\"")
   			rows = cursor.fetchall()
			while len(rows) > 0:
				venueID += 1
				cursor.execute("SELECT name FROM venues WHERE venueID = \"" + str(venueID) + "\"")
   				rows = cursor.fetchall()
   			print game.venue.names[0] + ' (' + game.venue.city + ', ' + game.venue.state + ') has a new ID : ' + str(venueID)
   			try:
		   		cursor.execute("INSERT INTO venues (venueID, name, city, state) VALUES ('" + str(venueID) + "', \"" + game.venue.name + "\", '" + game.venue.city + "', '" + game.venue.state + "')\n")
		   		cursor.execute("INSERT INTO storagedb.venues (venueID, name, city, state) VALUES ('" + str(venueID) + "', \"" + game.venue.name + "\", '" + game.venue.city + "', '" + game.venue.state + "')\n")
   			except MySQLdb.Error, e:
				print "Error inserting data into venues/storagedb.venues %d: %s" % (e.args[0], e.args[1])
				print venueID
				print game.venue.name
				print game.venue.city
				print game.venue.state
	
	cmd = """
		INSERT INTO games (gameID, time, year, month, day, venueID, homeTeamID, awayTeamID, homeScore, awayScore, numDrives, parserCode)
  		VALUES
   		"""
   	id = "'" + str(game.gameID) + "'"
   	time = ("'" + str(game.time) + "'") if game.time else "NULL"
   	year = ("'" + str(game.year) + "'") if game.year else "NULL"
   	month = ("'" + str(game.month) + "'") if game.month else "NULL"
   	day = ("'" + str(game.day) + "'") if game.day else "NULL"
   	venueID = "'" + str(venueID) + "'" if venueID else "NULL"
   	ids = "'" + str(homeTeamID) + "', '" + str(awayTeamID) + "'"
   	homeScore = ("'" + str(game.homeScore) + "'") if game.homeScore else "NULL"
   	awayScore = ("'" + str(game.awayScore) + "'") if game.awayScore else "NULL"
   	numDrives = "'" + str(len(game.drives)) + "'" if len(game.drives) > 0 else "NULL"
   	parserCode = "'" + str(parserCode) + "'"
   	
   	cmd += "(" + id + ", "
   	cmd += time + ", "
   	cmd += year + ", "
   	cmd += month + ", "
   	cmd += day + ", "
   	cmd += venueID + ", "
   	cmd += ids + ", "
   	cmd += homeScore + ", "
   	cmd += awayScore + ", "
   	cmd += numDrives + ", "
   	cmd += parserCode + ")\n"
	
   	try:
		cursor.execute(cmd)
	except MySQLdb.Error, e:
		print "Error inserting data into games %d: %s" % (e.args[0], e.args[1])
		print cmd
	
	i = 0
	while i < len(game.drives):
		drive = game.drives[i]
		insertDrive(drive, game.gameID, i, cursor)
		i += 1
	
	if closeConnection:
		cursor.close()
		conn.close()

def insertDrive(drive, gameID, driveID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cursor.execute("SELECT teamID FROM teams WHERE teamName = \"" + drive.teamPoss + "\"")
   	teamPossID = cursor.fetchall()[0][0]
	
	cmd = """
		INSERT INTO drives (gameID, driveID, teamPossID, pointsThisDrive, defPointsThisDrive, homeScore, awayScore, numFirstDowns, numPlays)
  		VALUES
   		"""
   	ids = "'" + str(gameID) + "', '" + str(driveID) + "', '" + str(teamPossID) + "'"
   	pointsThisDrive = ("'" + str(drive.pointsThisDrive) + "'") if drive.pointsThisDrive else "NULL"
   	defensivePointsThisDrive = ("'" + str(drive.defensivePointsThisDrive) + "'") if drive.defensivePointsThisDrive else "NULL"
   	homeScore = ("'" + str(drive.homeScore) + "'") if drive.homeScore else "NULL"
   	awayScore = ("'" + str(drive.awayScore) + "'") if drive.awayScore else "NULL"
   	firstDownsThisDrive = ("'" + str(drive.firstDownsThisDrive) + "'") if drive.firstDownsThisDrive else "NULL"
   	numPlays = "'" + str(len(drive.plays)) + "'" if len(drive.plays) > 0 else "NULL"
   	
   	cmd += "(" + ids + ", "
   	cmd += pointsThisDrive + ", "
   	cmd += defensivePointsThisDrive + ", "
   	cmd += homeScore + ", "
   	cmd += awayScore + ", "
   	cmd += firstDownsThisDrive + ", "
   	cmd += numPlays + ")\n"
	
   	try:
		cursor.execute(cmd)
	except MySQLdb.Error, e:
		print "Error inserting data into drives %d: %s" % (e.args[0], e.args[1])
		print cmd
	
	i = 0
	while i < len(drive.plays):
		play = drive.plays[i]
		insertPlay(play, gameID, driveID, i, cursor)
		i += 1
	
	if closeConnection:
		cursor.close()
		conn.close()

def insertPlay(play, gameID, driveID, playID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cmd = """
		INSERT INTO plays (gameID, driveID, playID, playText, pointsThisPlay, quarter, down, distance, startingYard, endingYard, result, numEvents)
  		VALUES
   		"""
   	ids = "'" + str(gameID) + "', '" + str(driveID) + "', '" + str(playID) + "'"
   	body = ("\"" + play.body + "\"") if play.body else "NULL"
   	pointsThisPlay = ("'" + str(play.pointsThisPlay) + "'") if play.pointsThisPlay else "NULL"
   	quarter = ("'" + str(play.quarter) + "'") if play.quarter else "NULL"
   	down = ("'" + str(play.down) + "'") if play.down else "NULL"
   	distance = ("'" + str(play.distance) + "'") if play.distance else "NULL"
   	startingYard = ("'" + str(play.startingYard) + "'") if play.startingYard else "NULL"
   	endingYard = ("'" + str(play.endingYard) + "'") if play.endingYard else "NULL"
   	result = "'" + str(play.result) + "'"
   	numEvents = "'" + str(len(play.events)) + "'" if len(play.events) > 0 else "NULL"
   	
   	cmd += "(" + ids + ", "
   	cmd += body + ", "
   	cmd += pointsThisPlay + ", "
   	cmd += quarter + ", "
   	cmd += down + ", "
   	cmd += distance + ", "
   	cmd += startingYard + ", "
   	cmd += endingYard + ", "
   	cmd += result + ", "
   	cmd += numEvents + ")\n"
	
   	try:
		cursor.execute(cmd)
	except MySQLdb.Error, e:
		print "Error inserting data into plays %d: %s" % (e.args[0], e.args[1])
		print cmd
	
	i = 0
	while i < len(play.events):
		event = play.events[i]
		insertEvent(event, gameID, driveID, playID, i, cursor)
		i += 1
	
	if closeConnection:
		cursor.close()
		conn.close()

def insertEvent(event, gameID, driveID, playID, eventID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cmd = """
		INSERT INTO events (gameID, driveID, playID, eventID, eventType, startingYard, endingYard, offense1, offense2, defense1, defense2)
  		VALUES
   		"""
   	ids = "'" + str(gameID) + "', '" + str(driveID) + "', '" + str(playID) + "', '" + str(eventID) + "'"
   	eventType = "'" + str(event.eventType) + "'"
   	startingYard = ("'" + str(event.startingYard) + "'") if event.startingYard else "NULL"
   	endingYard = ("'" + str(event.endingYard) + "'") if event.endingYard else "NULL"
   	offense1 = ("\"" + event.offense1 + "\"") if event.offense1 else "NULL"
   	offense2 = ("\"" + event.offense2 + "\"") if event.offense2 else "NULL"
   	defense1 = ("\"" + event.defense1 + "\"") if event.defense1 else "NULL"
   	defense2 = ("\"" + event.defense2 + "\"") if event.defense2 else "NULL"
   	
   	cmd += "(" + ids + ", "
   	cmd += eventType + ", "
   	cmd += startingYard + ", "
   	cmd += endingYard + ", "
   	cmd += offense1 + ", "
   	cmd += offense2 + ", "
   	cmd += defense1 + ", "
   	cmd += defense2 + ")\n"
	
   	try:
		cursor.execute(cmd)
	except MySQLdb.Error, e:
		print "Error inserting data into events %d: %s" % (e.args[0], e.args[1])
		print cmd
	
	if closeConnection:
		cursor.close()
		conn.close()

def selectGame(gameID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	cursor.execute("SELECT time, year, month, day, venueID, homeTeamID, awayTeamID, homeScore, awayScore, numDrives FROM games WHERE gameID = \"" + str(gameID) + "\"")
   	row = cursor.fetchall()[0]
   	time = row[0]
   	year = row[1]
   	month = row[2]
   	day = row[3]
   	venueID = row[4]
   	homeTeamID = row[5]
   	awayTeamID = row[6]
   	homeTeamScore = row[7]
   	awayTeamScore = row[8]
   	numDrives = row[9]
   	
   	venue = None
   	city = None
   	if venueID:
   		cursor.execute("SELECT name, city FROM venues WHERE venueID = \"" + str(venueID) + "\"")
   		row = cursor.fetchall()[0]
   		venue = row[0]
   		city = row[1]
   	
	cursor.execute("SELECT teamName FROM teams WHERE teamID = \"" + str(homeTeamID) + "\"")
   	homeTeamName = cursor.fetchall()[0][0]
	cursor.execute("SELECT teamName FROM teams WHERE teamID = \"" + str(awayTeamID) + "\"")
   	awayTeamName = cursor.fetchall()[0][0]
   	
   	# time, year, month, day, venue, city, homeTeamScore, awayTeamScore, and numDrives might all be 'None'
   	string = 'G' + str(gameID) + ' : ' + awayTeamName + ' ' + str(awayTeamScore) + ' @ ' + homeTeamName + ' ' + str(homeTeamScore)
   	string2 = ' - ' + str(month) + '/' + str(day) + '/' + str(year) + ' @ ' + str(time) + ' hrs; ' + venue + ', ' + city
   	print string + string2
   	if closeConnection:
		cursor.close()
		conn.close()
   	return numDrives

def selectDrive(gameID, driveID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
   	cursor.execute("SELECT teamPossID, pointsThisDrive, defPointsThisDrive, homeScore, awayScore, numFirstDowns, numPlays FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   	row = cursor.fetchall()[0]
   	teamPossID = row[0]
   	points = row[1]
   	defPoints = row[2]
   	homeScore = row[3]
   	awayScore = row[4]
   	numFirstDowns = row[5]
   	numPlays = row[6]
   	
	cursor.execute("SELECT teamName FROM teams WHERE teamID = \"" + str(teamPossID) + "\"")
   	teamPoss = cursor.fetchall()[0][0]
   	
   	# points, defPoints, homeScore, awayScore, numFirstDowns, and numPlays might all be 'None'
   	string = 'G' + str(gameID) + ' D' + str(driveID) + ' : Score = ' + str(awayScore) + '-' + str(homeScore) + ' '
   	string2 = teamPoss + ' scoring ' + str(points) + ' points while giving up ' + str(defPoints) + ', gaining ' + str(numFirstDowns) + ' first downs'
   	print string + string2
   	if closeConnection:
		cursor.close()
		conn.close()
   	return numPlays

def selectPlay(gameID, driveID, playID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
   	cursor.execute("SELECT playText, pointsThisPlay, quarter, down, distance, startingYard, endingYard, result, numEvents FROM plays WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\"")
   	row = cursor.fetchall()[0]
   	text = row[0]
   	points = row[1]
   	quarter = row[2]
   	down = row[3]
   	distance = row[4]
   	startingYard = row[5]
   	endingYard = row[6]
   	result = row[7]
   	numEvents = row[8]
   	
   	# text, points, quarter, down, distance, startingYard, endingYard, and numEvents might all be 'None'
   	string = 'G' + str(gameID) + ' D' + str(driveID) + ' P' + str(playID) + ' : '
   	string2 = 'Q' + str(quarter) + ', Dn ' + str(down) + ', Dist ' + str(distance)
   	string3 = ' @ ' + str(startingYard) + 'Y to ' + str(endingYard) + 'Y - '
   	string4 = gameDefs.resultString(result) + ' scoring ' + str(points) + ' points'
   	print string + string2 + string3 + string4
   	print text
   	if closeConnection:
		cursor.close()
		conn.close()
   	return numEvents

def selectEvent(gameID, driveID, playID, eventID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
   	cursor.execute("SELECT eventType, startingYard, endingYard, offense1, offense2, defense1, defense2 FROM events WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\" AND eventID = \"" + str(eventID) + "\"")
   	row = cursor.fetchall()[0]
   	eventType = row[0]
   	startingYard = row[1]
   	endingYard = row[2]
   	offense1 = row[3]
   	offense2 = row[4]
   	defense1 = row[5]
   	defense2 = row[6]
   	
   	# startingYard, endingYard, offense1, offense2, defense1, and defense2 might all be 'None'
   	string = 'G' + str(gameID) + ' D' + str(driveID) + ' P' + str(playID) + ' E' + str(eventID) + ' : '
   	string2 = gameDefs.eventString(eventType) + ' @ ' + str(startingYard) + 'Y to ' + str(endingYard) + 'Y.'
   	string3 = ' O = ' + offense1 + ', ' + offense2 + '. D = ' + defense1 + ', ' + defense2
   	print string + string2 + string3
   	if closeConnection:
		cursor.close()
		conn.close()

def selectDrives(gameID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	numDrives = selectGame(gameID, cursor)
	i = 0
	while i < numDrives:
		selectDrive(gameID, i, cursor)
		i += 1
	if closeConnection:
		cursor.close()
		conn.close()

def selectPlays(gameID, driveID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	numPlays = selectDrive(gameID, driveID, cursor)
	i = 0
	while i < numPlays:
		selectPlay(gameID, driveID, i, cursor)
		i += 1
	if closeConnection:
		cursor.close()
		conn.close()

def selectEvents(gameID, driveID, playID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	numEvents = selectPlay(gameID, driveID, playID, cursor)
	i = 0
	while i < numEvents:
		selectEvent(gameID, driveID, playID, i, cursor)
		i += 1
	if closeConnection:
		cursor.close()
		conn.close()

def deleteGame(gameID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	try:
		cursor.execute("DELETE FROM events WHERE gameID = \"" + str(gameID) + "\"")
		cursor.execute("DELETE FROM plays WHERE gameID = \"" + str(gameID) + "\"")
		cursor.execute("DELETE FROM drives WHERE gameID = \"" + str(gameID) + "\"")
		cursor.execute("DELETE FROM games WHERE gameID = \"" + str(gameID) + "\"")
	except MySQLdb.Error, e:
		print "Error deleting game data %d: %s" % (e.args[0], e.args[1])
	
	if closeConnection:
		cursor.close()
		conn.close()

def deleteDrive(gameID, driveID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cursor.execute("SELECT teamPossID, pointsThisDrive, defPointsThisDrive FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   	row = cursor.fetchall()[0]
   	teamPossID = row[0]
   	points = row[1]
   	defPoints = row[2]
   	if points > 0 or defPoints > 0:
   		cursor.execute("SELECT homeTeamID, numDrives FROM games WHERE gameID = \"" + str(gameID) + "\"")
		row = cursor.fetchall()[0]
   		homeTeamID = row[0]
   		numDrives = row[1]
   		currentDrive = driveID + 1
   		while currentDrive < numDrives:
   			cursor.execute("SELECT homeScore, awayScore FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
   			row = cursor.fetchall()[0]
   			homeScore = row[0]
   			awayScore = row[1]
			if teamPossID == homeTeamID:
				if points > 0 and homeScore:
					cursor.execute("UPDATE drives SET homeScore = \"" + str(homeScore-points) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
				if defPoints > 0 and awayScore:
					cursor.execute("UPDATE drives SET awayScore = \"" + str(awayScore-defPoints) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
			else:
				if points > 0 and awayScore:
					cursor.execute("UPDATE drives SET awayScore = \"" + str(awayScore-points) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
				if defPoints > 0 and homeScore:
					cursor.execute("UPDATE drives SET homeScore = \"" + str(homeScore-defPoints) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
			currentDrive += 1
	
	cursor.execute("DELETE FROM events WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
	cursor.execute("DELETE FROM plays WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
	cursor.execute("DELETE FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
	
	cursor.execute("SELECT numDrives FROM games WHERE gameID = \"" + str(gameID) + "\"")
   	numDrives = cursor.fetchall()[0][0]
   	currentDrive = driveID + 1
   	while currentDrive < numDrives:
		cursor.execute("UPDATE events SET driveID = \"" + str(currentDrive-1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
		cursor.execute("UPDATE plays SET driveID = \"" + str(currentDrive-1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
		cursor.execute("UPDATE drives SET driveID = \"" + str(currentDrive-1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
		currentDrive += 1
	cursor.execute("UPDATE games SET numDrives = \"" + str(numDrives-1) + "\" WHERE gameID = \"" + str(gameID) + "\"")
	
	if closeConnection:
		cursor.close()
		conn.close()

def deletePlay(gameID, driveID, playID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cursor.execute("SELECT pointsThisPlay, result FROM plays WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\"")
   	row = cursor.fetchall()[0]
   	points = row[0]
   	result = row[1]
   	if points > 0:
   		defensiveScore = False
   		if result == gameDefs.RESULT_DEFENSIVE_TOUCHDOWN or result == gameDefs.RESULT_SAFETY:
   			defensiveScore = True
   		
   		if defensiveScore:
	   		cursor.execute("SELECT defPointsThisDrive FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   			defDrivePoints = cursor.fetchall()[0][0]
   			cursor.execute("UPDATE drives SET defPointsThisDrive = \"" + str(defDrivePoints-points) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
		else:
			cursor.execute("SELECT pointsThisDrive FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   			drivePoints = cursor.fetchall()[0][0]
   			cursor.execute("UPDATE drives SET pointsThisDrive = \"" + str(drivePoints-points) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
		
		cursor.execute("SELECT teamPossID FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   		teamPossID = cursor.fetchall()[0][0]
		
		cursor.execute("SELECT homeTeamID, numDrives FROM games WHERE gameID = \"" + str(gameID) + "\"")
		row = cursor.fetchall()[0]
   		homeTeamID = row[0]
  		numDrives = row[1]
   		currentDrive = driveID + 1
   		while currentDrive < numDrives:
   			if (teamPossID == homeTeamID) is not defensiveScore:
   				cursor.execute("SELECT homeScore FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
   				homeScore = cursor.fetchall()[0][0]
				cursor.execute("UPDATE drives SET homeScore = \"" + str(homeScore-points) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
			else:
				cursor.execute("SELECT awayScore FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
   				awayScore = cursor.fetchall()[0][0]
				cursor.execute("UPDATE drives SET awayScore = \"" + str(awayScore-points) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
			currentDrive += 1
	
	if result == gameDefs.RESULT_FIRST_DOWN:
		cursor.execute("SELECT numFirstDowns FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   		numFirstDowns = cursor.fetchall()[0][0]
   		cursor.execute("UPDATE drives SET numFirstDowns = \"" + str(numFirstDowns-1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
		
	
	cursor.execute("DELETE FROM events WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\"")
	cursor.execute("DELETE FROM plays WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\"")
	cursor.execute("SELECT numPlays FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   	numPlays = cursor.fetchall()[0][0]
   	currentPlay = playID + 1
   	while currentPlay < numPlays:
   		cursor.execute("UPDATE events SET playID = \"" + str(currentPlay-1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(currentPlay) + "\"")
		cursor.execute("UPDATE plays SET playID = \"" + str(currentPlay-1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(currentPlay) + "\"")
		currentPlay += 1
	cursor.execute("UPDATE drives SET numPlays = \"" + str(numPlays-1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
	
	if closeConnection:
		cursor.close()
		conn.close()

def deleteEvent(gameID, driveID, playID, eventID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cursor.execute("DELETE FROM events WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\" AND eventID = \"" + str(eventID) + "\"")
	cursor.execute("SELECT numEvents FROM plays WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\"")
   	numEvents = cursor.fetchall()[0][0]
   	currentEvent = eventID + 1
   	while currentEvent < numEvents:
		cursor.execute("UPDATE events SET eventID = \"" + str(currentEvent-1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\" AND eventID = \"" + str(currentEvent) + "\"")
		currentEvent += 1
	cursor.execute("UPDATE plays SET numEvents = \"" + str(numEvents-1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\"")
	
	if closeConnection:
		cursor.close()
		conn.close()

def update(label, value, gameID, driveID = -1, playID = -1, eventID = -1, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	if eventID != -1:
		cursor.execute("UPDATE events SET " + str(label) + " = \"" + str(value) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\" AND eventID = \"" + str(eventID) + "\"")
	elif playID != -1:
		cursor.execute("UPDATE plays SET " + str(label) + " = \"" + str(value) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\"")
	elif driveID != -1:
		cursor.execute("UPDATE drives SET " + str(label) + " = \"" + str(value) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
	else:
		cursor.execute("UPDATE games SET " + str(label) + " = \"" + str(value) + "\" WHERE gameID = \"" + str(gameID) + "\"")
	
	if closeConnection:
		cursor.close()
		conn.close()

# these next few routines I wrote especially to correct certain situations
# they are not terribly general, but they could be made so
# hopefully, they are at least useful

def insertPlayAtIndex(play, gameID, driveID, playID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	if play.pointsThisPlay > 0:
   		defensiveScore = False
   		if play.result == gameDefs.RESULT_DEFENSIVE_TOUCHDOWN or play.result == gameDefs.RESULT_SAFETY:
   			defensiveScore = True
   		
   		if defensiveScore:
	   		cursor.execute("SELECT defPointsThisDrive FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   			defDrivePoints = cursor.fetchall()[0][0]
   			cursor.execute("UPDATE drives SET defPointsThisDrive = \"" + str(defDrivePoints+play.pointsThisPlay) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
		else:
			cursor.execute("SELECT pointsThisDrive FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   			drivePoints = cursor.fetchall()[0][0]
   			cursor.execute("UPDATE drives SET pointsThisDrive = \"" + str(drivePoints+play.pointsThisPlay) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
		
		cursor.execute("SELECT teamPossID FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   		teamPossID = cursor.fetchall()[0][0]
		
		cursor.execute("SELECT homeTeamID, numDrives FROM games WHERE gameID = \"" + str(gameID) + "\"")
		row = cursor.fetchall()[0]
   		homeTeamID = row[0]
  		numDrives = row[1]
   		currentDrive = driveID + 1
   		while currentDrive < numDrives:
   			if (teamPossID == homeTeamID) is not defensiveScore:
   				cursor.execute("SELECT homeScore FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
   				homeScore = cursor.fetchall()[0][0]
				cursor.execute("UPDATE drives SET homeScore = \"" + str(homeScore+play.pointsThisPlay) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
			else:
				cursor.execute("SELECT awayScore FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
   				awayScore = cursor.fetchall()[0][0]
				cursor.execute("UPDATE drives SET awayScore = \"" + str(awayScore+play.pointsThisPlay) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(currentDrive) + "\"")
			currentDrive += 1
	
	if play.result == gameDefs.RESULT_FIRST_DOWN:
		cursor.execute("SELECT numFirstDowns FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   		numFirstDowns = cursor.fetchall()[0][0]
   		if numFirstDowns:
	   		cursor.execute("UPDATE drives SET numFirstDowns = \"" + str(numFirstDowns+1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
		
	
	cursor.execute("SELECT numPlays FROM drives WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   	numPlays = cursor.fetchall()[0][0]
   	currentPlay = playID
   	while currentPlay < numPlays:
   		cursor.execute("UPDATE events SET playID = \"" + str(currentPlay+1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(currentPlay) + "\"")
		cursor.execute("UPDATE plays SET playID = \"" + str(currentPlay+1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(currentPlay) + "\"")
		currentPlay += 1
	cursor.execute("UPDATE drives SET numPlays = \"" + str(numPlays+1) + "\" WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
	
	insertPlay(play, gameID, driveID, playID, cursor)
	
	if closeConnection:
		cursor.close()
		conn.close()

def storeGame(gameID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cursor.execute("SELECT (*) FROM games WHERE gameID = \"" + str(gameID) + "\"")
   	row = cursor.fetchall()[0]
   	time = row[1]
   	year = row[2]
   	month = row[3]
   	day = row[4]
   	venue = row[5]
   	city = row[6]
   	homeTeamID = row[7]
   	awayTeamID = row[8]
   	homeTeamScore = row[9]
   	awayTeamScore = row[10]
   	numDrives = row[11]
   	parserCode = row[12]
	
	cmd = """
		INSERT INTO storagedb.games (gameID, time, year, month, day, venue, city, homeTeamID, awayTeamID, homeScore, awayScore, numDrives, parserCode)
  		VALUES
   		"""
   	id = "'" + str(gameID) + "'"
   	time = ("'" + str(time) + "'") if time else "NULL"
   	year = ("'" + str(year) + "'") if year else "NULL"
   	month = ("'" + str(month) + "'") if month else "NULL"
   	day = ("'" + str(day) + "'") if day else "NULL"
   	venue = ("\"" + venue + "\"") if venue else "NULL"
   	city = ("\"" + city + "\"") if city else "NULL"
   	ids = "'" + str(homeTeamID) + "', '" + str(awayTeamID) + "'"
   	homeScore = ("'" + str(homeTeamScore) + "'") if homeTeamScore else "NULL"
   	awayScore = ("'" + str(awayTeamScore) + "'") if awayTeamScore else "NULL"
   	numDrives = "'" + str(numDrives) + "'" if numDrives else "NULL"
   	parserCode = "'" + str(parserCode) + "'"
   	
   	cmd += "(" + id + ", "
   	cmd += time + ", "
   	cmd += year + ", "
   	cmd += month + ", "
   	cmd += day + ", "
   	cmd += venue + ", "
   	cmd += city + ", "
   	cmd += ids + ", "
   	cmd += homeScore + ", "
   	cmd += awayScore + ", "
   	cmd += numDrives + ", "
   	cmd += parserCode + ")\n"
	
   	try:
		cursor.execute(cmd)
	except MySQLdb.Error, e:
		print "Error inserting data into games %d: %s" % (e.args[0], e.args[1])
		print cmd
   	
   	if closeConnection:
		cursor.close()
		conn.close()

def verifyNextGame(skiplist = [], cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	cursor.execute("SELECT gameID FROM games WHERE parserCode = \"" + str(gameDefs.PARSER_ESPN) + "\"")
	rows = cursor.fetchall()
	i = 0
	noErrors = True
	while noErrors and i < len(rows):
   		gameID = rows[i][0]
   		if not skiplist.contains(gameID):
	   		noErrors = verifyGame(gameID, cursor)
	   		if noErrors:
	   			storeGame(gameID, cursor)
   		i += 1
   	
   	if closeConnection:
		cursor.close()
		conn.close()
	
	if noErrors:
		return None
	else:
	   	return gameID

def verifyGame(gameID, cursor = None):
	closeConnection = False
	if cursor == None:
		conn = MySQLdb.connect(host = parsingHost, user = parsingUser, db = parsingDatabase)
		cursor = conn.cursor()
		closeConnection = True
	
	noErrors = True

	cursor.execute("SELECT homeTeamID, awayTeamID, homeScore, awayScore FROM games WHERE gameID = \"" + str(gameID) + "\"")
   	rows = cursor.fetchall()
   	gameRow = rows[0]
   	homeTeamID = gameRow[0]
   	awayTeamID = gameRow[1]
   	homeTeamScore = gameRow[2]	# might be 'None'
   	awayTeamScore = gameRow[3]	# might be 'None'
	
	homeScore = 0
	awayScore = 0
	
   	prevDown = -1
   	prevYard = 20
   	prevQtr = 0
   	prevResult = gameDefs.RESULT_NONE
   	newQtr = True
   	score = False
   	cursor.execute("SELECT driveID, teamPossID, pointsThisDrive, defPointsThisDrive FROM drives WHERE gameID = \"" + str(gameID) + "\"")
   	rows = list(cursor.fetchall())
   	rows.sort()
   	for row in rows:
   		driveID = row[0]
   		teamPossID = row[1]
   		points = row[2]		# might be 'None'
   		defPoints = row[3]	# might be 'None'
   		
   		# check for 'None' values on all inputs that might have them
   		# if a value is None, don't trigger an error -- simply ignore that value
   	   	cursor.execute("SELECT playID, playText, quarter, down, startingYard, endingYard, result FROM plays WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\"")
   		playRows = list(cursor.fetchall())
   		playRows.sort()
   		for playRow in playRows:
   			playID = playRow[0]
   			text = playRow[1]			# might be 'None'
   			qtr = playRow[2]			# might be 'None'
   			down = playRow[3]			# might be 'None'
   			startingYard = playRow[4]	# might be 'None'
   			endingYard = playRow[5]		# might be 'None'
   			result = playRow[6]
   			
   			isReturning = False
   			mightChangePoss = False
   			hasChangePossPenalty = False
   			
   			eventPrevYard = startingYard
   	   		cursor.execute("SELECT eventID, eventType, startingYard, endingYard FROM events WHERE gameID = \"" + str(gameID) + "\" AND driveID = \"" + str(driveID) + "\" AND playID = \"" + str(playID) + "\"")
   			eventRows = list(cursor.fetchall())
   			eventRows.sort()
   			for eventRow in eventRows:
   				eventID = eventRow[0]
   				eventType = eventRow[1]
   				eventStartingYard = eventRow[2]	# might be 'None'
   				eventEndingYard = eventRow[3]	# might be 'None'
   				
   				idEStr = 'G' + str(gameID) + ' D' + str(driveID) + ' P' + str(playID) + ' E' + str(eventID)
   				if eventType == gameDefs.EVENT_RETURN:
   					isReturning = not isReturning
   					if eventPrevYard and eventStartingYard and eventStartingYard != 100 - eventPrevYard:
   						noErrors = False
   						print idEStr + ': prevEndYard = ' + str(eventPrevYard) + ', startYard = ' + str(eventStartingYard)
   				elif eventType == gameDefs.EVENT_PENALTY and mightChangePoss:
   					hasChangePossPenalty = True
   					if eventPrevYard and eventStartingYard and eventStartingYard != 100 - eventPrevYard:
   						noErrors = False
   						print idEStr + ': prevEndYard = ' + str(eventPrevYard) + ', startYard = ' + str(eventStartingYard)
				elif eventPrevYard and eventStartingYard and eventStartingYard != eventPrevYard:
   					noErrors = False
   					print idEStr + ': prevEndYard = ' + str(eventPrevYard) + ', startYard = ' + str(eventStartingYard)
				if eventType == gameDefs.EVENT_KICKOFF or eventType == gameDefs.EVENT_PUNT or eventType == gameDefs.EVENT_INTERCEPTION:
					mightChangePoss = True
				elif eventType == gameDefs.EVENT_RECOVERY and result == gameDefs.RESULT_TURNOVER:
					mightChangePoss = True
				else:
					mightChangePoss = False
				eventPrevYard = eventEndingYard
			
			idEStr = 'G' + str(gameID) + ' D' + str(driveID) + ' P' + str(playID) + ' E' + str(eventID) + ' ' + gameDefs.resultString(result)
   			if (result == gameDefs.RESULT_KICK_RECEIVED or result == gameDefs.RESULT_TURNOVER) and (isReturning or hasChangePossPenalty):
   				if eventPrevYard and eventStartingYard and eventPrevYard != 100 - endingYard:
   					noErrors = False
   					print idEStr + ': eventPrevYard = ' + str(eventPrevYard) + ', endingYard = ' + str(endingYard)
			elif result == gameDefs.RESULT_DEFENSIVE_TOUCHDOWN or result == gameDefs.RESULT_DEFENSIVE_SAFETY or result == gameDefs.RESULT_DEFENSIVE_TOUCHBACK:
   				if eventPrevYard and eventStartingYard and eventPrevYard != 100 - endingYard:
   					noErrors = False
   					print idEStr + ': eventPrevYard = ' + str(eventPrevYard) + ', endingYard = ' + str(endingYard)
			elif (result == gameDefs.RESULT_DEFENSIVE_TURNOVER or result == gameDefs.RESULT_TOUCHBACK) and isReturning:
   				if eventPrevYard and eventStartingYard and eventPrevYard != 100 - endingYard:
   					noErrors = False
   					print idEStr + ': eventPrevYard = ' + str(eventPrevYard) + ', endingYard = ' + str(endingYard)
			elif eventPrevYard and eventStartingYard and eventPrevYard != endingYard:
   				noErrors = False
   				print idEStr + ': eventPrevYard = ' + str(eventPrevYard) + ', endingYard = ' + str(endingYard)
			
   			if qtr and qtr > prevQtr:
   				prevQtr = qtr
   				if qtr != 2 and qtr != 4:
   					newQtr = True
   			
   			idStr = 'G' + str(gameID) + ' D' + str(driveID) + ' P' + str(playID)
   			if newQtr and (qtr == 1 or qtr == 3):
   				# down should == 0, startingYard should == 30
   				if down and down != 0:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be 0 (new qtr)'
   				if startingYard and startingYard != 30:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be 30 (new qtr)'
   			elif prevResult == gameDefs.RESULT_NONE:
   				noErrors = False
   				print idStr + ': no result?'
   			elif newQtr and qtr > 4:
   				# down should == 1, startingYard should == 75
   				if down and down != 1:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be 1 (overtime)'
   				if startingYard and startingYard != 75:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be 75 (overtime)'
   			elif prevResult == gameDefs.RESULT_REPEAT_DOWN:
   				# down should == prevDown, startingYard should == prevYard
   				if down and prevDown and down != prevDown:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be ' + str(prevDown) + ' (previous down)'
   				if startingYard and prevYard and startingYard != prevYard:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be ' + str(prevYard) + ' (previous yard)'
   			elif prevDown == -1:
   				# down should == 0, startingYard should == 30
   				if down and down != 0:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be 0 (kickoff after score)'
   				if startingYard and startingYard != 30:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be 30 (kickoff after score)'
   			elif prevResult == gameDefs.RESULT_ADVANCE_DOWN:
   				# down should == prevDown+1, startingYard should == prevYard
   				if down and prevDown and down != prevDown+1:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be ' + str(prevDown+1) + ' (previous down+1)'
   				if startingYard and prevYard and startingYard != prevYard:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be ' + str(prevYard) + ' (previous yard)'
   			elif prevResult == gameDefs.RESULT_FIRST_DOWN or prevResult == gameDefs.RESULT_DEFENSIVE_TURNOVER:
   				# down should == 1, startingYard should == prevYard
   				if down and down != 1:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be 1 (first down)'
   				if startingYard and prevYard and startingYard != prevYard:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be ' + str(prevYard) + ' (previous yard)'
   			elif prevResult == gameDefs.RESULT_TURNOVER_ON_DOWNS or prevResult == gameDefs.RESULT_KICK_RECEIVED or prevResult == gameDefs.RESULT_TURNOVER:
   				# down should == 1, startingYard should == (100 - prevYard)
   				if down and down != 1:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be 1 (first down defense)'
   				if startingYard and prevYard and startingYard != (100 - prevYard):
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be ' + str(100 - prevYard) + ' (100 - previous yard)'
   			elif prevResult == gameDefs.RESULT_FIELD_GOAL or prevDown == -1:
   				# down should == 0, startingYard should == 30
   				if down and down != 0:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be 0 (kickoff after score)'
   				if startingYard and startingYard != 30:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be 30 (kickoff after score)'
   			elif prevResult == gameDefs.RESULT_MISSED_FIELD_GOAL:
   				# down should == 1, startingYard should == (> of (100 - prevYard) and 20)
   				if down and down != 1:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be 1 (missed field goal)'
   				if prevYard:
   					if prevYard > 80:
   						presumedYard = 20
   					else:
   						presumedYard = 100 - prevYard
   					if startingYard and startingYard != presumedYard:
   						noErrors = False
   						print idStr + ': startingYard = ' + str(startingYard) + ', should be ' + str(presumedYard) + ' (> of (100 - prevYard) and 20)'
   			elif prevResult == gameDefs.RESULT_TOUCHDOWN or prevResult == gameDefs.RESULT_DEFENSIVE_TOUCHDOWN:
   				# down should == -1, startingYard should == 97
   				if down and down != -1:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be -1 (touchdown)'
   				if startingYard and startingYard != 97:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be 97 (touchdown)'
   			elif prevResult == gameDefs.RESULT_SAFETY or prevResult == gameDefs.RESULT_DEFENSIVE_SAFETY:
   				# down should == 0, startingYard should == 20
   				if down and down != 0:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be 0 (safety)'
   				if startingYard and startingYard != 20:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be 20 (safety)'
   			elif prevResult == gameDefs.RESULT_TOUCHBACK or prevResult == gameDefs.RESULT_DEFENSIVE_TOUCHBACK:
   				# down should == 1, startingYard should == 20
   				if down and down != 1:
   					noErrors = False
   					print idStr + ': down = ' + str(down) + ', should be 1 (touchback)'
   				if startingYard and startingYard != 20:
   					noErrors = False
   					print idStr + ': startingYard = ' + str(startingYard) + ', should be 20 (touchback)'
   			
   			#kickoff = (prevDown == -1) or (prevResult == gameDefs.RESULT_FIELD_GOAL) or newQtr
   			
   			#if startingYard != prevYard and not kickoff:
   			#	if not (playID == 0 and startingYard == 100 - prevYard):
	   		#		print 'P ' + str(playID) + ' of D ' + str(driveID) + ': down = ' + str(down) + ', prevEndYard = ' + str(prevYard) + ', startYard = ' + str(startingYard)
   			#		print text
			prevDown = down
   			prevYard = endingYard
   			prevResult = result
   			newQtr = False
   		
   		if points and defPoints:
			if teamPossID == homeTeamID:
				homeScore += points
				awayScore += defPoints
			else:
				homeScore += defPoints
				awayScore += points
   		
   		#if startingYard != 100 - prevYard and prevYard != 100:
   		#	print 'Drive ' + str(driveID) + ': prevYard = ' + str(prevYard) + ', nextYard = ' + str(startingYard)
   		prevYard = endingYard
   	
   	if homeTeamScore and homeScore != homeTeamScore:
		cursor.execute("SELECT teamName FROM teams WHERE teamID = \"" + str(homeTeamID) + "\"")
   		homeTeamName = cursor.fetchall()[0][0]
   		noErrors = False
		print "Home team (" + homeTeamName + ") score doesn't match : " + str(homeTeamScore) + " vs. " + str(homeScore)
	if awayTeamScore and awayScore != awayTeamScore:
		cursor.execute("SELECT teamName FROM teams WHERE teamID = \"" + str(awayTeamID) + "\"")
   		awayTeamName = cursor.fetchall()[0][0]
   		noErrors = False
		print "Away team (" + awayTeamName + ") score doesn't match : " + str(awayTeamScore) + " vs. " + str(awayScore)
	
	if noErrors:
		cursor.execute("SELECT parserCode FROM games WHERE gameID = \"" + str(gameID) + "\"")
   		parserCode = cursor.fetchall()[0][0]
   		parserCode |= gameDefs.PARSER_VERIFIED
   		cursor.execute("UPDATE games SET parserCode = \"" + str(parserCode) + "\" WHERE gameID = \"" + str(gameID) + "\"")
   		
		cursor.execute("INSERT INTO storagedb.games SELECT * FROM games WHERE gameID = \"" + str(gameID) + "\"")
		cursor.execute("INSERT INTO storagedb.drives SELECT * FROM drives WHERE gameID = \"" + str(gameID) + "\"")
		cursor.execute("INSERT INTO storagedb.plays SELECT * FROM plays WHERE gameID = \"" + str(gameID) + "\"")
		cursor.execute("INSERT INTO storagedb.events SELECT * FROM events WHERE gameID = \"" + str(gameID) + "\"")
		
		cursor.execute("DELETE FROM events WHERE gameID = \"" + str(gameID) + "\"")
		cursor.execute("DELETE FROM plays WHERE gameID = \"" + str(gameID) + "\"")
		cursor.execute("DELETE FROM drives WHERE gameID = \"" + str(gameID) + "\"")
		cursor.execute("DELETE FROM games WHERE gameID = \"" + str(gameID) + "\"")
		
	
	if closeConnection:
		cursor.close()
		conn.close()
	
	return noErrors
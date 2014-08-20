import espn
import gameDefs

def espnRecap(url):
	game = espn.getGame(url)
	#game = espn.getTestGame()
	if game:
		rushers = calc(game)
		printResults(rushers)

def calc(game):
	rushers = {}
	
	i = 0
	numDrives = len(game.drives)
	while i < numDrives:
		drive = game.drives[i]
		
		if drive.homePoss:
			pointsAhead = drive.homeScore - drive.awayScore
		else:
			pointsAhead = drive.awayScore - drive.homeScore
		
		j = 0
		numPlays = len(drive.plays)
		while j < numPlays:
			play = drive.plays[j]
			
			firstEvent = play.events[0]
			if firstEvent.eventType == gameDefs.EVENT_RUSH:
				netYards = firstEvent.endingYard - firstEvent.startingYard
				pctGained = netYards / float(play.distance)
				rusher = firstEvent.offense1
				#play.printSelf()
				#print rusher + ' rushed for ' + str(netYards) + ' of ' + str(play.distance) + ' yards (' + str(pctGained) + ')'
				
				if play.quarter == 4 and pointsAhead > 0:
					if play.down == 1:
						hit = pctGained >= 0.3
					elif play.down == 2:
						hit = pctGained >= 0.5
					else:
						hit = pctGained >= 1
				elif play.quarter == 4 and pointsAhead < -8:
					if play.down == 1:
						hit = pctGained >= 0.5
					elif play.down == 2:
						hit = pctGained >= 0.65
					else:
						hit = pctGained >= 1
				else:
					if play.down == 1:
						hit = pctGained >= 0.4
					elif play.down == 2:
						hit = pctGained >= 0.6
					else:
						hit = pctGained >= 1
				
				if rusher not in rushers:
					rushers[rusher] = [0,0]
				if hit:
					rushers[rusher][0] += 1
				else:
					rushers[rusher][1] += 1
				
			j += 1
		
		i += 1
	
	return rushers

def printResults(rushers):
	for rusher, results in rushers.items():
		print rusher + ' has ' + str(results[0]) + ' hits and ' + str(results[1]) + ' misses'
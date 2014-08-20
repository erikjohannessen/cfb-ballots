import sys
sys.path.append('CFBDB')
import gameDefs

BALLOT_SIZE = 25

def readBallot(ballot, aggregateVotes):
	# split into lines
	teamNames = ballot.strip().split('\n')
	# check for wrong number of votes
	if len(teamNames) != BALLOT_SIZE:
		print "Wrong number " + len(teamnames) + " of teams!"
		return None
	i = 0
	votes = {}
	while i < BALLOT_SIZE:
		teamName = teamNames[i]
		# remove any leading ranking (numerals)
		j = 0
		while teamName[j].isdigit():
			j += 1
		# then strip periods and spaces
		teamName = teamName[j:].strip('. \t')
		teamCode = gameDefs.teamCode(teamName)
		if teamCode == -1:
			print teamName + " not found!"
			return None
		if teamCode in votes:
			print "Multiple votes for " + teamName + "!"
			return None
		else:
			votes[teamCode] = BALLOT_SIZE - i
		i += 1
	for teamCode in votes.keys():
		if teamCode in aggregateVotes:
			aggregateVotes[teamCode] += votes[teamCode]
		else:
			aggregateVotes[teamCode] = votes[teamCode]
	return aggregateVotes

def printResults(votes):
	# build votes array
	totals = []
	for code, numVotes in votes.items():
		totals.append([code, numVotes])
	# sort votes
	totals = sorted(totals, key=lambda tuple: tuple[1], reverse=True)
	# print votes
	rank = 0
	count = 0
	currentNumVotes = 100000 # way more than we'll ever have?
	for entry in totals:
		count += 1
		teamCode = entry[0]
		numVotes = entry[1]
		if numVotes < currentNumVotes:
			if count > BALLOT_SIZE and rank <= BALLOT_SIZE:
				print ""
			rank = count
			currentNumVotes = numVotes
		print str(rank) + ". " + gameDefs.teamName(teamCode) + " -> " + str(numVotes)

def readBallots(fileName):
	# split file into individual ballots
	f = file(fileName)
	fileContents = f.read()
	ballots = fileContents.split('---')
	votes = {}
	for ballot in ballots:
		votes = readBallot(ballot, votes)
	printResults(votes)
	
if __name__ == "__main__":
    readBallots(sys.argv[1])
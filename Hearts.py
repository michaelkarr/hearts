from Deck import Deck
from Card import Card, Suit, Rank
from Player import Player
from Trick import Trick
from AutoPlayer import AutoPlayer,QLearningBoi
from HumanPlayer import HumanPlayer
from MCTSPlayer import MCTSPlayer

'''
Change auto to False if you would like to play the game manually.
This allows you to make all passes, and plays for all four players.
When auto is True, passing is disabled and the computer plays the
game by "guess and check", randomly trying moves until it finds a
valid one.
'''
auto = True

totalTricks = 13
maxScore = 100
queen = 12
noSuit = 0
spades = 2
hearts = 3
cardsToPass = 3

class Hearts:
	def __init__(self, players):
		
		self.roundNum = 0
		self.trickNum = 0 # initialization value such that first round is round 0
		self.dealer = -1 # so that first dealer is 0
		self.passes = [1, -1, 2, 0] # left, right, across, no pass
		self.currentTrick = Trick()
		self.trickWinner = -1
		self.heartsBroken = False
		self.losingPlayer = None
		self.passingCards = [[], [], [], []]


		# Make four players

		self.players = players
                #self.players = [QLearningBoi("Dani"), AutoPlayer("Desmond"), AutoPlayer("Ben"), AutoPlayer("Tyler")]
		
		'''
		Player physical locations:
		Game runs clockwise

			p3
		p2		p4
			p1

		'''

		# Generate a full deck of cards and shuffle it
		self.newRound()

	def handleScoring(self):
		p, highestScore = None, 0
		print("\nScores:\n")
		for player in self.players:
			print(player.name + ": " + str(player.score))
			if player.score > highestScore:
				p = player
				highestScore = player.score
			self.losingPlayer = p

		

	def newRound(self):
		self.deck = Deck()
		self.deck.shuffle()
		self.roundNum += 1
		self.trickNum = 0
		self.trickWinner = -1
		self.heartsBroken = False
		self.dealer = (self.dealer + 1) % len(self.players)
		self.dealCards()
		self.currentTrick = Trick()
		self.passingCards = [[], [], [], []]
		for p in self.players:
			p.discardTricks()

	def getFirstTrickStarter(self):
		for i,p in enumerate(self.players):
			if p.hand.contains2ofclubs:
				self.trickWinner = i

	def dealCards(self):
		i = 0
		while(self.deck.size() > 0):
			self.players[i % len(self.players)].addCard(self.deck.deal())
			i += 1


	def evaluateTrick(self, printOut=True):
		self.trickWinner = self.currentTrick.winner
		p = self.players[self.trickWinner]
		p.trickWon(self.currentTrick)
		self.printCurrentTrick()
		if printOut:
			print(f"{p.name} won the trick.")
		# print 'Making new trick'
		self.currentTrick = Trick()
		if printOut:
			print(self.currentTrick.suit)
		

	def passCards(self, index):
		print(self.printPassingCards())
		passTo = self.passes[self.trickNum] # how far to pass cards
		passTo = (index + passTo) % len(self.players) # the index to which cards are passed
		while len(self.passingCards[passTo]) < cardsToPass: # pass three cards
			passCard = None
			while passCard is None: # make sure string passed is valid
				passCard = self.players[index].play(self, option='pass')
				if passCard is not None:
					# remove card from player hand and add to passed cards
					self.passingCards[passTo].append(passCard)
					self.players[index].removeCard(passCard)

	def distributePassedCards(self):
		for i,passed in enumerate(self.passingCards):
			for card in passed:
				self.players[i].addCard(card)
		self.passingCards = [[], [], [], []]


	def printPassingCards(self):
		out = "[ "
		for passed in self.passingCards:
			out += "["
			for card in passed:
				out += card.__str__() + " "
			out += "] "
		out += " ]"
		return out


	def playersPassCards(self):
		
		self.printPlayers()
		if not self.trickNum % 4 == 3: # don't pass every fourth hand
			for i in range(0, len(self.players)):
				print('\n')
				self.printPlayer(i)
				self.passCards(i % len(self.players))

			self.distributePassedCards()
			self.printPlayers()

	def finishTrick(self, start, action):
		print("finishTrick start")
		if self.trickNum >= totalTricks:
			print('end game')
			return
		playersLeft = len(self.players) - self.currentTrick.cardsInTrick
		# have each player take their turn
		for i in range(start, start + playersLeft):
			# print("playerNum: ", i)
			# self.printCurrentTrick()
			curPlayerIndex = i % len(self.players)
			# self.printPlayer(curPlayerIndex)
			curPlayer = self.players[curPlayerIndex]
			addCard = None

			while addCard is None: # wait until a valid card is passed
				if i == 0:
					addCard = action
				else:
					addCard = curPlayer.play(self) # change auto to False to play manually


				# the rules for what cards can be played
				# card set to None if it is found to be invalid
				if addCard is not None:
					
					# if it is not the first trick and no cards have been played,
					# set the first card played as the trick suit if it is not a heart
					# or if hearts have been broken
					if self.trickNum != 0 and self.currentTrick.cardsInTrick == 0:
						if addCard.suit == Suit(hearts) and not self.heartsBroken:
							# if player only has hearts but hearts have not been broken,
							# player can play hearts
							if not curPlayer.hasOnlyHearts():
								# print(curPlayer.hasOnlyHearts())
								# print(curPlayer.hand.__str__())
								print("Hearts have not been broken.")
								addCard = None
							else:
								self.currentTrick.setTrickSuit(addCard)
						else:
							self.currentTrick.setTrickSuit(addCard)

					# player tries to play off suit but has trick suit
					if addCard is not None and addCard.suit != self.currentTrick.suit:
						if curPlayer.hasSuit(self.currentTrick.suit):
							print("Must play the suit of the current trick.")
							addCard = None
						elif addCard.suit == Suit(hearts):
							self.heartsBroken = True

					if self.trickNum == 0:
						if addCard is not None:
							if addCard.suit == Suit(hearts):
								print("Hearts cannot be broken on the first hand.")
								self.heartsBroken = False
								addCard = None
							elif addCard.suit == Suit(spades) and addCard.rank == Rank(queen):
								print("The queen of spades cannot be played on the first hand.")
								addCard = None

					if addCard is not None and self.currentTrick.suit == Suit(noSuit):
						if addCard.suit == Suit(hearts) and not self.heartsBroken:
							print("Hearts not yet broken.")
							addCard = None

					

					if addCard is not None:
						if addCard == Card(queen, spades):
							self.heartsBroken = True
						curPlayer.removeCard(addCard)


			self.currentTrick.addCard(addCard, curPlayerIndex)
			print('all players played')
		self.evaluateTrick(printOut=False)
		self.trickNum += 1

	def playTrick(self, start):
		shift = 0
		if self.trickNum == 0:
			startPlayer = self.players[start]
			addCard = startPlayer.play(self, option="play", c='2c')
			startPlayer.removeCard(addCard)

			self.currentTrick.addCard(addCard, start)

			shift = 1 # alert game that first player has already played

		# have each player take their turn
		for i in range(start + shift, start + len(self.players)):
			self.printCurrentTrick()
			curPlayerIndex = i % len(self.players)
			self.printPlayer(curPlayerIndex)
			curPlayer = self.players[curPlayerIndex]
			addCard = None

			while addCard is None: # wait until a valid card is passed
				
				addCard = curPlayer.play(self) # change auto to False to play manually
				# print('addCard', addCard)

				# the rules for what cards can be played
				# card set to None if it is found to be invalid
				if addCard is not None:
					
					# if it is not the first trick and no cards have been played,
					# set the first card played as the trick suit if it is not a heart
					# or if hearts have been broken
					if self.trickNum != 0 and self.currentTrick.cardsInTrick == 0:
						if addCard.suit == Suit(hearts) and not self.heartsBroken:
							# if player only has hearts but hearts have not been broken,
							# player can play hearts
							if not curPlayer.hasOnlyHearts():
								print(curPlayer.hasOnlyHearts())
								print(curPlayer.hand.__str__())
								print("Hearts have not been broken.")
								addCard = None
							else:
								self.currentTrick.setTrickSuit(addCard)
						else:
							self.currentTrick.setTrickSuit(addCard)

					# player tries to play off suit but has trick suit
					if addCard is not None and addCard.suit != self.currentTrick.suit:
						if curPlayer.hasSuit(self.currentTrick.suit):
							print("Must play the suit of the current trick.")
							addCard = None
						elif addCard.suit == Suit(hearts):
							self.heartsBroken = True

					if self.trickNum == 0:
						if addCard is not None:
							if addCard.suit == Suit(hearts):
								print("Hearts cannot be broken on the first hand.")
								self.heartsBroken = False
								addCard = None
							elif addCard.suit == Suit(spades) and addCard.rank == Rank(queen):
								print("The queen of spades cannot be played on the first hand.")
								addCard = None

					if addCard is not None and self.currentTrick.suit == Suit(noSuit):
						if addCard.suit == Suit(hearts) and not self.heartsBroken:
							print("Hearts not yet broken.")
							addCard = None

					

					if addCard is not None:
						if addCard == Card(queen, spades):
							self.heartsBroken = True
						curPlayer.removeCard(addCard)


			self.currentTrick.addCard(addCard, curPlayerIndex)
			
		self.evaluateTrick()
		self.trickNum += 1

	# print player's hand
	def printPlayer(self, i):
		p = self.players[i]
		print (p.name + "'s hand: " + str(p.hand))

	# print all players' hands
	def printPlayers(self):
		for p in self.players:
			print (p.name + ": " + str(p.hand))

	# show cards played in current trick
	def printCurrentTrick(self):
		trickStr = '\nCurrent table:\n'
		trickStr += "Trick suit: " + self.currentTrick.suit.__str__() + "\n"
		for i, card in enumerate(self.currentTrick.trick):
			if self.currentTrick.trick[i] is not 0:
				trickStr += self.players[i].name + ": " + str(card) + "\n"
			else:
				trickStr += self.players[i].name + ": None\n"
		print(trickStr)

	def getWinner(self):
		minScore = 200 # impossibly high
		winner = None
		for p in self.players:
			if p.score < minScore:
				winner = p
				minScore = p.score
		return winner




def main(players):
	hearts = Hearts(players)

	# play until someone loses
	while hearts.losingPlayer is None or hearts.losingPlayer.score < maxScore:
		while hearts.trickNum < totalTricks:
			print("Round", hearts.roundNum)
			if hearts.trickNum == 0:
				if not auto:
					hearts.playersPassCards()
				hearts.getFirstTrickStarter()
			print('\nPlaying trick number', hearts.trickNum + 1)
			hearts.playTrick(hearts.trickWinner)

		# tally scores
		hearts.handleScoring()

		# new round if no one has lost
		if hearts.losingPlayer.score < maxScore:
			print("New round")
			hearts.newRound()

	print('\n')# spacing
	print(hearts.getWinner().name, "wins!")
	return hearts.getWinner().name



if __name__ == '__main__':
	players = [MCTSPlayer("Dani"), AutoPlayer("Desmond"), AutoPlayer("Ben"), AutoPlayer("Tyler")]
	# players = [QLearningBoi("Dani"), AutoPlayer("Desmond"), AutoPlayer("Ben"), AutoPlayer("Tyler")]

	main(players)


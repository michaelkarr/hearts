from Player import Player
import time
import math
from collections import defaultdict
import copy
import random
from Card import Card, Suit, Rank


class MCTSPlayer(Player):

	def __init__(self, name):
		super().__init__(name)
		self.q = defaultdict(int)
		self.n = defaultdict(int)
		self.name = name
		self.lastAction = None

		self.visitedStates = set()

    # Synthesize the state from the player information
	def getState(self, game):
		state = []
		actions = []
		for sublist in self.hand.hand:
			for a in sublist:
				actions.append(a.__str__())
		state.append(tuple(actions))
		trick = []
		for t in game.currentTrick.trick:
			trick.append(t.__str__())
		state.append(tuple(trick))
		return tuple(state)

	def valid(self, state, action):
		if state[1][-1] == '0':
			return True
		suit = state[1][-1][1] # 2nd character of 1st word in trick
		return action[1] == suit

	def getActions(self, state):
		hand = state[0]
		cards = []
		for card in hand:
			cards.append(card)
		return cards

	def isValid(self, addCard, state, game):
		spades = 2
		noSuit = 0
		hearts = 3
		queen = 12
		# print("curr suit", game.currentTrick.suit)
		curPlayer = self
		if addCard is not None:		
			# if it is not the first trick and no cards have been played,
			# set the first card played as the trick suit if it is not a heart
			# or if hearts have been broken
			if game.trickNum != 0 and game.currentTrick.cardsInTrick == 0:
				if addCard.suit == Suit(hearts) and not game.heartsBroken:
					# if player only has hearts but hearts have not been broken,
					# player can play hearts
					if not curPlayer.hasOnlyHearts():
						# print(curPlayer.hasOnlyHearts())
						# print(curPlayer.hand.__str__())
						# print("Hearts have not been broken.")
						addCard = None
						return False
					# else:
						# game.currentTrick.setTrickSuit(addCard)
				# else:
					# game.currentTrick.setTrickSuit(addCard)
			if game.currentTrick.suit == Suit(-1):
				return True
			# player tries to play off suit but has trick suit
			
			if addCard is not None and addCard.suit != game.currentTrick.suit:
				if curPlayer.hasSuit(game.currentTrick.suit):
					# print('invalid 2', addCard)
					# print("Must play the suit of the current trick.")
					addCard = None
					return False
				elif addCard.suit == Suit(hearts):
					game.heartsBroken = True

			if game.trickNum == 0:
				if addCard is not None:
					if addCard.suit == Suit(hearts):
						# print("Hearts cannot be broken on the first hand.")
						game.heartsBroken = False
						addCard = None
						return False
					elif addCard.suit == Suit(spades) and addCard.rank == Rank(queen):
						# print("The queen of spades cannot be played on the first hand.")
						addCard = None
						return False

			if addCard is not None and game.currentTrick.suit == Suit(noSuit):
				if addCard.suit == Suit(hearts) and not game.heartsBroken:
					# print("Hearts not yet broken.")
					addCard = None
					return False


			if addCard is not None:
				return True
			else:
				return False


	#str2index not working
	def getValidActions(self, state, game):
		valid = []
		# print(game.currentTrick.suit)
		actions = self.getActions(state)
		for action in actions:
			if self.isValid(self.str2card(actions, action), state, game):
				valid.append(action)
		# print('all actions', actions)
		# print('valid actions', valid)
		return valid

	def bestAction(self, state, game, explorationBonus=False):
	    return self.bestActionAndVal(state, game)[0]
	    
	def bestActionVal(self, state, game, explorationBonus=False):
	    return self.bestActionAndVal(state, game)[1]

	def getExplorationBonus(self, state, action):
		c = 0.9 #exploration constant
		n_state = 0
		for action in getActions(state):
			n_state += self.n[(state, action)]
		return c*math.sqrt(n_state/self.n[(state, action)])

	def bestActionAndVal(self, state, game, explorationBonus=False):
		max_val = float('-inf')
		max_action = self.getValidActions(state, game)[0]
		# print(self.getActions(state))
		for action in self.getValidActions(state, game):
			val = self.q[(state, action)]
			if explorationBonus: 
				val+=self.getExplorationBonus(state, action)
			if val > max_val:
				max_val = val
				max_action = action
		return (max_action, max_val)

	def selectAction(self, state, game, originalGame):
		print('\n\n\n\n\n\n')
		print("start selectAction")
		startTime = time.time()
		numSecs = 10
		# print('start time', startTime)
		d = 3
		while time.time() < startTime+numSecs:
			# print('stopTime', startTime+numSecs)
			self.simulate(state, d, copy.deepcopy(game))
			# d+=1
		print("completed SelectAction")
		print('\n\n\n\n\n\n')


		return self.bestAction(state, originalGame)

	def rollout(self, state, d, game):
		if d == 0: 
			return 0
		#could change to be a better policy
		action = random.choice(self.getValidActions(state, game)) 
		game.finishTrick(0, self.str2card(self.getActions(state), action))
		nextState = self.getState(game)
		nextScore = game.players[0].score
		reward = 13 - (self.score - nextScore)
		return reward + self.rollout(nextState, d-1, game)

	def explore(self, state, d, game):
		self.visitedStates.add(state)
		return self.rollout(state, d, game)

	def simulate(self, state, d, game):
		if d==0: 
			return 0
		numTricks = 13
		if game.trickNum >= numTricks:
			return 0
		if state not in self.visitedStates:
			self.explore(state, d, game)
		# action = random.choice(self.getValidActions(state, game))
		action = self.bestAction(state, game, True) #use explorationBonus
		game.finishTrick(0, self.str2card(self.getActions(state), action))
		nextState = self.getState(game)
		nextScore = game.players[0].score
		reward = 13 - (self.score - nextScore)
		q = reward + self.simulate(nextState, d-1, game)
		self.n[(state,action)] += 1
		self.q[(state, action)] += q - self.q[(state, action)]/self.n[(state, action)]
		return q 

	def str2card(self, actions, string):
		idx = list(actions).index(string)
		for sublist in self.hand.hand:
			for card in sublist:
				if idx == 0:
					return card
				else:
					idx -= 1

	def play(self, game, option='play', c=None):
		if c is not None:
			return self.hand.playCard(c)
		state = self.getState(game)
		newGame = copy.deepcopy(game)
		action = self.selectAction(state, newGame, game)
		# action = random.choice(self.getValidActions(state, game))
		print('state', state)
		print('!!!')
		print(self.q)
		print('action', action)

		return self.str2card(self.getActions(state), action)
		return self.str2card(self.getActions(state), action)
		# return self.hand.getRandomCard()




		

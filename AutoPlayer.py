import os
import pickle
from Player import Player
from collections import defaultdict

class AutoPlayer(Player):
	def play(self, option='play', c=None):
		if c is not None:
			return self.hand.playCard(c)
		return self.hand.getRandomCard()


class QLearningBoi(Player):
    
    def __init__(self):
        self.q = defaultdict(int)
        self.n = 1
        self.q_filename = self.name + '.pickle'
        self.n_filename = self.name + 'n.pickle'
        self.lastAction = None
        self.lastState = None
        self.lastReward = None
        self.syncQAndn()

    def syncQAndn(self):
        if os.path.exists(self.q_filename):
            self.q = pickle.load(open(self.q_filename, 'rb+'))
        else:
            self.q = defaultdict(int)
        if os.path.exists(self.n_filename):
            self.n = pickle.load(open(self.n_filename, 'rb+'))
        else:
            self.n = 1

    # Synthesize the state from the player information
    def getState(self, game):
        state = []
        state.append(tuple(self.hand.hand))
        state.append(tuple(game.currentTrick.Trick))
        return tuple(state)

    def getActions(self, state):
        hand = state[0]
        return hand

    def bestAction(self, state):
        return self.bestActionAndVal(state)[0]
        
    def bestActionVal(self, state):
        return self.bestActionAndVal(state)[1]

    def bestActionAndVal(self, state):
        max_val = float('-inf')
        max_action = getActions(state)[0]
        for action in getActions(state):
            val = self.q[(state, action)]
            if val > max_val:
                max_val = val
                max_action = action
        return (max_action, max_val)

    def writeQAndn(self):
        pickle.write(self.q, open(self.q_filename, 'wb+'))
        pickle.write(self.n, open(self.n_filename, 'wb+'))

    # Qlearning update
    def updateQ(self, state, gamma=0.9):
        lr = (1/self.n)
        prev = (self.lastState, self.lastAction)
        self.q[prev] += \
                lr*(self.lastReward + gamma*self.bestActionVal(state)-self.q[prev])
        self.n += 1
        self.writeQAndn()

    def play(self, game, option='play', c=None):
        state = self.getState(game)
        if self.lastAction and self.lastState and self.lastReward: #Qlearning update
            self.updateQ(state)
        if c is not None:
            return self.hand.playCard(c)
        action = self.bestAction(state)
        reward = self.bestActionVal(state)
        # So we can update Q
        self.lastState = state
        self.lastAction = action
        self.lastReward = reward
        return action

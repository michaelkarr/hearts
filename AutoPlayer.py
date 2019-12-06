import os
import pickle
import numpy as np
from Player import Player
from collections import defaultdict

class AutoPlayer(Player):

    def play(self, game, option='play', c=None):
        if c is not None:
            return self.hand.playCard(c)
        return self.hand.getRandomCard()

class QLearningBoi(Player):
    
    def __init__(self, name):
        super().__init__(name)
        self.q = defaultdict(int)
        self.n = 1
        self.q_filename = self.name + '.pickle'
        self.n_filename = self.name + 'n.pickle'
        self.lastAction = None
        self.lastState = None
        self.lastReward = None
        self.lastScore = 0
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
            if self.valid(state, card):
                cards.append(card)
        return cards

    def bestAction(self, state):
        return self.bestActionAndVal(state)[0]
        
    def bestActionVal(self, state):
        return self.bestActionAndVal(state)[1]

    def bestActionAndVal(self, state):
        max_val = float('-inf')
        max_action = self.getActions(state)[0]
        for action in self.getActions(state):
            val = self.q[tuple([state[0], state[1], tuple([action])])]
            if val > max_val:
                max_val = val
                max_action = action
        return (max_action, max_val)

    def writeQAndn(self):
       pickle.dump(self.q, open(self.q_filename, 'wb'))
       pickle.dump(self.n, open(self.n_filename, 'wb'))

    # Qlearning update
    def updateQ(self, state, gamma=0.9):
        lr = (1/self.n)
        prev = (self.lastState[0], self.lastState[1], tuple(self.lastAction))
        self.q[prev] += \
                lr*(self.lastReward + gamma*self.bestActionVal(state)-self.q[prev])
        self.n += 1
        self.writeQAndn()

    def str2card(self, state, string):
        idx = list(self.getActions(state)).index(string)
        for sublist in self.hand.hand:
            for card in sublist:
                if idx == 0:
                    return card
                else:
                    idx -= 1
    
    def epsilon_greedy(self, card, eps=0.2):
        x = np.random.rand()
        if x < eps:
            return self.hand.getRandomCard()
        else:
            return card

    def play(self, game, option='play', c=None):
        state = self.getState(game)
        if len(self.getActions(state)) == 0:
            return self.hand.getRandomCard()
        #if self.lastAction and self.lastState and self.lastReward: #Qlearning update
        #    self.updateQ(state)
        if c is not None:
            return self.hand.playCard(c)
        action = self.bestAction(state)
        reward = 13 - (self.score - self.lastScore)
        # So we can update Q
        self.lastState = state
        self.lastAction = action
        self.lastReward = reward
        self.lastScore = self.score
        play_card = self.str2card(state, action)
        return self.epsilon_greedy(play_card)

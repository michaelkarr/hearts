from Player import Player

class AutoPlayer(Player):
	def play(self, option='play', c=None):
		if c is not None:
			return self.hand.playCard(c)
		return self.hand.getRandomCard()

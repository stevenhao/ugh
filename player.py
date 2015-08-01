import random

class Player:
    def __init__(self, game, name):
        self.cards = []
        self.game = game
        self.name = name

    def play(self, card):
        self.game.play(self, card)

    def action(self):
        # default - random
        self.play(random.choice(self.cards))



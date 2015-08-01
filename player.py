import random

class Player:
  def __init__(self, game, name):
    self.cards = []
    self.game = game
    self.table = game.table
    self.name = name

  def __str__(self):
    return '%s %s' % (self.__class__.__name__, self.name)

  def update_on_action(self, acting_player, action, args):
    pass

  def best_play(self):
    return ('PLAY', random.choice(self.cards))


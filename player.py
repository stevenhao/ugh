import random
from utils import nested_dict
from card import Card

class Player(object):
  def __init__(self, game, name):
    self.cards = []
    self.game = game
    self.table = game.table
    self.name = name

  def get_card_data(self, card):
    if 'number' in self.info[card] and 'color' in self.info[card]:
      return Card(self.info[card]['number'], self.info[card]['color'])

  def learn_card_data(self, card, attr, value):
    self.info[card][attr] = value

  def start_game(self, position):
    self.position = position
    self.info = nested_dict()
    self.other_players = filter(lambda player: player != self, self.game.players)

  def __str__(self):
    return '%s %s' % (self.__class__.__name__, self.name)

  def update_on_action(self, acting_player, action, args):
    pass

  def best_play(self):
    return ('PLAY', random.choice(self.cards))


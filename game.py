from player import Player
from cheater import Cheater
from card import Card
from smartPlayer import SmartPlayer
from configs import colors, numbers, frequencies
from random import shuffle

class Game:
  def __init__(self):
    self.table = Table()

  def init_deck(self):
    colors = [0, 1, 2, 3, 4]
    numbers = [0, 0, 0, 1, 1, 2, 2, 3, 3, 4]
    self.deck = [Card(number, color) for color in colors for number in numbers]
    shuffle(self.deck)
    self.deck_position = 0

  def get_other_players(self, player):
    return filter(lambda p: p != player, self.players)

  def tell_color(self, player, card):
    color = self.deck[card].color
    player.learn_card_data(card, 'color', color)
    #player.knows(card.color == color)

  def tell_number(self, player, card):
    number = self.deck[card].number
    player.learn_card_data(card, 'number', number)

  def tell_not_color(self, player, card, color):
    pass
  
  def tell_not_number(self, player, card, number):
    pass

  def deal(self, player):
    if self.deck_position >= len(self.deck):
      return False
    card = self.deck_position
    self.deck_position += 1
    player.cards.append(card)
    for other_player in self.get_other_players(player):
      self.tell_color(other_player, card)
      self.tell_number(other_player, card)
    return True

  def play(self, player, card):
    player.cards.remove(card)
    self.table.play(self.deck[card])
    print 'Player %s plays card %s: %s' % (player.name, card, self.deck[card])
    self.deal(player)

  def discard(self, player, card):
    print 'Player %s discards card %s: %s' % (player.name, card, self.deck[card])
    player.cards.remove(card)
    self.table.discard(self.deck[card])
    self.deal(player)

  def hint(self, player, other_player, attr, val):
    # tell everyone about the hint
    self.table.hints -= 1

  def action(self, acting_player, action, args):
    print 'ACTION: %s %s: %s' % (acting_player, action, args)
    self.action_log.append((acting_player, action, args))
    for player in players:
      player.update_on_action(acting_player, action, args)
    if action == 'PLAY':
      card = args
      self.play(acting_player, card)
    elif action == 'HINT':
      other_player, attr, val = args
      self.hint(acting_player, other_player, attr, val)
    elif action == 'DISCARD':
      card = args
      self.discard(acting_player, card)

  def start(self, players):
    self.endgame = False
    self.init_deck()    
    print "Starting with deck %s" % [str(x) for x in self.deck]
    self.action_log = []
    self.players = players
    for position, player in enumerate(self.players):
      player.start_game(position)

    for player in self.players:
      for i in range(4):
        self.deal(player)

    self.player_turn = 0

  def step(self):
    if self.endgame:
      if self.turns_left <= 0:
        print 'GAME OVER'
        return
      print 'ENDGAME, TURNS_LEFT = %d' % self.turns_left
      self.turns_left -= 1
    acting_player = self.players[self.player_turn]
    self.action(acting_player, *acting_player.best_play())
    self.player_turn = (self.player_turn + 1) % 5
    for player in self.players:
      print "%s: %s" % (player.name, [str(self.deck[card]) for card in player.cards])
    print self.table
    if self.deck_position == len(self.deck):
      if not self.endgame:
        self.endgame = True
        self.turns_left = 5
    return True


class Table:
  def __init__(self):
    self.played_cards = []
    self.discarded_cards = []
    self.stacks = [[] for x in range(5)]
    self.hints = 8
    self.lives = 3

  def is_complete(self, color):
    return len(self.stacks[color]) == 5
    
  def can_play(self, card):
    return len(self.stacks[card.color]) == card.number

  def play(self, card):
    if self.can_play(card):
      self.played_cards.append(card)
      self.stacks[card.color].append(card)
      if self.is_complete(card.color):
        self.hints += 1
    else:
      self.lives -= 1

  def discard(self, card):
    self.hints += 1
    self.discarded_cards.append(card)

  def __str__(self):
    header = 'Hints: %d Lives: %d' % (self.hints, self.lives)
    body = '\n'.join('%s: %s' % (
      colors[color], ' '.join(str(x) for x in self.stacks[color]))
       for color in range(5))
    return '\n'.join((header, body))


if __name__ == '__main__':
  num_players = 5
  game = Game()
  # players = [Player(game, str(i + 1)) for i in range(num_players)]
  players = [SmartPlayer(game, str(i + 1)) for i in range(num_players)]
  game.start(players)
  cnt = 0
  while game.step():
    raw_input()


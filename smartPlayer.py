from player import Player
from utils import nested_dict

class SmartPlayer(Player): # 'experiment 3'
  def get_index(self, card, card_list):
    return card_list.index(card) + 1 if card in card_list else 0

  def first_playable(self, cards):
    for card in cards:
      if self.table.can_play(self.get_card_data(card)):
        return card
    return -1

  def first_discardable(self, cards):
    for card in cards:
      if self.get_card_data(card) in self.table.played_cards:
        return card
    return -1


  def infer_playable(self, hinter, value):
    total = 0
    for player in self.other_players:
      if player == hinter:
        continue
      total += self.memory['first_playable'][player.position]
    index = (value - total) % 5
    if index < 0:
      index += 5
    if index == 0:
      return -1
    else:
      return self.cards[index - 1]

  def infer_discardable(self, hinter, value):
    total = 0
    for player in self.other_players:
      if player == hinter:
        continue
      total += self.memory['first_discardable'][player.position]
    index = (value - total) % 5
    if index < 0:
      index += 5
    if index == 0:
      return -1
    else:
      return self.cards[index - 1]


  def remember_first_playable(self, player, card=None):
    position = player.position  
    if card == None:
      card = self.first_playable(player.cards)  
    index = self.get_index(card, player.cards)
    self.memory['first_playable'][position] = index

  def remember_first_discardable(self, player):
    position = player.position
    card = self.first_discardable(player.cards)
    index = self.get_index(card, player.cards)
    self.memory['first_discardable'][position] = index

  def remember_playable(self, card):
    self.memory['playable'] = card

  def remember_discardable(self, card):
    self.memory['discardable'] = card

  def make_play(self):
    if 'playable' in self.memory:
      card = self.memory['playable']
      return ('PLAY', card)
    else:
      return None

  def make_discard(self):
    if 'discardable' in self.memory:
      card = self.memory['discardable']
      return ('DISCARD', card)
    else:
      return None

  def make_hint(self, hint_type):
    total = 0
    for player in self.other_players:
      card = self.first_playable(player.cards) if hint_type == 'color' else self.first_discardable(player.cards)
      index = self.get_index(card, player.cards)
      total += index

    player = self.other_players[0]
    attr = hint_type
    val = total % 5
    return ('HINT', (player, attr, val))


  """ Play according to strategy:
    1. Play playable
    2. Discard discardable
    3. Hint playable/discardable (whichever expires sooner)
  """
  def best_play(self):
    # process all meta-hints
    number_time, color_time = 0, 0
    if 'last_number_hint' in self.memory:
      number_time, hinter, action, args = self.memory['last_number_hint']
      del self.memory['last_number_hint']
      other_player, attr, value = args
      card = self.infer_discardable(hinter, value)
      if card != -1:
        self.remember_discardable(card)

    if 'last_color_hint' in self.memory:
      color_time, hinter, action, args = self.memory['last_color_hint']
      del self.memory['last_color_hint']
      other_player, attr, value = args
      card = self.infer_playable(hinter, value)
      if card != -1:
        self.remember_playable(card)

    play = self.make_play()
    discard = self.make_discard()
    hint = self.make_hint('color' if color_time <= number_time else 'number')
    print dict(play=play, discard=discard, hint=hint)

    # if can play, then play
    # if can discard, then discard
    # if can hint, then hint
    return play or discard or hint # short-circuit magic

  def update_on_action(self, acting_player, action, args):
    # done before the action is completed
    # no cards have been played/discarded yet
    self.memory['action_count'] += 1
    if acting_player == self:
      if action == 'PLAY':
        del self.memory['playable']
      if action == 'DISCARD':
        del self.memory['discardable']

    position = acting_player.position
    if action == 'PLAY':
      card = args
      self.remember_first_playable(acting_player, card)
    else:
      self.remember_first_playable(acting_player, -1)

    if action == 'HINT':
      other_playre, attr, value = args
      if attr == 'color':
        self.memory['last_color_hint'] = (self.memory['action_count'], acting_player, action, args)
        for player in self.other_players:
          self.remember_first_playable(player)
      else:
        self.memory['last_number_hint'] = (self.memory['action_count'], acting_player, action, args)
        for player in self.other_players:
          self.remember_first_discardable(player)

    self.memory['last_action'][acting_player.position] = (action, args)

  def start_game(self, position):
    super(SmartPlayer, self).start_game(position)
    self.memory = nested_dict()
    self.memory['action_count'] = 0



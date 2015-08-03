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

  def remember_first_playable(self, player, card=None):
    position = player.position  
    if card == None:
      card = self.first_playable(player.cards)  
    index = self.get_index(card, player.cards)
    self.memory['first_playable'][position] = index

  def start_game(self, position):
    super(SmartPlayer, self).start_game(position)
    self.memory = nested_dict()

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

  def make_hint(self):
    total = 0
    for player in self.other_players:
      card = self.first_playable(player.cards)
      index = self.get_index(card, player.cards)
      total += index

    player = self.other_players[0]
    attr = 'color'
    val = total % 5
    return (player, attr, val)

  """ Play according to strategy:
    1. Play playable
    2. Discard discardable
    3. Hint playable
    4. Hint discardable
  """
  def best_play(self):
    # process all meta-hints
    if 'last_hint' in self.memory:
      hinter, action, args = self.memory['last_hint']
      del self.memory['last_hint']
      other_player, attr, value = args
      card = self.infer_playable(hinter, value)
      if card != -1:
        return ('PLAY', card)

    hint = self.make_hint()
    return ('HINT', hint)



  def update_on_action(self, acting_player, action, args):
    # done before the action is completed
    # no cards have been played/discarded yet
    if acting_player == self:
      return

    position = acting_player.position
    if action == 'PLAY':
      card = args
      self.remember_first_playable(acting_player, card)
    else:
      self.remember_first_playable(acting_player, -1)

    if action == 'HINT':
      self.memory['last_hint'] = (acting_player, action, args)
      for player in self.other_players:
        self.remember_first_playable(player)

    self.memory['last_action'][acting_player.position] = (action, args)

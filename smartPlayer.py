from player import Player
from utils import nested_dict

class SmartPlayer(Player): # 'experiment 3'
  def get_index(self, card, card_list):
    if card == -1:
      return 0
    return len(filter(lambda other_card: card > other_card, card_list)) + 1

  def get_first_playable(self, cards, other_playables):
    def duplicate(card_a, card_b):
      if card_b == -1 or card_a == -1:
        return False
      if self.get_card_data(card_b) == self.get_card_data(card_a):
        print 'found duplicate: %d == %d' % (card_a, card_b)
        self.memory['dups'] = True
        return True
      else:
        return False
    playables = filter(lambda card: self.table.can_play(self.get_card_data(card)), cards)
    non_duplicate_playables = filter(lambda card: all(not duplicate(card, other_card) for other_card in other_playables), playables)
#    playables = non_duplicate_playables
    if playables:
      return min(playables)
#      return min(playables, key=lambda card: (self.get_card_data(card).number + 1) % 5)
    else:
      return -1

  def first_discardable(self, cards):
    for card in cards:
      if self.get_card_data(card) in self.table.played_cards:
        return card
    return -1


  def infer_playable(self, hinter, value):
    total = 0
    print 'inferring playable using %s' % self.memory['first_playable']
    for player in self.get_other_players(start=hinter):
      card = self.memory['first_playable'][player.position]
      index = self.get_index(card, player.cards)
      total += index
    index = (value - total) % 5
    if index < 0:
      index += 5
    if index == 0:
      return -1
    else:
      return self.cards[index - 1]

  def infer_discardable(self, hinter, value):
    total = 0
    for player in self.get_other_players(start=hinter):
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
    self.memory['first_playable'][position] = card

  def get_all_first_playables(self, start=None):
    ans = {}
    for player in reversed(self.get_other_players(start=start)):
      ans[player.position] = self.get_first_playable(player.cards, ans.values())
    return ans

  def remember_first_discardable(self, player):
    position = player.position
    card = self.first_discardable(player.cards)
    index = self.get_index(card, player.cards)
    self.memory['first_discardable'][position] = index
    return index

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

  def make_random_discard(self):
    return ('DISCARD', self.cards[0])

  def make_hint(self, hint_type):
    total = 0
    if hint_type == 'color':
      first_playables = self.get_all_first_playables()
      print 'making hint using %s' % first_playables
      for player in self.get_other_players():
        card = first_playables[player.position]
        index = self.get_index(card, player.cards)
        total += index
    else:
      for player in self.get_other_players():
        card = self.first_discardable(player.cards)
        index = self.get_index(card, player.cards)
        total += index

    player = self.get_other_players()[0]
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
    print 'inferring hint using %s' % self.memory['first_playable']
    if 'last_color_hint' in self.memory:
      color_time, hinter, action, args = self.memory['last_color_hint']
      del self.memory['last_color_hint']
      other_player, attr, value = args
      card = self.infer_playable(hinter, value)
      if card != -1:
        self.remember_playable(card)
      else:
        if 'playable' in self.memory:
          del self.memory['playable']

    was_dup = self.memory['dups']
    self.memory['dups'] = False

    play = self.make_play()
    discard = self.make_discard()
    random_discard = self.make_random_discard()
    old_playables = self.memory['first_playable'].values()
    playables = self.get_all_first_playables().values()
    hint_play = self.make_hint('color')
    hint_discard = self.make_hint('number')

    is_dup = self.memory['dups']
    self.memory['dups'] = False
    print dict(is_dup=is_dup, was_dup=was_dup)

    new_playables = filter(lambda card: card not in old_playables, playables)
    discardables = filter(lambda card: card != -1, [self.first_discardable(player.cards) for player in self.get_other_players()])

    hint_power = len(new_playables)
#    if was_dup and is_dup:
#      hint_power -= 2

    hints_left = self.table.hints

#    print dict(play=play, discard=discard, hint=hint)

    cards_left = self.table.get_cards_left()
    if play:
      return play
    print dict(playables=playables, old_playables=old_playables, new_playables=new_playables, cards_left=cards_left, hints_left=hints_left)
    if hints_left > 4 and hint_power > 0:
      return hint_play
    if hints_left > 2 and hint_power > 1:
      return hint_play
    if hints_left > 0 and hint_power > 2:
      return hint_play
    if hints_left > 0 and cards_left == 0:
      return hint_play
    if hints_left > 0 and cards_left < 3:
      return hint_play
    if discard:
      return discard
    if hints_left > 0 and len(discardables) > 1 and self.memory['discards_left'] <= 1:
      return hint_discard
    if hints_left > 0:
      return hint_play
    return random_discard

  def update_on_action(self, acting_player, action, args):
    # done before the action is completed
    # no cards have been played/discarded yet
    self.memory['action_count'] += 1
    if acting_player == self:
      if action == 'PLAY':
        del self.memory['playable']
      if action == 'DISCARD':
        if 'discardable' in self.memory:
          del self.memory['discardable']

        self.memory['discards_left'] -= 1
      return

    position = acting_player.position
    if action == 'PLAY':
      card = args
      self.remember_first_playable(acting_player, card)
    else:
      self.remember_first_playable(acting_player, -1)

    if action == 'HINT':
      other_player, attr, value = args
      if attr == 'color':
        self.memory['last_color_hint'] = (self.memory['action_count'], acting_player, action, args)
        self.memory['first_playable'] = self.get_all_first_playables(start=acting_player)
      else:
        self.memory['discards_left'] = 0
        for player in self.get_other_players():
          if self.remember_first_discardable(player):
            self.memory['discards_left'] += 1
        card = self.infer_discardable(acting_player, value)
        if card != -1:
          self.remember_discardable(card)

    if action == 'DISCARD':
      self.memory['discards_left'] -= 1

    self.memory['last_action'][acting_player.position] = (action, args)

  def get_other_players(self, start=None):
    if start == None:
      start = self
    ret = []
    position = (start.position + 1) % 5
    while position != start.position:
      if position != self.position:
        ret.append(self.game.players[position])
      position = (position + 1) % 5
    return ret

  def start_game(self, position):
    super(SmartPlayer, self).start_game(position)
    self.memory = nested_dict()
    self.memory['action_count'] = 0
    self.memory['discards_left'] = 0



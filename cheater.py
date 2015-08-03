from player import Player
from configs import frequencies

class Cheater(Player):
  def can_play(self, card):
    if self.table.can_play(card):
      return 6 - card.number
    else:
      return 0

  def can_discard(self, card):
    if card in self.table.played_cards:
      return 3
    discarded = len(filter(card.__eq__, self.table.discarded_cards))
    total = frequencies[card.number]
    left = total - discarded - 1
    if left:
      if card.number > 2:
        return 2
      elif card.number == 1:
        if left == 2:
          return 2
      return 1
    else:
      return 0
      
  def best_play(self):
    def playable(card):
      card_data = self.game.deck[card]
      return self.can_play(card_data)
    def discardable(card):
      card_data = self.game.deck[card]
      return self.can_discard(card_data)

    play_candidate = max(self.cards, key=playable)
    discard_candidate = max(self.cards, key=discardable)
    discard_score = discardable(discard_candidate)
    if playable(play_candidate):
      return ('PLAY', play_candidate)

    other_players = self.game.get_other_players(self)
    hint = ('HINT', (other_players[0], 0, 0))
    discard = ('DISCARD', discard_candidate)

    if self.table.hints >= 8:
      return hint
    elif discard_score >= 3:
      return discard
    elif self.table.hints >= 4:
      return hint
    elif discard_score >= 2:
      return discard
    elif self.table.hints >= 1:
      return hint
    else:
      return discard
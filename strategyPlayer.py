from player import Player
from configs import frequencies

class StrategyPlayer(Player):
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
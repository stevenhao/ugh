from player import Player
from strategyPlayer import StrategyPlayer

class Cheater(StrategyPlayer):
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

    if discard_score >= 3:
      return discard

    if self.table.hints >= 4:
      return hint

    if discard_score >= 2:
      return discard

    if self.table.hints >= 1:
      return hint

    return discard
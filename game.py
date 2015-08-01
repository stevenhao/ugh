from player import Player

from random import shuffle

class Game:
    def __init__(self):
        self.init_deck()

    def init_deck(self):
        colors = [0, 1, 2, 3, 4]
        numbers = [0, 0, 0, 1, 1, 2, 2, 3, 3, 4]
        self.deck = [Card(color, number) for color in colors for number in numbers]
        shuffle(self.deck)
        self.deck_position = 0

    def get_other_players(self, player):
        return filter(lambda p: p != player, self.players)

    def tell_color(self, player, card):
        color = self.deck[card].color
        #player.knows(card.color == color)

    def tell_number(self, player, card):
        number = self.deck[card].number
        #player.knows(card.number == number)

    def deal(self, player):
        if self.deck_position >= len(self.deck):
            print 'out of cards'
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
        player.cards.remove(card)
        self.table.discard(self.deck[card])
        self.deal(player)

    def start(self, players):
        self.players = players
        self.table = Table()
        for player in self.players:
            for i in range(4):
                self.deal(player)
        self.player_turn = 0

    def step(self):
        self.players[self.player_turn].action()
        self.player_turn = (self.player_turn + 1) % 5
        return True


class Table:
    def __init__(self):
        self.discarded_cards = []
        self.stacks = [0] * 5
        self.hints = 8
        self.lives = 3

    def can_play(self, card):
        return self.stacks[card.color] == card.number

    def play(self, card):
        if self.can_play(card):
            self.stacks[card.color] += 1
        else:
            self.lives -= 1

    def discard(self, card):
        self.hints += 1
        self.discarded_cards.append(card)


class Card:
    def __init__(self, number, color):
        self.number = number
        self.color = color

    def __str__(self):
        colors = 'BRGYW'
        numbers = '12345'
        return colors[self.color] + numbers[self.number]


if __name__ == '__main__':
    num_players = 5
    game = Game()
    players = [Player(game, str(i + 1)) for i in range(num_players)]
    game.start(players)
    cnt = 0
    while game.step():
        #print '%d ...' % cnt
        cnt += 1
        raw_input()


from configs import colors, numbers
class Card:
  def __init__(self, number, color):
    self.number = number
    self.color = color

  def __eq__(self, other):
    return (self.number, self.color) == (other.number, other.color)

  def __str__(self):
    return colors[self.color] + numbers[self.number]

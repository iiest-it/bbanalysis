from Ball import Ball
from Player import Player

class Moment:
    def __init__(self, moment):
        self.quarter = moment[0]
        self.game_clock = moment[2]
        self.shot_clock = moment[3]
        ball = moment[5][0]
        self.ball = Ball(ball)
        players = moment[5][1:]
        self.players = [Player(player) for player in players]

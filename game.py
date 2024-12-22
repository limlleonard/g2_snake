# direction right:0, up:1, left:2, down:3
from collections import namedtuple
import random

Point = namedtuple('Point', 'x, y')
lohn_stoß=-10
lohn_essen=10

class Game:
    def __init__(self, w=10, h=10):
        self.w=w
        self.h=h
        self.reset()
    def reset(self):
        self.direction=0
        self.head=Point(2,0)
        self.body=[self.head, Point(1,0), Point(0,0)]
        self.score = 0
        self.food = None
        self._place_food()
        self.n_move=0
        self.vir=True
    def _place_food(self):
        x = random.randint(0, self.w-1)
        y = random.randint(0, self.h-1)
        self.food = Point(x, y)
        if self.food in self.body:
            self._place_food()
    def play_step(self, turn=None):
        self.n_move+=1
        # 1. collect user input of quit xx
        if turn=='left':
            self.direction=(self.direction+1)%4
        if turn=='right':
            self.direction=(self.direction+3)%4
        # 2. move
        if not self.vir:
            # ganz am Anfang bleib Snake bei der Start Position für ein Zyklus
            self._move(self.direction) # update the head
            self.body.insert(0, self.head)
        # 3. check if game over
        reward=0
        game_over = False
        if self.is_collision():
            game_over = True
            reward=lohn_stoß
            return reward, game_over, self.score, self.body, self.food
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward=lohn_essen
            self._place_food()
        else:
            if not self.vir:
                self.body.pop()
            else:
                self.vir=False
        # 5. update ui and clock
        # 6. return game over and score
        return reward, game_over, self.score, self.body, self.food
    
    def _move(self, direction): # identify the position of new head
        x = self.head.x
        y = self.head.y
        if direction == 0:
            x += 1
        elif direction == 1:
            y -= 1
        elif direction == 2:
            x -= 1
        elif direction == 3:
            y += 1
        self.head = Point(x, y)    

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.x > self.w - 1 or pt.x < 0 or pt.y > self.h - 1 or pt.y < 0:
            return True
        # hits itself
        if pt in self.body[1:]:
            return True
        return False
    

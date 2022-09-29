# TODO - Change keyboard backend
# TODO - Add mouse support

import eng
import math
from pynput.keyboard import Key

env = [[1, 1, 1, 1, 1],
       [1, 0, 0, 0, 1],
       [1, 0, 1, 0, 1],
       [1, 0, 0, 0, 1],
       [1, 1, 1, 1, 1]]

class Game:
    def __init__(self) -> None:
        
        self.engine = eng.Engine_0(None, self.on_key)
        self.pos = [1, 1]
        self.map = None
        self.rot = 0
        
        # Settings
        self.FOV = 80
        self.SENS = math.pi / 256
        self.SPEED = .01
        self.PRECISION = .02
        
        
        self.win_width, self.win_height = self.engine.size.size
    
    def on_key(self, _, key) -> None:
        
        x, y = self.pos
        
        if key is Key.up:
            # W
            x, y = x + self.SPEED * math.cos(self.rot), y + self.SPEED * math.sin(self.rot)
            
        if key is Key.down:
            # S
            x, y = x - self.SPEED * math.cos(self.rot), y - self.SPEED * math.sin(self.rot)
        
        if key is Key.left:
            # A
            self.rot -= self.SENS
        
        if key is Key.right:
            # D
            self.rot += self.SENS
            
        # If not blocked
        if not self.map[int(x)][int(y)]: self.pos = [x, y]
        
        # Erase
        self.engine.grid.__post_init__()
        
        # Render
        for i in range(self.FOV + 1):
            
            rot_d = self.rot + math.radians(i - self.FOV / 2)
            x, y = self.pos
            
            sin, cos = self.PRECISION * math.sin(rot_d), self.PRECISION * math.cos(rot_d)
            
            j = 0
            
            while 1:
                x, y = x + cos, y + sin
                j += 1
                
                if self.map[int(x)][int(y)]:                    
                    tile = self.map[int(x)][int(y)]
                    
                    d = j
                    j = j * math.cos(math.radians(i - self.FOV / 2))
                    height = (10 / j * 2500)
                    
                    break
            
            if d / 2 > 255: d = 510
            
            # win_w, win_h = self.engine.grid.size.size
            
            # p1 = [abs(int(i * (win_w / self.FOV)) - 1), abs(int((win_h / 2) + height) - 1)]
            # p2 = [abs(int(i * (win_w / self.FOV)) - 1), abs(int((win_h / 2) - height) - 1)]
            
            
            
            p1 = [abs(int(i * (self.win_width / self.FOV))), abs(int((self.win_height / 2) + height))]
            p2 = [abs(int(i * (self.win_width / self.FOV))), abs(int((self.win_height / 2) - height))]
            
            width = int(self.win_width / self.FOV)
            
            # print(self.engine.size.size)
            
            p1 = [p1[0], p1[1]]
            p2 = [p2[0], p2[1]]
            
            
            # print(p1, p2)
            
            self.engine.grid.line(p1, p2, '#')
            
            # TODO - add width
    
    def start(self, env: list, spawn: list) -> None:
        
        self.map = env
        self.pos = spawn
        self.engine.run()


game = Game()
game.start(env, [1, 1])
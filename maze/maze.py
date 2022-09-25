import eng
import threading
from copy import copy, deepcopy
from time import sleep
from pynput.keyboard import Key
from dataclasses import dataclass

'''
  N
W + E
  S
'''

@dataclass
class MAP:
    level: str
    
    def __post_init__(self):
        self.map = [list(l) for l in self.level.split('\n')]
    
    def get(self, x: int, y: int, orient) -> dict:
        '''
        orient = N | S | W | E
        '''
        
        res = {
            'left': None,
            'right': None,
            'fw': None
        }
        
        pixel = self.map[y][x]
        
        if orient == 'N':
            # Right
            if self.map[y][x + 1] == ' ': res['right'] = 'entrance'
            elif self.map[y][x + 1] == '█': res['right'] = 'wall'
            elif self.map[y][x + 1] == 'E': res['right'] = 'exit'
            
            # Left
            if self.map[y][x - 1] == ' ': res['left'] = 'entrance'
            elif self.map[y][x - 1] == '█': res['left'] = 'wall'
            elif self.map[y][x - 1] == 'E': res['left'] = 'exit'
            
            # FW
            if self.map[y - 1][x] == ' ': res['fw'] = 'entrance'
            elif self.map[y - 1][x] == '█': res['fw'] = 'wall'
            elif self.map[y - 1][x] == 'E': res['fw'] = 'exit'
        
        elif orient == 'S':
            # Right
            if self.map[y][x - 1] == ' ': res['right'] = 'entrance'
            elif self.map[y][x - 1] == '█': res['right'] = 'wall'
            elif self.map[y][x - 1] == 'E': res['right'] = 'exit'
            
            # Left
            if self.map[y][x + 1] == ' ': res['left'] = 'entrance'
            elif self.map[y][x + 1] == 'E': res['left'] = 'exit'
            
            # FW
            if self.map[y + 1][x] == ' ': res['fw'] = 'entrance'
            elif self.map[y + 1][x] == '█': res['fw'] = 'wall'
            elif self.map[y + 1][x] == 'e': res['fw'] = 'exit'
        
        elif orient == 'W': # on left
            # Right
            if self.map[y - 1][x] == ' ': res['right'] = 'entrance'
            elif self.map[y - 1][x] == '█': res['right'] = 'wall'
            elif self.map[y - 1][x] == 'E': res['right'] = 'exit'
            
            # Left
            if self.map[y + 1][x] == ' ': res['left'] = 'entrance'
            elif self.map[y + 1][x] == '█': res['left'] = 'wall'
            
            # FW
            if self.map[y][x - 1] == ' ': res['fw'] = 'entrance'
            elif self.map[y][x - 1] == '█': res['fw'] = 'wall'
            
        elif orient == 'E': # on right
            # Right
            if self.map[y + 1][x] == ' ': res['right'] = 'entrance'
            elif self.map[y + 1][x] == '█': res['right'] = 'wall'
            elif self.map[y + 1][x] == 'E': res['right'] = 'exit'
            
            # Left
            if self.map[y - 1][x] == ' ': res['left'] = 'entrance'
            elif self.map[y - 1][x] == '█': res['left'] = 'wall'
            elif self.map[y - 1][x] == 'E': res['left'] = 'exit'
            
            # FW
            if self.map[y][x + 1] == ' ': res['fw'] = 'entrance'
            elif self.map[y][x + 1] == '█': res['fw'] = 'wall'
            elif self.map[y][x + 1] == 'E': res['fw'] = 'exit'
        
        return res

    def rep(self, x: int, y: int, o, join = True) -> str:
        
        char = {
            'N': '▲',
            'S': '▼',
            'W': '◀',
            'E': '▶'
        }[o]
        
        r = deepcopy(self.map)
        r[y][x] = char
        
        if join: return '\n'.join(map(''.join, r))
        return r

    def allowed(self, x: int, y: int, orient: str) -> bool:
        
        data = self.get(x, y, orient)
        res = []
        
        if data['left'] == 'entrance': res += ['left']
        if data['right'] == 'entrance': res += ['right']
        if data['fw'] == 'entrance': res += ['fw']
        
        return res

class Game:
    def __init__(self) -> None:
        
        self.engine = eng.Engine_0(None, self.on_key)
        self.map: MAP = None
        self.player = [0, 0]
        self.heading = 'S'
        self.show_map = True
    
    def draw_context(self, data: dict) -> None:
        
        mid = [self.engine.size.x // 2,
               self.engine.size.y // 2]
        
        x, y = self.engine.size.size
        
        x -= 1
        y -= 1
        
        ratio = x / y
        
        lenx = round(x / 2)
        leny = round(y / 2)
        
        frame = [
            [lenx - lenx // 2, leny - leny // 2],
            [lenx + lenx // 2, leny + leny // 2]
        ]
        
        char = '\033[92m#\033[0m'
        
        # === LEFT === #
        
        def gen_wall_left():
            self.engine.grid.triangle([0, 0], mid, [0, mid[1]], '/', '/')
            self.engine.grid.triangle([0, y], mid, [0, mid[1]], '/', '/')
        
        def gen_entrance_left():
            # Left side
            # Fill
            self.engine.grid.triangle([0, 0], mid, [0, mid[1]], '/', '/')
            self.engine.grid.triangle([0, y], mid, [0, mid[1]], '/', '/')
            
            # Case: entrance
            eg = 4 # entrance gap
            
            self.engine.grid.triangle([eg, int(eg * 1.5)],
                                    [mid[0] - eg, mid[1]],
                                    [eg, mid[1]], ' ', ' ')
            
            self.engine.grid.triangle([eg, y],
                                    [mid[0] - eg, mid[1]],
                                    [eg, mid[1]], ' ', ' ')

            self.engine.grid.rectangle([frame[0][0] - eg, frame[0][1]],
                                    [mid[0], mid[1] + leny // 2 + eg],
                                    '/', '/')

        # === RIGHT === #
        
        def gen_wall_right():
            self.engine.grid.triangle([x, 0], mid, [x, mid[1]], '\\', '\\')
            self.engine.grid.triangle([x, y], mid, [x, mid[1]], '\\', '\\')
        
        def gen_entrance_right():
            # Right side
            
            # right side
            # Fill
            self.engine.grid.triangle([x, 0], mid, [x, mid[1]], '\\', '\\')
            self.engine.grid.triangle([x, y], mid, [x, mid[1]], '\\', '\\')
            
            # Case: entrance
            eg = 4 # entrance gap
            
            self.engine.grid.triangle([x - eg, int(eg * 1.5)],
                                      [mid[0] + eg, mid[1]],
                                      [x - eg, mid[1]],
                                      ' ', ' ')
            
            self.engine.grid.triangle([x - eg, mid[1]],
                                      [mid[0] + eg, mid[1]],
                                      [x - eg, y],
                                      ' ', ' ')
            
            self.engine.grid.rectangle([frame[1][0] - lenx // 2, frame[0][1]],
                                       [frame[1][0] + eg, frame[1][1] + eg],
                                       '\\', '\\')
        
        # === FORWARD === #
        
        def gen_wall_fw():
            self.engine.grid.rectangle(*frame, char, fill = '=')
        
        def gen_entrance_fw():
            gen_wall_fw()
            
            eg = 4
            
            self.engine.grid.rectangle([frame[0][0] + eg, frame[0][1] + eg],
                                       [frame[1][0] - eg, frame[1][1]],
                                       ' ', ' ')
        
        def gen_exit_fw():
            self.engine.grid.rectangle(*frame, char, fill = '\033[92m*\033[0m')
            
            lines = open('exit.txt', 'r').readlines()
            
            for line in lines:
                self.engine.grid.write(*mid, line, 0.5)
        
        # Gen left and right
        
        if data['left'] == 'entrance':
            gen_entrance_left()
        elif data['left'] == 'wall':
            gen_wall_left()
            
        elif data['left'] == 'exit':
            pass
        
        if data['right'] == 'entrance':
            gen_entrance_right()
        elif data['right'] == 'wall':
            gen_wall_right()
            
        elif data['right'] == 'exit':
            pass
        
        # === ROOF and FLOOR === #
        self.engine.grid.triangle([0, 0], mid, [mid[0], 0], ' ', ' ')
        self.engine.grid.triangle([x, 0], mid, [mid[0], 0], ' ', ' ')
        
        self.engine.grid.triangle([0, y], mid, [mid[0], y], ' ', ' ')
        self.engine.grid.triangle([x, y], mid, [mid[0], y], ' ', ' ')
        
        # === Main lines === #
        self.engine.grid.line([0, 0], mid, char)
        self.engine.grid.line([x, 0], mid, char)
        self.engine.grid.line([0, y], mid, char)
        self.engine.grid.line([x, y], mid, char)
        
        # Gen forward
        if data['fw'] == 'entrance':
            gen_entrance_fw()
        elif data['fw'] == 'wall':
            gen_wall_fw()
        elif data['fw'] == 'exit':
            gen_exit_fw()
        
        # Draw frame
        self.engine.grid.rectangle(*frame, char) # fill = ' '

    def on_key(self, _, key: Key) -> None:
        '''Keyboard listener.'''
        
        if not key in (Key.left, Key.right, Key.up, Key.down): return
        
        # Check if movement is possible
        allowed = self.map.allowed(*self.player, self.heading)
        
        # Go left
        if key is Key.left:
            if not 'left' in allowed:
                print('Movement impossible.')
                return
            
            if self.heading == 'N': self.player[0] -= 1
            if self.heading == 'S': self.player[0] += 1
            if self.heading == 'W': self.player[1] += 1
            if self.heading == 'E': self.player[1] -= 1
            
            self.heading = {
                'N': 'W',
                'E': 'N',
                'S': 'E',
                'W': 'S'
            }[self.heading]
                
        # Go right
        if key is Key.right:
            if not 'right' in allowed:
                print('Movement impossible.')
                return
            
            if self.heading == 'N': self.player[0] += 1
            if self.heading == 'S': self.player[0] -= 1
            if self.heading == 'W': self.player[1] -= 1
            if self.heading == 'E': self.player[1] += 1
            
            self.heading = {
                'N': 'E',
                'E': 'S',
                'S': 'W',
                'W': 'N'
            }[self.heading]
        
        # Go forward
        if key is Key.up:
            if not 'fw' in allowed:
                print('Movement impossible.')
                return
        
            if self.heading == 'N': self.player[1] -= 1
            if self.heading == 'S': self.player[1] += 1
            if self.heading == 'W': self.player[0] -= 1
            if self.heading == 'E': self.player[0] += 1
        
        # Go backward
        if key is Key.down:
            if self.heading == 'N': self.player[1] += 1
            if self.heading == 'S': self.player[1] -= 1
            if self.heading == 'W': self.player[0] += 1
            if self.heading == 'E': self.player[0] -= 1
            
            self.heading = {
                'N': 'S',
                'E': 'W',
                'S': 'N',
                'W': 'E'
            }[self.heading]
        
        # Req level data and draw context
        data = self.map.get(*self.player, self.heading)
        self.draw_context(data)
        
        # Add minimap
        if self.show_map:
            for y, line in enumerate(self.map.rep(*self.player, self.heading, False)):
                for x, char in enumerate(line):
                    self.engine.grid.set(x + 1, y + 1, char)
    
    def start(self, start: list, _map: MAP) -> None:
        '''Start playing on a map.'''
        
        self.map = _map
        self.player = start
        self.engine.run()

def parse_level(file: str) -> tuple:
    
    lines = [l.rstrip() for l in open(file, 'r').readlines()]
    spawn = eval(lines.pop(0))
    
    return spawn, MAP('\n'.join(lines))


game = Game()
game.start(*parse_level('/home/egsagon/docs/engine/maze/level2.txt'))

# TODO - recursive foward vision
# TODO - animations
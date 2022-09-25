import os
import sys
import copy
import platform
import threading
import multiprocessing
from time import time, sleep
from dataclasses import dataclass
from pynput.keyboard import Listener, Key

@dataclass
class Size:
    size: list[int]
    def __post_init__(self): self.x, self.y = self.size

@dataclass
class Grid:
    size: Size
    default: str = '#'
    
    def __post_init__(self):
        self.grid = [[copy.copy(self.default) for _ in range(self.size.x)]
                     for _ in range(self.size.y)]

    # Basic utilities
    def set(self, x: int, y: int, val: str): self.grid[y][x] = self.default if val is None else val
    def get(self, x: int, y: int): return self.grid[y][x]
    def join(self): return '\n'.join(map(''.join, self.grid))
    
    # Writing text
    def write(self, x: int, y: int, text: str, origin: int = 0) -> None:
        '''
        origin:
        0    -    0.5    -    1
        left -   middle  -  right
        '''
        
        if not text: raise Exception('Text must be at least 1 char.')
        if not 0 <= origin <= 1: raise Exception('')
        
        # Weight of the origin (o0->+0, o1->+len, o0.5->+len/2)
        sup = int(len(text) * origin)
        
        for i, char in enumerate(text): self.set(x + i - sup, y, char)

class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill()
    method."""
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False
    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run     
        threading.Thread.start(self)
    def __run(self):
        """Hacked run function, which installs the
    trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup
    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None
    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace
    def kill(self):
        self.killed = True

# Engine
class Engine_0:
    def __init__(self, ms: list = None, on_press: callable = None, default: str = ' ', on_rel: callable = None) -> None:
        '''
        Represents an instance of the engine.
        '''
        
        # Fetch size
        ts = list(os.get_terminal_size())
        ts[1] -= 1 # Remove one line for PS1 (help perf)
        self.size = Size(ts if ms is None else list(map(min, zip(ms, ts))))
        
        # Gen grid
        self.grid = Grid(self.size, default)
        
        # Gen keyboard listener
        self.kb = Listener(on_press = self.on_event, on_release = on_rel)
        
        # vsync utilities
        self.running = True
        self.drawing = False
        self.keys_stock = []
        
        self.default = default
        self.user_event = on_press
        self.user_event_rel = on_rel

    def print(self, flush: bool = True) -> None:
        '''
        Render the current state of the grid.
        '''
        
        # clear esc seq (better perf?)
        if flush: print('\033c')
        
        print(self.grid.join())

    def on_event(self, key: Key) -> None:
        '''
        Listen to the keyboard events.
        '''
        
        # Wait for previous frame to be drawed
        while self.drawing: sleep(0.1)    
        drawing = True
        
        # Cancel if too much keyboard events
        self.keys_stock.append(key)
        if len(self.keys_stock) > 1: return
        
        # Call user event
        if self.user_event is not None:
            self.user_event(self, key)
        
        # Update
        self.print()
        self.keys_stock.remove(key)
        drawing = False

    def run(self, thread: bool = False) -> None:
        '''
        Init the shell and run the engine.
        '''
        
        # Hide user input
        print("\x1b[?25l") # Hide cursor
        os.system('stty -icanon -echo -ctlecho -crterase extproc')
        
        # Run
        with self.kb as ln: ln.join()
        
    def stop(self, msg: str = None, flush: bool = True) -> None:
        '''
        Stop the engine.
        '''
        
        # Stop listener
        self.kb.stop()
        del self.kb
        
        # Reset
        if flush: print('\033c')
        os.system('stty icanon echo ctlecho crterase -extproc')
        
        # TODO
        # Small hack to force quiting the kb thread
        os.system('xdotool key space')
        
        if msg is not None: print(msg)

# /
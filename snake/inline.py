import os
import copy
import platform
from time import time, sleep
from typing import Union, Any

# Fetch OS
OS_IS_WIN = platform.system() == 'Windows'

# Hide cursor
print("\x1b[?25l")

# + perf on linux
if not OS_IS_WIN: os.system('stty -icanon -echo -ctlecho -crterase extproc')

# Fetch shell size
MAX_SIZE = [30, 30]
size = os.get_terminal_size().columns, os.get_terminal_size().lines

if MAX_SIZE is not None: size = list(map(min, zip(size, MAX_SIZE)))

# Make grid acording to size
grid = [[' ' for _ in range(size[0])] for _ in range(size[1])]
# █

# Utilities
join_grid = lambda: '\n'.join(map(''.join, grid))

CLEAR_METHOD = 'full'
if CLEAR_METHOD == 'full': clear = lambda: os.system('cls' if OS_IS_WIN else 'clear')
elif CLEAR_METHOD == 'space':
    gap = os.get_terminal_size().columns - size[1]
    clear = lambda: print('\n' * gap)
else: clear = lambda: 0

mid = size[0] // 2, size[1] // 2
animation = ['-', '/', '|', '\\']

LATENCY = .1

i = 0
while 1:
    i += 1
    if i >= len(animation): i = 0
    
    grid[mid[1]][mid[0]] = animation[i]
    
    print(join_grid())
    sleep(LATENCY)
    clear()
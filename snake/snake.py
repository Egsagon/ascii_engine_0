import eng
import threading
from copy import copy
from time import sleep
from random import randint
from pynput.keyboard import Key

score = 0
player = []
player_pos = [3, 3]
apple = [0, 0] # oob pos to let time for init
is_eaten = True
direction = 'right'
running = True
boost = False
game_state = 'menu'
COR_SPEED = True
INIT_LEN = 3

# Default lenght
[player.append([0, 0]) for _ in range(INIT_LEN)]

def on_key(egn, key):
    # Listen to keys
    
    if globals()['game_state'] == 'menu':
        globals()['game_state'] = 'play'
        return
    
    old = globals()['direction']
    
    if key is Key.left and globals()['direction'] != 'right':
        globals()['direction'] = 'left'
    
    if key is Key.right and globals()['direction'] != 'left':
        globals()['direction'] = 'right'
    
    if key is Key.up and globals()['direction'] != 'down':
        globals()['direction'] = 'up'
    
    if key is Key.down and globals()['direction'] != 'up':
        globals()['direction'] = 'down'
    
    # Boost
    if key is Key.space: globals()['boost'] = True
    
    if str(key) == "'e'":
        globals()['running'] = False

def on_rel(key):
    # When key is released
    
    # Boost
    if key is Key.space:
        globals()['boost'] = False

engine = eng.Engine_0(None, on_key, on_rel = on_rel)
threading.Thread(target = engine.run).start()

# Main menu
engine.grid.write(engine.grid.size.x // 2, 5, "\033[7m<-> SNAKE IN THE SHELL <->\033[0m", .5)
engine.grid.write(engine.grid.size.x // 2, -5, "\033[3mPress any key to start\033[0m", .5)
engine.print()

# Wait for key press
while 1:
    if game_state == 'play': break

# Clear main menu
engine.grid.__post_init__()

# Main game loop
while 1:
    
    try:
        
        # Remove old player
        for body in player: engine.grid.set(*body, None)
        
        # Draw frame
        for x in range(engine.grid.size.x):
            engine.grid.set(x, 0, '#')
            engine.grid.set(x, -1, '#')
        
        for y in range(engine.grid.size.y):
            engine.grid.set(0, y, '#')
            engine.grid.set(-1, y, '#')
        
        # Draw corners
        corners = [(0, 0), (0, -1), (-1, 0), (-1, -1)]
        [engine.grid.set(x, y, '#') for x, y in corners]
        
        if [*player_pos] == [*apple]: is_eaten = True
        
        # Draw apple
        player.insert(0, list(player_pos))
        
        if is_eaten: # Gen new apple
            engine.grid.set(*apple, ' ')
            apple = randint(1, engine.grid.size.x - 2), randint(1, engine.grid.size.y - 2)
            is_eaten = False
            score += 1
            
        else: player.pop()
        
        engine.grid.set(*apple, 'A')
        
        # Move forward
        if direction == 'left': player_pos[0] -= 1
        elif direction == 'right': player_pos[0] += 1
        elif direction == 'up': player_pos[1] -= 1
        elif direction == 'down': player_pos[1] += 1
        
        # Check for death
        if engine.grid.get(*player_pos) in ('●', '#'):

            running = False
            engine.stop()
            
            print(f'You died! Your score was of {score}.')
            raise SystemExit()
        
        if not running:
            engine.stop()
            exit()
            
        # Write score on top left
        engine.grid.write(1, 1, f'Score: {score}')
        
        # Update player
        for body in player:
            engine.grid.set(*body, '●')
        
        engine.print()
        
        speed = .06
        
        if boost: speed -= .04
        if COR_SPEED and direction in ('up', 'down'): speed += .04
        
        sleep(speed)
    
    
    except Exception as e:
        engine.stop()
        raise e
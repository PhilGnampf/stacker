# -------------------------------------------------------------------------------------------------------------
# This file is an implementation of the arcade game Stacker. The game is a simple game where the players goal is to stack blocks as a tower. The playing field consists of a 7x13 block grid wherethe blocks move in a group of 3 side by side. When the player activates a button the three blocks should be placed. If they are not aligned with the lower blocks the not aligned blocks will be deleted and only the aligned blocks will be placed. The side movement of the blocks will get faster until the player misses all blocks.
# The game has a simple GUI with a start screen, a game screen and a game over screen with a leaderboard. The game is controlled using only the spacebar and the blocks automatically move from side to side.
# The game is implemented in python using the Pygame library.
# -------------------------------------------------------------------------------------------------------------

from itertools import cycle
import json
import time
import pygame
import sys
import RPi.GPIO as GPIO

# GPIO setup
BUTTON_PIN = 17
SET_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SET_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize Pygame
pygame.init()

# Game grid dimensions
GRID_WIDTH = 7

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 1024
BLOCK_RATIO = 0.94
GAP_RATIO = 0.06
BLOCK_SIZE = SCREEN_WIDTH * BLOCK_RATIO / GRID_WIDTH
GAP_SIZE = SCREEN_WIDTH * GAP_RATIO / (GRID_WIDTH + 1)

GRID_HEIGHT = int(SCREEN_HEIGHT / (BLOCK_SIZE + GAP_SIZE))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (31, 81, 255)

# Game variables
clock = pygame.time.Clock()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Stacker Game")

# Load custom font
font_path = "./RetroGaming.ttf"

# Initialize grid
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Block movement variables
block_amount = 3
block_x = 0
block_y = GRID_HEIGHT - 1
tick_speed = 240
direction = 1
init_move_speed = 60
current_move_speed = init_move_speed
move_speed = init_move_speed
move_speed_diff = 1

score = 0
button_pressed = False
button_pressed_set = False

# ------------------------------------------------------------------- Menu screen starts here -------------------------------------------------------------------
def start_menu():
    global button_pressed
    while True:
        pygame.font.init()
        font = pygame.font.Font(font_path, 36)
        
        # Start screen
        screen.fill(BLACK)
        text = font.render("Press space to start", True, BLUE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(tick_speed)
        
        if GPIO.input(BUTTON_PIN) == GPIO.LOW and not button_pressed:
            print("Button pressed")
            button_pressed = True
            start_game()
            break
        elif GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            button_pressed = False
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

# ------------------------------------------------------------------- Menu screen ends here -------------------------------------------------------------------
# ------------------------------------------------------------------- Main Game functions start here -------------------------------------------------------------------

### Draw simple rectangle
def draw_simple_rect(x, y, color):
    pygame.draw.rect(screen, color, (x * (BLOCK_SIZE + GAP_SIZE) + GAP_SIZE, y * (BLOCK_SIZE + GAP_SIZE) + GAP_SIZE, BLOCK_SIZE, BLOCK_SIZE))

### Draw scrolling grid when the grid is full
def scroll_grid():
    global grid
    
    # Scroll the grid up by multiple rows
    for _ in range(GRID_HEIGHT - 1):
        # Scroll the grid up by one row
        for y in range(GRID_HEIGHT - 1, 0, -1):
            grid[y] = grid[y - 1][:]
        # Insert a new empty row at the top
        grid[0] = [0 for _ in range(GRID_WIDTH)]
        draw_full_grid()
        time.sleep(0.2)
 
def draw_full_grid():
    screen.fill(BLACK)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 1:
                draw_simple_rect(x, y, BLUE)
    pygame.display.flip()

### Draw static grid
def draw_staticgrid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 1:
                draw_simple_rect(x, y, BLUE)

### Place blocks on grid
def place_blocks():
    global block_amount, block_y, block_x, score, current_move_speed

    # Check for first row
    if block_y == GRID_HEIGHT - 1:
        for i in range(block_amount):
            grid[block_y][block_x + i] = 1
        current_move_speed -= move_speed_diff
        block_y -= 1
        block_x = 0
        return
    
    # Check for alignment
    for i in range(block_amount):
        if grid[block_y + 1][block_x + i] == 1:
            grid[block_y][block_x + i] = 1
        else:
            block_amount -= 1

    # Check for game over
    if block_amount <= 0:
        print("Game Over")
        print("Score: ", score)
        start_highscore(score)

    # Update score
    current_move_speed -= move_speed_diff
    score += 1
    print("Score: ", score)
    print("Current move speed: ", current_move_speed)
    block_y -= 1
    block_x = 0

    # Check for full row
    if block_y < 0:
        scroll_grid()
        block_y = GRID_HEIGHT - 2

# ------------------------------------------------------------------- Main game loop starts here -------------------------------------------------------------------

def start_game():
    global block_amount, block_x, block_y, score, direction, move_speed, tick_speed, current_move_speed, button_pressed

    # Reset game variables
    block_amount = 3
    block_x = 0
    block_y = GRID_HEIGHT - 1
    score = 0
    direction = 1
    move_speed = init_move_speed
    current_move_speed = init_move_speed

    # reset grid
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            grid[y][x] = 0

    # Game loop
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW and not button_pressed:
            print("Button pressed")
            button_pressed = True
            place_blocks()
        elif GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            button_pressed = False

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Draw static grid
        screen.fill(BLACK)
        draw_staticgrid()

        # Draw moving blocks
        for i in range(block_amount):
            draw_simple_rect(block_x + i, block_y, BLUE)
        
        # Move blocks for next turn
        if move_speed == 0:
            move_speed = current_move_speed
            if block_x == 0:
                direction = 1
            elif block_x == GRID_WIDTH - block_amount:
                direction = -1
            block_x += direction

        move_speed -= 1

        pygame.display.flip()
        clock.tick(tick_speed)

# ------------------------------------------------------------------- Main game loop ends here -------------------------------------------------------------------
# ------------------------------------------------------------------- High Score Functions start here --------------------------------------------------------------

def load_highscores():
    try:
        with open("highscore.json", "r") as file:
            return json.load(file)
    except:
        return {}
    
def save_highscores(highscores):
    with open("highscore.json", "w") as file:
        json.dump(highscores, file, indent=4)

def character_selection(characters, label, max_length):
    global button_pressed, button_pressed_set
    
    index_cycle = cycle(range(len(characters)))
    current_char = next(index_cycle)
    input_string = ""

    while True:
        screen.fill((0, 0, 0))  # Schwarzer Hintergrund
        font = pygame.font.Font(font_path, 36)
        display_string = f"{label}: {input_string + characters[current_char]}"
        text = font.render(display_string, True, BLUE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(text, text_rect)
        pygame.display.flip()

        if GPIO.input(BUTTON_PIN) == GPIO.LOW and not button_pressed:
            print("Button pressed")
            current_char = next(index_cycle)
            button_pressed = True
        elif GPIO.input(BUTTON_PIN) == GPIO.HIGH:
            button_pressed = False
        
        if GPIO.input(SET_PIN) == GPIO.LOW and not button_pressed_set:
            print("Button pressed")
            input_string += characters[current_char]
            if len(input_string) == max_length:
                return input_string
            index_cycle = cycle(range(len(characters)))  # Zyklus zurücksetzen
            current_char = next(index_cycle)
            button_pressed_set = True
        elif GPIO.input(SET_PIN) == GPIO.HIGH:
            button_pressed_set = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def show_message(message, duration):
    screen.fill((0, 0, 0))  # Schwarzer Hintergrund
    font = pygame.font.Font(font_path, 36)
    text = font.render(message, True, (255, 0, 0))  # Rote Schrift für Fehler
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(duration * 1000)  # Warte für die angegebene Dauer in Millisekunden

# ------------------------------------------------------------------- High Score Screen starts here --------------------------------------------------------------

def start_highscore(score):
    while True:
        highscores = load_highscores()
        alphabet = "ABCDE"
        digits = "1234"

        # Namen eingeben
        name = character_selection(alphabet, "Name", max_length=3)
        # Passwort eingeben
        password = character_selection(digits, "Password", max_length=2)
        
        # Überprüfe, ob der Name existiert und das Passwort korrekt ist
        if name in highscores:
            if highscores[name]['password'] == password:
                # Update the highscore if the new score is higher
                if score > highscores[name]['highscore']:
                    highscores[name]['highscore'] = score
            else:
                show_message("Wrong Password!", 2)
                return start_highscore(score)  # Benutzer zurück zum Start der Eingabe
        else:
            # Neuen Eintrag erstellen, wenn der Benutzername nicht existiert
            highscores[name] = {"password": password, "highscore": score}

        save_highscores(highscores)
        print("Highscores:", highscores)
        start_menu()

# ------------------------------------------------------------------- High Score Screen ends here ----------------------------------------------------------------

def main():
    start_menu()

if __name__ == "__main__":
    main()
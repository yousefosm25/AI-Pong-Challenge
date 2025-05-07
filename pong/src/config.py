import pygame

# Initialize Pygame with AVX2 support
import os
os.environ['PYGAME_DETECT_AVX2'] = '1'
os.environ['SDL_VIDEODRIVER'] = 'x11'  # Use X11 video driver instead of GTK
pygame.init()

# Window dimensions
WIDTH, HEIGHT = 800, 600

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
PADDLE_SPEED = 8

# Ball settings
BALL_SIZE = 15
BALL_SPEED = 6
MAX_BALL_SPEED = 10
SPEED_INCREASE = 0.05

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
HIGHLIGHT = (200, 200, 200)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
PURPLE = (150, 0, 255)

# Background settings
GRADIENT_COLORS = [
    (20, 20, 30),    # Dark blue
    (30, 20, 40),    # Dark purple
    (20, 30, 40),    # Dark teal
    (30, 30, 20)     # Dark olive
]
GRADIENT_SPEED = 0.5
CENTER_LINE_DASH_LENGTH = 20
CENTER_LINE_GAP = 10
CENTER_LINE_SPEED = 2

# Game states
MENU = 0
PLAYING = 1
CONTROLS = 2
MODE_SELECT = 3
GAME_OVER = 4

# Game modes
PVP = 0
PVAI = 1 
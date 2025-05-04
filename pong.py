import pygame
import sys
import random
import math
from pygame import gfxdraw

# Initialize Pygame with AVX2 support
import os
os.environ['PYGAME_DETECT_AVX2'] = '1'
os.environ['SDL_VIDEODRIVER'] = 'x11'  # Use X11 video driver instead of GTK
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
PADDLE_SPEED = 7
BALL_SPEED = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
HIGHLIGHT = (200, 200, 200)
BLUE = (0, 100, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
PURPLE = (150, 0, 255)

# Add these constants after the existing color constants
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

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

# Game states
MENU = 0
PLAYING = 1
CONTROLS = 2
MODE_SELECT = 3
GAME_OVER = 4
game_state = MENU

# Game modes
PVP = 0
PVAI = 1
game_mode = PVP

# Particle class for effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= self.decay
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life <= 0:
            return
            
        alpha = int(255 * self.life)
        size = int(self.size)
        
        # Create a surface for the particle
        particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        
        # Get RGB components
        if len(self.color) == 3:
            r, g, b = self.color
        else:
            r, g, b = self.color[:3]
            
        # Draw the particle with alpha
        pygame.draw.circle(particle_surface, (r, g, b, alpha), (size, size), size)
        
        # Blit the particle surface onto the main surface
        surface.blit(particle_surface, (int(self.x) - size, int(self.y) - size))

# Particle system
particles = []

def add_particles(x, y, color, count=10):
    for _ in range(count):
        particles.append(Particle(x, y, color))

# Paddle class
class Paddle:
    def __init__(self, x, y, color=WHITE):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.score = 0
        self.color = color
        self.glow_radius = 0
        self.glow_direction = 1
        self.hit_animation = 0

    def move(self, up=True):
        if up and self.rect.top > 0:
            self.rect.y -= PADDLE_SPEED
        elif not up and self.rect.bottom < HEIGHT:
            self.rect.y += PADDLE_SPEED

    def draw(self):
        # Draw glow effect
        if self.glow_radius > 0:
            glow_surface = pygame.Surface((PADDLE_WIDTH + self.glow_radius*2, PADDLE_HEIGHT + self.glow_radius*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.color, 50), (0, 0, PADDLE_WIDTH + self.glow_radius*2, PADDLE_HEIGHT + self.glow_radius*2), border_radius=5)
            screen.blit(glow_surface, (self.rect.x - self.glow_radius, self.rect.y - self.glow_radius))
        
        # Draw paddle with rounded corners and gradient
        for i in range(PADDLE_HEIGHT):
            alpha = int(255 * (1 - abs(i - PADDLE_HEIGHT/2) / (PADDLE_HEIGHT/2)))
            color = (*self.color, alpha)
            pygame.draw.line(screen, color, 
                           (self.rect.x, self.rect.y + i),
                           (self.rect.x + PADDLE_WIDTH, self.rect.y + i))
        
        # Hit animation
        if self.hit_animation > 0:
            hit_surface = pygame.Surface((PADDLE_WIDTH + 20, PADDLE_HEIGHT + 20), pygame.SRCALPHA)
            alpha = int(255 * (1 - self.hit_animation))
            pygame.draw.rect(hit_surface, (*WHITE, alpha), (0, 0, PADDLE_WIDTH + 20, PADDLE_HEIGHT + 20), border_radius=10)
            screen.blit(hit_surface, (self.rect.x - 10, self.rect.y - 10))
            self.hit_animation -= 0.1
        
        # Update glow effect
        self.glow_radius += 0.5 * self.glow_direction
        if self.glow_radius >= 10 or self.glow_radius <= 0:
            self.glow_direction *= -1

# Ball class
class Ball:
    def __init__(self):
        self.speed = BALL_SPEED  # Initialize speed before reset
        self.reset()
        self.trail = []
        self.hit_animation = 0
        self.last_collision = None
        self.subpixel_x = 0.0
        self.subpixel_y = 0.0
        self.max_trail_length = 10

    def reset(self):
        self.rect = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.dx = self.speed * random.choice([1, -1])
        self.dy = self.speed * random.choice([1, -1])
        self.subpixel_x = self.rect.x
        self.subpixel_y = self.rect.y
        self.trail = []
        self.hit_animation = 0
        self.last_collision = None

    def move(self):
        # Update sub-pixel position
        self.subpixel_x += self.dx
        self.subpixel_y += self.dy

        # Store current position for trail
        self.trail.append((self.subpixel_x + BALL_SIZE/2, self.subpixel_y + BALL_SIZE/2))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Update actual rect position
        self.rect.x = int(self.subpixel_x)
        self.rect.y = int(self.subpixel_y)

        # Ball collision with top and bottom
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1
            # Adjust sub-pixel position to prevent sticking
            if self.rect.top <= 0:
                self.subpixel_y = 0
            else:
                self.subpixel_y = HEIGHT - self.rect.height
            add_particles(self.rect.centerx, self.rect.centery, WHITE, 15)

    def check_paddle_collision(self, paddle):
        # Check if ball is moving towards paddle
        if (self.dx < 0 and paddle == player) or (self.dx > 0 and paddle == opponent):
            # Get the intersection point
            if self.rect.colliderect(paddle.rect):
                # Calculate where on the paddle the ball hit
                relative_intersect_y = (paddle.rect.centery - self.rect.centery) / (paddle.rect.height / 2)
                
                # Calculate bounce angle (max 45 degrees)
                bounce_angle = relative_intersect_y * (math.pi / 4)
                
                # Calculate new speed components
                speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
                self.dx = speed * math.cos(bounce_angle) * (-1 if self.dx > 0 else 1)
                self.dy = speed * -math.sin(bounce_angle)
                
                # Add some randomness to prevent predictable bounces
                self.dy += random.uniform(-0.5, 0.5)
                
                # Ensure minimum speed
                min_speed = self.speed
                current_speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
                if current_speed < min_speed:
                    self.dx *= min_speed / current_speed
                    self.dy *= min_speed / current_speed
                
                # Add hit effects
                self.hit_animation = 1.0
                paddle.hit_animation = 1.0
                add_particles(self.rect.centerx, self.rect.centery, paddle.color, 15)
                
                # Adjust sub-pixel position to prevent sticking
                if paddle == player:
                    self.subpixel_x = paddle.rect.right
                else:
                    self.subpixel_x = paddle.rect.left - self.rect.width
                
                return True
        return False

    def draw(self):
        # Draw trail with smooth gradient
        for i, (x, y) in enumerate(self.trail):
            alpha = int(255 * (i + 1) / len(self.trail))
            size = int(BALL_SIZE * (i + 1) / len(self.trail))
            # Use gfxdraw for smoother circles
            pygame.gfxdraw.filled_circle(screen, int(x), int(y), size, (*WHITE, alpha))
        
        # Draw ball with glow
        if self.hit_animation > 0:
            glow_surface = pygame.Surface((int(BALL_SIZE * 3), int(BALL_SIZE * 3)), pygame.SRCALPHA)
            alpha = int(255 * (1 - self.hit_animation))
            pygame.gfxdraw.filled_circle(glow_surface, 
                                       int(BALL_SIZE * 1.5), 
                                       int(BALL_SIZE * 1.5), 
                                       int(BALL_SIZE * 1.5), 
                                       (*WHITE, alpha))
            screen.blit(glow_surface, (self.rect.x - BALL_SIZE, self.rect.y - BALL_SIZE))
            self.hit_animation -= 0.1
        
        # Draw ball with smooth gradient
        for i in range(BALL_SIZE):
            alpha = int(255 * (1 - i / BALL_SIZE))
            # Use gfxdraw for smoother circles
            pygame.gfxdraw.filled_circle(screen, 
                                       self.rect.centerx, 
                                       self.rect.centery, 
                                       BALL_SIZE - i, 
                                       (*WHITE, alpha))

# Create game objects
player = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, BLUE)
opponent = Paddle(WIDTH - 35, HEIGHT // 2 - PADDLE_HEIGHT // 2, RED)
ball = Ball()

# Fonts
title_font = pygame.font.Font(None, 100)
menu_font = pygame.font.Font(None, 50)
score_font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 36)

def render_text(text, font, color, antialias=True):
    """Helper function to render text with proper color handling"""
    if len(color) == 3:
        # For RGB colors
        return font.render(text, antialias, color)
    else:
        # For RGBA colors
        text_surface = font.render(text, antialias, color[:3])
        alpha_surface = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        alpha_surface.blit(text_surface, (0, 0))
        alpha_surface.fill((*color[:3], color[3]), special_flags=pygame.BLEND_RGBA_MULT)
        return alpha_surface

# Menu buttons
class Button:
    def __init__(self, x, y, width, height, text, font, color=WHITE, hover_color=HIGHLIGHT):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False
        self.color = color
        self.hover_color = hover_color
        self.animation_offset = 0
        self.animation_direction = 1
        self.click_animation = 0

    def draw(self):
        # Animate button position
        self.rect.y += math.sin(self.animation_offset) * 2
        self.animation_offset += 0.1
        if self.animation_offset >= 2 * math.pi:
            self.animation_offset = 0

        color = self.hover_color if self.is_hovered else self.color
        
        # Draw button with rounded corners and glow
        if self.is_hovered:
            glow_surface = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*color, 50), (0, 0, self.rect.width + 10, self.rect.height + 10), border_radius=10)
            screen.blit(glow_surface, (self.rect.x - 5, self.rect.y - 5))
        
        # Click animation
        if self.click_animation > 0:
            click_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            alpha = int(255 * (1 - self.click_animation))
            pygame.draw.rect(click_surface, (*color, alpha), (0, 0, self.rect.width + 20, self.rect.height + 20), border_radius=10)
            screen.blit(click_surface, (self.rect.x - 10, self.rect.y - 10))
            self.click_animation -= 0.1
        
        # Draw button with gradient
        for i in range(self.rect.height):
            alpha = int(255 * (1 - abs(i - self.rect.height/2) / (self.rect.height/2)))
            pygame.draw.line(screen, (*color, alpha), 
                           (self.rect.x, self.rect.y + i),
                           (self.rect.x + self.rect.width, self.rect.y + i))
        
        # Draw button border
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=10)
        
        # Render and draw text with proper color handling
        text_surface = render_text(self.text, self.font, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        
        # Draw text with shadow for better visibility
        shadow_surface = render_text(self.text, self.font, BLACK)
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def click(self):
        self.click_animation = 1.0
        add_particles(self.rect.centerx, self.rect.centery, self.color, 20)

# Create menu buttons with adjusted positions
start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Start Game", menu_font, BLUE, (100, 150, 255))
controls_button = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Controls", menu_font, GREEN, (100, 255, 100))
quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 90, 200, 50, "Quit", menu_font, RED, (255, 100, 100))

# Create mode selection buttons
pvp_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Player vs Player", menu_font, BLUE, (100, 150, 255))
pvai_button = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Player vs AI", menu_font, GREEN, (100, 255, 100))
back_button = Button(WIDTH//2 - 100, HEIGHT//2 + 90, 200, 50, "Back", menu_font, RED, (255, 100, 100))

# Create game over button
menu_button = Button(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, "Main Menu", menu_font, WHITE, HIGHLIGHT)

def draw_center_line():
    for i in range(0, HEIGHT, 30):
        alpha = int(255 * (1 - abs(i - HEIGHT/2) / (HEIGHT/2)))
        pygame.draw.rect(screen, (*WHITE, alpha), (WIDTH//2 - 2, i, 4, 20))

# Add this class after the Particle class
class Background:
    def __init__(self):
        self.gradient_offset = 0
        self.center_line_offset = 0
        self.particles = []
        self.grid_size = 50
        self.grid_opacity = 30

    def update(self):
        # Update gradient offset
        self.gradient_offset += GRADIENT_SPEED
        if self.gradient_offset >= len(GRADIENT_COLORS):
            self.gradient_offset = 0

        # Update center line offset
        self.center_line_offset += CENTER_LINE_SPEED
        if self.center_line_offset >= CENTER_LINE_DASH_LENGTH + CENTER_LINE_GAP:
            self.center_line_offset = 0

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

    def draw(self, surface):
        # Draw gradient background
        for y in range(HEIGHT):
            # Calculate gradient color
            color_index = int((y + self.gradient_offset) / HEIGHT * len(GRADIENT_COLORS)) % len(GRADIENT_COLORS)
            next_color_index = (color_index + 1) % len(GRADIENT_COLORS)
            progress = ((y + self.gradient_offset) / HEIGHT * len(GRADIENT_COLORS)) % 1

            # Interpolate between colors
            r = int(GRADIENT_COLORS[color_index][0] * (1 - progress) + GRADIENT_COLORS[next_color_index][0] * progress)
            g = int(GRADIENT_COLORS[color_index][1] * (1 - progress) + GRADIENT_COLORS[next_color_index][1] * progress)
            b = int(GRADIENT_COLORS[color_index][2] * (1 - progress) + GRADIENT_COLORS[next_color_index][2] * progress)

            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # Draw grid
        for x in range(0, WIDTH, self.grid_size):
            for y in range(0, HEIGHT, self.grid_size):
                alpha = int(self.grid_opacity * (1 - abs(x - WIDTH/2) / (WIDTH/2)))
                pygame.draw.line(surface, (*WHITE, alpha), (x, 0), (x, HEIGHT), 1)
                pygame.draw.line(surface, (*WHITE, alpha), (0, y), (WIDTH, y), 1)

        # Draw animated center line
        y = self.center_line_offset
        while y < HEIGHT:
            # Draw dash
            pygame.draw.line(surface, (*WHITE, 100), (WIDTH//2, y), (WIDTH//2, y + CENTER_LINE_DASH_LENGTH), 2)
            y += CENTER_LINE_DASH_LENGTH + CENTER_LINE_GAP

        # Draw particles
        for particle in self.particles:
            particle.draw(surface)

    def add_particles(self, x, y, color, count=5):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

# Create background instance after the game objects
background = Background()

def draw_game():
    # Update and draw background
    background.update()
    background.draw(screen)
    
    # Update and draw particles
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.life <= 0:
            particles.remove(particle)
    
    player.draw()
    opponent.draw()
    ball.draw()
    
    # Draw scores with glow effect
    for score, x_pos, color in [(player.score, WIDTH // 4, BLUE), (opponent.score, 3 * WIDTH // 4, RED)]:
        # Draw glow
        glow_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*color, 50), (50, 50), 40)
        screen.blit(glow_surface, (x_pos - 50, 20 - 50))
        
        # Draw score
        score_text = render_text(str(score), score_font, color)
        screen.blit(score_text, (x_pos, 20))

def draw_menu():
    # Update and draw background
    background.update()
    background.draw(screen)
    
    # Draw title with glow effect
    title = render_text("PONG", title_font, WHITE)
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
    
    # Draw title glow
    glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
    pygame.draw.rect(glow_surface, (*WHITE, 30), (0, 0, title_rect.width + 40, title_rect.height + 40), border_radius=20)
    screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
    
    screen.blit(title, title_rect)
    
    # Draw buttons
    start_button.draw()
    controls_button.draw()
    quit_button.draw()

def draw_mode_select():
    # Update and draw background
    background.update()
    background.draw(screen)
    
    # Draw title with glow effect
    title = render_text("SELECT MODE", title_font, WHITE)
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
    
    # Draw title glow
    glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
    pygame.draw.rect(glow_surface, (*WHITE, 30), (0, 0, title_rect.width + 40, title_rect.height + 40), border_radius=20)
    screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
    
    screen.blit(title, title_rect)
    
    # Draw buttons
    pvp_button.draw()
    pvai_button.draw()
    back_button.draw()

def draw_controls():
    # Update and draw background
    background.update()
    background.draw(screen)
    
    # Draw title with glow effect
    title = render_text("CONTROLS", title_font, WHITE)
    title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
    
    # Draw title glow
    glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
    pygame.draw.rect(glow_surface, (*WHITE, 30), (0, 0, title_rect.width + 40, title_rect.height + 40), border_radius=20)
    screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
    
    screen.blit(title, title_rect)
    
    # Draw control instructions with glow effect
    controls = [
        "Player 1: Use UP and DOWN arrow keys",
        "Player 2: Use W and S keys (in PvP mode)",
        "First player to score 5 points wins",
        "Press ESC to return to menu"
    ]
    
    for i, text in enumerate(controls):
        control_text = render_text(text, menu_font, WHITE)
        control_rect = control_text.get_rect(center=(WIDTH//2, HEIGHT//2 + i*50))
        
        # Draw text glow
        glow_surface = pygame.Surface((control_rect.width + 20, control_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*WHITE, 20), (0, 0, control_rect.width + 20, control_rect.height + 20), border_radius=10)
        screen.blit(glow_surface, (control_rect.x - 10, control_rect.y - 10))
        
        screen.blit(control_text, control_rect)

def draw_game_over():
    # Update and draw background
    background.update()
    background.draw(screen)
    
    # Draw winner text with glow effect
    winner = "Player 1" if player.score > opponent.score else "Player 2" if game_mode == PVP else "AI"
    winner_text = render_text(f"{winner} Wins!", title_font, WHITE)
    winner_rect = winner_text.get_rect(center=(WIDTH//2, HEIGHT//3))
    
    # Draw winner glow
    glow_surface = pygame.Surface((winner_rect.width + 40, winner_rect.height + 40), pygame.SRCALPHA)
    pygame.draw.rect(glow_surface, (*WHITE, 30), (0, 0, winner_rect.width + 40, winner_rect.height + 40), border_radius=20)
    screen.blit(glow_surface, (winner_rect.x - 20, winner_rect.y - 20))
    
    screen.blit(winner_text, winner_rect)
    
    # Draw final score with glow effect
    score_text = render_text(f"{player.score} - {opponent.score}", menu_font, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    
    # Draw score glow
    glow_surface = pygame.Surface((score_rect.width + 20, score_rect.height + 20), pygame.SRCALPHA)
    pygame.draw.rect(glow_surface, (*WHITE, 20), (0, 0, score_rect.width + 20, score_rect.height + 20), border_radius=10)
    screen.blit(glow_surface, (score_rect.x - 10, score_rect.y - 10))
    
    screen.blit(score_text, score_rect)
    
    # Draw menu button
    menu_button.draw()

# Game loop
clock = pygame.time.Clock()
while True:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == MENU:
                if start_button.rect.collidepoint(mouse_pos):
                    start_button.click()
                    game_state = MODE_SELECT
                elif controls_button.rect.collidepoint(mouse_pos):
                    controls_button.click()
                    game_state = CONTROLS
                elif quit_button.rect.collidepoint(mouse_pos):
                    quit_button.click()
                    pygame.quit()
                    sys.exit()
            
            elif game_state == MODE_SELECT:
                if pvp_button.rect.collidepoint(mouse_pos):
                    pvp_button.click()
                    game_mode = PVP
                    game_state = PLAYING
                    player.score = 0
                    opponent.score = 0
                    ball.reset()
                elif pvai_button.rect.collidepoint(mouse_pos):
                    pvai_button.click()
                    game_mode = PVAI
                    game_state = PLAYING
                    player.score = 0
                    opponent.score = 0
                    ball.reset()
                elif back_button.rect.collidepoint(mouse_pos):
                    back_button.click()
                    game_state = MENU
            
            elif game_state == GAME_OVER:
                if menu_button.rect.collidepoint(mouse_pos):
                    menu_button.click()
                    game_state = MENU
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state in [PLAYING, CONTROLS]:
                    game_state = MENU

    if game_state == MENU:
        start_button.check_hover(mouse_pos)
        controls_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        draw_menu()
    
    elif game_state == MODE_SELECT:
        pvp_button.check_hover(mouse_pos)
        pvai_button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
        draw_mode_select()
    
    elif game_state == CONTROLS:
        draw_controls()
    
    elif game_state == PLAYING:
        # Player 1 movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.move(up=True)
        if keys[pygame.K_DOWN]:
            player.move(up=False)

        # Player 2 or AI movement
        if game_mode == PVP:
            if keys[pygame.K_w]:
                opponent.move(up=True)
            if keys[pygame.K_s]:
                opponent.move(up=False)
        else:  # AI mode
            if opponent.rect.centery < ball.rect.centery:
                opponent.move(up=False)
            elif opponent.rect.centery > ball.rect.centery:
                opponent.move(up=True)

        # Move ball
        ball.move()

        # Ball collision with paddles
        if ball.check_paddle_collision(player) or ball.check_paddle_collision(opponent):
            # Collision is handled in the check_paddle_collision method
            pass

        # Scoring
        if ball.rect.left <= 0:
            opponent.score += 1
            add_particles(ball.rect.centerx, ball.rect.centery, RED, 30)
            ball.reset()
        elif ball.rect.right >= WIDTH:
            player.score += 1
            add_particles(ball.rect.centerx, ball.rect.centery, BLUE, 30)
            ball.reset()
        
        # Check for win condition
        if player.score >= 5 or opponent.score >= 5:
            game_state = GAME_OVER
        
        draw_game()
    
    elif game_state == GAME_OVER:
        menu_button.check_hover(mouse_pos)
        draw_game_over()

    pygame.display.flip()
    clock.tick(60) 
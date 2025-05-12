"""
AI Pong Trainer using NEAT learning algorithm.
"""
import pygame
import neat
import os
import pickle
import time
import math
import random
from random import randint
from pygame import gfxdraw
from .config import WIDTH, HEIGHT, BLUE, RED, PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_SPEED, WHITE, BLACK
from .config import BALL_SIZE, BALL_SPEED, MAX_BALL_SPEED, SPEED_INCREASE

GEN = 0
WIN_ON = True

class Paddle:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.color = color
        self.glow_radius = 0
        self.glow_direction = 1
        self.hit_animation = 0
        self.speed = PADDLE_SPEED * 2  # Double the base speed
        self.velocity = 0
        self.target_y = y
        self.acceleration = 1.2  # Increased acceleration
        self.max_speed = self.speed
        self.friction = 0.9  # Less friction for faster movement

    def move_up(self):
        self.velocity -= self.acceleration
        if self.velocity < -self.max_speed:
            self.velocity = -self.max_speed

    def move_down(self):
        self.velocity += self.acceleration
        if self.velocity > self.max_speed:
            self.velocity = self.max_speed

    def move_stop(self):
        self.velocity *= self.friction

    def move(self):
        # Apply velocity
        self.rect.y += self.velocity
        
        # Apply friction
        self.velocity *= self.friction
        
        # Keep paddle in bounds
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0
        elif self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.velocity = 0

    def draw(self, screen):
        # Draw glow effect
        if self.glow_radius > 0:
            glow_surface = pygame.Surface((PADDLE_WIDTH + self.glow_radius*2, PADDLE_HEIGHT + self.glow_radius*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*self.color, 50), (0, 0, PADDLE_WIDTH + self.glow_radius*2, PADDLE_HEIGHT + self.glow_radius*2), border_radius=15)
            screen.blit(glow_surface, (self.rect.x - self.glow_radius, self.rect.y - self.glow_radius))
        
        # Draw paddle with rounded corners and gradient
        paddle_surface = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT), pygame.SRCALPHA)
        for i in range(PADDLE_HEIGHT):
            alpha = int(255 * (1 - abs(i - PADDLE_HEIGHT/2) / (PADDLE_HEIGHT/2)))
            color = (*self.color, alpha)
            pygame.draw.line(paddle_surface, color, 
                           (0, i),
                           (PADDLE_WIDTH, i))
        
        # Draw the rounded rectangle
        pygame.draw.rect(paddle_surface, self.color, (0, 0, PADDLE_WIDTH, PADDLE_HEIGHT), border_radius=15)
        screen.blit(paddle_surface, self.rect)
        
        # Hit animation
        if self.hit_animation > 0:
            hit_surface = pygame.Surface((PADDLE_WIDTH + 20, PADDLE_HEIGHT + 20), pygame.SRCALPHA)
            alpha = int(255 * (1 - self.hit_animation))
            pygame.draw.rect(hit_surface, (*WHITE, alpha), (0, 0, PADDLE_WIDTH + 20, PADDLE_HEIGHT + 20), border_radius=20)
            screen.blit(hit_surface, (self.rect.x - 10, self.rect.y - 10))
            self.hit_animation -= 0.1
        
        # Update glow effect
        self.glow_radius += 0.5 * self.glow_direction
        if self.glow_radius >= 10 or self.glow_radius <= 0:
            self.glow_direction *= -1

    def get_y(self):
        return self.rect.y

    def get_x(self):
        return self.rect.x

class Ball:
    def __init__(self, x, y, color):
        self.speed = BALL_SPEED
        self.rect = pygame.Rect(x, y, BALL_SIZE, BALL_SIZE)
        self.color = color
        self.trail = []
        self.hit_animation = 0
        self.last_collision = None
        self.subpixel_x = float(x)
        self.subpixel_y = float(y)
        self.max_trail_length = 12
        self.dx = self.speed * random.choice([1, -1])
        self.dy = self.speed * random.choice([1, -1])

    def change_vel_y(self):
        self.dy = -self.dy

    def change_vel_x(self):
        self.dx = -self.dx

    def move(self):
        self.subpixel_x += self.dx
        self.subpixel_y += self.dy

        self.trail.append((self.subpixel_x + BALL_SIZE/2, self.subpixel_y + BALL_SIZE/2))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        self.rect.x = int(self.subpixel_x)
        self.rect.y = int(self.subpixel_y)

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.dy *= -1
            if self.rect.top <= 0:
                self.subpixel_y = 0
            else:
                self.subpixel_y = HEIGHT - self.rect.height

    def draw(self, screen):
        # Draw trail
        for i, (x, y) in enumerate(self.trail):
            alpha = int(180 * (i + 1) / len(self.trail))
            size = BALL_SIZE * (i + 1) / len(self.trail)
            gfxdraw.aacircle(screen, int(x), int(y), int(size), (*self.color, alpha))
            gfxdraw.filled_circle(screen, int(x), int(y), int(size), (*self.color, alpha))
        
        # Draw hit animation
        if self.hit_animation > 0:
            glow_surface = pygame.Surface((int(BALL_SIZE * 3), int(BALL_SIZE * 3)), pygame.SRCALPHA)
            alpha = int(255 * (1 - self.hit_animation))
            gfxdraw.filled_circle(glow_surface, 
                                int(BALL_SIZE * 1.5), 
                                int(BALL_SIZE * 1.5), 
                                int(BALL_SIZE * 1.5), 
                                (*self.color, alpha))
            screen.blit(glow_surface, (self.rect.x - BALL_SIZE, self.rect.y - BALL_SIZE))
            self.hit_animation -= 0.1
        
        # Draw ball with gradient
        for i in range(BALL_SIZE):
            alpha = int(255 * (1 - i / BALL_SIZE))
            gfxdraw.filled_circle(screen, 
                                self.rect.centerx, 
                                self.rect.centery, 
                                BALL_SIZE - i, 
                                (*self.color, alpha))

    def get_x(self):
        return self.rect.x

    def get_y(self):
        return self.rect.y

    def collide(self, paddle):
        if self.rect.colliderect(paddle):
            relative_intersect_y = (paddle.rect.centery - self.rect.centery) / (paddle.rect.height / 2)
            bounce_angle = relative_intersect_y * (math.pi / 4)
            
            self.speed = min(MAX_BALL_SPEED, self.speed + SPEED_INCREASE)
            
            speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
            self.dx = speed * math.cos(bounce_angle) * (-1 if self.dx > 0 else 1)
            self.dy = speed * -math.sin(bounce_angle)
            
            self.dy += random.uniform(-0.5, 0.5)
            
            min_speed = self.speed
            current_speed = math.sqrt(self.dx * self.dx + self.dy * self.dy)
            if current_speed < min_speed:
                self.dx *= min_speed / current_speed
                self.dy *= min_speed / current_speed
            
            self.hit_animation = 1.0
            paddle.hit_animation = 1.0
            
            if paddle.rect.x < WIDTH/2:
                self.subpixel_x = paddle.rect.right
            else:
                self.subpixel_x = paddle.rect.left - self.rect.width
            
            return True
        return False

def random_sign():
    return -1 if randint(0, 1) == 0 else 1

class AITrainer:
    def __init__(self, game):
        self.game = game
        self.config = None
        self.population = None
        self.training_screen = None
        self.load_config()
        self.STAT_FONT = pygame.font.SysFont("comicsans", 40)

    def load_config(self):
        local_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(local_dir, 'config.txt')
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    def draw_window(self, paddles, paddles_r, balls):
        self.training_screen.fill(BLACK)
        
        for ball in balls:
            ball.draw(self.training_screen)
        for paddle in paddles:
            paddle.draw(self.training_screen)
        for paddle in paddles_r:
            paddle.draw(self.training_screen)

        score_label = self.STAT_FONT.render(f"Gens: {GEN-1}", 1, WHITE)
        self.training_screen.blit(score_label, (10, 10))
        
        # Add ESC instruction
        esc_label = self.STAT_FONT.render("Press ESC to exit", 1, WHITE)
        self.training_screen.blit(esc_label, (WIDTH - 300, 10))
        
        pygame.display.flip()

    def eval_genomes(self, genomes, config):
        global GEN
        GEN += 1
        score = 0

        paddles = []
        paddles_r = []
        balls = []
        nets = []
        ge = []

        # Create training screen if needed
        if WIN_ON and not self.training_screen:
            self.training_screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("NEAT Pong Training")

        # Initialize genomes
        for genome_id, g in genomes:
            tmp_color = (randint(100,255), randint(100,255), randint(100,255))
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            paddles.append(Paddle(20, HEIGHT//2 - PADDLE_HEIGHT//2, tmp_color))
            paddles_r.append(Paddle(WIDTH - 35, HEIGHT//2 - PADDLE_HEIGHT//2, tmp_color))
            balls.append(Ball(WIDTH//2, HEIGHT//2, tmp_color))
            g.fitness = 0
            ge.append(g)

        clock = pygame.time.Clock()
        run = True

        while run and len(paddles) > 0:
            if WIN_ON:
                clock.tick(60)  # Increased frame rate for smoother movement

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

            # Left paddle movement
            for x, paddle in enumerate(paddles):
                ge[x].fitness += 0.05
                paddle.move()

                # Calculate ball's predicted position
                ball = balls[x]
                ball_x = ball.get_x()
                ball_y = ball.get_y()
                ball_dx = ball.dx
                ball_dy = ball.dy

                # Predict where the ball will be when it reaches the paddle
                if ball_dx < 0:  # Ball moving towards left paddle
                    time_to_reach = (ball_x - paddle.get_x()) / abs(ball_dx)
                    predicted_y = ball_y + (ball_dy * time_to_reach)
                    
                    # Bounce prediction
                    while predicted_y < 0 or predicted_y > HEIGHT:
                        if predicted_y < 0:
                            predicted_y = -predicted_y
                        elif predicted_y > HEIGHT:
                            predicted_y = 2 * HEIGHT - predicted_y

                    # Use the original 3 inputs but with predicted position
                    outputs = nets[x].activate((
                        paddle.get_y(),
                        abs(paddle.get_x() - ball_x),
                        predicted_y
                    ))

                    if outputs[0] > outputs[1]:
                        if outputs[0] > 0.5:
                            paddle.move_up()
                        else:
                            paddle.move_stop()
                    elif outputs[1] > 0.5:
                        paddle.move_down()
                    else:
                        paddle.move_stop()

            # Right paddle movement
            for x, paddle in enumerate(paddles_r):
                ge[x].fitness += 0.05
                paddle.move()

                # Calculate ball's predicted position
                ball = balls[x]
                ball_x = ball.get_x()
                ball_y = ball.get_y()
                ball_dx = ball.dx
                ball_dy = ball.dy

                # Predict where the ball will be when it reaches the paddle
                if ball_dx > 0:  # Ball moving towards right paddle
                    time_to_reach = (paddle.get_x() - ball_x) / abs(ball_dx)
                    predicted_y = ball_y + (ball_dy * time_to_reach)
                    
                    # Bounce prediction
                    while predicted_y < 0 or predicted_y > HEIGHT:
                        if predicted_y < 0:
                            predicted_y = -predicted_y
                        elif predicted_y > HEIGHT:
                            predicted_y = 2 * HEIGHT - predicted_y

                    # Use the original 3 inputs but with predicted position
                    outputs = nets[x].activate((
                        paddle.get_y(),
                        abs(paddle.get_x() - ball_x),
                        predicted_y
                    ))

                    if outputs[0] > outputs[1]:
                        if outputs[0] > 0.5:
                            paddle.move_up()
                        else:
                            paddle.move_stop()
                    elif outputs[1] > 0.5:
                        paddle.move_down()
                    else:
                        paddle.move_stop()

            # Ball movement and collision
            for ball in balls:
                if ball.collide(paddles[balls.index(ball)]):
                    ge[balls.index(ball)].fitness += 5
                    score += 1
                if ball.collide(paddles_r[balls.index(ball)]):
                    ge[balls.index(ball)].fitness += 5
                    score += 1
                ball.move()
                if ball.get_x() < 0 or ball.get_x() > WIDTH:
                    ge[balls.index(ball)].fitness -= 2
                    nets.pop(balls.index(ball))
                    ge.pop(balls.index(ball))
                    paddles.pop(balls.index(ball))
                    paddles_r.pop(balls.index(ball))
                    balls.pop(balls.index(ball))

            if WIN_ON:
                self.draw_window(paddles, paddles_r, balls)

            if score > 500:
                break

        return False

    def cleanup(self):
        if self.training_screen:
            # Instead of quitting the display, just set it to None
            self.training_screen = None
            # Reset the display to the main game's screen
            pygame.display.set_mode((WIDTH, HEIGHT))

    def run_neat(self):
        self.population = neat.Population(self.config)
        self.population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        self.population.add_reporter(stats)
        self.population.add_reporter(neat.Checkpointer(1))
        winner = self.population.run(self.eval_genomes, 1000)
        with open("best.pickle", "wb") as f:
            pickle.dump(winner, f)
        self.cleanup()

    def test_best_network(self):
        with open("best.pickle", "rb") as f:
            winner = pickle.load(f)
        winner_net = neat.nn.FeedForwardNetwork.create(winner, self.config)
        # Optionally, you can implement a visual test here using the main Game class 
import pygame
import random
import math
from pygame import gfxdraw
from .config import BALL_SIZE, BALL_SPEED, MAX_BALL_SPEED, SPEED_INCREASE, WHITE, HEIGHT, WIDTH

class Ball:
    def __init__(self):
        self.speed = BALL_SPEED
        self.reset()
        self.trail = []
        self.hit_animation = 0
        self.last_collision = None
        self.subpixel_x = 0.0
        self.subpixel_y = 0.0
        self.max_trail_length = 12

    def reset(self):
        self.rect = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.dx = self.speed * random.choice([1, -1])
        self.dy = self.speed * random.choice([1, -1])
        self.subpixel_x = self.rect.x
        self.subpixel_y = self.rect.y
        self.trail = []
        self.hit_animation = 0
        self.last_collision = None
        self.speed = BALL_SPEED

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

    def check_paddle_collision(self, paddle):
        # Check if ball is moving towards paddle
        if (self.dx < 0 and paddle.rect.x < WIDTH/2) or (self.dx > 0 and paddle.rect.x > WIDTH/2):
            if self.rect.colliderect(paddle.rect):
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

    def draw(self, screen):
        for i, (x, y) in enumerate(self.trail):
            alpha = int(180 * (i + 1) / len(self.trail))
            size = BALL_SIZE * (i + 1) / len(self.trail)
            gfxdraw.aacircle(screen, int(x), int(y), int(size), (*WHITE, alpha))
            gfxdraw.filled_circle(screen, int(x), int(y), int(size), (*WHITE, alpha))
        
        if self.hit_animation > 0:
            glow_surface = pygame.Surface((int(BALL_SIZE * 3), int(BALL_SIZE * 3)), pygame.SRCALPHA)
            alpha = int(255 * (1 - self.hit_animation))
            gfxdraw.filled_circle(glow_surface, 
                                int(BALL_SIZE * 1.5), 
                                int(BALL_SIZE * 1.5), 
                                int(BALL_SIZE * 1.5), 
                                (*WHITE, alpha))
            screen.blit(glow_surface, (self.rect.x - BALL_SIZE, self.rect.y - BALL_SIZE))
            self.hit_animation -= 0.1
        
        for i in range(BALL_SIZE):
            alpha = int(255 * (1 - i / BALL_SIZE))
            gfxdraw.filled_circle(screen, 
                                self.rect.centerx, 
                                self.rect.centery, 
                                BALL_SIZE - i, 
                                (*WHITE, alpha)) 
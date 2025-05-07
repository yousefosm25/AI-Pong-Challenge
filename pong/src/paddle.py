import pygame
from .config import PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, WHITE, HEIGHT

class Paddle:
    def __init__(self, x, y, color=WHITE):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.score = 0
        self.color = color
        self.glow_radius = 0
        self.glow_direction = 1
        self.hit_animation = 0
        self.target_y = y
        self.speed = PADDLE_SPEED
        self.last_prediction = y
        self.prediction_update_timer = 0

    def move(self, up=True):
        if up and self.rect.top > 0:
            self.rect.y -= self.speed
        elif not up and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def move_to_target(self):
        if abs(self.rect.centery - self.target_y) > 2:
            distance = self.target_y - self.rect.centery
            move_amount = distance * 0.2
            
            if abs(move_amount) < 0.5:
                move_amount = 0.5 if move_amount > 0 else -0.5
                
            self.rect.centery += move_amount
            self.rect.top = max(0, min(HEIGHT - PADDLE_HEIGHT, self.rect.top))

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
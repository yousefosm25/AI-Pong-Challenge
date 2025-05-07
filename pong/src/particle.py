import pygame
import random
import math
from .config import WHITE

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 4)
        self.speed = random.uniform(0.5, 2)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = 1.0
        self.decay = random.uniform(0.05, 0.1)

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= self.decay
        self.size = max(0, self.size - 0.2)

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
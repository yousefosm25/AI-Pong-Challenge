import pygame
import random
import math
from .config import WHITE, WIDTH, HEIGHT

class IceParticle:
    def __init__(self):
        self.reset()
        self.alpha = random.randint(50, 150)
        self.size = random.uniform(1, 3)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.wobble_offset = random.uniform(0, 2 * math.pi)
        self.wobble_speed = random.uniform(0.02, 0.05)
        self.wobble_amount = random.uniform(0.5, 2)

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-100, 0)
        self.speed = random.uniform(1, 3)
        self.alpha = random.randint(50, 150)
        self.size = random.uniform(1, 3)

    def update(self):
        # Update position
        self.y += self.speed
        self.x += math.sin(self.wobble_offset) * self.wobble_amount
        self.wobble_offset += self.wobble_speed
        self.rotation += self.rotation_speed

        # Reset if out of screen
        if self.y > HEIGHT:
            self.reset()

    def draw(self, surface):
        # Create a surface for the ice particle
        particle_surface = pygame.Surface((int(self.size * 4), int(self.size * 4)), pygame.SRCALPHA)
        
        # Draw the ice particle with a diamond shape
        points = [
            (self.size * 2, 0),  # Top
            (self.size * 4, self.size * 2),  # Right
            (self.size * 2, self.size * 4),  # Bottom
            (0, self.size * 2)  # Left
        ]
        
        # Rotate the points
        rotated_points = []
        center = (self.size * 2, self.size * 2)
        for point in points:
            # Translate point to origin
            x = point[0] - center[0]
            y = point[1] - center[1]
            
            # Rotate
            rad = math.radians(self.rotation)
            cos_val = math.cos(rad)
            sin_val = math.sin(rad)
            new_x = x * cos_val - y * sin_val
            new_y = x * sin_val + y * cos_val
            
            # Translate back
            rotated_points.append((new_x + center[0], new_y + center[1]))
        
        # Draw the rotated diamond
        pygame.draw.polygon(particle_surface, (*WHITE, self.alpha), rotated_points)
        
        # Add a highlight
        highlight_points = [
            (self.size * 2, self.size * 0.5),  # Top
            (self.size * 3, self.size * 2),  # Right
            (self.size * 2, self.size * 3.5),  # Bottom
            (self.size, self.size * 2)  # Left
        ]
        
        # Rotate highlight points
        rotated_highlight = []
        for point in highlight_points:
            x = point[0] - center[0]
            y = point[1] - center[1]
            new_x = x * cos_val - y * sin_val
            new_y = x * sin_val + y * cos_val
            rotated_highlight.append((new_x + center[0], new_y + center[1]))
        
        # Draw the highlight
        pygame.draw.polygon(particle_surface, (*WHITE, self.alpha + 50), rotated_highlight)
        
        # Blit the particle surface onto the main surface
        surface.blit(particle_surface, (int(self.x - self.size * 2), int(self.y - self.size * 2))) 
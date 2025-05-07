import pygame
import random
from .config import GRADIENT_COLORS, GRADIENT_SPEED, CENTER_LINE_DASH_LENGTH, CENTER_LINE_GAP, CENTER_LINE_SPEED, HEIGHT, WIDTH, WHITE
from .particle import Particle
from .ice_particle import IceParticle

class Background:
    def __init__(self):
        self.gradient_offset = 0
        self.center_line_offset = 0
        self.particles = []
        self.grid_size = 100
        self.grid_opacity = 20
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
        self.ice_particles = [IceParticle() for _ in range(30)]  # Create 30 ice particles

    def update(self):
        self.gradient_offset += GRADIENT_SPEED
        if self.gradient_offset >= len(GRADIENT_COLORS):
            self.gradient_offset = 0

        self.center_line_offset = (self.center_line_offset + 1) % (CENTER_LINE_DASH_LENGTH + CENTER_LINE_GAP)

        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        # Update ice particles
        for particle in self.ice_particles:
            particle.update()

    def draw(self, surface):
        # Draw gradient background
        for y in range(HEIGHT):
            color_index = int((y + self.gradient_offset) / HEIGHT * len(GRADIENT_COLORS)) % len(GRADIENT_COLORS)
            next_color_index = (color_index + 1) % len(GRADIENT_COLORS)
            progress = ((y + self.gradient_offset) / HEIGHT * len(GRADIENT_COLORS)) % 1
            r = int(GRADIENT_COLORS[color_index][0] * (1 - progress) + GRADIENT_COLORS[next_color_index][0] * progress)
            g = int(GRADIENT_COLORS[color_index][1] * (1 - progress) + GRADIENT_COLORS[next_color_index][1] * progress)
            b = int(GRADIENT_COLORS[color_index][2] * (1 - progress) + GRADIENT_COLORS[next_color_index][2] * progress)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # Draw stars
        for x, y in self.stars:
            brightness = random.randint(100, 255)
            pygame.draw.circle(surface, (brightness, brightness, brightness), (x, y), 1)

        # Draw particles
        for particle in self.particles:
            particle.draw(surface)

        # Draw ice particles
        for particle in self.ice_particles:
            particle.draw(surface)

    def add_particles(self, x, y, color, count=3):
        for _ in range(count):
            self.particles.append(Particle(x, y, color)) 
import pygame
import math
from .config import WHITE, BLACK, HIGHLIGHT, WIDTH, HEIGHT

class Button:
    def __init__(self, center_x, center_y, min_width, min_height, text, font, color=WHITE, hover_color=HIGHLIGHT):
        self.text = text
        self.font = font
        self.is_hovered = False
        self.color = color
        self.hover_color = hover_color
        self.animation_offset = 0
        self.animation_direction = 1
        self.click_animation = 0
        self.original_font_size = font.get_height()
        self.current_font = font
        
        # Calculate initial size based on text
        text_surface = self.font.render(text, True, WHITE)
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        # Set button size with padding
        self.width = max(min_width, text_width + 40)
        self.height = max(min_height, text_height + 20)
        
        # Use a fixed border radius for all corners
        self.radius = min(self.height // 2, 30)
        
        # Create rect with calculated size, centered at the given coordinates
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (center_x, center_y)
        self.original_rect = self.rect.copy()

    def draw(self, screen):
        # Animate button position with smooth floating
        self.rect.y = self.original_rect.y + math.sin(self.animation_offset) * 3
        self.animation_offset += 0.2
        if self.animation_offset >= 2 * math.pi:
            self.animation_offset = 0

        color = self.hover_color if self.is_hovered else self.color
        shadow_offset_x = 6
        shadow_offset_y = 6
        r = self.radius

        # --- Draw shadow as a rounded rectangle, only to the right and down, never on the left/top ---
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(shadow_offset_x, shadow_offset_y, self.rect.width - shadow_offset_x, self.rect.height - shadow_offset_y)
        pygame.draw.rect(shadow_surface, (*BLACK, 80), shadow_rect, border_radius=r)
        screen.blit(shadow_surface, self.rect)

        # --- Draw button background as a rounded rectangle ---
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for i in range(self.rect.height):
            alpha = int(255 * (1 - abs(i - self.rect.height/2) / (self.rect.height/2)))
            pygame.draw.line(button_surface, (*color, alpha), (0, i), (self.rect.width, i))
        pygame.draw.rect(button_surface, color, (0, 0, self.rect.width, self.rect.height), border_radius=r)
        screen.blit(button_surface, self.rect)

        # --- Draw border as a rounded rectangle ---
        pygame.draw.rect(screen, color, self.rect, 2, border_radius=r)

        # --- Draw text ---
        text_surface = self.current_font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        # Draw text with shadow
        shadow_surface = self.font.render(self.text, True, BLACK)
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def click(self):
        self.click_animation = 1.0 
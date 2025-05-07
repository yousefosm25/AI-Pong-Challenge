import pygame
import sys
import random
from .config import *
from .paddle import Paddle
from .ball import Ball
from .background import Background
from .button import Button
from .particle import Particle

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong")
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 100)
        self.menu_font = pygame.font.Font(None, 50)
        self.score_font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        
        # Initialize game objects
        self.player = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, BLUE)
        self.opponent = Paddle(WIDTH - 35, HEIGHT // 2 - PADDLE_HEIGHT // 2, RED)
        self.ball = Ball()
        self.background = Background()
        
        # Initialize buttons
        self.start_button = Button(WIDTH//2, HEIGHT//2 - 20, 200, 50, "Start Game", self.menu_font, BLUE, (100, 150, 255))
        self.controls_button = Button(WIDTH//2, HEIGHT//2 + 50, 200, 50, "Controls", self.menu_font, GREEN, (100, 255, 100))
        self.quit_button = Button(WIDTH//2, HEIGHT//2 + 120, 200, 50, "Quit", self.menu_font, RED, (255, 100, 100))
        
        self.pvp_button = Button(WIDTH//2, HEIGHT//2 - 20, 200, 50, "Player vs Player", self.menu_font, BLUE, (100, 150, 255))
        self.pvai_button = Button(WIDTH//2, HEIGHT//2 + 50, 200, 50, "Player vs AI", self.menu_font, GREEN, (100, 255, 100))
        self.back_button = Button(WIDTH//2, HEIGHT//2 + 120, 200, 50, "Back", self.menu_font, RED, (255, 100, 100))
        
        self.menu_button = Button(WIDTH//2, HEIGHT//2 + 80, 200, 50, "Main Menu", self.menu_font, WHITE, HIGHLIGHT)
        
        # Game state
        self.game_state = MENU
        self.game_mode = PVP
        self.particles = []
        
        # Clock for FPS
        self.clock = pygame.time.Clock()

    def add_particles(self, x, y, color, count=5):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def draw_game(self):
        self.background.update()
        self.background.draw(self.screen)
        
        # Draw animated center line
        y = self.background.center_line_offset
        while y < HEIGHT:
            pygame.draw.line(self.screen, (*WHITE, 100), (WIDTH//2, y), (WIDTH//2, y + CENTER_LINE_DASH_LENGTH), 2)
            y += CENTER_LINE_DASH_LENGTH + CENTER_LINE_GAP
        
        # Update and draw particles
        for particle in self.particles[:]:
            particle.update()
            particle.draw(self.screen)
            if particle.life <= 0:
                self.particles.remove(particle)
        
        self.player.draw(self.screen)
        self.opponent.draw(self.screen)
        self.ball.draw(self.screen)
        
        # Draw scores
        for score, x_pos, color in [(self.player.score, WIDTH // 4, BLUE), (self.opponent.score, 3 * WIDTH // 4, RED)]:
            score_text = self.score_font.render(str(score), True, color)
            score_rect = score_text.get_rect(center=(x_pos, 70))
            self.screen.blit(score_text, score_rect)

    def draw_menu(self):
        self.screen.fill(BLACK)
        self.background.update()
        self.background.draw(self.screen)
        
        # Draw title
        title = self.title_font.render("PONG", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        
        # Draw title glow
        glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*WHITE, 30), (0, 0, title_rect.width + 40, title_rect.height + 40), border_radius=20)
        self.screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
        self.screen.blit(title, title_rect)
        
        # Draw buttons
        self.start_button.draw(self.screen)
        self.controls_button.draw(self.screen)
        self.quit_button.draw(self.screen)

    def draw_mode_select(self):
        self.screen.fill(BLACK)
        self.background.update()
        self.background.draw(self.screen)
        
        # Draw title
        title = self.title_font.render("SELECT MODE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        
        # Draw title glow
        glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*WHITE, 30), (0, 0, title_rect.width + 40, title_rect.height + 40), border_radius=20)
        self.screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
        self.screen.blit(title, title_rect)
        
        # Draw buttons
        self.pvp_button.draw(self.screen)
        self.pvai_button.draw(self.screen)
        self.back_button.draw(self.screen)

    def draw_controls(self):
        self.screen.fill(BLACK)
        self.background.update()
        self.background.draw(self.screen)
        
        # Draw title
        title = self.title_font.render("CONTROLS", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        
        # Draw title glow
        glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*WHITE, 30), (0, 0, title_rect.width + 40, title_rect.height + 40), border_radius=20)
        self.screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 20))
        self.screen.blit(title, title_rect)
        
        # Draw control instructions
        controls = [
            "Player 1: Use UP and DOWN arrow keys",
            "Player 2: Use W and S keys (in PvP mode)",
            "First player to score 5 points wins",
            "Press ESC to return to menu"
        ]
        
        for i, text in enumerate(controls):
            control_text = self.menu_font.render(text, True, WHITE)
            control_rect = control_text.get_rect(center=(WIDTH//2, HEIGHT//2 + i*50))
            
            # Draw text glow
            glow_surface = pygame.Surface((control_rect.width + 20, control_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*WHITE, 20), (0, 0, control_rect.width + 20, control_rect.height + 20), border_radius=10)
            self.screen.blit(glow_surface, (control_rect.x - 10, control_rect.y - 10))
            
            self.screen.blit(control_text, control_rect)

    def draw_game_over(self):
        self.screen.fill(BLACK)
        self.background.update()
        self.background.draw(self.screen)
        
        # Draw winner text
        winner = "Player 1" if self.player.score > self.opponent.score else "Player 2" if self.game_mode == PVP else "AI"
        winner_text = self.title_font.render(f"{winner} Wins!", True, WHITE)
        winner_rect = winner_text.get_rect(center=(WIDTH//2, HEIGHT//3))
        
        # Draw winner glow
        glow_surface = pygame.Surface((winner_rect.width + 40, winner_rect.height + 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*WHITE, 30), (0, 0, winner_rect.width + 40, winner_rect.height + 40), border_radius=20)
        self.screen.blit(glow_surface, (winner_rect.x - 20, winner_rect.y - 20))
        self.screen.blit(winner_text, winner_rect)
        
        # Draw final score
        score_text = self.menu_font.render(f"{self.player.score} - {self.opponent.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        # Draw score glow
        glow_surface = pygame.Surface((score_rect.width + 20, score_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (*WHITE, 20), (0, 0, score_rect.width + 20, score_rect.height + 20), border_radius=10)
        self.screen.blit(glow_surface, (score_rect.x - 10, score_rect.y - 10))
        
        self.screen.blit(score_text, score_rect)
        
        # Draw menu button
        self.menu_button.draw(self.screen)

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == MENU:
                        if self.start_button.rect.collidepoint(mouse_pos):
                            self.start_button.click()
                            self.game_state = MODE_SELECT
                        elif self.controls_button.rect.collidepoint(mouse_pos):
                            self.controls_button.click()
                            self.game_state = CONTROLS
                        elif self.quit_button.rect.collidepoint(mouse_pos):
                            self.quit_button.click()
                            pygame.quit()
                            sys.exit()
                    
                    elif self.game_state == MODE_SELECT:
                        if self.pvp_button.rect.collidepoint(mouse_pos):
                            self.pvp_button.click()
                            self.game_mode = PVP
                            self.game_state = PLAYING
                            self.player.score = 0
                            self.opponent.score = 0
                            self.ball.reset()
                        elif self.pvai_button.rect.collidepoint(mouse_pos):
                            self.pvai_button.click()
                            self.game_mode = PVAI
                            self.game_state = PLAYING
                            self.player.score = 0
                            self.opponent.score = 0
                            self.ball.reset()
                        elif self.back_button.rect.collidepoint(mouse_pos):
                            self.back_button.click()
                            self.game_state = MENU
                    
                    elif self.game_state == GAME_OVER:
                        if self.menu_button.rect.collidepoint(mouse_pos):
                            self.menu_button.click()
                            self.game_state = MENU
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.game_state in [PLAYING, CONTROLS]:
                            self.game_state = MENU

            if self.game_state == MENU:
                self.start_button.check_hover(mouse_pos)
                self.controls_button.check_hover(mouse_pos)
                self.quit_button.check_hover(mouse_pos)
                self.draw_menu()
            
            elif self.game_state == MODE_SELECT:
                self.pvp_button.check_hover(mouse_pos)
                self.pvai_button.check_hover(mouse_pos)
                self.back_button.check_hover(mouse_pos)
                self.draw_mode_select()
            
            elif self.game_state == CONTROLS:
                self.draw_controls()
            
            elif self.game_state == PLAYING:
                # Player 1 movement
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    self.player.move(up=True)
                if keys[pygame.K_DOWN]:
                    self.player.move(up=False)

                # Player 2 or AI movement
                if self.game_mode == PVP:
                    if keys[pygame.K_w]:
                        self.opponent.move(up=True)
                    if keys[pygame.K_s]:
                        self.opponent.move(up=False)
                else:  # AI mode
                    self.opponent.prediction_update_timer += 1
                    
                    if self.ball.dx > 0:
                        if self.opponent.prediction_update_timer >= 10:
                            time_to_reach = (self.opponent.rect.left - self.ball.rect.right) / self.ball.dx
                            predicted_y = self.ball.rect.centery + (self.ball.dy * time_to_reach)
                            predicted_y += random.uniform(-20, 20)
                            predicted_y = max(PADDLE_HEIGHT/2, min(HEIGHT - PADDLE_HEIGHT/2, predicted_y))
                            
                            self.opponent.target_y = (predicted_y + self.opponent.last_prediction) / 2
                            self.opponent.last_prediction = predicted_y
                            self.opponent.prediction_update_timer = 0
                    else:
                        if abs(self.opponent.rect.centery - HEIGHT/2) > 5:
                            self.opponent.target_y = HEIGHT/2
                            self.opponent.last_prediction = HEIGHT/2
                    
                    self.opponent.move_to_target()

                # Move ball
                self.ball.move()

                # Ball collision with paddles
                if self.ball.check_paddle_collision(self.player) or self.ball.check_paddle_collision(self.opponent):
                    pass

                # Scoring
                if self.ball.rect.left <= 0:
                    self.opponent.score += 1
                    self.add_particles(self.ball.rect.centerx, self.ball.rect.centery, RED, 30)
                    self.ball.reset()
                elif self.ball.rect.right >= WIDTH:
                    self.player.score += 1
                    self.add_particles(self.ball.rect.centerx, self.ball.rect.centery, BLUE, 30)
                    self.ball.reset()
                
                # Check for win condition
                if self.player.score >= 10 or self.opponent.score >= 10:
                    self.game_state = GAME_OVER
                
                self.draw_game()
            
            elif self.game_state == GAME_OVER:
                self.menu_button.check_hover(mouse_pos)
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run() 
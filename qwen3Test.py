import pygame
import sys
import math
import random

# Initialisierung
pygame.init()

# Konstanten
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (20, 20, 30)
GRID_COLOR = (40, 40, 50)
SNAKE_COLOR = (50, 200, 100)
FOOD_COLOR = (220, 60, 60)
TEXT_COLOR = (220, 220, 220)
HEX_RADIUS = 20
HEX_WIDTH = HEX_RADIUS * 2
HEX_HEIGHT = HEX_RADIUS * math.sqrt(3)

# Hexagon-Funktionen
def hex_to_pixel(q, r):
    x = HEX_WIDTH * (q + r/2)
    y = HEX_HEIGHT * r
    return (x + WIDTH//2, y + HEIGHT//2)

def pixel_to_hex(x, y):
    q = (x - WIDTH//2) / HEX_WIDTH - (y - HEIGHT//2) / (HEX_HEIGHT * 2)
    r = (y - HEIGHT//2) / HEX_HEIGHT
    return (q, r)

def get_neighbors(q, r):
    directions = [
        (1, 0), (1, -1), (0, -1),
        (-1, 0), (-1, 1), (0, 1)
    ]
    neighbors = []
    for dq, dr in directions:
        neighbors.append((q + dq, r + dr))
    return neighbors

def get_hex_distance(q1, r1, q2, r2):
    return max(abs(q1 - q2), abs(r1 - r2), abs((q1 + r1) - (q2 + r2)))

# Spielklasse
class HexSnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Hex Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

        # Spielzustand
        self.reset_game()

    def reset_game(self):
        self.snake = [(0, 0)]
        self.direction = (1, 0)  # Startrichtung nach rechts
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.speed = 8  # Bewegungsgeschwindigkeit

    def generate_food(self):
        while True:
            q = random.randint(-10, 10)
            r = random.randint(-10, 10)
            if (q, r) not in self.snake:
                return (q, r)

    def move_snake(self):
        if self.game_over:
            return

        head_q, head_r = self.snake[0]
        new_head_q = head_q + self.direction[0]
        new_head_r = head_r + self.direction[1]

        # Kollision mit Wänden (hexagonale Grenzen)
        if get_hex_distance(0, 0, new_head_q, new_head_r) > 15:
            self.game_over = True
            return

        # Kollision mit sich selbst
        if (new_head_q, new_head_r) in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, (new_head_q, new_head_r))

        # Essen aufnehmen
        if (new_head_q, new_head_r) == self.food:
            self.score += 10
            self.food = self.generate_food()
            self.speed = min(self.speed + 0.1, 15)  # Geschwindigkeit erhöhen
        else:
            self.snake.pop()

    def draw_hexagon(self, q, r, color):
        x, y = hex_to_pixel(q, r)
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + HEX_RADIUS * math.cos(angle)
            py = y + HEX_RADIUS * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, (200, 200, 200), points, 1)

    def draw_grid(self):
        # Zeichne Gitter
        for q in range(-20, 20):
            for r in range(-20, 20):
                x, y = hex_to_pixel(q, r)
                if abs(x - WIDTH//2) < WIDTH and abs(y - HEIGHT//2) < HEIGHT:
                    self.draw_hexagon(q, r, GRID_COLOR)

    def draw_snake(self):
        for i, (q, r) in enumerate(self.snake):
            color = SNAKE_COLOR
            if i == 0:  # Kopf
                color = (30, 180, 80)
            self.draw_hexagon(q, r, color)

    def draw_food(self):
        self.draw_hexagon(self.food[0], self.food[1], FOOD_COLOR)

    def draw_score(self):
        score_text = self.font.render(f"Punkte: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("Spiel vorbei!", True, TEXT_COLOR)
        score_text = self.small_font.render(f"Punkte: {self.score}", True, TEXT_COLOR)
        restart_text = self.small_font.render("Drücke R zum Neustart", True, TEXT_COLOR)

        self.screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        self.screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))

    def draw_instructions(self):
        instructions = [
            "Steuerung:",
            "Pfeiltasten: Bewegung",
            "R: Neustart",
            "ESC: Beenden"
        ]

        for i, text in enumerate(instructions):
            text_surface = self.small_font.render(text, True, TEXT_COLOR)
            self.screen.blit(text_surface, (WIDTH - text_surface.get_width() - 10, 10 + i * 30))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    elif not self.game_over:
                        if event.key == pygame.K_UP:
                            self.direction = (0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.direction = (0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.direction = (1, 0)

            # Bewegung
            self.move_snake()

            # Zeichnen
            self.screen.fill(BACKGROUND_COLOR)
            self.draw_grid()
            self.draw_food()
            self.draw_snake()
            self.draw_score()
            self.draw_instructions()

            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(self.speed)

# Hauptprogramm
if __name__ == "__main__":
    game = HexSnakeGame()
    game.run()
    pygame.quit()
    sys.exit()

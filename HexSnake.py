import pygame
import random
import math

# --- Einstellungen ---
BOARD_COLS = 15       # Anzahl der Zellen (Spalten) im Spielfeld
BOARD_ROWS = 15       # Anzahl der Zellen (Zeilen) im Spielfeld
HEX_SIZE = 20         # Radius (Größe) der einzelnen Hexagone in Pixeln
WINDOW_WIDTH = 800    # Fensterbreite
WINDOW_HEIGHT = 600   # Fensterhöhe

# Farben (RGB)
BG_COLOR = (0, 0, 0)
GRID_COLOR = (50, 50, 50)
SNAKE_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (0, 200, 0)
FOOD_COLOR = (255, 0, 0)

# --- Steuerung ---
# Wir verwenden für das Hex-Snake folgende Axialkoordinaten für einen flat-topped Hex:
# Standard-Nachbarn (axial):
#   (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)
# Tastenbelegung:
# Pfeiltasten: Up, Down, Left, Right
# Zusätzlich:
#    E -> Richtung (1, -1) (Up‑right)
#    Q -> Richtung (-1, 1) (Down‑left)
KEY_TO_DIRECTION = {
    pygame.K_RIGHT: (1, 0),
    pygame.K_DOWN:  (0, 1),
    pygame.K_LEFT:  (-1, 0),
    pygame.K_UP:    (0, -1),
    pygame.K_e:     (1, -1),
    pygame.K_q:     (-1, 1)
}

# --- Funktionen zur Umrechnung von Axial- in Pixelkoordinaten und zur Berechnung eines Hexagons ---
def axial_to_pixel(q, r, hex_size):
    """
    Konvertiert Axialkoordinaten (q, r) in Pixelkoordinaten für ein flat-topped Hex.
    Formel: 
      x = hex_size * (3/2 * q)
      y = hex_size * (sqrt(3) * (r + q/2))
    """
    x = hex_size * 1.5 * q
    y = hex_size * math.sqrt(3) * (r + q / 2)
    return (x, y)

def hex_corners(center, hex_size):
    """
    Berechnet die Eckpunkte (als Liste von (x,y)-Tupeln) eines Hexagons,
    das an der Stelle center gezeichnet wird.
    Bei einem flat-topped Hex gehen die Winkel von 0° bis 300° in 60°-Schritten.
    """
    cx, cy = center
    corners = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        x = cx + hex_size * math.cos(angle_rad)
        y = cy + hex_size * math.sin(angle_rad)
        corners.append((x, y))
    return corners

def get_random_food(snake):
    """
    Wählt zufällig eine Zelle (q, r) aus, die nicht vom Snake belegt ist.
    """
    possible = [(q, r) for q in range(BOARD_COLS) for r in range(BOARD_ROWS) if (q, r) not in snake]
    return random.choice(possible) if possible else None

# --- Hauptfunktion ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Hex Snake")
    clock = pygame.time.Clock()

    # Bestimme die Größe des Gitters in Pixeln, um es im Fenster zu zentrieren.
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    for q in range(BOARD_COLS):
        for r in range(BOARD_ROWS):
            x, y = axial_to_pixel(q, r, HEX_SIZE)
            min_x = min(min_x, x - HEX_SIZE)
            max_x = max(max_x, x + HEX_SIZE)
            min_y = min(min_y, y - HEX_SIZE)
            max_y = max(max_y, y + HEX_SIZE)
    grid_width = max_x - min_x
    grid_height = max_y - min_y
    offset_x = (WINDOW_WIDTH - grid_width) / 2 - min_x
    offset_y = (WINDOW_HEIGHT - grid_height) / 2 - min_y

    # Initialisiere die Snake
    snake = [(BOARD_COLS // 2, BOARD_ROWS // 2)]
    current_direction = (1, 0)  # Anfangsrichtung: nach rechts
    food = get_random_food(snake)
    move_delay = 150  # Bewegungstempo in Millisekunden
    last_move_time = pygame.time.get_ticks()
    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in KEY_TO_DIRECTION:
                    new_direction = KEY_TO_DIRECTION[event.key]
                    # Verhindere, dass die Schlange in die entgegengesetzte Richtung fährt
                    if new_direction[0] == -current_direction[0] and new_direction[1] == -current_direction[1]:
                        pass
                    else:
                        current_direction = new_direction
                elif event.key == pygame.K_r and game_over:
                    # Neustart, wenn das Spiel vorbei ist und R gedrückt wird
                    snake = [(BOARD_COLS // 2, BOARD_ROWS // 2)]
                    current_direction = (1, 0)
                    food = get_random_food(snake)
                    game_over = False
                    last_move_time = pygame.time.get_ticks()

        # Aktualisiere den Spielzustand (Bewegung der Snake)
        if not game_over:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > move_delay:
                last_move_time = current_time
                head = snake[0]
                new_head = (head[0] + current_direction[0], head[1] + current_direction[1])
                # Überprüfe, ob die neue Position außerhalb des Spielfelds liegt
                if (new_head[0] < 0 or new_head[0] >= BOARD_COLS or 
                    new_head[1] < 0 or new_head[1] >= BOARD_ROWS):
                    game_over = True
                elif new_head in snake:
                    game_over = True
                else:
                    snake.insert(0, new_head)
                    if food and new_head == food:
                        food = get_random_food(snake)
                    else:
                        snake.pop()

        # Zeichne das Spielfeld
        screen.fill(BG_COLOR)

        # Zeichne das Hex-Gitter (optional)
        for q in range(BOARD_COLS):
            for r in range(BOARD_ROWS):
                x, y = axial_to_pixel(q, r, HEX_SIZE)
                x += offset_x
                y += offset_y
                corners = hex_corners((x, y), HEX_SIZE)
                pygame.draw.polygon(screen, GRID_COLOR, corners, 1)

        # Zeichne das Futter
        if food:
            fq, fr = food
            fx, fy = axial_to_pixel(fq, fr, HEX_SIZE)
            fx += offset_x
            fy += offset_y
            food_corners = hex_corners((fx, fy), HEX_SIZE)
            pygame.draw.polygon(screen, FOOD_COLOR, food_corners)

        # Zeichne die Schlange
        for i, segment in enumerate(snake):
            q, r = segment
            sx, sy = axial_to_pixel(q, r, HEX_SIZE)
            sx += offset_x
            sy += offset_y
            seg_corners = hex_corners((sx, sy), HEX_SIZE)
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_COLOR
            pygame.draw.polygon(screen, color, seg_corners)

        # Zeige Game-Over-Text, falls das Spiel vorbei ist
        if game_over:
            font = pygame.font.SysFont(None, 48)
            text_surface = font.render("Game Over! Drücke R zum Neustarten", True, (255, 255, 255))
            rect = text_surface.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            screen.blit(text_surface, rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()

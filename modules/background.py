# modules/background.py
# Background generator with retro pixel art style

import pygame
from settings import *


def create_retro_background():
    """Create a retro-style background with pixel art."""
    bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Retro gradient sky (purple to dark blue)
    for y in range(SCREEN_HEIGHT):
        progress = y / SCREEN_HEIGHT
        r = int(30 + (70 - 30) * progress)
        g = int(20 + (30 - 20) * progress)
        b = int(60 + (90 - 60) * progress)
        pygame.draw.line(bg, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    # Draw retro grid floor at bottom
    grid_start_y = SCREEN_HEIGHT - 150
    grid_spacing = 40

    # Horizontal grid lines
    for y in range(grid_start_y, SCREEN_HEIGHT, 20):
        alpha = int(100 * ((y - grid_start_y) / 150))
        color = (100 + alpha, 50, 150 + alpha)
        pygame.draw.line(bg, color, (0, y), (SCREEN_WIDTH, y), 2)

    # Vertical grid lines with perspective
    for x in range(0, SCREEN_WIDTH + 40, grid_spacing):
        # Perspective effect
        top_x = x
        bottom_x = SCREEN_WIDTH // 2 + (x - SCREEN_WIDTH // 2) * 1.5
        pygame.draw.line(bg, (150, 50, 200), (top_x, grid_start_y), (int(bottom_x), SCREEN_HEIGHT), 2)

    # Draw pixelated stars
    import random
    random.seed(42)  # Consistent stars
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT // 2)
        size = random.choice([1, 2, 2, 3])
        brightness = random.randint(150, 255)
        pygame.draw.rect(bg, (brightness, brightness, brightness), (x, y, size, size))

    return bg


def draw_retro_platform(surface, rect, color=(200, 100, 255)):
    """Draw a platform with retro pixel art style."""
    # Main platform body with gradient
    for i in range(rect.height):
        shade = 1.0 - (i / rect.height) * 0.3
        line_color = tuple(int(c * shade) for c in color)
        pygame.draw.line(surface, line_color,
                        (rect.x, rect.y + i),
                        (rect.x + rect.width, rect.y + i))

    # Pixel border (retro style)
    border_color = tuple(min(255, c + 50) for c in color)
    pygame.draw.rect(surface, border_color, rect, 3)

    # Inner highlight (top)
    highlight = tuple(min(255, c + 80) for c in color)
    pygame.draw.line(surface, highlight,
                    (rect.x + 3, rect.y + 3),
                    (rect.x + rect.width - 3, rect.y + 3), 2)

    # Pixel decoration on platform
    pixel_size = 4
    for x in range(rect.x + 10, rect.x + rect.width - 10, 20):
        pygame.draw.rect(surface, border_color, (x, rect.y + 5, pixel_size, pixel_size))


# modules/menu_background.py
# Menu background generator with retro arcade style

import pygame
import math


def create_menu_background(width, height):
    """Create an animated retro menu background."""
    bg = pygame.Surface((width, height))

    # Deep space gradient
    for y in range(height):
        progress = y / height
        r = int(10 + (30 - 10) * progress)
        g = int(5 + (15 - 5) * progress)
        b = int(40 + (70 - 40) * progress)
        pygame.draw.line(bg, (r, g, b), (0, y), (width, y))

    return bg


def draw_animated_stars(surface, time_offset):
    """Draw twinkling stars."""
    import random
    random.seed(42)
    width, height = surface.get_size()

    for i in range(150):
        x = random.randint(0, width)
        y = random.randint(0, height)

        # Twinkling effect
        twinkle = abs(math.sin(time_offset * 2 + i * 0.1))
        brightness = int(150 + 105 * twinkle)
        size = random.choice([1, 1, 2, 2, 3])

        color = (brightness, brightness, brightness)
        pygame.draw.rect(surface, color, (x, y, size, size))


def draw_grid_lines(surface, time_offset):
    """Draw animated grid lines like retro games."""
    width, height = surface.get_size()

    # Horizontal lines moving down
    for i in range(20):
        y = int((i * 40 + time_offset * 50) % height)
        alpha = int(100 - (y / height) * 80)
        color = (100, 50, 200)
        pygame.draw.line(surface, color, (0, y), (width, y), 2)

    # Vertical lines with perspective
    for i in range(15):
        x = i * 100
        # Perspective effect
        top_offset = (x - width // 2) * 0.3
        pygame.draw.line(surface, (80, 40, 180),
                        (int(x + top_offset), height // 2),
                        (x, height), 2)


def draw_menu_particles(surface, particles, dt):
    """Draw and update particle effects."""
    import random

    width, height = surface.get_size()

    # Update particles
    for particle in particles[:]:
        particle['y'] -= particle['speed'] * dt
        particle['x'] += particle['drift'] * dt
        particle['life'] -= dt

        if particle['life'] <= 0 or particle['y'] < -10:
            particles.remove(particle)
        else:
            # Draw particle
            alpha = int(255 * (particle['life'] / particle['max_life']))
            size = particle['size']
            color = (*particle['color'], min(alpha, 255))

            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (size // 2, size // 2), size // 2)
            surface.blit(surf, (int(particle['x']), int(particle['y'])))

    # Add new particles
    if random.random() < 0.3:
        particles.append({
            'x': random.randint(0, width),
            'y': height + 10,
            'speed': random.uniform(30, 80),
            'drift': random.uniform(-20, 20),
            'life': random.uniform(3, 6),
            'max_life': 6,
            'size': random.randint(2, 5),
            'color': random.choice([
                (0, 255, 255),  # Cyan
                (255, 0, 255),  # Magenta
                (255, 255, 0),  # Yellow
                (0, 255, 0),    # Green
            ])
        })


# modules/sprite_generator.py
# Generate retro pixel art character sprites

import pygame


def create_retro_character_sprite(color, size=(40, 60)):
    """Create a retro pixel art character sprite."""
    sprite = pygame.Surface(size, pygame.SRCALPHA)
    width, height = size

    # Define pixel art character (8-bit style)
    # Head (top third)
    head_color = tuple(min(255, c + 30) for c in color)
    pygame.draw.rect(sprite, head_color, (width//4, 5, width//2, height//4))

    # Eyes (white with black pupils)
    eye_size = 4
    pygame.draw.rect(sprite, (255, 255, 255), (width//3 - 2, 12, eye_size, eye_size))
    pygame.draw.rect(sprite, (255, 255, 255), (2*width//3 - 2, 12, eye_size, eye_size))
    pygame.draw.rect(sprite, (0, 0, 0), (width//3, 14, 2, 2))
    pygame.draw.rect(sprite, (0, 0, 0), (2*width//3, 14, 2, 2))

    # Body (middle section)
    body_y = height//4 + 5
    pygame.draw.rect(sprite, color, (width//4 - 2, body_y, width//2 + 4, height//2))

    # Arms
    arm_color = tuple(max(0, c - 20) for c in color)
    pygame.draw.rect(sprite, arm_color, (5, body_y + 5, 8, 15))  # Left arm
    pygame.draw.rect(sprite, arm_color, (width - 13, body_y + 5, 8, 15))  # Right arm

    # Legs
    leg_y = body_y + height//2
    pygame.draw.rect(sprite, arm_color, (width//3 - 3, leg_y, 8, height//4))  # Left leg
    pygame.draw.rect(sprite, arm_color, (2*width//3 - 5, leg_y, 8, height//4))  # Right leg

    # Add pixel border for definition
    pygame.draw.rect(sprite, (0, 0, 0), sprite.get_rect(), 2)

    return sprite


def create_retro_weapon_sprite(weapon_name, color, size=30):
    """Create retro pixel art weapon sprite."""
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)

    # Simple sword sprite
    if 'sword' in weapon_name.lower():
        # Blade
        pygame.draw.rect(sprite, (200, 200, 220), (size//2 - 2, 5, 4, size - 15))
        # Handle
        pygame.draw.rect(sprite, color, (size//2 - 3, size - 12, 6, 8))
        # Guard
        pygame.draw.rect(sprite, (150, 150, 150), (size//2 - 6, size - 15, 12, 3))

    # Hammer sprite
    elif 'hammer' in weapon_name.lower():
        # Handle
        pygame.draw.rect(sprite, (139, 69, 19), (size//2 - 2, 10, 4, size - 15))
        # Head
        pygame.draw.rect(sprite, color, (size//4, 5, size//2, 10))

    # Axe sprite
    elif 'axe' in weapon_name.lower():
        # Handle
        pygame.draw.rect(sprite, (139, 69, 19), (size//2 - 2, 8, 4, size - 12))
        # Blade
        points = [(size//4, 8), (3*size//4, 8), (size//2, 15)]
        pygame.draw.polygon(sprite, color, points)

    # Spear sprite
    elif 'spear' in weapon_name.lower():
        # Shaft
        pygame.draw.rect(sprite, (139, 69, 19), (size//2 - 1, 8, 2, size - 10))
        # Tip
        points = [(size//2, 3), (size//2 - 4, 10), (size//2 + 4, 10)]
        pygame.draw.polygon(sprite, color, points)

    # Default energy ball
    else:
        pygame.draw.circle(sprite, color, (size//2, size//2), size//3)
        pygame.draw.circle(sprite, (255, 255, 255), (size//2, size//2), size//5)

    return sprite


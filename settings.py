# settings.py
# Global settings and constants for Prompt Wars
import pygame

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Player settings
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 5
JUMP_STRENGTH = 15
GRAVITY = 0.8
MAX_HEALTH = 100

# Platform settings
PLATFORM_COLOR = (100, 100, 100)

# Game settings
ROUND_TIME = 180  # 3 minutes in seconds
RESPAWN_TIME = 3  # seconds
MAX_PLAYERS = 4

# UI settings
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
UI_FONT_SIZE = 24
TIMER_FONT_SIZE = 48
INPUT_BOX_WIDTH = 400
INPUT_BOX_HEIGHT = 40

# Weapon settings
WEAPON_COOLDOWN = 5  # seconds between weapon forges

# Platform definitions - created after pygame init
def get_platforms():
    """Return list of platform rectangles."""
    import pygame
    return [
        pygame.Rect(200, 500, 300, 30),
        pygame.Rect(700, 500, 300, 30),
        pygame.Rect(450, 350, 200, 30),
        pygame.Rect(100, 250, 150, 30),
        pygame.Rect(900, 250, 150, 30),
    ]

PLATFORMS = [
    pygame.Rect(291, 468, 835, 46),
    pygame.Rect(1122, 494, 116, 16),
    pygame.Rect(1128, 476, 62, 18),
    pygame.Rect(150, 491, 139, 20),
    pygame.Rect(213, 472, 76, 17),
] # Will be initialized in main.py

# settings.py
# Global settings and constants for Prompt Wars
import pygame

# Screen settings - Resizable window
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
FULLSCREEN = False  # Start in windowed mode

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)

# Additional colors for game
DANGER_RED = (255, 50, 80)
SUCCESS_GREEN = (50, 255, 150)
WARNING_YELLOW = (255, 220, 50)
INFO_BLUE = (80, 180, 255)
LIGHT_GRAY = (180, 180, 200)

# Player movement constants (for enhanced player.py)
PLAYER_MOVE_SPEED = 6.5
PLAYER_AIR_SPEED = 5.5
PLAYER_JUMP_POWER = 16
PLAYER_DOUBLE_JUMP = True
PLAYER_MAX_HEALTH = 100
PLAYER_RESPAWN_TIME = 3.5
PLAYER_INVULN_TIME = 2.0
PLAYER_HIT_STUN = 0.15

# Physics
GRAVITY_STRENGTH = 0.7
MAX_VELOCITY_Y = 18
FRICTION_GROUND = 0.75
FRICTION_AIR = 0.92

# Visual effects
HIT_FLASH_DURATION = 0.12

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

# Audio settings
AUDIO_ICON_SIZE = 50  # Larger for better visibility
AUDIO_BUTTON_POS = (20, 100)  # Position for audio button

# Fullscreen button settings
FULLSCREEN_BUTTON_POS = (20, 160)  # Below audio button
FULLSCREEN_BUTTON_SIZE = 50

# Platform definitions - FIXED positions that match your background
# These are the exact coordinates you set in the platform editor
PLATFORMS = [
    pygame.Rect(291, 468, 835, 46),
    pygame.Rect(1122, 494, 116, 16),
    pygame.Rect(1128, 476, 62, 18),
    pygame.Rect(150, 491, 139, 20),
    pygame.Rect(213, 472, 76, 17),
]

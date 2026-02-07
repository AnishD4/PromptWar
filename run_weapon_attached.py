"""
Run a small Pygame demo that shows a player with a weapon attached.
Controls:
  A/D or Left/Right - move player
  W/Up - jump
  ESC or close window - quit

This script uses the existing Player and Weapon classes from modules/

This version adds debug drawing and on-screen FPS/position info so you can
confirm the weapon is attached and visible.
"""
import pygame
from modules.player import Player
from modules.weapon import Weapon
from modules.ai_client import AIClient
from settings import *

DEBUG = True
SHOW_DEBUG_BG = True

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Weapon Attached Demo')

print("Weapon attached demo starting. If you don't see a window, ensure it's not minimized or behind other windows.")

# Create a player near center
# We'll place a ground platform and put the player on it
platform_y = SCREEN_HEIGHT // 2 + 80
platform = pygame.Rect(SCREEN_WIDTH//3 - 150, platform_y, 300, 20)
platforms = [platform]

player = Player(0, platform.x + 60, platform.y - PLAYER_HEIGHT, BLUE)

# Create a sample weapon (will be attached to player)
weapon_data = {
    'name': 'Test Sword',
    'damage': 12,
    'knockback': 6,
    'size': 40,
    'speed': 0,
    'color': (200, 200, 255)
}
weapon = Weapon(weapon_data, owner_id=0, x=0, y=0)
weapon_attached = True
# tweak the hand offset so the weapon sits near player's right-hand
hand_offset = (8, 6)  # x,y offset from player's center

font = pygame.font.Font(None, 24)

# Create AI client and set callback
ai = AIClient()

# When AI spawns weapon, equip to our demo player
def _on_spawn(weapon_data, player_id):
    # create and equip
    w = Weapon(weapon_data, player_id, player.rect.centerx, player.rect.centery)
    # Make the weapon larger for visibility in the demo
    try:
        w.size = int(w.size * 1.6)
    except Exception:
        pass
    player.equip_weapon(w)
    print('AI spawned weapon:', weapon_data.get('name'))

ai.set_weapon_spawned_callback(_on_spawn)

# Auto-forge a weapon once at startup so demo shows immediate result
ai.forge_weapon('flaming sword', 0)

running = True
frame = 0
last_screenshot_time = 0.0
while running:
    dt = clock.tick(FPS) / 1000.0
    frame += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_f:
                print('Forging weapon: flaming sword...')
                ai.forge_weapon('flaming sword', 0)

    keys = pygame.key.get_pressed()
    # Movement
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player.move(-1)
    elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player.move(1)
    else:
        player.velocity_x = 0
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player.jump()

    # Update player physics (no platforms for demo)
    player.update(platforms, dt)

    # Attach weapon to player hand
    if weapon_attached:
        wx = player.rect.centerx + hand_offset[0] - weapon.rect.width // 2
        wy = player.rect.centery + hand_offset[1] - weapon.rect.height // 2
        weapon.rect.x = int(wx)
        weapon.rect.y = int(wy)
        weapon.velocity_x = 0
        weapon.velocity_y = 0

    # Draw
    screen.fill((30, 40, 30))  # dark background so sprites pop

    if SHOW_DEBUG_BG:
        dbg_rect = pygame.Rect(SCREEN_WIDTH//2 - 220, SCREEN_HEIGHT//2 - 140, 440, 280)
        pygame.draw.rect(screen, (20, 20, 20), dbg_rect)
        pygame.draw.rect(screen, (80, 80, 80), dbg_rect, 2)

    # draw player (which will draw equipped weapon if any)
    player.draw(screen)

    # Draw platform
    pygame.draw.rect(screen, (100, 100, 100), platform)
    pygame.draw.rect(screen, WHITE, platform, 2)

    # Debug overlays
    if DEBUG:
        # Draw rect outlines
        pygame.draw.rect(screen, (255, 255, 0), player.rect, 1)
        pygame.draw.rect(screen, (0, 255, 255), weapon.rect, 1)

        # On-screen text
        fps_text = font.render(f'FPS: {int(clock.get_fps())}', True, WHITE)
        ppos_text = font.render(f'Player: ({player.rect.x}, {player.rect.y})', True, WHITE)
        wpos_text = font.render(f'Weapon: ({weapon.rect.x}, {weapon.rect.y})', True, WHITE)
        screen.blit(fps_text, (10, 8))
        screen.blit(ppos_text, (10, 30))
        screen.blit(wpos_text, (10, 52))

    # small HUD
    text = font.render('Move: A/D or Arrow keys. Press ESC to quit.', True, WHITE)
    screen.blit(text, (10, SCREEN_HEIGHT - 30))

    pygame.display.flip()

    # Print periodic console info so the user sees activity in terminal and save screenshot
    if frame % max(1, int(FPS)) == 0:
        now = pygame.time.get_ticks() / 1000.0
        print(f'FPS={int(clock.get_fps())} Player=({player.rect.x},{player.rect.y}) Weapon=({weapon.rect.x},{weapon.rect.y})')
        # Save screenshot once per second
        if now - last_screenshot_time >= 1.0:

            last_screenshot_time = now

pygame.quit()

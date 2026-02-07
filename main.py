# main.py
# Main game loop for Prompt Wars

import pygame
import sys
import settings
from settings import *
from modules.player import Player
from modules.weapon import Weapon
from modules.ui import UI
from modules.ai_client import AIClient
from modules.game_manager import GameManager
from modules.menu import MenuScreen


def show_menu(screen):
    """Display menu and wait for user choice."""
    menu = MenuScreen(screen)
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT", None

            result = menu.handle_event(event)
            if result == "QUIT":
                return "QUIT", None
            elif result == "START_GAME":
                return "START_GAME", menu.room_name
            elif result == "JOIN_GAME":
                return "JOIN_GAME", menu.room_code

        menu.update(dt)
        menu.draw()
        pygame.display.flip()

    return "QUIT", None


def run_game(room_info=None):
    """Run the main game."""
    # Initialize platforms BEFORE creating game objects
    settings.PLATFORMS = get_platforms()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PROMPT WARS - Retro Edition")
    clock = pygame.time.Clock()

    # Load custom background image
    try:
        background = pygame.image.load("backgrounds/bg.png")
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print("✓ Custom background loaded successfully!")
    except Exception as e:
        print(f"✗ Could not load background: {e}")
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill((50, 30, 80))

    # Initialize game systems
    game_manager = GameManager()
    ui = UI(screen)
    ai_client = AIClient()

    # Display room info if available
    if room_info:
        ui.add_notification(f"ROOM: {room_info}", 5.0, (0, 255, 255))

    # Create players with retro colors
    player_colors = [(0, 200, 255), (255, 80, 180), (0, 255, 100), (255, 200, 0)]
    for i in range(2):
        spawn_x, spawn_y = game_manager.spawn_points[i]
        player = Player(i, spawn_x, spawn_y, player_colors[i])
        player.set_health_changed_callback(ui.health_changed)
        ui.register_player(i, player_colors[i])
        game_manager.add_player(player)

    # Connect AI weapon spawned events to UI
    def on_weapon_spawned(weapon_data, player_id):
        player = game_manager.players[player_id]
        spawn_x = player.rect.centerx
        spawn_y = player.rect.centery
        weapon = Weapon(weapon_data, player_id, spawn_x, spawn_y)
        game_manager.add_weapon(weapon)
        ui.weapon_spawned(weapon_data['name'], player_id)

    ai_client.set_weapon_spawned_callback(on_weapon_spawned)

    def on_forge_weapon(prompt, player_id):
        ai_client.forge_weapon(prompt, player_id)

    ui.set_forge_weapon_callback(on_forge_weapon)
    game_manager.start_round()

    # Game loop
    running = True
    current_player = 0

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not ui.handle_event(event, current_player):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        current_player = (current_player + 1) % len(game_manager.players)
                    elif event.key == pygame.K_ESCAPE:
                        return "MENU"

        keys = pygame.key.get_pressed()

        if len(game_manager.players) > 0:
            p0 = game_manager.players[0]
            if keys[pygame.K_a]:
                p0.move(-1)
            elif keys[pygame.K_d]:
                p0.move(1)
            else:
                p0.velocity_x = 0
            if keys[pygame.K_w]:
                p0.jump()

        if len(game_manager.players) > 1:
            p1 = game_manager.players[1]
            if keys[pygame.K_LEFT]:
                p1.move(-1)
            elif keys[pygame.K_RIGHT]:
                p1.move(1)
            else:
                p1.velocity_x = 0
            if keys[pygame.K_UP]:
                p1.jump()

        game_manager.update(dt)
        ui.update(dt)

        if ui.time_remaining <= 0:
            game_manager.end_round()
            ui.reset_timer()
            ui.add_notification("ROUND OVER! NEW ROUND STARTING...", 3.0, WHITE)
            pygame.time.delay(3000)
            game_manager.start_round()

        screen.blit(background, (0, 0))
        game_manager.draw_weapons(screen)
        game_manager.draw_players(screen)
        ui.draw(screen)

        indicator_text = ui.small_font.render(f"<< P{current_player + 1} FORGING >> [TAB]", True, (0, 255, 255))
        screen.blit(indicator_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 115))

        esc_text = ui.small_font.render("[ESC] MENU", True, (100, 100, 100))
        screen.blit(esc_text, (10, 10))

        pygame.display.flip()

    return "QUIT"


def main():
    """Main entry point."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    while True:
        action, room_info = show_menu(screen)

        if action == "QUIT":
            break

        elif action == "START_GAME":
            result = run_game(room_info)
            if result == "QUIT":
                break

        elif action == "JOIN_GAME":
            result = run_game(f"CODE: {room_info}")
            if result == "QUIT":
                break

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()

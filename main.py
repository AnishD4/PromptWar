# main.py
# Main game loop for Prompt Wars

import pygame
import sys
from settings import *
from modules.player import Player
from modules.weapon import Weapon
from modules.ui import UI
from modules.ai_client import AIClient
from modules.game_manager import GameManager


def main():
    """Main game loop."""
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Prompt Wars")
    clock = pygame.time.Clock()

    # Initialize game systems
    game_manager = GameManager()
    ui = UI(screen)
    ai_client = AIClient()

    # Create players
    player_colors = [BLUE, RED, GREEN, YELLOW]
    for i in range(2):  # Start with 2 players for testing
        spawn_x, spawn_y = game_manager.spawn_points[i]
        player = Player(i, spawn_x, spawn_y, player_colors[i])

        # Connect player health events to UI
        player.set_health_changed_callback(ui.health_changed)

        # Register player with UI and game manager
        ui.register_player(i, player_colors[i])
        game_manager.add_player(player)

    # Connect AI weapon spawned events to UI
    def on_weapon_spawned(weapon_data, player_id):
        """Callback when weapon is forged."""
        # Find player position to spawn weapon
        player = game_manager.players[player_id]
        spawn_x = player.rect.centerx
        spawn_y = player.rect.centery

        # Create and add weapon
        weapon = Weapon(weapon_data, player_id, spawn_x, spawn_y)
        game_manager.add_weapon(weapon)

        # Notify UI
        ui.weapon_spawned(weapon_data['name'], player_id)

    ai_client.set_weapon_spawned_callback(on_weapon_spawned)

    # Connect UI forge button to AI client
    def on_forge_weapon(prompt, player_id):
        """Callback when player clicks forge button."""
        ai_client.forge_weapon(prompt, player_id)

    ui.set_forge_weapon_callback(on_forge_weapon)

    # Start first round
    game_manager.start_round()

    # Game loop
    running = True
    current_player = 0  # For UI input (which player is forging)

    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Let UI handle events first
            if not ui.handle_event(event, current_player):
                # Handle other game events here
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        # Switch active player for weapon forging
                        current_player = (current_player + 1) % len(game_manager.players)

        # Handle player input (movement)
        keys = pygame.key.get_pressed()

        # Player 0 controls (WASD)
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

        # Player 1 controls (Arrow keys)
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

        # Update game state
        game_manager.update(dt)
        ui.update(dt)

        # Check if round should end
        if ui.time_remaining <= 0:
            game_manager.end_round()
            ui.reset_timer()
            ui.add_notification("Round Over! Starting new round...", 3.0)
            pygame.time.delay(3000)
            game_manager.start_round()

        # Draw everything
        screen.fill(BLACK)

        # Draw game elements
        game_manager.draw_platforms(screen)
        game_manager.draw_weapons(screen)
        game_manager.draw_players(screen)

        # Draw UI on top
        ui.draw(screen)

        # Draw current player indicator
        indicator_text = ui.font.render(f"Forging Player: {current_player} (TAB to switch)", True, WHITE)
        screen.blit(indicator_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 140))

        # Update display
        pygame.display.flip()

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()

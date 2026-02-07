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
from modules.audio_manager import AudioManager
from modules.network import GameClient, start_server, get_local_ip


def show_menu(screen, audio_manager):
    """Display menu and wait for user choice."""
    menu = MenuScreen(screen)
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT", None, None

            # Handle audio button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                audio_manager.handle_click(event.pos)

            result = menu.handle_event(event)
            if result == "QUIT":
                return "QUIT", None, None
            elif result == "START_GAME":
                return "START_GAME", menu.room_name, None
            elif result == "JOIN_GAME":
                return "JOIN_GAME", menu.room_code, menu.server_ip

        menu.update(dt)
        menu.draw()

        # Draw audio button
        audio_manager.draw(screen)

        pygame.display.flip()

    return "QUIT", None, None


def run_game(room_info=None, audio_manager=None, is_host=False, network_client=None):
    """Run the main game."""
    # Use resizable window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("PROMPT WARS - Retro Edition")
    clock = pygame.time.Clock()

    # Store original dimensions for scaling
    ORIGINAL_WIDTH = 1280
    ORIGINAL_HEIGHT = 720

    # Load custom background image (keep original for scaling)
    try:
        background_original = pygame.image.load("backgrounds/bg.png")
        background = pygame.transform.scale(background_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print("✓ Custom background loaded successfully!")
    except Exception as e:
        print(f"✗ Could not load background: {e}")
        background_original = None
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill((50, 30, 80))

    # Multiplayer setup
    is_multiplayer = network_client is not None and network_client.connected
    local_player_id = 0 if is_host else 1

    # Initialize game systems
    game_manager = GameManager()
    ui = UI(screen)
    ai_client = AIClient()

    # Display room info if available
    if room_info:
        ui.add_notification(f"ROOM: {room_info}", 5.0, (0, 255, 255))
    
    if is_multiplayer:
        status = "HOST" if is_host else "CLIENT"
        ui.add_notification(f"MULTIPLAYER: {status}", 3.0, (0, 255, 0))

    # Create players with retro colors
    player_colors = [(0, 200, 255), (255, 80, 180), (0, 255, 100), (255, 200, 0)]
    
    # Create 2 players for multiplayer games
    num_initial_players = 2
    
    for i in range(num_initial_players):
        spawn_x, spawn_y = game_manager.spawn_points[i]
        player = Player(i, spawn_x, spawn_y, player_colors[i])
        player.set_health_changed_callback(ui.health_changed)
        ui.register_player(i, player_colors[i])
        game_manager.add_player(player)

    # Connect AI weapon spawned events to UI
    def on_weapon_spawned(weapon_data, player_id):
        if player_id < len(game_manager.players):
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
    current_player = local_player_id if is_multiplayer else 0
    current_screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    network_update_timer = 0

    while running:
        dt = clock.tick(FPS) / 1000.0
        network_update_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle window resize
            elif event.type == pygame.VIDEORESIZE:
                current_screen_size = (event.w, event.h)
                screen = pygame.display.set_mode(current_screen_size, pygame.RESIZABLE)

                # Calculate scale factors
                scale_x = current_screen_size[0] / ORIGINAL_WIDTH
                scale_y = current_screen_size[1] / ORIGINAL_HEIGHT

                # Rescale background
                if background_original:
                    background = pygame.transform.scale(background_original, current_screen_size)
                else:
                    background = pygame.Surface(current_screen_size)
                    background.fill((50, 30, 80))

                # Scale platforms to match background
                settings.PLATFORMS = []
                original_platforms = [
                    pygame.Rect(291, 468, 835, 46),
                    pygame.Rect(1122, 494, 116, 16),
                    pygame.Rect(1128, 476, 62, 18),
                    pygame.Rect(150, 491, 139, 20),
                    pygame.Rect(213, 472, 76, 17),
                ]
                for plat in original_platforms:
                    scaled_plat = pygame.Rect(
                        int(plat.x * scale_x),
                        int(plat.y * scale_y),
                        int(plat.width * scale_x),
                        int(plat.height * scale_y)
                    )
                    settings.PLATFORMS.append(scaled_plat)

            # Handle audio button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                audio_manager.handle_click(event.pos)

            if not ui.handle_event(event, current_player):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB and not is_multiplayer:
                        current_player = (current_player + 1) % len(game_manager.players)
                    elif event.key == pygame.K_ESCAPE:
                        if is_multiplayer and network_client:
                            network_client.disconnect()
                        return "MENU"

        keys = pygame.key.get_pressed()

        # Control local player
        if len(game_manager.players) > local_player_id:
            p = game_manager.players[local_player_id]
            
            # Player 0 controls (host or single player)
            if local_player_id == 0:
                if keys[pygame.K_a]:
                    p.move(-1)
                elif keys[pygame.K_d]:
                    p.move(1)
                else:
                    p.velocity_x = 0
                if keys[pygame.K_w]:
                    p.jump()
            # Player 1 controls (client in multiplayer)
            else:
                if keys[pygame.K_LEFT]:
                    p.move(-1)
                elif keys[pygame.K_RIGHT]:
                    p.move(1)
                else:
                    p.velocity_x = 0
                if keys[pygame.K_UP]:
                    p.jump()

        # Non-local player controls (for single player mode with 2 players)
        if not is_multiplayer:
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

        # Send network updates
        if is_multiplayer and network_update_timer >= 0.033:  # ~30 updates per second
            network_update_timer = 0
            if local_player_id < len(game_manager.players):
                player = game_manager.players[local_player_id]
                network_client.send_update({
                    'x': player.rect.x,
                    'y': player.rect.y,
                    'vx': player.velocity_x,
                    'vy': player.velocity_y,
                    'health': player.health,
                    'alive': player.alive
                })
            
            # Receive network updates
            remote_state = network_client.get_game_state()
            if remote_state:
                # Update remote player
                remote_player_id = 1 - local_player_id
                if remote_player_id < len(game_manager.players):
                    remote_player = game_manager.players[remote_player_id]
                    remote_player.rect.x = remote_state.get('x', remote_player.rect.x)
                    remote_player.rect.y = remote_state.get('y', remote_player.rect.y)
                    remote_player.velocity_x = remote_state.get('vx', remote_player.velocity_x)
                    remote_player.velocity_y = remote_state.get('vy', remote_player.velocity_y)
                    if 'health' in remote_state:
                        remote_player.health = remote_state['health']
                    if 'alive' in remote_state:
                        remote_player.alive = remote_state['alive']

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

        # Dynamic positioning for text
        if is_multiplayer:
            player_text = f"<< YOU ARE P{local_player_id + 1} >>"
        else:
            player_text = f"<< P{current_player + 1} FORGING >> [TAB]"
        indicator_text = ui.small_font.render(player_text, True, (0, 255, 255))
        screen.blit(indicator_text, (current_screen_size[0] // 2 - 100, current_screen_size[1] - 115))

        esc_text = ui.small_font.render("[ESC] MENU", True, (100, 100, 100))
        screen.blit(esc_text, (10, 10))

        # Draw audio button
        audio_manager.draw(screen)

        pygame.display.flip()

    if is_multiplayer and network_client:
        network_client.disconnect()
    
    return "QUIT"


def main():
    """Main entry point."""
    pygame.init()

    # Create resizable window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("PROMPT WARS - Retro Edition")

    # Initialize audio manager only (no fullscreen button)
    audio_manager = AudioManager()

    # Load and play background music
    if audio_manager.load_music("assets/sounds/bgaudio.mp3"):
        audio_manager.play_music(loops=-1)
        print("✓ Background music loaded and playing!")
    else:
        print("✗ Could not load background music")

    while True:
        action, room_info, server_ip = show_menu(screen, audio_manager)

        if action == "QUIT":
            break

        elif action == "START_GAME":
            # Host a game - start server
            print(f"\n=== HOSTING GAME: {room_info} ===")
            if start_server():
                local_ip = get_local_ip()
                print(f"✓ Server started! Share this IP: {local_ip}")
                print(f"✓ Room Code: {room_info}")
                
                # Create network client and connect to own server
                network_client = GameClient()
                if network_client.connect(local_ip):
                    if network_client.create_room(room_info):
                        print("✓ Room created successfully!")
                        print("✓ Waiting for other players to join...")
                        result = run_game(room_info, audio_manager, is_host=True, network_client=network_client)
                        network_client.disconnect()
                    else:
                        print("✗ Failed to create room")
                        result = "MENU"
                else:
                    print("✗ Failed to connect to own server")
                    result = "MENU"
            else:
                print("✗ Failed to start server")
                result = "MENU"
            
            if result == "QUIT":
                break

        elif action == "JOIN_GAME":
            # Join a game - connect to server
            print(f"\n=== JOINING GAME: {room_info} ===")
            print(f"Connecting to server at: {server_ip}")
            
            network_client = GameClient()
            if network_client.connect(server_ip):
                if network_client.join_room(room_info):
                    print("✓ Joined room successfully!")
                    result = run_game(f"{room_info}", audio_manager, is_host=False, network_client=network_client)
                    network_client.disconnect()
                else:
                    print("✗ Failed to join room - check room code")
                    result = "MENU"
            else:
                print("✗ Failed to connect to server - check IP address")
                result = "MENU"
            
            if result == "QUIT":
                break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

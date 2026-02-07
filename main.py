# main.py
# Main game loop for Prompt Wars

import pygame
import sys
import time
import os
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
from modules.lobby import LobbyScreen


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
            elif result == "CREATE_LOBBY":
                return "CREATE_LOBBY", menu.room_name, None
            elif result == "JOIN_GAME":
                return "JOIN_GAME", menu.room_code, menu.server_ip

        menu.update(dt)
        menu.draw()

        # Draw audio button
        audio_manager.draw(screen)

        pygame.display.flip()

    return "QUIT", None, None


def show_lobby(screen, audio_manager, network_client, room_name, is_host):
    """Display lobby and wait for players."""
    lobby = LobbyScreen(screen, network_client, room_name, is_host)
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            # Handle audio button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                audio_manager.handle_click(event.pos)

                # Dismiss error popup on click
                if lobby.error_timer > 0:
                    lobby.error_timer = 0
                    lobby.error_message = ""

            result = lobby.handle_event(event)
            if result == "START":
                return "START"
            elif result == "CANCEL" or result == "LEAVE":
                return "CANCEL"

        # Check if lobby.update() returns START (for clients when host starts game)
        update_result = lobby.update(dt)
        if update_result == "START":
            print("✓ Received start signal from host!")
            return "START"

        lobby.draw()

        # Draw audio button
        audio_manager.draw(screen)

        pygame.display.flip()

    return "QUIT"


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

    # Multiplayer setup - ensure proper player ID assignment
    is_multiplayer = network_client is not None and network_client.connected

    # IMPORTANT: Use the player_id from the network client
    if is_multiplayer and network_client.player_id is not None:
        local_player_id = network_client.player_id
        print(f"✓ Assigned as Player {local_player_id + 1}")
    else:
        local_player_id = 0  # Single player defaults to P1

    # Initialize game systems
    game_manager = GameManager()
    ui = UI(screen)
    ai_client = AIClient()

    # Display room info if available
    if room_info:
        ui.add_notification(f"ROOM: {room_info}", 5.0, (0, 255, 255))

    if is_multiplayer:
        status = f"PLAYER {local_player_id + 1}"
        ui.add_notification(f"YOU ARE {status}", 3.0, (0, 255, 0))

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
    forged_players = set()

    def on_weapon_spawned(weapon_data, player_id):
        # Attach forged weapon visually to the player (equip)
        if player_id < len(game_manager.players):
            player = game_manager.players[player_id]
            spawn_x = player.rect.centerx
            spawn_y = player.rect.centery
            weapon = Weapon(weapon_data, player_id, spawn_x, spawn_y)
            try:
                # equip to player (visual)
                player.equip_weapon(weapon)
                forged_players.add(player_id)
            except Exception:
                # Fallback: add to game world if equip fails
                game_manager.add_weapon(weapon)
                forged_players.add(player_id)
        ui.weapon_spawned(weapon_data.get('name', 'Unknown'), player_id)

    ai_client.set_weapon_spawned_callback(on_weapon_spawned)

    def on_forge_weapon(prompt, player_id):
        ai_client.forge_weapon(prompt, player_id)

    ui.set_forge_weapon_callback(on_forge_weapon)

    # PRE-GAME: wait for all players to forge weapons (20s timeout)
    wait_seconds = 20.0
    wait_start = pygame.time.get_ticks() / 1000.0
    num_players = len(game_manager.players)
    ui.add_notification('Waiting for players to forge weapons...', 5.0, (0, 255, 255))
    # Simple blocking wait loop that still processes UI events so players can type prompts
    waiting = True
    while waiting:
        dt = clock.tick(FPS) / 1000.0
        now = pygame.time.get_ticks() / 1000.0
        elapsed = now - wait_start
        remaining = max(0.0, wait_seconds - elapsed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            # allow UI to handle input events (forge)
            ui.handle_event(event, 0)

        ui.update(dt)

        # Draw a waiting screen
        screen.blit(background, (0, 0))
        game_manager.draw_players(screen)
        ui.draw(screen)
        # draw countdown
        countdown_text = ui.small_font.render(f"Forge weapons: {int(remaining)}s", True, (255, 200, 0))
        screen.blit(countdown_text, (SCREEN_WIDTH // 2 - 80, 20))
        pygame.display.flip()

        # Check if all players forged
        if len(forged_players) >= num_players:
            waiting = False
            break

        if remaining <= 0.0:
            ui.add_notification('Timeout: not all players forged weapons. Closing...', 3.0, (255, 0, 0))
            pygame.time.delay(1500)
            return "QUIT"

    # Start the round once all players have forged
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

        # Control local player with enhanced controls
        if len(game_manager.players) > local_player_id:
            p = game_manager.players[local_player_id]

            # Player 0 controls (host or single player)
            if local_player_id == 0:
                # Movement
                if keys[pygame.K_a]:
                    p.move(-1)
                elif keys[pygame.K_d]:
                    p.move(1)
                else:
                    p.stop_move()

                # Jump
                if keys[pygame.K_w]:
                    p.jump()

                # Attack (new mechanic!)
                if keys[pygame.K_f]:
                    p.attack(Player.ATTACK_SWING)

            # Player 1 controls (client in multiplayer)
            else:
                # Movement
                if keys[pygame.K_LEFT]:
                    p.move(-1)
                elif keys[pygame.K_RIGHT]:
                    p.move(1)
                else:
                    p.stop_move()

                # Jump
                if keys[pygame.K_UP]:
                    p.jump()

                # Attack (new mechanic!)
                if keys[pygame.K_RSHIFT] or keys[pygame.K_RCTRL]:
                    p.attack(Player.ATTACK_SWING)

        # Non-local player controls (for single player mode with 2 players)
        if not is_multiplayer:
            if len(game_manager.players) > 1:
                p1 = game_manager.players[1]
                # Movement
                if keys[pygame.K_LEFT]:
                    p1.move(-1)
                elif keys[pygame.K_RIGHT]:
                    p1.move(1)
                else:
                    p1.stop_move()

                # Jump
                if keys[pygame.K_UP]:
                    p1.jump()

                # Attack
                if keys[pygame.K_RSHIFT] or keys[pygame.K_RCTRL]:
                    p1.attack(Player.ATTACK_SWING)

        # Send network updates (enhanced with new player state)
        if is_multiplayer and network_update_timer >= 0.033:  # ~30 updates per second
            network_update_timer = 0
            if local_player_id < len(game_manager.players):
                player = game_manager.players[local_player_id]
                network_client.send_update({
                    'x': player.rect.x,
                    'y': player.rect.y,
                    'vx': player.vel_x,
                    'vy': player.vel_y,
                    'health': player.health,
                    'alive': player.alive,
                    'facing_right': player.facing_right,
                    'attack_state': player.attack_state
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
                    remote_player.vel_x = remote_state.get('vx', remote_player.vel_x)
                    remote_player.vel_y = remote_state.get('vy', remote_player.vel_y)
                    if 'health' in remote_state:
                        remote_player.health = remote_state['health']
                    if 'alive' in remote_state:
                        remote_player.alive = remote_state['alive']
                    if 'facing_right' in remote_state:
                        remote_player.facing_right = remote_state['facing_right']
                    if 'attack_state' in remote_state:
                        remote_player.attack_state = remote_state['attack_state']

        game_manager.update(dt)

        # Check for melee attack collisions
        for i, attacker in enumerate(game_manager.players):
            if attacker.alive and attacker.attack_state != Player.ATTACK_NONE:
                hitbox = attacker.get_attack_hitbox()
                if hitbox:
                    for j, defender in enumerate(game_manager.players):
                        if i != j and defender.alive and hitbox.colliderect(defender.rect):
                            # Calculate knockback based on attack direction
                            knockback_x = 10 if attacker.facing_right else -10
                            knockback_y = -5
                            defender.take_damage(15, knockback_x, knockback_y)

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
            player_text = f"<< YOU ARE P{local_player_id + 1} >> [F] ATTACK"
        else:
            player_text = f"<< P{current_player + 1} FORGING >> [TAB] SWITCH [F] ATTACK"
        indicator_text = ui.small_font.render(player_text, True, (0, 255, 255))
        screen.blit(indicator_text, (current_screen_size[0] // 2 - 180, current_screen_size[1] - 115))

        esc_text = ui.small_font.render("[ESC] MENU", True, (100, 100, 100))
        screen.blit(esc_text, (10, 10))

        # Draw audio button
        audio_manager.draw(screen)

        pygame.display.flip()

    if is_multiplayer and network_client:
        network_client.disconnect()

    return "QUIT"


def run_ai_test_mode():
    """Run a quick AI image test (same as test_ai_images.py) and exit."""
    pygame.init()
    prompts = ["flaming sword", "icy spear", "giant Tiger"]
    ai = AIClient()
    results = []

    def _cb(weapon_data, player_id):
        has_image = 'image' in weapon_data and weapon_data['image'] is not None
        size = None
        path = None
        bg_removed = weapon_data.get('bg_removed') if isinstance(weapon_data, dict) else None
        bg_has_alpha = weapon_data.get('bg_has_alpha') if isinstance(weapon_data, dict) else None
        if has_image:
            surf = weapon_data['image']
            try:
                size = surf.get_size()
                fname = f"ai_image_{player_id}_{weapon_data.get('name','weapon').replace(' ','_')}.png"
                pygame.image.save(surf, fname)
                path = os.path.abspath(fname)
            except Exception as e:
                path = f"save_failed: {e}"
        results.append({'prompt': cur_prompt, 'has_image': has_image, 'size': size, 'path': path, 'bg_removed': bg_removed, 'bg_has_alpha': bg_has_alpha, 'data': weapon_data})

    ai.set_weapon_spawned_callback(_cb)

    print('HACKCLUB_API_KEY set:', bool(os.environ.get('HACKCLUB_API_KEY')))
    print('REMOVE_BG_API_KEY set:', bool(os.environ.get('REMOVE_BG_API_KEY')))

    for i, p in enumerate(prompts):
        cur_prompt = p
        print(f"\nForging prompt ({i+1}/{len(prompts)}): {p}")
        ai.forge_weapon(p, i)

    print('\nResults:')
    for r in results:
        print(f"Prompt: {r['prompt']}, has_image: {r['has_image']}, size: {r['size']}, saved: {r['path']}, bg_removed: {r['bg_removed']}, bg_has_alpha: {r['bg_has_alpha']}")

    pygame.quit()
    # exit after test
    sys.exit(0)


def main():
    """Main entry point."""
    pygame.init()
    # CLI test mode: run AI test and exit
    if '--test-ai' in sys.argv:
        run_ai_test_mode()
    # Create resizable window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("PROMPT WARS - Retro Edition")

    # Initialize audio manager
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

        elif action == "CREATE_LOBBY":
            # Host a game - start server and go to lobby
            print(f"\n=== CREATING LOBBY: {room_info} ===")
            if start_server():
                local_ip = get_local_ip()
                print(f"✓ Server started! Share this IP: {local_ip}")
                print(f"✓ Room Code: {room_info}")

                # Create network client and connect to own server
                network_client = GameClient()
                if network_client.connect(local_ip):
                    if network_client.create_room(room_info, 'Host'):
                        print("✓ Room created successfully!")
                        print("✓ Opening lobby...")

                        # Show lobby screen immediately - no freezing!
                        lobby_result = show_lobby(screen, audio_manager, network_client, room_info, is_host=True)

                        if lobby_result == "START":
                            print("✓ Starting game!")
                            result = run_game(room_info, audio_manager, is_host=True, network_client=network_client)
                            network_client.disconnect()
                        elif lobby_result == "CANCEL":
                            print("✓ Cancelled - returning to menu")
                            network_client.disconnect()
                            result = "MENU"
                        else:
                            network_client.disconnect()
                            result = "MENU"
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
                if network_client.join_room(room_info, 'Player2'):
                    print("✓ Joined room successfully!")

                    # Check if game already started during join
                    if network_client.game_starting:
                        print("✓ Game already starting - going straight to game!")
                        result = run_game(f"{room_info}", audio_manager, is_host=False, network_client=network_client)
                        network_client.disconnect()
                    else:
                        print("✓ Waiting in lobby...")
                        # Show lobby screen
                        lobby_result = show_lobby(screen, audio_manager, network_client, room_info, is_host=False)

                        if lobby_result == "START":
                            print("✓ Game starting!")
                            result = run_game(f"{room_info}", audio_manager, is_host=False, network_client=network_client)
                            network_client.disconnect()
                        elif lobby_result == "LEAVE" or lobby_result == "CANCEL":
                            print("✓ Left lobby - returning to menu")
                            network_client.disconnect()
                            result = "MENU"
                        else:
                            network_client.disconnect()
                            result = "MENU"
                else:
                    print("✗ Failed to join room - check room code")
                    network_client.disconnect()
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

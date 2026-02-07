# main.py
# Main game loop for Prompt Wars - Melee Combat Edition

import pygame
import sys
import settings
from settings import *
from modules.player import Player
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


def character_setup_phase(screen):
    """Let both players enter prompts for their character and weapon."""
    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 48)
    font_normal = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)

    current_player = 0
    current_prompt_type = "character"

    player_data = {
        0: {"character_prompt": "", "weapon_prompt": "", "character_image": None, "weapon_image": None},
        1: {"character_prompt": "", "weapon_prompt": "", "character_image": None, "weapon_image": None}
    }

    active_input = ""
    setup_complete = False
    ai_client = AIClient()

    running = True
    while running and not setup_complete:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_RETURN:
                    if active_input.strip():
                        if current_prompt_type == "character":
                            player_data[current_player]["character_prompt"] = active_input
                            player_data[current_player]["character_image"] = None
                            current_prompt_type = "weapon"
                            active_input = ""
                        elif current_prompt_type == "weapon":
                            player_data[current_player]["weapon_prompt"] = active_input
                            player_data[current_player]["weapon_image"] = None
                            if current_player == 0:
                                current_player = 1
                                current_prompt_type = "character"
                                active_input = ""
                            else:
                                setup_complete = True
                elif event.key == pygame.K_BACKSPACE:
                    active_input = active_input[:-1]
                else:
                    if len(active_input) < 100:
                        active_input += event.unicode

        screen.fill((20, 20, 40))

        title = font_large.render("⚔️ CHARACTER SETUP ⚔️", True, (255, 200, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        player_colors = [(0, 200, 255), (255, 80, 180)]
        player_text = font_normal.render(f"PLAYER {current_player + 1}", True, player_colors[current_player])
        screen.blit(player_text, (SCREEN_WIDTH // 2 - player_text.get_width() // 2, 120))

        prompt_label = "Describe your CHARACTER:" if current_prompt_type == "character" else "Describe your WEAPON:"
        prompt_text = font_normal.render(prompt_label, True, WHITE)
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 180))

        input_box = pygame.Rect(SCREEN_WIDTH // 2 - 400, 250, 800, 50)
        pygame.draw.rect(screen, (60, 60, 80), input_box)
        pygame.draw.rect(screen, (0, 255, 255), input_box, 3)

        input_surface = font_normal.render(active_input, True, WHITE)
        screen.blit(input_surface, (input_box.x + 10, input_box.y + 10))

        if int(pygame.time.get_ticks() / 500) % 2:
            cursor_x = input_box.x + 10 + input_surface.get_width()
            pygame.draw.line(screen, WHITE, (cursor_x, input_box.y + 10), (cursor_x, input_box.bottom - 10), 2)

        instructions = [
            "Type your prompt and press ENTER",
            "Example characters: 'ninja warrior', 'fire mage', 'robot knight'",
            "Example weapons: 'katana blade', 'magic staff', 'laser sword'",
            "",
            "Press ESC to cancel"
        ]

        y_offset = 350
        for instruction in instructions:
            inst_text = font_small.render(instruction, True, (150, 150, 150))
            screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, y_offset))
            y_offset += 30

        progress_text = ""
        if current_player == 0 and current_prompt_type == "character":
            progress_text = "Step 1/4: P1 Character"
        elif current_player == 0 and current_prompt_type == "weapon":
            progress_text = "Step 2/4: P1 Weapon"
        elif current_player == 1 and current_prompt_type == "character":
            progress_text = "Step 3/4: P2 Character"
        elif current_player == 1 and current_prompt_type == "weapon":
            progress_text = "Step 4/4: P2 Weapon"

        progress = font_small.render(progress_text, True, (100, 200, 100))
        screen.blit(progress, (SCREEN_WIDTH // 2 - progress.get_width() // 2, 500))

        y_offset = 550
        for i in range(2):
            if player_data[i]["character_prompt"]:
                char_display = font_small.render(f"P{i+1} Char: {player_data[i]['character_prompt'][:40]}...", True, player_colors[i])
                screen.blit(char_display, (50, y_offset))
                y_offset += 25
            if player_data[i]["weapon_prompt"]:
                weap_display = font_small.render(f"P{i+1} Weapon: {player_data[i]['weapon_prompt'][:40]}...", True, player_colors[i])
                screen.blit(weap_display, (50, y_offset))
                y_offset += 25

        pygame.display.flip()

    if setup_complete:
        screen.fill((20, 20, 40))
        loading_text = font_large.render("⚡ GENERATING FIGHTERS... ⚡", True, (255, 255, 0))
        screen.blit(loading_text, (SCREEN_WIDTH // 2 - loading_text.get_width() // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        return player_data

    return None


def round_end_choice(screen):
    """Ask players if they want to play again or choose new characters."""
    clock = pygame.time.Clock()
    font_large = pygame.font.Font(None, 56)
    font_normal = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 28)

    selected = 0
    options = ["PLAY AGAIN (Same Characters)", "NEW CHARACTERS", "MAIN MENU"]

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "MENU"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected == 0:
                        return "REPLAY"
                    elif selected == 1:
                        return "REPROMPT"
                    elif selected == 2:
                        return "MENU"
                elif event.key == pygame.K_ESCAPE:
                    return "MENU"

        screen.fill((20, 20, 40))

        title = font_large.render("ROUND COMPLETE!", True, (255, 200, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        subtitle = font_normal.render("What would you like to do?", True, (150, 150, 150))
        screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 180))

        y_offset = 280
        for i, option in enumerate(options):
            if i == selected:
                color = (0, 255, 255)
                prefix = "► "
                text = font_normal.render(prefix + option, True, color)
            else:
                color = (100, 100, 100)
                text = font_normal.render("  " + option, True, color)

            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 70

        inst = font_small.render("Use W/S or Arrow Keys to select, ENTER to confirm", True, (80, 80, 80))
        screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, SCREEN_HEIGHT - 80))

        pygame.display.flip()

    return "MENU"


def run_game(player_data, room_info=None):
    """Run the main melee combat game."""
    # PLATFORMS is already defined in settings.py

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PROMPT WARS - Melee Combat")
    clock = pygame.time.Clock()

    try:
        background = pygame.image.load("backgrounds/bg.png")
        background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        background.fill((50, 30, 80))

    game_manager = GameManager()
    ui = UI(screen)
    ai_client = AIClient()

    if room_info:
        ui.add_notification(f"ROOM: {room_info}", 5.0, (0, 255, 255))

    player_colors = [(0, 200, 255), (255, 80, 180)]
    for i in range(2):
        spawn_x, spawn_y = game_manager.spawn_points[i]
        player = Player(i, spawn_x, spawn_y, player_colors[i])

        player.character_prompt = player_data[i]["character_prompt"]
        player.weapon_prompt = player_data[i]["weapon_prompt"]
        player.character_image = player_data[i]["character_image"]
        player.weapon_image = player_data[i]["weapon_image"]

        player.set_health_changed_callback(ui.health_changed)
        ui.register_player(i, player_colors[i])
        game_manager.add_player(player)

    ui.add_notification(f"P1: {player_data[0]['character_prompt']} with {player_data[0]['weapon_prompt']}!", 3.0, player_colors[0])
    pygame.time.delay(1500)
    ui.add_notification(f"P2: {player_data[1]['character_prompt']} with {player_data[1]['weapon_prompt']}!", 3.0, player_colors[1])
    pygame.time.delay(1500)
    ui.add_notification("⚔️ FIGHT! ⚔️", 2.0, (255, 255, 0))

    game_manager.start_round()

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"

        keys = pygame.key.get_pressed()

        if len(game_manager.players) > 0:
            p0 = game_manager.players[0]
            move_dir = 0
            if keys[pygame.K_a]:
                move_dir = -1
            elif keys[pygame.K_d]:
                move_dir = 1

            if move_dir != 0:
                p0.move(move_dir)
            else:
                p0.stop_move()

            if keys[pygame.K_w]:
                p0.jump()

            if keys[pygame.K_j]:
                p0.attack()

        if len(game_manager.players) > 1:
            p1 = game_manager.players[1]
            move_dir = 0
            if keys[pygame.K_LEFT]:
                move_dir = -1
            elif keys[pygame.K_RIGHT]:
                move_dir = 1

            if move_dir != 0:
                p1.move(move_dir)
            else:
                p1.stop_move()

            if keys[pygame.K_UP]:
                p1.jump()

            if keys[pygame.K_RETURN]:
                p1.attack()

        game_manager.update(dt)
        ui.update(dt)

        alive_players = [p for p in game_manager.players if p.alive]

        if ui.time_remaining <= 0 and game_manager.round_active:
            game_manager.end_round()
            ui.reset_timer()

            if len(alive_players) == 1:
                winner = alive_players[0]
                ui.add_notification(f"⏰ TIME UP! {winner.character_prompt.upper()} WINS!", 3.0, WARNING_YELLOW)
            elif len(alive_players) > 1:
                ui.add_notification("⏰ TIME UP! IT'S A DRAW!", 3.0, WARNING_YELLOW)
            else:
                ui.add_notification("⏰ TIME UP! NO SURVIVORS!", 3.0, DANGER_RED)

            pygame.time.delay(3000)
            choice = round_end_choice(screen)
            return choice

        elif len(alive_players) == 1 and game_manager.round_active:
            winner = alive_players[0]
            game_manager.end_round()
            ui.reset_timer()

            ui.add_notification(f"💀 {winner.character_prompt.upper()} WINS!", 3.0, SUCCESS_GREEN)

            scores_text = " | ".join([f"P{i+1}: {game_manager.player_scores[i]}" for i in range(len(game_manager.players))])
            ui.add_notification(f"SCORE: {scores_text}", 3.0, WHITE)

            pygame.time.delay(3000)
            choice = round_end_choice(screen)
            return choice

        elif len(alive_players) == 0 and game_manager.round_active:
            game_manager.end_round()
            ui.reset_timer()
            ui.add_notification("💥 DOUBLE KILL! NOBODY WINS!", 3.0, ORANGE)
            pygame.time.delay(3000)
            choice = round_end_choice(screen)
            return choice

        screen.blit(background, (0, 0))
        game_manager.draw_players(screen)
        ui.draw(screen)

        controls_text = ui.small_font.render("P1: WASD+J | P2: Arrows+Enter | ESC: Menu", True, (150, 150, 150))
        screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()

    return "QUIT"


def main():
    """Main entry point."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    player_data = None

    while True:
        action, room_info = show_menu(screen)

        if action == "QUIT":
            break

        elif action == "START_GAME" or action == "JOIN_GAME":
            player_data = character_setup_phase(screen)

            if player_data is None:
                continue

            while True:
                result = run_game(player_data, room_info)

                if result == "REPLAY":
                    continue
                elif result == "REPROMPT":
                    player_data = character_setup_phase(screen)
                    if player_data is None:
                        break
                    continue
                elif result == "MENU" or result == "QUIT":
                    break

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()


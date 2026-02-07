# modules/lobby.py
# Lobby screen for multiplayer games
# Shows connected players and prevents starting until ready

import pygame
import math
from settings import *


class LobbyScreen:
    """Lobby screen showing connected players before game starts."""

    def __init__(self, screen, network_client, room_name, is_host):
        self.screen = screen
        self.network_client = network_client
        self.room_name = room_name
        self.is_host = is_host

        self.title_font = pygame.font.Font(None, 84)
        self.font = pygame.font.Font(None, 40)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 20)

        self.cyan = (0, 255, 255)
        self.magenta = (255, 0, 255)
        self.yellow = (255, 255, 0)
        self.green = (0, 255, 0)
        self.red = (255, 50, 50)
        self.white = (255, 255, 255)
        self.dark_bg = (15, 15, 30)

        self.time = 0
        self.error_message = ""
        self.error_timer = 0
        self.pulse_time = 0

        # Particle effects for background
        self.stars = []
        for _ in range(50):
            self.stars.append({
                'x': pygame.math.Vector2(
                    __import__('random').randint(0, SCREEN_WIDTH),
                    __import__('random').randint(0, SCREEN_HEIGHT)
                ),
                'speed': __import__('random').uniform(0.2, 1.0),
                'size': __import__('random').randint(1, 3)
            })

        # Create buttons with better positioning
        center_x = SCREEN_WIDTH // 2
        button_y_start = SCREEN_HEIGHT - 150

        if is_host:
            self.start_button = Button(center_x - 350, button_y_start, 320, 70, "START GAME", self.green)
            self.cancel_button = Button(center_x + 30, button_y_start, 320, 70, "CANCEL", self.red)
        else:
            self.ready_button = Button(center_x - 350, button_y_start, 320, 70, "READY", self.green)
            self.leave_button = Button(center_x + 30, button_y_start, 320, 70, "LEAVE", self.red)

        # Set up callback for player joins
        self.network_client.on_player_joined = self.on_player_joined

        # Track last update time
        self.last_update = 0
        self.connection_pulse = 0

    def on_player_joined(self, player_name):
        """Called when a player joins the lobby."""
        print(f"✓ {player_name} joined the lobby!")

    def can_start_game(self):
        """Check if we can start the game."""
        return len(self.network_client.lobby_players) >= 2

    def update(self, dt):
        """Update lobby state."""
        self.time += dt
        self.pulse_time += dt
        self.connection_pulse += dt
        self.last_update += dt

        # Update stars
        for star in self.stars:
            star['x'].y += star['speed'] * 30 * dt
            if star['x'].y > SCREEN_HEIGHT:
                star['x'].y = 0
                star['x'].x = __import__('random').randint(0, SCREEN_WIDTH)

        # Poll lobby status every 0.5 seconds
        if self.last_update >= 0.5 and self.is_host:
            self.last_update = 0

        # Update error timer
        if self.error_timer > 0:
            self.error_timer -= dt
            if self.error_timer <= 0:
                self.error_message = ""

        # Update buttons
        mouse_pos = pygame.mouse.get_pos()
        if self.is_host:
            self.start_button.update(mouse_pos, dt)
            self.cancel_button.update(mouse_pos, dt)
        else:
            self.ready_button.update(mouse_pos, dt)
            self.leave_button.update(mouse_pos, dt)

    def handle_event(self, event):
        """Handle lobby events."""
        if self.is_host:
            if self.start_button.is_clicked(event):
                if self.can_start_game():
                    return "START"
                else:
                    self.show_error("NEED AT LEAST 2 PLAYERS!")
                    return None

            if self.cancel_button.is_clicked(event):
                return "CANCEL"
        else:
            if self.ready_button.is_clicked(event):
                return None

            if self.leave_button.is_clicked(event):
                return "LEAVE"

        return None

    def show_error(self, message):
        """Show an error message."""
        self.error_message = message
        self.error_timer = 3.0

    def draw(self):
        """Draw lobby screen."""
        # Dark background
        self.screen.fill(self.dark_bg)

        # Draw animated stars
        for star in self.stars:
            alpha = int(128 + 127 * math.sin(self.time * 2 + star['x'].x))
            color = (alpha, alpha, alpha)
            pygame.draw.circle(self.screen, color, (int(star['x'].x), int(star['x'].y)), star['size'])

        # Draw grid effect (more subtle)
        self._draw_grid()

        # Title with glow effect
        title_text = "◄◄ LOBBY ►►"
        self._draw_glowing_text(title_text, SCREEN_WIDTH // 2, 60, self.title_font, self.cyan)

        # Room name box
        room_box_y = 130
        room_box_height = 50
        pygame.draw.rect(self.screen, self.cyan,
                        (SCREEN_WIDTH // 2 - 252, room_box_y - 2, 504, room_box_height + 4), 2)
        pygame.draw.rect(self.screen, (0, 0, 0, 200),
                        (SCREEN_WIDTH // 2 - 250, room_box_y, 500, room_box_height))

        room_text = f"ROOM: {self.room_name.upper()}"
        room_surface = self.font.render(room_text, True, self.yellow)
        room_rect = room_surface.get_rect(center=(SCREEN_WIDTH // 2, room_box_y + 25))
        self.screen.blit(room_surface, room_rect)

        # Connection indicator
        pulse = abs(math.sin(self.connection_pulse * 3))
        conn_color = (0, int(255 * pulse), int(128 + 127 * pulse))
        pygame.draw.circle(self.screen, conn_color, (SCREEN_WIDTH // 2 + 260, room_box_y + 25), 8)
        conn_text = self.tiny_font.render("CONNECTED", True, self.green)
        self.screen.blit(conn_text, (SCREEN_WIDTH // 2 + 275, room_box_y + 18))

        # Player list section
        players_y = 210
        players_title = "═══ CONNECTED PLAYERS ═══"
        self._draw_glowing_text(players_title, SCREEN_WIDTH // 2, players_y, self.small_font, self.magenta)

        # Draw player list box with better styling
        box_x = SCREEN_WIDTH // 2 - 300
        box_y = 250
        box_width = 600
        box_height = 280

        # Outer glow
        for i in range(3, 0, -1):
            alpha = 50 - i * 15
            glow_color = (*self.cyan, alpha)
            surf = pygame.Surface((box_width + i * 4, box_height + i * 4), pygame.SRCALPHA)
            pygame.draw.rect(surf, glow_color, surf.get_rect(), 2)
            self.screen.blit(surf, (box_x - i * 2, box_y - i * 2))

        # Main box
        pygame.draw.rect(self.screen, self.cyan, (box_x - 3, box_y - 3, box_width + 6, box_height + 6), 3)
        pygame.draw.rect(self.screen, (5, 5, 15), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, self.cyan, (box_x, box_y, box_width, box_height), 2)

        # Header line
        pygame.draw.line(self.screen, self.cyan, (box_x, box_y + 50), (box_x + box_width, box_y + 50), 2)

        # Column headers
        header_y = box_y + 15
        headers = [("SLOT", 50), ("PLAYER NAME", 180), ("STATUS", 480)]
        for text, x_offset in headers:
            header_surf = self.small_font.render(text, True, self.magenta)
            self.screen.blit(header_surf, (box_x + x_offset, header_y))

        # Draw players
        players = self.network_client.lobby_players
        if players:
            for i in range(2):  # Always show 2 slots
                y_pos = box_y + 80 + i * 90

                if i < len(players):
                    player_name = players[i]

                    # Slot number with color
                    slot_color = self.yellow if i == 0 else self.cyan
                    player_num = f"P{i + 1}"
                    num_surface = self.font.render(player_num, True, slot_color)
                    self.screen.blit(num_surface, (box_x + 40, y_pos))

                    # Player name with background
                    name_bg_rect = pygame.Rect(box_x + 120, y_pos - 5, 320, 50)
                    pygame.draw.rect(self.screen, (30, 30, 50), name_bg_rect)
                    pygame.draw.rect(self.screen, slot_color, name_bg_rect, 1)

                    name_surface = self.font.render(player_name.upper(), True, self.white)
                    self.screen.blit(name_surface, (box_x + 130, y_pos + 5))

                    # Status badge
                    if i == 0:
                        badge_text = "HOST"
                        badge_color = self.green
                    else:
                        badge_text = "GUEST"
                        badge_color = self.magenta

                    badge_rect = pygame.Rect(box_x + 460, y_pos, 100, 40)
                    pygame.draw.rect(self.screen, badge_color, badge_rect, 2)
                    badge_surface = self.small_font.render(badge_text, True, badge_color)
                    badge_rect_text = badge_surface.get_rect(center=badge_rect.center)
                    self.screen.blit(badge_surface, badge_rect_text)
                else:
                    # Empty slot
                    player_num = f"P{i + 1}"
                    num_surface = self.font.render(player_num, True, (80, 80, 80))
                    self.screen.blit(num_surface, (box_x + 40, y_pos))

                    empty_text = "[ WAITING FOR PLAYER... ]"
                    empty_surface = self.font.render(empty_text, True, (80, 80, 100))
                    self.screen.blit(empty_surface, (box_x + 130, y_pos + 5))

                    # Animated dots
                    dots = "." * (int(self.time * 2) % 4)
                    dots_surface = self.font.render(dots, True, (100, 100, 120))
                    self.screen.blit(dots_surface, (box_x + 430, y_pos + 5))

        # Player count indicator
        player_count = len(players)
        count_y = box_y + box_height + 25
        count_text = f"[ {player_count} / 2 PLAYERS CONNECTED ]"
        count_color = self.green if player_count >= 2 else self.yellow
        count_surface = self.font.render(count_text, True, count_color)
        count_rect = count_surface.get_rect(center=(SCREEN_WIDTH // 2, count_y))
        self.screen.blit(count_surface, count_rect)

        # Status message above buttons
        status_y = SCREEN_HEIGHT - 200
        if self.is_host:
            if player_count < 2:
                wait_text = "► Waiting for another player to join..."
                pulse = abs(math.sin(self.pulse_time * 2))
                wait_color = (255, int(255 * pulse), 0)
                wait_surface = self.small_font.render(wait_text, True, wait_color)
            else:
                wait_text = "► Ready to start! Click START GAME when ready."
                wait_color = self.green
                wait_surface = self.small_font.render(wait_text, True, wait_color)
        else:
            wait_text = "► Waiting for host to start the game..."
            wait_surface = self.small_font.render(wait_text, True, self.cyan)

        wait_rect = wait_surface.get_rect(center=(SCREEN_WIDTH // 2, status_y))
        self.screen.blit(wait_surface, wait_rect)

        # Draw buttons
        if self.is_host:
            self.start_button.draw(self.screen, self.font)
            self.cancel_button.draw(self.screen, self.font)
        else:
            self.ready_button.draw(self.screen, self.font)
            self.leave_button.draw(self.screen, self.font)

        # Draw error popup if active
        if self.error_message and self.error_timer > 0:
            self._draw_error_popup()

        # Draw scan lines (subtle)
        self._draw_scan_lines()

    def _draw_grid(self):
        """Draw subtle background grid."""
        grid_color = (25, 25, 45)
        spacing = 40
        for x in range(0, SCREEN_WIDTH, spacing):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, spacing):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)

    def _draw_glowing_text(self, text, x, y, font, color):
        """Draw text with a glow effect."""
        # Glow layers
        for offset in [4, 3, 2]:
            glow_surf = font.render(text, True, tuple(c // (offset + 1) for c in color))
            glow_rect = glow_surf.get_rect(center=(x, y))
            self.screen.blit(glow_surf, (glow_rect.x - offset, glow_rect.y))
            self.screen.blit(glow_surf, (glow_rect.x + offset, glow_rect.y))
            self.screen.blit(glow_surf, (glow_rect.x, glow_rect.y - offset))
            self.screen.blit(glow_surf, (glow_rect.x, glow_rect.y + offset))

        # Main text
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(x, y))
        self.screen.blit(text_surf, text_rect)

    def _draw_error_popup(self):
        """Draw polished error popup."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Error box
        box_width = 700
        box_height = 250
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT // 2 - box_height // 2

        # Pulsing effect
        pulse = abs(math.sin(self.time * 4))
        pulse_color = (255, int(50 + 100 * pulse), int(50 + 100 * pulse))

        # Multiple border layers for glow
        for i in range(5, 0, -1):
            alpha = int(100 - i * 15)
            glow_surf = pygame.Surface((box_width + i * 8, box_height + i * 8), pygame.SRCALPHA)
            glow_color = (*pulse_color, alpha)
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), 3)
            self.screen.blit(glow_surf, (box_x - i * 4, box_y - i * 4))

        # Main box
        pygame.draw.rect(self.screen, pulse_color,
                        (box_x - 4, box_y - 4, box_width + 8, box_height + 8), 4)
        pygame.draw.rect(self.screen, (10, 10, 20), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.screen, self.red, (box_x, box_y, box_width, box_height), 3)

        # Error icon
        icon_y = box_y + 50
        self._draw_glowing_text("⚠", SCREEN_WIDTH // 2, icon_y, self.title_font, self.red)

        # Error title
        error_title = "ERROR!"
        self._draw_glowing_text(error_title, SCREEN_WIDTH // 2, box_y + 110, self.title_font, self.red)

        # Error message
        msg_surface = self.font.render(self.error_message, True, self.yellow)
        msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 170))
        self.screen.blit(msg_surface, msg_rect)

        # Dismiss hint with animation
        hint_alpha = int(128 + 127 * math.sin(self.time * 3))
        hint = "[ CLICK ANYWHERE TO DISMISS ]"
        hint_surface = self.small_font.render(hint, True, (hint_alpha, hint_alpha, hint_alpha))
        hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 210))
        self.screen.blit(hint_surface, hint_rect)

    def _draw_scan_lines(self):
        """Draw subtle retro scan line effect."""
        scan_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 3):
            pygame.draw.line(scan_surface, (0, 0, 0, 20), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(scan_surface, (0, 0))


class Button:
    """Polished button for lobby screen."""

    def __init__(self, x, y, width, height, text, color=(0, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        self.click_animation = 0
        self.hover_pulse = 0

    def update(self, mouse_pos, dt):
        """Update button state."""
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.click_animation > 0:
            self.click_animation = max(0, self.click_animation - dt * 5)
        if self.hover:
            self.hover_pulse += dt * 5

    def draw(self, surface, font):
        """Draw polished button."""
        offset = int(self.click_animation * 5)
        rect = self.rect.copy()
        rect.x += offset
        rect.y += offset

        color = self.color
        if self.hover:
            pulse = abs(math.sin(self.hover_pulse))
            color = tuple(min(255, int(c + 80 * pulse)) for c in color)

            # Draw glow when hovering
            for i in range(3, 0, -1):
                glow_surf = pygame.Surface((rect.width + i * 6, rect.height + i * 6), pygame.SRCALPHA)
                glow_color = (*color, 40)
                pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), 3)
                surface.blit(glow_surf, (rect.x - i * 3, rect.y - i * 3))

        # Button border and fill
        pygame.draw.rect(surface, color, rect.inflate(6, 6), 4)
        pygame.draw.rect(surface, (10, 10, 20), rect)
        pygame.draw.rect(surface, color, rect, 3)

        # Inner accent line
        inner_rect = rect.inflate(-10, -10)
        pygame.draw.rect(surface, color, inner_rect, 1)

        # Text
        text_surf = font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """Check if button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover:
                self.click_animation = 1.0
                return True
        return False


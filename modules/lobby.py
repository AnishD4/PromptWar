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

        self.title_font = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.cyan = (0, 255, 255)
        self.magenta = (255, 0, 255)
        self.yellow = (255, 255, 0)
        self.green = (0, 255, 0)
        self.red = (255, 50, 50)
        self.white = (255, 255, 255)
        self.bg = (25, 25, 35)
        self.card_bg = (35, 35, 50)

        self.time = 0
        self.error_message = ""
        self.error_timer = 0

        # Success notification for when you join
        self.success_message = ""
        self.success_timer = 0

        # Show success message when joining as guest
        if not is_host and network_client.lobby_players:
            host_name = network_client.lobby_players[0] if len(network_client.lobby_players) > 0 else "Host"
            self.success_message = f"Successfully joined {host_name}'s lobby!"
            self.success_timer = 3.0

        # Create buttons with clean positioning
        center_x = SCREEN_WIDTH // 2
        button_y = SCREEN_HEIGHT - 120
        
        if is_host:
            self.start_button = Button(center_x - 280, button_y, 250, 60, "START GAME", self.green)
            self.cancel_button = Button(center_x + 30, button_y, 250, 60, "CANCEL", self.red)
        else:
            self.ready_button = Button(center_x - 280, button_y, 250, 60, "READY", self.green)
            self.leave_button = Button(center_x + 30, button_y, 250, 60, "LEAVE", self.red)

        # Set up callback for player joins
        self.network_client.on_player_joined = self.on_player_joined

        # Track last update time
        self.last_update = 0

    def on_player_joined(self, player_name):
        """Called when a player joins the lobby."""
        print(f"✓ {player_name} joined the lobby!")

    def can_start_game(self):
        """Check if we can start the game."""
        return len(self.network_client.lobby_players) >= 2

    def update(self, dt):
        """Update lobby state."""
        self.time += dt
        self.last_update += dt

        # Poll lobby status every 0.5 seconds
        if self.last_update >= 0.5:
            self.last_update = 0
            # Refresh lobby info to keep connection alive
            if self.network_client and self.network_client.connected:
                try:
                    # Send keep-alive by requesting lobby info
                    self.network_client.get_lobby_info()
                except:
                    pass

        # Check if host started the game (for guests)
        if not self.is_host and self.network_client:
            with self.network_client.response_lock:
                if self.network_client.pending_response and \
                   self.network_client.pending_response.get('type') == 'game_starting':
                    self.network_client.pending_response = None
                    return "START"  # Signal that game is starting

        # Update error timer
        if self.error_timer > 0:
            self.error_timer -= dt
            if self.error_timer <= 0:
                self.error_message = ""

        # Update success timer
        if self.success_timer > 0:
            self.success_timer -= dt
            if self.success_timer <= 0:
                self.success_message = ""

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
        # Dismiss success message on click
        if event.type == pygame.MOUSEBUTTONDOWN and self.success_timer > 0:
            self.success_timer = 0
            self.success_message = ""
            return None

        if self.is_host:
            if self.start_button.is_clicked(event):
                if self.can_start_game():
                    return "START"
                else:
                    self.show_error("Need at least 2 players to start")
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
        # Clean gradient background
        self.screen.fill(self.bg)
        
        # Subtle top-to-bottom gradient
        for y in range(0, SCREEN_HEIGHT, 4):
            alpha = int(10 * (y / SCREEN_HEIGHT))
            color = tuple(max(0, c - alpha) for c in self.bg)
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y), 4)

        # Title
        title_text = "LOBBY"
        title_surf = self.title_font.render(title_text, True, self.cyan)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_surf, title_rect)

        # Room name card
        room_y = 160
        room_width = 500
        room_height = 60
        room_x = SCREEN_WIDTH // 2 - room_width // 2
        
        pygame.draw.rect(self.screen, self.card_bg, (room_x, room_y, room_width, room_height), border_radius=8)
        pygame.draw.rect(self.screen, self.cyan, (room_x, room_y, room_width, room_height), 2, border_radius=8)
        
        room_label = self.small_font.render("ROOM CODE", True, (150, 150, 150))
        self.screen.blit(room_label, (room_x + 20, room_y + 10))
        
        room_text = self.font.render(self.room_name.upper(), True, self.white)
        self.screen.blit(room_text, (room_x + 20, room_y + 28))

        # Player list card
        card_y = 260
        card_width = 600
        card_height = 260
        card_x = SCREEN_WIDTH // 2 - card_width // 2

        # Card background
        pygame.draw.rect(self.screen, self.card_bg, (card_x, card_y, card_width, card_height), border_radius=12)
        pygame.draw.rect(self.screen, self.cyan, (card_x, card_y, card_width, card_height), 2, border_radius=12)

        # Card title
        card_title = self.font.render("PLAYERS", True, self.cyan)
        self.screen.blit(card_title, (card_x + 25, card_y + 20))

        # Divider line
        pygame.draw.line(self.screen, (60, 60, 80), 
                        (card_x + 25, card_y + 60), 
                        (card_x + card_width - 25, card_y + 60), 2)

        # Draw player slots
        players = self.network_client.lobby_players
        for i in range(2):
            slot_y = card_y + 85 + i * 80
            
            if i < len(players):
                # Filled slot
                player_name = players[i]
                
                # Player number badge
                badge_size = 40
                badge_x = card_x + 35
                badge_y = slot_y
                
                badge_color = self.yellow if i == 0 else self.cyan
                pygame.draw.rect(self.screen, badge_color, 
                               (badge_x, badge_y, badge_size, badge_size), 
                               border_radius=6)
                
                p_num = self.font.render(f"P{i+1}", True, (20, 20, 30))
                p_rect = p_num.get_rect(center=(badge_x + badge_size//2, badge_y + badge_size//2))
                self.screen.blit(p_num, p_rect)
                
                # Player name
                name_surf = self.font.render(player_name.upper(), True, self.white)
                self.screen.blit(name_surf, (badge_x + badge_size + 20, slot_y + 8))
                
                # Status tag
                status = "HOST" if i == 0 else "GUEST"
                status_color = self.green if i == 0 else self.magenta
                status_surf = self.small_font.render(status, True, status_color)
                self.screen.blit(status_surf, (card_x + card_width - 90, slot_y + 12))
                
            else:
                # Empty slot
                badge_size = 40
                badge_x = card_x + 35
                badge_y = slot_y
                
                pygame.draw.rect(self.screen, (50, 50, 60), 
                               (badge_x, badge_y, badge_size, badge_size), 
                               border_radius=6)
                pygame.draw.rect(self.screen, (70, 70, 80), 
                               (badge_x, badge_y, badge_size, badge_size), 
                               1, border_radius=6)
                
                p_num = self.font.render(f"P{i+1}", True, (70, 70, 80))
                p_rect = p_num.get_rect(center=(badge_x + badge_size//2, badge_y + badge_size//2))
                self.screen.blit(p_num, p_rect)
                
                # Waiting text
                wait_text = "Waiting for player..."
                wait_surf = self.small_font.render(wait_text, True, (100, 100, 110))
                self.screen.blit(wait_surf, (badge_x + badge_size + 20, slot_y + 12))

        # Player count at bottom of card
        player_count = len(players)
        count_text = f"{player_count}/2 Players"
        count_color = self.green if player_count >= 2 else (150, 150, 150)
        count_surf = self.small_font.render(count_text, True, count_color)
        count_rect = count_surf.get_rect(center=(card_x + card_width // 2, card_y + card_height - 25))
        self.screen.blit(count_surf, count_rect)

        # Status message
        status_y = SCREEN_HEIGHT - 190
        if self.is_host:
            if player_count < 2:
                status_text = "Waiting for another player to join..."
                status_color = self.yellow
            else:
                status_text = "Ready to start!"
                status_color = self.green
        else:
            status_text = "Waiting for host to start..."
            status_color = self.cyan
        
        status_surf = self.small_font.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(center=(SCREEN_WIDTH // 2, status_y))
        self.screen.blit(status_surf, status_rect)

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

        # Draw success message if active
        if self.success_message and self.success_timer > 0:
            self._draw_success_message()

    def _draw_error_popup(self):
        """Draw minimal error popup."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Error card
        card_width = 500
        card_height = 150
        card_x = SCREEN_WIDTH // 2 - card_width // 2
        card_y = SCREEN_HEIGHT // 2 - card_height // 2

        # Card background
        pygame.draw.rect(self.screen, (40, 20, 20), 
                        (card_x, card_y, card_width, card_height), 
                        border_radius=12)
        pygame.draw.rect(self.screen, self.red, 
                        (card_x, card_y, card_width, card_height), 
                        3, border_radius=12)

        # Error title
        title_surf = self.font.render("ERROR", True, self.red)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, card_y + 45))
        self.screen.blit(title_surf, title_rect)

        # Error message
        msg_surf = self.small_font.render(self.error_message, True, self.white)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, card_y + 85))
        self.screen.blit(msg_surf, msg_rect)

        # Dismiss hint
        hint_surf = self.small_font.render("Click anywhere to dismiss", True, (150, 150, 150))
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, card_y + 115))
        self.screen.blit(hint_surf, hint_rect)

    def _draw_success_message(self):
        """Draw success message when joining."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Success card
        card_width = 500
        card_height = 100
        card_x = SCREEN_WIDTH // 2 - card_width // 2
        card_y = SCREEN_HEIGHT // 2 - card_height // 2

        # Card background
        pygame.draw.rect(self.screen, (20, 40, 20),
                        (card_x, card_y, card_width, card_height),
                        border_radius=12)
        pygame.draw.rect(self.screen, self.green,
                        (card_x, card_y, card_width, card_height),
                        3, border_radius=12)

        # Success message
        msg_surf = self.small_font.render(self.success_message, True, self.white)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, card_y + 35))
        self.screen.blit(msg_surf, msg_rect)

        # Dismiss hint
        hint_surf = self.small_font.render("Click anywhere to dismiss", True, (150, 150, 150))
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, card_y + 65))
        self.screen.blit(hint_surf, hint_rect)


class Button:
    """Clean, minimal button."""

    def __init__(self, x, y, width, height, text, color=(0, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.base_color = color
        self.hover = False
        self.click_animation = 0

    def update(self, mouse_pos, dt):
        """Update button state."""
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.click_animation > 0:
            self.click_animation = max(0, self.click_animation - dt * 5)

    def draw(self, surface, font):
        """Draw clean button."""
        rect = self.rect.copy()
        
        # Adjust for click animation
        if self.click_animation > 0:
            offset = int(self.click_animation * 3)
            rect.x += offset
            rect.y += offset

        # Color based on hover state
        if self.hover:
            bg_color = self.color
            text_color = (20, 20, 30)
            border_width = 0
        else:
            bg_color = (45, 45, 60)
            text_color = self.color
            border_width = 2

        # Draw button
        pygame.draw.rect(surface, bg_color, rect, border_radius=8)
        if border_width > 0:
            pygame.draw.rect(surface, self.color, rect, border_width, border_radius=8)

        # Draw text
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        """Check if button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover:
                self.click_animation = 1.0
                return True
        return False

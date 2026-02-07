# modules/ui.py
# UI Manager - handles HUD, health bars, timer, weapon prompt input
# T3: UI

import pygame
from settings import *


class UI:
    """Manages all UI elements for the game."""

    def __init__(self, screen):
        """
        Initialize UI manager.

        Args:
            screen: Pygame display surface
        """
        self.screen = screen
        self.font = pygame.font.Font(None, UI_FONT_SIZE)
        self.timer_font = pygame.font.Font(None, TIMER_FONT_SIZE)

        # Health bar data {player_id: health}
        self.player_health = {}
        self.player_colors = {}

        # Timer
        self.time_remaining = ROUND_TIME

        # Weapon prompt input
        self.input_active = False
        self.input_text = ""
        self.input_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - INPUT_BOX_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            INPUT_BOX_WIDTH,
            INPUT_BOX_HEIGHT
        )
        self.forge_button_rect = pygame.Rect(
            self.input_rect.right + 10,
            self.input_rect.y,
            120,
            INPUT_BOX_HEIGHT
        )

        # Notifications
        self.notifications = []  # List of (message, time_left)

        # Callbacks
        self.forge_weapon_callback = None

    def set_forge_weapon_callback(self, callback):
        """Set callback for forging weapon: callback(prompt, player_id)"""
        self.forge_weapon_callback = callback

    def register_player(self, player_id, color, initial_health=MAX_HEALTH):
        """
        Register a player for health bar display.

        Args:
            player_id: Unique player identifier
            color: Player color tuple
            initial_health: Starting health value
        """
        self.player_health[player_id] = initial_health
        self.player_colors[player_id] = color

    def health_changed(self, player_id, new_health):
        """
        Update health for a player (callback from player.py).

        Args:
            player_id: Player whose health changed
            new_health: New health value
        """
        if player_id in self.player_health:
            self.player_health[player_id] = max(0, new_health)

    def weapon_spawned(self, weapon_name, player_id):
        """
        Show notification when weapon spawns (callback from ai_client.py).

        Args:
            weapon_name: Name of spawned weapon
            player_id: Player who forged the weapon
        """
        message = f"Player {player_id} forged: {weapon_name}!"
        self.add_notification(message, duration=3.0)

    def add_notification(self, message, duration=3.0):
        """
        Add a temporary notification to display.

        Args:
            message: Text to display
            duration: How long to show (seconds)
        """
        self.notifications.append([message, duration])

    def update(self, dt):
        """
        Update UI state.

        Args:
            dt: Delta time in seconds
        """
        # Update timer
        self.time_remaining = max(0, self.time_remaining - dt)

        # Update notifications
        for notification in self.notifications[:]:
            notification[1] -= dt
            if notification[1] <= 0:
                self.notifications.remove(notification)

    def handle_event(self, event, current_player_id=0):
        """
        Handle input events for UI elements.

        Args:
            event: Pygame event
            current_player_id: ID of player using input

        Returns:
            True if event was handled by UI, False otherwise
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked on input box
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                return True
            # Check if clicked forge button
            elif self.forge_button_rect.collidepoint(event.pos):
                if self.input_text.strip() and self.forge_weapon_callback:
                    self.forge_weapon_callback(self.input_text, current_player_id)
                    self.input_text = ""
                return True
            else:
                self.input_active = False

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                # Forge weapon on Enter
                if self.input_text.strip() and self.forge_weapon_callback:
                    self.forge_weapon_callback(self.input_text, current_player_id)
                    self.input_text = ""
                self.input_active = False
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            elif event.key == pygame.K_ESCAPE:
                self.input_active = False
                return True
            elif len(self.input_text) < 50:  # Max length
                self.input_text += event.unicode
                return True

        return False

    def draw(self, screen):
        """
        Draw all UI elements.

        Args:
            screen: Pygame display surface
        """
        self.screen = screen

        self._draw_health_bars()
        self._draw_timer()
        self._draw_weapon_input()
        self._draw_notifications()

    def _draw_health_bars(self):
        """Draw health bars for all players."""
        y_offset = 20
        spacing = 30

        for i, (player_id, health) in enumerate(self.player_health.items()):
            x = 20
            y = y_offset + i * (HEALTH_BAR_HEIGHT + spacing)

            # Background
            bg_rect = pygame.Rect(x, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
            pygame.draw.rect(self.screen, DARK_GRAY, bg_rect)

            # Health fill
            health_width = int((health / MAX_HEALTH) * HEALTH_BAR_WIDTH)
            health_rect = pygame.Rect(x, y, health_width, HEALTH_BAR_HEIGHT)
            color = self.player_colors.get(player_id, GREEN)
            pygame.draw.rect(self.screen, color, health_rect)

            # Border
            pygame.draw.rect(self.screen, WHITE, bg_rect, 2)

            # Player label
            label = self.font.render(f"P{player_id}: {int(health)}", True, WHITE)
            self.screen.blit(label, (x + HEALTH_BAR_WIDTH + 10, y))

    def _draw_timer(self):
        """Draw round timer at top center."""
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"

        # Change color when time is low
        color = RED if self.time_remaining < 30 else WHITE

        timer_surface = self.timer_font.render(time_text, True, color)
        timer_rect = timer_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))

        # Background for better visibility
        bg_rect = timer_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, BLACK, bg_rect)
        pygame.draw.rect(self.screen, color, bg_rect, 2)

        self.screen.blit(timer_surface, timer_rect)

    def _draw_weapon_input(self):
        """Draw weapon prompt input box and forge button."""
        # Input box
        box_color = WHITE if self.input_active else GRAY
        pygame.draw.rect(self.screen, DARK_GRAY, self.input_rect)
        pygame.draw.rect(self.screen, box_color, self.input_rect, 2)

        # Input text
        text_surface = self.font.render(self.input_text, True, WHITE)
        self.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 8))

        # Placeholder text
        if not self.input_text and not self.input_active:
            placeholder = self.font.render("Type weapon prompt...", True, GRAY)
            self.screen.blit(placeholder, (self.input_rect.x + 5, self.input_rect.y + 8))

        # Forge button
        pygame.draw.rect(self.screen, BLUE, self.forge_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.forge_button_rect, 2)

        button_text = self.font.render("FORGE", True, WHITE)
        text_rect = button_text.get_rect(center=self.forge_button_rect.center)
        self.screen.blit(button_text, text_rect)

    def _draw_notifications(self):
        """Draw temporary notifications."""
        y_offset = 150

        for i, (message, time_left) in enumerate(self.notifications):
            # Fade out effect
            alpha = min(255, int(time_left * 85))

            text_surface = self.font.render(message, True, YELLOW)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 30))

            # Background
            bg_rect = text_rect.inflate(20, 10)
            bg_surface = pygame.Surface(bg_rect.size)
            bg_surface.set_alpha(alpha)
            bg_surface.fill(BLACK)
            self.screen.blit(bg_surface, bg_rect)

            # Text with alpha
            text_surface.set_alpha(alpha)
            self.screen.blit(text_surface, text_rect)

    def reset_timer(self):
        """Reset the round timer."""
        self.time_remaining = ROUND_TIME


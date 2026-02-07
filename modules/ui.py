# modules/ui.py
# UI Manager - handles HUD, health bars, timer, weapon prompt input
# T3: UI - RETRO ARCADE THEME

import pygame
import math
from settings import *


class UI:
    """Manages all UI elements with retro arcade aesthetic."""

    def __init__(self, screen):
        """Initialize UI manager with retro styling."""
        self.screen = screen
        
        # Use retro-style fonts (pixelated)
        try:
            self.font = pygame.font.Font(None, UI_FONT_SIZE)
            self.timer_font = pygame.font.Font(None, TIMER_FONT_SIZE)
            self.small_font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 48)
        except:
            self.font = pygame.font.SysFont('courier', UI_FONT_SIZE, bold=True)
            self.timer_font = pygame.font.SysFont('courier', TIMER_FONT_SIZE, bold=True)
            self.small_font = pygame.font.SysFont('courier', 18)
            self.title_font = pygame.font.SysFont('courier', 48, bold=True)

        # Retro color palette (arcade style)
        self.retro_cyan = (0, 255, 255)
        self.retro_magenta = (255, 0, 255)
        self.retro_yellow = (255, 255, 0)
        self.retro_green = (0, 255, 0)
        self.retro_orange = (255, 165, 0)

        # Health bar data
        self.player_health = {}
        self.player_colors = {}
        self.player_names = {}
        self.health_animations = {}

        # Timer
        self.time_remaining = ROUND_TIME

        # Cooldown tracking (for compatibility)
        self.forge_cooldowns = {}

        # Notifications with retro style
        self.notifications = []
        self.screen_shake = 0

        # Callbacks (not used in melee-only mode)
        self.forge_weapon_callback = None
        
        # Animation effects
        self.pulse_time = 0
        self.scan_line_offset = 0

        # Retro banner
        self.show_banner = True
        self.banner_alpha = 255
        self.banner_timer = 3.0
        self.banner_glitch = 0

    def set_forge_weapon_callback(self, callback):
        """Set callback for forging weapon."""
        self.forge_weapon_callback = callback

    def register_player(self, player_id, color, initial_health=MAX_HEALTH, name=None):
        """Register a player for health bar display."""
        self.player_health[player_id] = initial_health
        self.player_colors[player_id] = color
        self.player_names[player_id] = name or f"P{player_id + 1}"
        self.forge_cooldowns[player_id] = 0
        self.health_animations[player_id] = initial_health

    def health_changed(self, player_id, new_health):
        """Update health for a player with visual feedback."""
        if player_id in self.player_health:
            old_health = self.player_health[player_id]
            self.player_health[player_id] = max(0, new_health)
            
            if new_health < old_health:
                damage = int(old_health - new_health)
                self.add_notification(f"{self.player_names[player_id]} -{damage} HP!", 2.0, self.retro_magenta)
                self.screen_shake = min(damage / 3, 8)

    def weapon_spawned(self, weapon_name, player_id):
        """Show notification when weapon spawns."""
        message = f"{self.player_names[player_id]}: {weapon_name}!"
        self.add_notification(message, duration=3.0, color=self.retro_cyan)
        self.forge_cooldowns[player_id] = WEAPON_COOLDOWN

    def add_notification(self, message, duration=3.0, color=WHITE):
        """Add a retro-style notification."""
        self.notifications.append({
            'message': message.upper(),  # Retro games = uppercase
            'time_left': duration,
            'color': color,
            'y_offset': 0
        })
        
        if len(self.notifications) > 4:
            self.notifications.pop(0)

    def update(self, dt):
        """Update UI state with retro animations."""
        # Update timer
        self.time_remaining = max(0, self.time_remaining - dt)
        
        # Update notifications
        for notif in self.notifications[:]:
            notif['time_left'] -= dt
            if notif['time_left'] <= 0:
                self.notifications.remove(notif)
        
        # Update cooldowns
        for player_id in self.forge_cooldowns:
            if self.forge_cooldowns[player_id] > 0:
                self.forge_cooldowns[player_id] = max(0, self.forge_cooldowns[player_id] - dt)
        
        # Smooth health bar animation
        for player_id in self.health_animations:
            target = self.player_health[player_id]
            current = self.health_animations[player_id]
            self.health_animations[player_id] += (target - current) * dt * 5
        
        # Update pulse animation
        self.pulse_time += dt
        
        # Scan line effect
        self.scan_line_offset = (self.scan_line_offset + dt * 100) % SCREEN_HEIGHT

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake = max(0, self.screen_shake - dt * 15)

        # Update banner
        if self.show_banner:
            self.banner_timer -= dt
            self.banner_glitch = abs(math.sin(self.pulse_time * 10))
            if self.banner_timer <= 0:
                self.banner_alpha = max(0, self.banner_alpha - dt * 150)
                if self.banner_alpha <= 0:
                    self.show_banner = False

    def handle_event(self, event, current_player_id=0):
        """Handle input events for UI elements (disabled in melee-only mode)."""
        # No input handling needed - all prompts are before rounds
        return False
        """Handle input events for UI elements."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                return True
            elif self.forge_button_rect.collidepoint(event.pos):
                self._attempt_forge(current_player_id)
                return True
            else:
                self.input_active = False

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self._attempt_forge(current_player_id)
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            elif event.key == pygame.K_ESCAPE:
                self.input_active = False
                return True
            elif len(self.input_text) < 50 and event.unicode.isprintable():
                self.input_text += event.unicode
                return True

        return False
    
    def _attempt_forge(self, player_id):
        """Attempt to forge a weapon."""
        if self.input_text.strip() and self.forge_weapon_callback:
            if self.forge_cooldowns.get(player_id, 0) <= 0:
                self.forge_weapon_callback(self.input_text, player_id)
                self.input_text = ""
                self.input_active = False
            else:
                cooldown = int(self.forge_cooldowns[player_id]) + 1
                self.add_notification(f"COOLDOWN: {cooldown}S!", 1.5, self.retro_orange)

    def draw(self, screen):
        """Draw all UI elements with retro arcade style."""
        self.screen = screen
        
        self._draw_scan_lines()
        self._draw_retro_banner()
        self._draw_retro_health_bars()
        self._draw_retro_timer()
        # self._draw_retro_weapon_input()  # Not needed in melee-only mode
        self._draw_retro_notifications()
        self._draw_retro_game_info()
        self._draw_crt_effect()

    def _draw_scan_lines(self):
        """Draw CRT scan line effect."""
        scan_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(scan_surface, (0, 0, 0, 30), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(scan_surface, (0, 0))

    def _draw_retro_banner(self):
        """Draw retro arcade banner at start."""
        if not self.show_banner or self.banner_alpha <= 0:
            return
        
        # Retro background
        overlay = pygame.Surface((SCREEN_WIDTH, 250), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.banner_alpha * 0.8)))
        self.screen.blit(overlay, (0, SCREEN_HEIGHT // 2 - 125))

        # Glitch effect on title
        glitch_offset = int(self.banner_glitch * 5)

        # Main title with retro colors
        title_text = "PROMPT WARS"
        title = self.title_font.render(title_text, True, self.retro_cyan)
        title.set_alpha(int(self.banner_alpha))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2 + glitch_offset, SCREEN_HEIGHT // 2 - 30))

        # Retro shadow/outline effect
        for offset in [(-2, -2), (2, 2), (-2, 2), (2, -2)]:
            shadow = self.title_font.render(title_text, True, self.retro_magenta)
            shadow.set_alpha(int(self.banner_alpha * 0.5))
            shadow_rect = title_rect.copy()
            shadow_rect.x += offset[0]
            shadow_rect.y += offset[1]
            self.screen.blit(shadow, shadow_rect)

        self.screen.blit(title, title_rect)
        
        # Pixelated subtitle
        subtitle = self.font.render(">>> FORGE - FIGHT - WIN <<<", True, self.retro_yellow)
        subtitle.set_alpha(int(self.banner_alpha))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(subtitle, sub_rect)

        # Retro decorative border
        border_color = (*self.retro_cyan, int(self.banner_alpha))
        for i in range(3):
            pygame.draw.line(self.screen, border_color,
                           (100, SCREEN_HEIGHT // 2 - 80 + i),
                           (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2 - 80 + i), 2)
            pygame.draw.line(self.screen, border_color,
                           (100, SCREEN_HEIGHT // 2 + 80 + i),
                           (SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2 + 80 + i), 2)

    def _draw_retro_health_bars(self):
        """Draw retro arcade-style health bars."""
        bar_width = 200
        bar_height = 20

        player_ids = list(self.player_health.keys())
        
        for i, player_id in enumerate(player_ids):
            health = self.player_health[player_id]
            animated_health = self.health_animations.get(player_id, health)
            
            # Position
            if i % 2 == 0:
                x = 20
                y = 20 + (i // 2) * 60
            else:
                x = SCREEN_WIDTH - bar_width - 20
                y = 20 + (i // 2) * 60

            # Retro player label
            name = self.player_names[player_id]
            name_text = f"[{name}]"
            name_surface = self.font.render(name_text, True, self.retro_cyan)
            self.screen.blit(name_surface, (x, y - 20))

            # Pixelated border (thick retro style)
            border_rect = pygame.Rect(x - 2, y - 2, bar_width + 4, bar_height + 4)
            pygame.draw.rect(self.screen, self.retro_cyan, border_rect, 2)

            # Black background
            bg_rect = pygame.Rect(x, y, bar_width, bar_height)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)

            # Pixelated health fill (blocky retro style)
            health_percent = animated_health / MAX_HEALTH
            health_blocks = int((bar_width // 8) * health_percent)

            # Color based on health
            if health_percent > 0.6:
                fill_color = self.retro_green
            elif health_percent > 0.3:
                fill_color = self.retro_yellow
            else:
                fill_color = self.retro_magenta

            # Draw blocky segments
            for block in range(health_blocks):
                block_x = x + block * 8
                pygame.draw.rect(self.screen, fill_color, (block_x + 1, y + 2, 6, bar_height - 4))

            # HP text (retro style)
            hp_text = f"{int(health):03d}"
            hp_surface = self.small_font.render(hp_text, True, WHITE)
            self.screen.blit(hp_surface, (x + bar_width + 10, y + 2))

    def _draw_retro_timer(self):
        """Draw retro arcade timer."""
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"

        # Retro color based on urgency
        if self.time_remaining < 30:
            color = self.retro_magenta
            # Blink effect
            if int(self.pulse_time * 3) % 2 == 0:
                color = self.retro_yellow
        elif self.time_remaining < 60:
            color = self.retro_yellow
        else:
            color = self.retro_cyan

        # Pixelated timer box
        box_width = 150
        box_height = 60
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = 20

        # Box border (double border retro style)
        pygame.draw.rect(self.screen, color, (box_x - 4, box_y - 4, box_width + 8, box_height + 8), 3)
        pygame.draw.rect(self.screen, color, (box_x - 2, box_y - 2, box_width + 4, box_height + 4), 1)
        pygame.draw.rect(self.screen, (0, 0, 0), (box_x, box_y, box_width, box_height))

        # TIME label
        label = self.small_font.render("TIME", True, color)
        label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, box_y + 15))
        self.screen.blit(label, label_rect)

        # Timer digits
        timer_surface = self.timer_font.render(time_text, True, color)
        timer_rect = timer_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 40))
        self.screen.blit(timer_surface, timer_rect)

    def _draw_retro_weapon_input(self):
        """Draw retro arcade weapon input."""
        # Input box with thick retro border
        border_color = self.retro_yellow if self.input_active else self.retro_cyan

        # Triple border for arcade look
        pygame.draw.rect(self.screen, border_color, self.input_rect.inflate(6, 6), 3)
        pygame.draw.rect(self.screen, (0, 0, 0), self.input_rect)
        pygame.draw.rect(self.screen, border_color, self.input_rect, 2)

        # Input text (uppercase retro style)
        display_text = self.input_text.upper()
        text_surface = self.font.render(display_text, True, self.retro_cyan)
        text_x = self.input_rect.x + 10
        text_y = self.input_rect.y + (INPUT_BOX_HEIGHT - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))
        
        # Blinking cursor (retro block)
        if self.input_active and int(self.pulse_time * 2) % 2 == 0:
            cursor_x = text_x + text_surface.get_width() + 5
            cursor_rect = pygame.Rect(cursor_x, text_y, 8, text_surface.get_height())
            pygame.draw.rect(self.screen, self.retro_yellow, cursor_rect)

        # Placeholder
        if not self.input_text and not self.input_active:
            placeholder = self.small_font.render(">>> ENTER WEAPON PROMPT <<<", True, (100, 100, 100))
            self.screen.blit(placeholder, (text_x, text_y + 5))

        # Forge button (retro arcade button)
        pygame.draw.rect(self.screen, self.retro_magenta, self.forge_button_rect.inflate(4, 4), 3)
        pygame.draw.rect(self.screen, (0, 0, 0), self.forge_button_rect)
        pygame.draw.rect(self.screen, self.retro_magenta, self.forge_button_rect, 2)

        # Button text
        button_text = self.font.render("FORGE!", True, self.retro_yellow)
        text_rect = button_text.get_rect(center=self.forge_button_rect.center)
        self.screen.blit(button_text, text_rect)
        
        # Instruction
        instruction = self.small_font.render("[ENTER] TO FORGE", True, self.retro_cyan)
        inst_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))
        self.screen.blit(instruction, inst_rect)

    def _draw_retro_notifications(self):
        """Draw retro-style notifications."""
        y_base = 110

        for i, notif in enumerate(self.notifications):
            y = y_base + i * 30

            # Retro notification box
            text_surface = self.font.render(notif['message'], True, notif['color'])
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y))

            # Box background
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, notif['color'], bg_rect, 2)

            self.screen.blit(text_surface, text_rect)

    def _draw_retro_game_info(self):
        """Draw retro game info."""
        # Controls in retro style
        controls = [
            "[P1] W/A/S/D",
            "[P2] ARROWS"
        ]
        y = SCREEN_HEIGHT - 130
        for text in controls:
            surf = self.small_font.render(text, True, self.retro_cyan)
            self.screen.blit(surf, (15, y))
            y += 20

    def _draw_crt_effect(self):
        """Draw CRT monitor effect."""
        # Vignette effect (darker edges)
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(100):
            alpha = int(i * 0.5)
            thickness = 100 - i
            rect = pygame.Rect(i, i, SCREEN_WIDTH - i * 2, SCREEN_HEIGHT - i * 2)
            pygame.draw.rect(vignette, (0, 0, 0, alpha), rect, 1)
        self.screen.blit(vignette, (0, 0))

    def reset_timer(self):
        """Reset the round timer."""
        self.time_remaining = ROUND_TIME
        self.show_banner = True
        self.banner_alpha = 255
        self.banner_timer = 2.5

    def get_forge_cooldown(self, player_id):
        """Get remaining cooldown time for a player."""
        return self.forge_cooldowns.get(player_id, 0)

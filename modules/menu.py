# modules/menu.py
# Main menu system with room creation and joining
# T3: UI

import pygame
from settings import *
from modules.menu_background import (
    create_menu_background, 
    draw_animated_stars, 
    draw_grid_lines, 
    draw_menu_particles
)
from modules.network import get_local_ip


class Button:
    """Retro-style button for menu."""
    
    def __init__(self, x, y, width, height, text, color=(0, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        self.click_animation = 0
        
    def update(self, mouse_pos, dt):
        """Update button state."""
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.click_animation > 0:
            self.click_animation = max(0, self.click_animation - dt * 5)
    
    def draw(self, surface, font):
        """Draw retro button."""
        offset = int(self.click_animation * 5)
        rect = self.rect.copy()
        rect.x += offset
        rect.y += offset
        
        color = self.color
        if self.hover:
            color = tuple(min(255, c + 50) for c in color)
        
        pygame.draw.rect(surface, color, rect.inflate(6, 6), 3)
        pygame.draw.rect(surface, (0, 0, 0), rect)
        pygame.draw.rect(surface, color, rect, 2)
        
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


class TextInput:
    """Retro-style text input box."""
    
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def update(self, dt):
        """Update text input."""
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def handle_event(self, event):
        """Handle input events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif len(self.text) < 20 and event.unicode.isprintable():
                self.text += event.unicode
        
        return False
    
    def draw(self, surface, font):
        """Draw text input box."""
        color = (255, 255, 0) if self.active else (0, 255, 255)
        
        pygame.draw.rect(surface, color, self.rect.inflate(6, 6), 3)
        pygame.draw.rect(surface, (0, 0, 0), self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        display_text = self.text.upper() if self.text else self.placeholder
        text_color = color if self.text else (100, 100, 100)
        text_surf = font.render(display_text, True, text_color)
        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        surface.blit(text_surf, (text_x, text_y))
        
        if self.active and self.cursor_visible and self.text:
            cursor_x = text_x + text_surf.get_width() + 5
            cursor_rect = pygame.Rect(cursor_x, text_y, 8, text_surf.get_height())
            pygame.draw.rect(surface, color, cursor_rect)


class MenuScreen:
    """Main menu system."""
    
    def __init__(self, screen):
        self.screen = screen
        self.state = "HOME"
        self.room_code = ""
        self.room_name = ""
        self.server_ip = ""

        self.title_font = pygame.font.Font(None, 72)
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        
        self.background = create_menu_background(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.time = 0
        self.particles = []
        
        self.cyan = (0, 255, 255)
        self.magenta = (255, 0, 255)
        self.yellow = (255, 255, 0)
        
        self._init_home_screen()
        self._init_create_room_screen()
        self._init_join_room_screen()
    
    def _init_home_screen(self):
        """Initialize home screen elements."""
        center_x = SCREEN_WIDTH // 2
        
        self.home_buttons = [
            Button(center_x - 150, 300, 300, 60, "CREATE ROOM", self.cyan),
            Button(center_x - 150, 400, 300, 60, "JOIN ROOM", self.magenta),
            Button(center_x - 150, 500, 300, 60, "QUIT", self.yellow),
        ]
    
    def _init_create_room_screen(self):
        """Initialize create room screen elements."""
        center_x = SCREEN_WIDTH // 2
        
        self.room_name_input = TextInput(center_x - 200, 280, 400, 50, ">>> ENTER ROOM NAME <<<")
        self.create_buttons = [
            Button(center_x - 150, 420, 300, 60, "CREATE LOBBY", self.cyan),
            Button(center_x - 150, 500, 300, 60, "BACK", self.yellow),
        ]
    
    def _init_join_room_screen(self):
        """Initialize join room screen elements."""
        center_x = SCREEN_WIDTH // 2
        
        # Properly aligned with labels - label at 170, input at 200 (30px gap)
        self.server_ip_input = TextInput(center_x - 200, 200, 400, 50, ">>> SERVER IP <<<")
        # Label at 290, input at 320 (30px gap)
        self.room_code_input = TextInput(center_x - 200, 320, 400, 50, ">>> ROOM CODE <<<")
        self.join_buttons = [
            Button(center_x - 150, 440, 300, 60, "JOIN", self.magenta),
            Button(center_x - 150, 520, 300, 60, "BACK", self.yellow),
        ]
    
    def update(self, dt):
        """Update menu state."""
        self.time += dt
        mouse_pos = pygame.mouse.get_pos()
        
        if self.state == "HOME":
            for button in self.home_buttons:
                button.update(mouse_pos, dt)
        elif self.state == "CREATE_ROOM":
            self.room_name_input.update(dt)
            for button in self.create_buttons:
                button.update(mouse_pos, dt)
        elif self.state == "JOIN_ROOM":
            self.server_ip_input.update(dt)
            self.room_code_input.update(dt)
            for button in self.join_buttons:
                button.update(mouse_pos, dt)
    
    def handle_event(self, event):
        """Handle menu events."""
        if self.state == "HOME":
            return self._handle_home_events(event)
        elif self.state == "CREATE_ROOM":
            return self._handle_create_room_events(event)
        elif self.state == "JOIN_ROOM":
            return self._handle_join_room_events(event)
        return None
    
    def _handle_home_events(self, event):
        """Handle home screen events."""
        if self.home_buttons[0].is_clicked(event):
            self.state = "CREATE_ROOM"
        elif self.home_buttons[1].is_clicked(event):
            self.state = "JOIN_ROOM"
            # Pre-fill with local IP as hint
            self.server_ip_input.text = get_local_ip()
        elif self.home_buttons[2].is_clicked(event):
            return "QUIT"
        return None
    
    def _handle_create_room_events(self, event):
        """Handle create room screen events."""
        if self.room_name_input.handle_event(event):
            if self.room_name_input.text.strip():
                self.room_name = self.room_name_input.text
                return "CREATE_LOBBY"

        if self.create_buttons[0].is_clicked(event):
            if self.room_name_input.text.strip():
                self.room_name = self.room_name_input.text
                return "CREATE_LOBBY"
        elif self.create_buttons[1].is_clicked(event):
            self.state = "HOME"
            self.room_name_input.text = ""
        return None
    
    def _handle_join_room_events(self, event):
        """Handle join room screen events."""
        self.server_ip_input.handle_event(event)

        if self.room_code_input.handle_event(event):
            if self.room_code_input.text.strip() and self.server_ip_input.text.strip():
                self.room_code = self.room_code_input.text
                self.server_ip = self.server_ip_input.text
                return "JOIN_GAME"
        
        if self.join_buttons[0].is_clicked(event):
            if self.room_code_input.text.strip() and self.server_ip_input.text.strip():
                self.room_code = self.room_code_input.text
                self.server_ip = self.server_ip_input.text
                return "JOIN_GAME"
        elif self.join_buttons[1].is_clicked(event):
            self.state = "HOME"
            self.room_code_input.text = ""
            self.server_ip_input.text = ""
        return None
    
    def draw(self):
        """Draw menu screen."""
        self.screen.blit(self.background, (0, 0))
        draw_grid_lines(self.screen, self.time)
        draw_animated_stars(self.screen, self.time)
        draw_menu_particles(self.screen, self.particles, 1/60)
        
        if self.state == "HOME":
            self._draw_home_screen()
        elif self.state == "CREATE_ROOM":
            self._draw_create_room_screen()
        elif self.state == "JOIN_ROOM":
            self._draw_join_room_screen()
        
        self._draw_scan_lines()
    
    def _draw_home_screen(self):
        """Draw home screen."""
        title_text = "PROMPT WARS"
        
        for offset in [(-3, -3), (3, 3)]:
            shadow = self.title_font.render(title_text, True, self.magenta)
            shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + offset[0], 150 + offset[1]))
            self.screen.blit(shadow, shadow_rect)
        
        title = self.title_font.render(title_text, True, self.cyan)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font.render(">>> AI WEAPON FIGHTING <<<", True, self.yellow)
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle, sub_rect)
        
        for button in self.home_buttons:
            button.draw(self.screen, self.font)
        
        footer = self.small_font.render("RETRO EDITION - 2026", True, (100, 100, 100))
        footer_rect = footer.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        self.screen.blit(footer, footer_rect)
    
    def _draw_create_room_screen(self):
        """Draw create room screen."""
        title = self.title_font.render("CREATE ROOM", True, self.cyan)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)
        
        instruction = self.small_font.render("ENTER A NAME FOR YOUR ROOM", True, self.yellow)
        inst_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(instruction, inst_rect)
        
        # Show local IP
        local_ip = get_local_ip()
        ip_text = self.small_font.render(f"YOUR IP: {local_ip}", True, self.cyan)
        ip_rect = ip_text.get_rect(center=(SCREEN_WIDTH // 2, 360))
        self.screen.blit(ip_text, ip_rect)

        self.room_name_input.draw(self.screen, self.font)
        
        for button in self.create_buttons:
            button.draw(self.screen, self.font)

        hint = self.small_font.render("Share your IP with other players!", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 390))
        self.screen.blit(hint, hint_rect)

    def _draw_join_room_screen(self):
        """Draw join room screen with clean layout."""
        # Title at top
        title = self.title_font.render("JOIN ROOM", True, self.magenta)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Server IP section - label positioned above input box
        instruction1 = self.small_font.render("HOST'S IP ADDRESS", True, self.yellow)
        inst1_rect = instruction1.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(instruction1, inst1_rect)

        self.server_ip_input.draw(self.screen, self.font)

        # Room code section - label positioned above input box
        instruction2 = self.small_font.render("ROOM CODE", True, self.yellow)
        inst2_rect = instruction2.get_rect(center=(SCREEN_WIDTH // 2, 290))
        self.screen.blit(instruction2, inst2_rect)

        self.room_code_input.draw(self.screen, self.font)
        
        # Buttons with proper spacing
        for button in self.join_buttons:
            button.draw(self.screen, self.font)

        # Bottom hint - properly positioned at bottom
        hint = self.small_font.render("Ask the host for their IP address and room code", True, (150, 150, 150))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
        self.screen.blit(hint, hint_rect)

    def _draw_scan_lines(self):
        """Draw retro scan line effect."""
        scan_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(scan_surface, (0, 0, 0, 30), (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(scan_surface, (0, 0))

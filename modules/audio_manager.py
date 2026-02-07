# modules/audio_manager.py
# Audio manager for background music and sound effects

import pygame
import os


class AudioManager:
    """Manages all audio for the game."""

    def __init__(self):
        """Initialize audio manager."""
        pygame.mixer.init()

        self.music_playing = False
        self.muted = False
        self.music_volume = 0.3  # 30% volume

        # Load audio icon - larger and MORE VISIBLE with bright colors
        try:
            self.audio_icon_original = pygame.image.load("assets/images/audio.png")
            # Tint it to make it more visible
            self.audio_icon = pygame.transform.scale(self.audio_icon_original, (50, 50))
        except:
            # Create a bright visible audio icon if file not found
            self.audio_icon = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.audio_icon, (255, 255, 0), (25, 25), 20, 4)
            pygame.draw.polygon(self.audio_icon, (255, 255, 0), [(12, 18), (12, 32), (5, 32), (5, 18)])

        self.button_rect = pygame.Rect(20, 100, 50, 50)

    def load_music(self, filepath):
        """Load background music."""
        try:
            if os.path.exists(filepath):
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)
                return True
            else:
                print(f"Music file not found: {filepath}")
                return False
        except Exception as e:
            print(f"Error loading music: {e}")
            return False

    def play_music(self, loops=-1):
        """Play background music. loops=-1 means infinite loop."""
        if not self.muted:
            try:
                pygame.mixer.music.play(loops)
                self.music_playing = True
            except Exception as e:
                print(f"Error playing music: {e}")

    def stop_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()
        self.music_playing = False

    def toggle_mute(self):
        """Toggle mute on/off."""
        self.muted = not self.muted

        if self.muted:
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(self.music_volume)

    def is_muted(self):
        """Check if audio is muted."""
        return self.muted

    def handle_click(self, pos):
        """Handle click on audio button."""
        if self.button_rect.collidepoint(pos):
            self.toggle_mute()
            return True
        return False

    def draw(self, screen):
        """Draw audio button with mute indicator - BRIGHT AND VISIBLE."""
        # Draw bright background for maximum visibility
        bg_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        bg_surface.fill((50, 50, 50, 200))  # Darker, more opaque background
        screen.blit(bg_surface, (self.button_rect.x - 5, self.button_rect.y - 5))

        # Create a tinted version of the icon for better visibility
        tinted_icon = self.audio_icon.copy()
        # Add a yellow tint overlay
        tint_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        tint_surface.fill((255, 255, 0, 100))  # Yellow tint
        tinted_icon.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Draw the tinted audio icon
        screen.blit(tinted_icon, self.button_rect)

        # Draw a bright yellow border for visibility
        pygame.draw.rect(screen, (255, 255, 0), self.button_rect, 3)

        # If muted, draw a VERY THICK red X over the icon
        if self.muted:
            pygame.draw.line(screen, (255, 0, 0),
                           (self.button_rect.left + 5, self.button_rect.top + 5),
                           (self.button_rect.right - 5, self.button_rect.bottom - 5), 8)
            pygame.draw.line(screen, (255, 0, 0),
                           (self.button_rect.right - 5, self.button_rect.top + 5),
                           (self.button_rect.left + 5, self.button_rect.bottom - 5), 8)


class FullscreenButton:
    """Button to toggle fullscreen mode."""

    def __init__(self):
        """Initialize fullscreen button."""
        self.button_rect = pygame.Rect(20, 160, 50, 50)
        self.is_fullscreen = False

        # Create windowed mode icon (small rectangle)
        self.windowed_icon = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(self.windowed_icon, (255, 255, 0), (10, 10, 30, 30), 4)

        # Create fullscreen mode icon (larger rectangle with arrows)
        self.fullscreen_icon = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.rect(self.fullscreen_icon, (255, 255, 0), (5, 5, 40, 40), 4)
        # Corner arrows
        pygame.draw.polygon(self.fullscreen_icon, (255, 255, 0), [(5, 15), (5, 5), (15, 5)])
        pygame.draw.polygon(self.fullscreen_icon, (255, 255, 0), [(45, 15), (45, 5), (35, 5)])
        pygame.draw.polygon(self.fullscreen_icon, (255, 255, 0), [(5, 35), (5, 45), (15, 45)])
        pygame.draw.polygon(self.fullscreen_icon, (255, 255, 0), [(35, 45), (45, 45), (45, 35)])

    def handle_click(self, pos):
        """Handle click on fullscreen button."""
        if self.button_rect.collidepoint(pos):
            self.is_fullscreen = not self.is_fullscreen
            pygame.display.toggle_fullscreen()
            return True
        return False

    def draw(self, screen):
        """Draw fullscreen button."""
        # Draw semi-transparent background
        bg_surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        screen.blit(bg_surface, (self.button_rect.x - 5, self.button_rect.y - 5))

        # Draw appropriate icon
        if self.is_fullscreen:
            screen.blit(self.windowed_icon, self.button_rect)
        else:
            screen.blit(self.fullscreen_icon, self.button_rect)

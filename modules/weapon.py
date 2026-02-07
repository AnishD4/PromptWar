# modules/weapon.py
# Weapon class - handles weapon properties, collision, damage
# T2: AI Weapons

import pygame
from settings import *
from modules.sprite_generator import create_retro_weapon_sprite


class Weapon:
    """Represents a weapon in the game."""

    def __init__(self, weapon_data, owner_id, x, y):
        """
        Initialize a weapon.

        Args:
            weapon_data: Dictionary with weapon properties from AI
                {
                    'name': str,
                    'damage': int,
                    'knockback': float,
                    'size': int,
                    'speed': float,
                    'color': tuple
                }
            owner_id: ID of player who forged this weapon
            x, y: Starting position
        """
        self.name = weapon_data.get('name', 'Unknown Weapon')
        self.damage = weapon_data.get('damage', 10)
        self.knockback = weapon_data.get('knockback', 5)
        self.size = weapon_data.get('size', 30)
        self.speed = weapon_data.get('speed', 3)
        self.color = weapon_data.get('color', YELLOW)
        self.gravity_affected = weapon_data.get('gravity_affected', False)
        self.lifetime = weapon_data.get('lifetime', 5.0)
        self.owner_id = owner_id

        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.velocity_x = self.speed
        self.velocity_y = 0
        self.active = True
        self.time_alive = 0

        # Visual
        self.rotation = 0
        self.has_hit = False

        # Optionally track where AI image bytes were saved (for debugging)
        self.saved_path = weapon_data.get('saved_path') if isinstance(weapon_data, dict) else None
        # Store AI-provided image surface if present
        self.image = weapon_data.get('image') if isinstance(weapon_data, dict) else None

    def set_direction(self, direction_x):
        """Set weapon travel direction (-1 for left, 1 for right)."""
        self.velocity_x = self.speed * direction_x

    def update(self, dt):
        """Update weapon position and physics."""
        if not self.active:
            return

        self.time_alive += dt

        # Check lifetime
        if self.time_alive >= self.lifetime:
            self.active = False
            return

        # Move weapon
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Apply gravity if affected
        if self.gravity_affected:
            if hasattr(settings, 'GRAVITY_STRENGTH'):
                self.velocity_y += settings.GRAVITY_STRENGTH
            else:
                self.velocity_y += GRAVITY * 0.5

        # Rotation for visual effect
        self.rotation += 5

        # Deactivate if off screen
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.top > SCREEN_HEIGHT):
            self.active = False

    def check_collision(self, player):
        """
        Check if weapon collides with a player.

        Args:
            player: Player object to check collision with

        Returns:
            True if collision occurred, False otherwise
        """
        if not self.active or not player.alive:
            return False

        if player.player_id == self.owner_id:
            return False  # Don't hit owner

        if self.rect.colliderect(player.rect):
            # Calculate knockback direction
            knockback_x = self.knockback if self.velocity_x > 0 else -self.knockback
            knockback_y = -abs(self.knockback) * 0.5

            player.take_damage(self.damage, knockback_x, knockback_y)
            self.active = False
            return True

        return False

    def draw(self, screen):
        """Draw the weapon with effects."""
        if self.active:
            # If this weapon has an AI image, draw that instead of projectile graphics
            try:
                surf = self.get_surface()
                if surf:
                    rect = surf.get_rect(center=self.rect.center)
                    screen.blit(surf, rect)
                    return
            except Exception:
                pass
            # Draw glow effect
            glow_size = int(self.size * 1.4)
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, 60),
                             (glow_size // 2, glow_size // 2), glow_size // 2)
            glow_rect = glow_surface.get_rect(center=self.rect.center)
            screen.blit(glow_surface, glow_rect)

            # Draw main projectile
            pygame.draw.circle(screen, self.color, self.rect.center, self.size // 2)
            pygame.draw.circle(screen, WHITE, self.rect.center, self.size // 2, 2)

            # Draw inner glow
            inner_color = tuple(min(255, c + 100) for c in self.color)
            pygame.draw.circle(screen, inner_color, self.rect.center, self.size // 4)

            # Draw trail
            trail_length = 15
            trail_surface = pygame.Surface((trail_length, self.size // 2), pygame.SRCALPHA)
            for i in range(trail_length):
                alpha = int(100 * (1 - i / trail_length))
                if self.velocity_x > 0:
                    trail_x = self.rect.left - i
                else:
                    trail_x = self.rect.right + i
                pygame.draw.line(screen, (*self.color, alpha),
                               (trail_x, self.rect.centery),
                               (trail_x, self.rect.centery), 2)

    def get_surface(self, desired_size=None):
        """Return a pygame.Surface for this weapon: AI image if present, else generated sprite.

        desired_size: optional (w,h) or single int for square.
        """
        # If AI supplied an image surface, return a copy (scaled if requested)
        if getattr(self, 'image', None):
            try:
                surf = self.image
                if desired_size:
                    if isinstance(desired_size, int):
                        size = (desired_size, desired_size)
                    else:
                        size = desired_size
                    return pygame.transform.smoothscale(surf, size)
                return surf
            except Exception:
                pass

        # Fallback: generated retro sprite
        try:
            sprite = create_retro_weapon_sprite(self.name or 'weapon', self.color, size=self.size)
            return sprite
        except Exception:
            # Very basic fallback
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(s, self.color, (self.size//2, self.size//2), self.size//2)
            return s


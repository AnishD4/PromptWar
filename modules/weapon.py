# modules/weapon.py
# Weapon class - handles weapon properties, collision, damage
# T2: AI Weapons

import pygame
from settings import *


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
        self.owner_id = owner_id

        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.velocity_x = self.speed
        self.velocity_y = 0
        self.active = True

    def update(self, dt):
        """Update weapon position and physics."""
        if not self.active:
            return

        # Move weapon
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Apply gravity (if weapon falls)
        self.velocity_y += GRAVITY * 0.5

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
        """Draw the weapon."""
        if self.active:
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw a simple weapon icon (sword-like)
            pygame.draw.line(screen, WHITE,
                           (self.rect.centerx, self.rect.top),
                           (self.rect.centerx, self.rect.bottom), 2)


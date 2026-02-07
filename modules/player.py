# modules/player.py
# Player class - handles movement, knockback, health
# T1: Gameplay / Player

import pygame
from settings import *


class Player:
    """Represents a player character in the game."""

    def __init__(self, player_id, x, y, color):
        """
        Initialize a player.

        Args:
            player_id: Unique identifier for the player
            x, y: Starting position
            color: Player color tuple (R, G, B)
        """
        self.player_id = player_id
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.color = color
        self.health = MAX_HEALTH
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.alive = True
        self.respawn_timer = 0

        # Event callbacks
        self.health_changed_callback = None

    def set_health_changed_callback(self, callback):
        """Set callback for health changes: callback(player_id, new_health)"""
        self.health_changed_callback = callback

    def update(self, platforms, dt):
        """Update player physics and position."""
        if not self.alive:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.respawn()
            return

        # Apply gravity
        self.velocity_y += GRAVITY

        # Update position
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Platform collision (placeholder)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform) and self.velocity_y > 0:
                self.rect.bottom = platform.top
                self.velocity_y = 0
                self.on_ground = True

        # Check if fallen off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.take_damage(50)  # Fall damage

    def move(self, direction):
        """Move player left (-1) or right (1)."""
        self.velocity_x = direction * PLAYER_SPEED

    def jump(self):
        """Make player jump if on ground."""
        if self.on_ground:
            self.velocity_y = -JUMP_STRENGTH

    def take_damage(self, damage, knockback_x=0, knockback_y=0):
        """
        Apply damage and knockback to player.

        Args:
            damage: Amount of damage to take
            knockback_x, knockback_y: Knockback force
        """
        self.health -= damage
        self.velocity_x += knockback_x
        self.velocity_y += knockback_y

        # Trigger health changed event
        if self.health_changed_callback:
            self.health_changed_callback(self.player_id, max(0, self.health))

        if self.health <= 0:
            self.die()

    def die(self):
        """Handle player death."""
        self.alive = False
        self.respawn_timer = RESPAWN_TIME

    def respawn(self):
        """Respawn player at starting position."""
        self.health = MAX_HEALTH
        self.alive = True
        self.velocity_x = 0
        self.velocity_y = 0
        # Reset position (would be set by game_manager)
        if self.health_changed_callback:
            self.health_changed_callback(self.player_id, self.health)

    def draw(self, screen):
        """Draw the player."""
        if self.alive:
            pygame.draw.rect(screen, self.color, self.rect)
            # Draw a simple face
            eye_y = self.rect.y + 20
            pygame.draw.circle(screen, BLACK, (self.rect.x + 12, eye_y), 3)
            pygame.draw.circle(screen, BLACK, (self.rect.x + 28, eye_y), 3)


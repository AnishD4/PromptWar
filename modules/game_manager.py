# modules/game_manager.py
# Game Manager - handles round management, respawn logic, game state
# T1: Gameplay / Player

import pygame
from settings import *


class GameManager:
    """Manages game state, rounds, and player spawning."""

    def __init__(self):
        """Initialize game manager."""
        self.players = []
        self.weapons = []
        self.round_active = False
        self.round_number = 1
        self.player_scores = {}  # {player_id: score}

        # Spawn points for players
        self.spawn_points = [
            (200, 400),
            (900, 400),
            (300, 200),
            (800, 200)
        ]

    def add_player(self, player):
        """
        Add a player to the game.

        Args:
            player: Player object
        """
        self.players.append(player)
        self.player_scores[player.player_id] = 0

    def add_weapon(self, weapon):
        """
        Add a weapon to the game.

        Args:
            weapon: Weapon object
        """
        self.weapons.append(weapon)

    def start_round(self):
        """Start a new round."""
        self.round_active = True

        # Respawn all players at spawn points
        for i, player in enumerate(self.players):
            if i < len(self.spawn_points):
                spawn_x, spawn_y = self.spawn_points[i]
                player.rect.x = spawn_x
                player.rect.y = spawn_y
                player.respawn()

        # Clear weapons
        self.weapons.clear()

    def end_round(self):
        """End the current round."""
        self.round_active = False
        self.round_number += 1

        # Calculate scores (placeholder)
        for player in self.players:
            if player.alive:
                self.player_scores[player.player_id] += 1

    def update(self, dt):
        """
        Update game state.

        Args:
            dt: Delta time in seconds
        """
        if not self.round_active:
            return

        # Update all players
        for player in self.players:
            player.update(PLATFORMS, dt)

        # Update all weapons
        for weapon in self.weapons[:]:
            weapon.update(dt)

            # Check weapon collisions with players
            for player in self.players:
                weapon.check_collision(player)

            # Remove inactive weapons
            if not weapon.active:
                self.weapons.remove(weapon)

    def draw_platforms(self, screen):
        """Draw all platforms."""
        if PLATFORMS:
            for platform in PLATFORMS:
                pygame.draw.rect(screen, PLATFORM_COLOR, platform)
                pygame.draw.rect(screen, WHITE, platform, 2)  # Border

    def draw_weapons(self, screen):
        """Draw all weapons."""
        for weapon in self.weapons:
            weapon.draw(screen)

    def draw_players(self, screen):
        """Draw all players."""
        for player in self.players:
            player.draw(screen)

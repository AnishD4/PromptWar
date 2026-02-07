# modules/ai_client.py
# AI Client - handles communication with AI backend for weapon generation
# T2: AI Weapons

import random
from settings import *


class AIClient:
    """Handles AI weapon generation from prompts."""

    def __init__(self):
        """Initialize AI client."""
        self.weapon_spawned_callback = None
        self.is_processing = False

    def set_weapon_spawned_callback(self, callback):
        """Set callback for weapon spawned: callback(weapon_data, player_id)"""
        self.weapon_spawned_callback = callback

    def forge_weapon(self, prompt, player_id):
        """
        Generate a weapon from a text prompt.

        Args:
            prompt: Text description of weapon to create
            player_id: ID of player forging the weapon

        Returns:
            Dictionary with weapon data or None if failed
        """
        if self.is_processing:
            return None

        self.is_processing = True

        # TODO: Replace with actual AI API call
        # For now, generate mock weapon based on prompt keywords
        weapon_data = self._generate_mock_weapon(prompt)

        self.is_processing = False

        # Trigger weapon spawned callback
        if self.weapon_spawned_callback and weapon_data:
            self.weapon_spawned_callback(weapon_data, player_id)

        return weapon_data

    def _generate_mock_weapon(self, prompt):
        """
        Generate mock weapon data based on prompt (placeholder for AI).

        Args:
            prompt: Text description

        Returns:
            Dictionary with weapon properties
        """
        prompt_lower = prompt.lower()

        # Parse prompt for keywords
        damage = 10
        knockback = 5
        size = 30
        speed = 3
        color = YELLOW
        name = "Forged Weapon"

        # Damage modifiers
        if any(word in prompt_lower for word in ['massive', 'huge', 'giant', 'powerful']):
            damage += 15
            size += 20
            knockback += 3
            name = f"Massive {prompt.split()[0].capitalize()}"
        elif any(word in prompt_lower for word in ['quick', 'fast', 'swift', 'rapid']):
            damage += 5
            speed += 4
            name = f"Swift {prompt.split()[0].capitalize()}"

        # Weapon type
        if 'sword' in prompt_lower:
            damage += 10
            color = (200, 200, 255)
            name = "Forged Sword"
        elif 'hammer' in prompt_lower:
            damage += 15
            knockback += 5
            speed -= 1
            color = (150, 150, 150)
            name = "Mighty Hammer"
        elif 'spear' in prompt_lower:
            damage += 12
            speed += 2
            size = 40
            color = (255, 200, 100)
            name = "Sharp Spear"
        elif 'axe' in prompt_lower:
            damage += 13
            knockback += 3
            color = (180, 100, 100)
            name = "Heavy Axe"

        # Element modifiers
        if 'fire' in prompt_lower:
            damage += 8
            color = (255, 100, 0)
            name = f"Flaming {name}"
        elif 'ice' in prompt_lower:
            damage += 5
            speed -= 1
            color = (100, 200, 255)
            name = f"Frozen {name}"
        elif 'lightning' in prompt_lower:
            damage += 10
            speed += 3
            color = (255, 255, 100)
            name = f"Lightning {name}"

        return {
            'name': name,
            'damage': min(damage, 50),  # Cap damage
            'knockback': min(knockback, 15),  # Cap knockback
            'size': min(size, 60),  # Cap size
            'speed': max(1, min(speed, 10)),  # Cap speed
            'color': color
        }


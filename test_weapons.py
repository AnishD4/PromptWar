# test_weapons.py
# Test weapon generator for development/testing
# AI-ready: Easy to modify weapon properties

import random
from settings import *


class TestWeaponGenerator:
    """
    Generate test weapons for development.

    AI-Friendly:
    - Clear weapon templates
    - Easy-to-modify properties
    - Randomization for variety
    """

    WEAPON_TEMPLATES = {
        "fireball": {
            "name": "🔥 Fireball",
            "damage": 20,
            "knockback": 10,
            "speed": 8,
            "size": 30,
            "color": (255, 100, 50),
            "lifetime": 3.0,
            "gravity_affected": False,
        },
        "ice_shard": {
            "name": "❄️ Ice Shard",
            "damage": 15,
            "knockback": 8,
            "speed": 10,
            "size": 25,
            "color": (100, 200, 255),
            "lifetime": 2.5,
            "gravity_affected": False,
        },
        "boulder": {
            "name": "🪨 Boulder",
            "damage": 30,
            "knockback": 15,
            "speed": 5,
            "size": 45,
            "color": (120, 100, 80),
            "lifetime": 4.0,
            "gravity_affected": True,
        },
        "energy_blast": {
            "name": "⚡ Energy Blast",
            "damage": 18,
            "knockback": 12,
            "speed": 12,
            "size": 28,
            "color": (255, 255, 100),
            "lifetime": 2.0,
            "gravity_affected": False,
        },
        "poison_cloud": {
            "name": "☠️ Poison Cloud",
            "damage": 12,
            "knockback": 5,
            "speed": 4,
            "size": 50,
            "color": (100, 255, 100),
            "lifetime": 5.0,
            "gravity_affected": False,
        },
    }

    @staticmethod
    def generate_random_weapon():
        """Generate a random test weapon."""
        template_name = random.choice(list(TestWeaponGenerator.WEAPON_TEMPLATES.keys()))
        return TestWeaponGenerator.get_weapon(template_name)

    @staticmethod
    def get_weapon(template_name):
        """
        Get a specific weapon by template name.

        Args:
            template_name: Key from WEAPON_TEMPLATES

        Returns:
            dict: Weapon data
        """
        if template_name in TestWeaponGenerator.WEAPON_TEMPLATES:
            return TestWeaponGenerator.WEAPON_TEMPLATES[template_name].copy()
        else:
            # Default weapon
            return {
                "name": "✨ Magic Missile",
                "damage": 15,
                "knockback": 8,
                "speed": 7,
                "size": 25,
                "color": (200, 100, 255),
                "lifetime": 3.0,
                "gravity_affected": False,
            }

    @staticmethod
    def get_all_weapon_names():
        """Get list of all weapon template names."""
        return list(TestWeaponGenerator.WEAPON_TEMPLATES.keys())


# Convenience functions for quick testing
def get_fireball():
    """Quick access to fireball weapon."""
    return TestWeaponGenerator.get_weapon("fireball")


def get_random_weapon():
    """Quick access to random weapon."""
    return TestWeaponGenerator.generate_random_weapon()


if __name__ == "__main__":
    # Test the generator
    print("=== Test Weapon Generator ===")
    print("\nAvailable weapons:")
    for name in TestWeaponGenerator.get_all_weapon_names():
        print(f"  - {name}")

    print("\nRandom weapon:")
    weapon = get_random_weapon()
    print(f"  Name: {weapon['name']}")
    print(f"  Damage: {weapon['damage']}")
    print(f"  Speed: {weapon['speed']}")
    print(f"  Color: {weapon['color']}")


import pygame
from modules.weapon import Weapon
from modules.player import Player
from settings import *

pygame.init()
# Create a surface to draw on
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

# Sample weapon data
weapon_data = {
    'name': 'Test Sword',
    'damage': 12,
    'knockback': 6,
    'size': 32,
    'speed': 5,
    'color': (200, 200, 255)
}

# Create weapon and player
weapon = Weapon(weapon_data, owner_id=0, x=100, y=100)
player = Player(1, 110, 100, (255, 0, 0))

# Update and draw
weapon.update(0.016)
weapon.draw(screen)

# Check collision
collided = weapon.check_collision(player)
print('Collision occurred:', collided)

pygame.quit()


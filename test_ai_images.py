"""
Test AI image generation: forge three sample prompts and report whether an AI image surface
was attached to the returned weapon_data. Any returned surfaces are saved as PNGs.

Usage:
  .\venv312\Scripts\Activate
  python test_ai_images.py

This script respects environment variables:
  HACKCLUB_API_KEY (required to attempt AI image generation)
  REMOVE_BG_API_KEY (optional)

If no HACKCLUB_API_KEY is set the script will report that the mock generator was used.
"""

import os
import pygame
from modules.ai_client import AIClient

pygame.init()

prompts = [
    "flaming sword",
    "icy spear",
    "giant Tiger"
]

ai = AIClient()
results = []

# Callback will be used by AIClient when it completes (synchronous in current impl)
def _cb(weapon_data, player_id):
    has_image = 'image' in weapon_data and weapon_data['image'] is not None
    size = None
    path = None
    bg_removed = weapon_data.get('bg_removed') if isinstance(weapon_data, dict) else None
    bg_has_alpha = weapon_data.get('bg_has_alpha') if isinstance(weapon_data, dict) else None
    if has_image:
        surf = weapon_data['image']
        try:
            size = surf.get_size()
            # Save to disk for inspection
            fname = f"ai_image_{player_id}_{weapon_data.get('name','weapon').replace(' ','_')}.png"
            pygame.image.save(surf, fname)
            path = os.path.abspath(fname)
        except Exception as e:
            path = f"save_failed: {e}"
    results.append({'prompt': cur_prompt, 'has_image': has_image, 'size': size, 'path': path, 'bg_removed': bg_removed, 'bg_has_alpha': bg_has_alpha, 'data': weapon_data})

ai.set_weapon_spawned_callback(_cb)

print('HACKCLUB_API_KEY set:', bool(os.environ.get('HACKCLUB_API_KEY')))
print('REMOVE_BG_API_KEY set:', bool(os.environ.get('REMOVE_BG_API_KEY')))

for i, p in enumerate(prompts):
    cur_prompt = p
    print(f"\nForging prompt ({i+1}/3): {p}")
    ai.forge_weapon(p, i)

# Summary
print('\nResults:')
for r in results:
    print(f"Prompt: {r['prompt']}, has_image: {r['has_image']}, size: {r['size']}, saved: {r['path']}, bg_removed: {r['bg_removed']}, bg_has_alpha: {r['bg_has_alpha']}")

pygame.quit()


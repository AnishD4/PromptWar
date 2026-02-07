# modules/ai_client.py
# AI Client - handles communication with AI backend for weapon generation
# T2: AI Weapons

import os
import io
import time
import base64
import requests
import pygame
from settings import *

# Optional: load keys from a local .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # python-dotenv is optional; if not installed, environment variables still work
    pass

# Ensure generated images directory exists
GENERATED_DIR = os.path.join('assets', 'generated')
if not os.path.exists(GENERATED_DIR):
    try:
        os.makedirs(GENERATED_DIR, exist_ok=True)
    except Exception:
        pass


class AIClient:
    """Handles AI weapon generation from prompts."""

    def __init__(self):
        """Initialize AI client."""
        self.weapon_spawned_callback = None
        self.is_processing = False

        # Read API keys from environment - safer than hardcoding
        self.hackclub_key = os.environ.get('HACKCLUB_API_KEY')
        self.removebg_key = os.environ.get('REMOVE_BG_API_KEY')

    def set_weapon_spawned_callback(self, callback):
        """Set callback for weapon spawned: callback(weapon_data, player_id)"""
        self.weapon_spawned_callback = callback

    def _post_with_retries(self, url, headers=None, json=None, files=None, data=None, timeout=60, retries=2, backoff=1.5):
        """POST with simple retry/backoff, returns requests.Response or raises."""
        last_exc = None
        for attempt in range(1, retries + 1):
            try:
                resp = requests.post(url, headers=headers, json=json, files=files, data=data, timeout=timeout)
                return resp
            except Exception as e:
                last_exc = e
                time.sleep(backoff * attempt)
        raise last_exc

    def forge_weapon(self, prompt, player_id):
        """
        Generate a weapon from a text prompt.

        If HACKCLUB_API_KEY (and optionally REMOVE_BG_API_KEY) are set in the
        environment, this will attempt to (1) refine the prompt, (2) request an
        image from HackClub, (3) remove the background via remove.bg, and (4)
        return a pygame.Surface attached to weapon_data['image'].

        If the API keys are not present or calls fail, falls back to the
        internal mock weapon generator.
        """
        if self.is_processing:
            return None
        self.is_processing = True

        weapon_data = None

        # Try real AI flow only if we have a HackClub API key
        if self.hackclub_key:
            try:
                weapon_data = self._forge_with_ai(prompt)
            except Exception as e:
                print('AI image generation failed, falling back to mock:', e)
                weapon_data = None

        # Fallback to mock generator
        if weapon_data is None:
            weapon_data = self._generate_mock_weapon(prompt)

        self.is_processing = False

        # Trigger weapon spawned callback
        if self.weapon_spawned_callback and weapon_data:
            try:
                self.weapon_spawned_callback(weapon_data, player_id)
            except Exception as e:
                print('Error in weapon_spawned_callback:', e)

        return weapon_data

    def _save_bytes_to_file(self, bts, prompt):
        """Save binary image bytes into GENERATED_DIR with safe filename and return path."""
        try:
            safe = ''.join(c if c.isalnum() else '_' for c in (prompt or 'weapon'))[:40]
            ts = int(time.time())
            fname = f"ai_{safe}_{ts}.png"
            path = os.path.join(GENERATED_DIR, fname)
            with open(path, 'wb') as f:
                f.write(bts)
            return path
        except Exception as e:
            print('Failed to save AI image to disk:', e)
            return None

    def _forge_with_ai(self, prompt):
        """Perform two-step AI call: refine prompt, generate image, remove bg."""
        headers = {
            'Authorization': f'Bearer {self.hackclub_key}',
            'Content-Type': 'application/json'
        }

        def _has_alpha_bytes(bts):
            """Return True if image bytes appear to contain an alpha channel."""
            try:
                img = pygame.image.load(io.BytesIO(bts))
                # Check per-pixel alpha mask or alpha channel
                masks = img.get_masks() if hasattr(img, 'get_masks') else (0,0,0,0)
                has_alpha = False
                try:
                    if len(masks) >= 4 and masks[3] != 0:
                        has_alpha = True
                except Exception:
                    pass
                try:
                    if img.get_alpha() is not None:
                        has_alpha = True
                except Exception:
                    pass
                try:
                    if img.get_flags() & pygame.SRCALPHA:
                        has_alpha = True
                except Exception:
                    pass
                return has_alpha
            except Exception:
                return False

        # Step 1: refine prompt (explicit about visibility, game icon, retro style)
        refine_payload = {
            'model': 'qwen/qwen3-32b',
            'messages': [
                {
                    'role': 'user',
                    'content': (
                        f"Make this prompt very specific for a weapon image: {prompt}. "
                        "Output a concise, detailed image prompt suitable for an image-generation model. "
                        "Important constraints: produce a single square PNG with a TRANSPARENT BACKGROUND, "
                        "in RETRO PIXEL-ART style (pixelated, limited palette), suitable for a 2D game sprite/icon. "
                        "Ensure the weapon is FULLY VISIBLE and clearly readable at small icon sizes. "
                        "This is an in-game icon; center the weapon, prioritize silhouette and visibility, no text. "
                        "Return only the prompt text for image generation."
                    )
                }
            ]
        }
        resp = self._post_with_retries('https://ai.hackclub.com/proxy/v1/chat/completions', headers=headers, json=refine_payload, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f'HackClub refine error: {resp.status_code} {resp.text}')
        refined = resp.json()
        specific_prompt = None
        try:
            specific_prompt = refined['choices'][0]['message']['content']
        except Exception:
            specific_prompt = prompt

        # Step 2: request image generation (model that supports image)
        image_payload = {
            'model': 'google/gemini-2.5-flash-image',
            'messages': [
                {
                    'role': 'user',
                    'content': (
                        f"Create a 32-bit PNG image for the following prompt: {specific_prompt}. "
                        "Constraints: output a single square PNG with TRANSPARENT BACKGROUND, pixel-art / retro aesthetic, "
                        "no text in image, centered composition, clean silhouette. This will be used as an in-game ICON — make the weapon fully visible and legible at icon size. "
                        "Return the image inline as base64 (data URL or b64_json) if possible."
                    )
                }
            ],
            'modalities': ['image', 'text'],
            'image_config': {'aspect_ratio': '1:1', 'size': '512x512'}
        }
        resp2 = self._post_with_retries('https://ai.hackclub.com/proxy/v1/chat/completions', headers=headers, json=image_payload, timeout=90)
        if resp2.status_code != 200:
            raise RuntimeError(f'HackClub image error: {resp2.status_code} {resp2.text}')
        out = resp2.json()

        # Parse image data - support base64 inline, b64_json, or returned URL
        image_bytes = None
        # 1) data URL (data:image/...) or http URL in image_url.url
        try:
            images_info = out['choices'][0]['message'].get('images')
            if images_info and len(images_info) > 0:
                info = images_info[0]
                image_url_field = info.get('image_url')
                if isinstance(image_url_field, dict):
                    image_url = image_url_field.get('url')
                else:
                    image_url = image_url_field

                if isinstance(image_url, str) and image_url.startswith('data:image'):
                    base64_data = image_url.split(',', 1)[1]
                    image_bytes = base64.b64decode(base64_data)
                elif isinstance(image_url, str) and image_url.startswith('http'):
                    # Download the image with retries
                    last_exc = None
                    for attempt in range(2):
                        try:
                            r = requests.get(image_url, timeout=30)
                            if r.status_code == 200:
                                image_bytes = r.content
                                break
                        except Exception as e:
                            last_exc = e
                            time.sleep(1.5 * (attempt + 1))
                    if image_bytes is None and last_exc:
                        raise last_exc
        except Exception:
            image_bytes = None

        # 2) b64_json field
        if image_bytes is None:
            try:
                b64 = out['choices'][0]['message']['images'][0].get('b64_json')
                if b64:
                    image_bytes = base64.b64decode(b64)
            except Exception:
                image_bytes = None

        # 3) search entire response for first data:image occurrence
        if image_bytes is None:
            try:
                txt = str(out)
                idx = txt.find('data:image')
                if idx != -1:
                    start = txt.find(',', idx) + 1
                    end = txt.find("'", start)
                    if end == -1:
                        end = len(txt)
                    b64data = txt[start:end]
                    image_bytes = base64.b64decode(b64data)
            except Exception:
                image_bytes = None

        if image_bytes is None:
            # Try one fallback image-generation attempt with a very explicit prompt
            try:
                fallback_prompt = (
                    f"Retro pixel-art icon sprite of: {specific_prompt}. "
                    "Return a single square PNG with TRANSPARENT BACKGROUND, centered weapon, no text, low color palette, sprite-style. Make it fully visible and readable as an in-game icon."
                )
                image_payload['messages'][0]['content'] = fallback_prompt
                resp3 = self._post_with_retries('https://ai.hackclub.com/proxy/v1/chat/completions', headers=headers, json=image_payload, timeout=90)
                if resp3.status_code == 200:
                    out2 = resp3.json()
                    # attempt same extraction logic on out2
                    try:
                        images_info = out2['choices'][0]['message'].get('images')
                        if images_info and len(images_info) > 0:
                            info = images_info[0]
                            image_url_field = info.get('image_url')
                            if isinstance(image_url_field, dict):
                                image_url = image_url_field.get('url')
                            else:
                                image_url = image_url_field
                            if isinstance(image_url, str) and image_url.startswith('data:image'):
                                base64_data = image_url.split(',', 1)[1]
                                image_bytes = base64.b64decode(base64_data)
                            elif isinstance(image_url, str) and image_url.startswith('http'):
                                r = requests.get(image_url, timeout=30)
                                if r.status_code == 200:
                                    image_bytes = r.content
                    except Exception:
                        # If parsing the fallback response fails, ensure we don't crash
                        image_bytes = None
            except Exception:
                image_bytes = None
            if image_bytes is None:
                raise RuntimeError('Could not extract image from AI response')

        # Optionally remove background via remove.bg
        final_bytes = image_bytes
        bg_removed = False
        bg_has_alpha = False
        try:
            bg_has_alpha = _has_alpha_bytes(image_bytes)
        except Exception:
            bg_has_alpha = False

        if self.removebg_key:
            try:
                r = self._post_with_retries(
                    'https://api.remove.bg/v1.0/removebg',
                    files={'image_file': io.BytesIO(image_bytes)},
                    data={'size': 'auto'},
                    headers={'X-Api-Key': self.removebg_key},
                    timeout=30
                )
                if r.status_code == 200:
                    final_bytes = r.content
                    bg_removed = True
                else:
                    print('remove.bg failed:', r.status_code, r.text)
                    # if original image already has alpha, consider background effectively removed
                    if bg_has_alpha:
                        bg_removed = True
            except Exception as e:
                print('remove.bg call failed:', e)
                if bg_has_alpha:
                    bg_removed = True

        # Save the final bytes to disk for inspection
        saved_path = None
        try:
            saved_path = self._save_bytes_to_file(final_bytes, prompt)
            if saved_path:
                print('Saved AI image to:', saved_path)
        except Exception as e:
            print('Failed to save final AI bytes:', e)

        # Load into pygame surface (robust against headless environments)
        try:
            image_file = io.BytesIO(final_bytes)
            image_file.seek(0)
            surf = pygame.image.load(image_file)
            try:
                surf = surf.convert_alpha()
            except Exception:
                try:
                    surf = surf.convert()
                except Exception:
                    pass
        except Exception as e:
            raise RuntimeError('Failed to load image into pygame surface: ' + str(e))

        # Now create a weapon data dict enriched with the image
        base = self._generate_mock_weapon(prompt)
        base['image'] = surf
        base['name'] = base.get('name', prompt)
        if saved_path:
            base['saved_path'] = saved_path
        base['bg_removed'] = bg_removed
        base['bg_has_alpha'] = bg_has_alpha
        return base

    def _generate_mock_weapon(self, prompt):
        """
        Generate mock weapon data based on prompt (placeholder for AI).

        Args:
            prompt: Text description

        Returns:
            Dictionary with weapon properties
        """
        prompt_lower = (prompt or '').lower()

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


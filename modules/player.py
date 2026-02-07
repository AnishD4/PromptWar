# modules/player.py
# T1: Enhanced Player Controller with smooth movement and attacks
# AI-ready: Clear structure for easy modification

import pygame
import math
from settings import *


class Player:
    """
    Player controller with polished movement and combat.

    AI-Friendly Features:
    - All constants in settings.py
    - Clear method separation
    - Event-driven system
    - Documented attack system
    """

    # Attack types
    ATTACK_NONE = 0
    ATTACK_SWING = 1
    ATTACK_THRUST = 2

    def __init__(self, player_id, x, y, color):
        """Initialize player."""
        self.player_id = player_id
        self.color = color

        # Position
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

        # Health
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.alive = True
        self.invulnerable = False
        self.invuln_timer = 0

        # State
        self.respawn_timer = 0
        self.hit_stun_timer = 0

        # Jump
        self.jumps_remaining = 2 if PLAYER_DOUBLE_JUMP else 1
        self.coyote_timer = 0

        # Attack
        self.attack_state = self.ATTACK_NONE
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_hitbox = None

        # Visual
        self.hit_flash_timer = 0
        self.anim_timer = 0

        # AI-generated content (set by main.py after prompt input)
        self.character_prompt = "warrior"
        self.weapon_prompt = "sword"
        self.character_image = None  # pygame.Surface from AI
        self.weapon_image = None  # pygame.Surface from AI

        # Callbacks
        self.on_health_changed = None
        self.on_attack = None

    def set_health_changed_callback(self, callback):
        """Set health callback."""
        self.on_health_changed = callback

    def update(self, platforms, dt):
        """Main update loop."""
        self._update_timers(dt)

        if not self.alive:
            self._update_death_state(dt)
            return

        # Physics
        self._apply_gravity()
        self._apply_friction()
        self.vel_y = min(self.vel_y, MAX_VELOCITY_Y)

        # Movement
        self._move_horizontal(platforms)
        self._move_vertical(platforms)
        self._handle_screen_bounds()

        # Attack
        self._update_attack(dt)

    def _update_timers(self, dt):
        """Update timers."""
        if self.invuln_timer > 0:
            self.invuln_timer -= dt
            self.invulnerable = self.invuln_timer > 0
        if self.hit_stun_timer > 0:
            self.hit_stun_timer -= dt
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= dt
        if self.coyote_timer > 0:
            self.coyote_timer -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        self.anim_timer += dt

    def _apply_gravity(self):
        """Apply gravity."""
        self.vel_y += GRAVITY_STRENGTH

    def _apply_friction(self):
        """Apply friction."""
        if self.on_ground:
            self.vel_x *= FRICTION_GROUND
        else:
            self.vel_x *= FRICTION_AIR
        if abs(self.vel_x) < 0.15:
            self.vel_x = 0

    def _move_horizontal(self, platforms):
        """Move horizontally."""
        self.rect.x += self.vel_x
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_x > 0:
                    self.rect.right = platform.left
                    self.vel_x = 0
                elif self.vel_x < 0:
                    self.rect.left = platform.right
                    self.vel_x = 0

    def _move_vertical(self, platforms):
        """Move vertically."""
        was_on_ground = self.on_ground
        self.rect.y += self.vel_y
        self.on_ground = False

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jumps_remaining = 2 if PLAYER_DOUBLE_JUMP else 1
                elif self.vel_y < 0:
                    self.rect.top = platform.bottom
                    self.vel_y = 0

        if was_on_ground and not self.on_ground:
            self.coyote_timer = 0.15

    def _handle_screen_bounds(self):
        """Handle screen edges."""
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vel_x = 0

        if self.rect.top > SCREEN_HEIGHT:
            self.die()

    def _update_death_state(self, dt):
        """Update death."""
        self.respawn_timer -= dt
        self.vel_y += GRAVITY_STRENGTH * 0.3
        self.rect.y += self.vel_y

    # ═══════════════════════════════════════════════════
    # PLAYER ACTIONS
    # ═══════════════════════════════════════════════════

    def move(self, direction):
        """Move with smooth acceleration."""
        if not self.alive or self.hit_stun_timer > 0:
            return

        if direction != 0:
            self.facing_right = direction > 0

        if self.on_ground:
            acceleration = 1.5
            target_speed = PLAYER_MOVE_SPEED
        else:
            acceleration = 0.8
            target_speed = PLAYER_AIR_SPEED

        self.vel_x += direction * acceleration

        if abs(self.vel_x) > target_speed:
            self.vel_x = target_speed * (1 if self.vel_x > 0 else -1)

    def stop_move(self):
        """Stop movement."""
        if self.on_ground and abs(self.vel_x) < PLAYER_MOVE_SPEED * 1.2:
            self.vel_x *= 0.4

    def jump(self):
        """Jump with double jump."""
        if not self.alive or self.hit_stun_timer > 0:
            return

        can_jump = self.on_ground or self.coyote_timer > 0 or self.jumps_remaining > 0

        if can_jump:
            self.vel_y = -PLAYER_JUMP_POWER
            self.on_ground = False
            self.coyote_timer = 0
            if not self.on_ground:
                self.jumps_remaining -= 1

    def attack(self, attack_type=ATTACK_SWING):
        """Perform melee attack."""
        if not self.alive or self.attack_cooldown > 0:
            return

        self.attack_state = attack_type
        self.attack_timer = 0.3
        self.attack_cooldown = 0.5

        hitbox_width = 50
        hitbox_height = 40

        if self.facing_right:
            hitbox_x = self.rect.right
        else:
            hitbox_x = self.rect.left - hitbox_width

        self.attack_hitbox = pygame.Rect(
            hitbox_x,
            self.rect.centery - hitbox_height // 2,
            hitbox_width,
            hitbox_height
        )

        if self.on_attack:
            self.on_attack(self.player_id, self.attack_hitbox)

    def _update_attack(self, dt):
        """Update attack."""
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_state = self.ATTACK_NONE
                self.attack_hitbox = None

    def get_attack_hitbox(self):
        """Get attack hitbox."""
        if self.attack_state != self.ATTACK_NONE and self.attack_hitbox:
            return self.attack_hitbox
        return None

    # ═══════════════════════════════════════════════════
    # COMBAT
    # ═══════════════════════════════════════════════════

    def take_damage(self, damage, knockback_x=0, knockback_y=0):
        """Take damage with knockback."""
        if not self.alive or self.invulnerable:
            return

        self.health -= damage
        self.health = max(0, self.health)

        self.vel_x += knockback_x
        self.vel_y += knockback_y

        self.hit_flash_timer = HIT_FLASH_DURATION
        self.hit_stun_timer = PLAYER_HIT_STUN

        if self.on_health_changed:
            self.on_health_changed(self.player_id, self.health)

        if self.health <= 0:
            self.die()

    def die(self):
        """Die."""
        if not self.alive:
            return
        self.alive = False
        self.health = 0
        self.respawn_timer = PLAYER_RESPAWN_TIME
        self.vel_x = 0
        if self.on_health_changed:
            self.on_health_changed(self.player_id, 0)

    def respawn(self, x=None, y=None):
        """Respawn."""
        self.alive = True
        self.health = PLAYER_MAX_HEALTH
        self.vel_x = 0
        self.vel_y = 0
        self.invulnerable = True
        self.invuln_timer = PLAYER_INVULN_TIME

        if x is not None and y is not None:
            self.rect.x = x
            self.rect.y = y

        self.jumps_remaining = 2 if PLAYER_DOUBLE_JUMP else 1

        if self.on_health_changed:
            self.on_health_changed(self.player_id, self.health)

    # ═══════════════════════════════════════════════════
    # RENDERING
    # ═══════════════════════════════════════════════════

    def draw(self, screen):
        """Draw the player with retro sprite."""
        if self.alive:
            # Flip sprite based on direction
            if self.vel_x < 0 and self.facing_right:
                self.facing_right = False
            elif self.vel_x > 0 and not self.facing_right:
                self.facing_right = True

            sprite_to_draw = self.sprite if self.facing_right else pygame.transform.flip(self.sprite, True, False)
            screen.blit(sprite_to_draw, self.rect)

            # Draw equipped weapon attached to the player hand (stable, flipped with player)
            if hasattr(self, 'equipped_weapon') and self.equipped_weapon:
                w = self.equipped_weapon
                # Place weapon near hand
                hand_x = self.rect.centerx + (self.rect.width // 4 if self.facing_right else -self.rect.width // 4)
                hand_y = self.rect.centery

                # Get weapon surface and scale/flip for facing
                surf = w.get_surface()
                if not self.facing_right:
                    try:
                        surf = pygame.transform.flip(surf, True, False)
                    except Exception:
                        pass

                # Scale surface to weapon size if needed
                try:
                    surf = pygame.transform.smoothscale(surf, (w.size, w.size))
                except Exception:
                    pass

                surf_rect = surf.get_rect(center=(hand_x, hand_y))
                screen.blit(surf, surf_rect)

                # Keep weapon rect in sync (useful for collisions/debug)
                w.rect = surf_rect

            # Draw pixel shadow beneath player
            shadow_rect = pygame.Rect(self.rect.x + 5, self.rect.bottom - 3, self.rect.width - 10, 3)
            shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 100))
            screen.blit(shadow_surface, shadow_rect)

    def _draw_dead(self, screen):
        """Draw death."""
        ghost_color = tuple(c // 4 for c in self.color)
        pygame.draw.circle(screen, ghost_color, self.rect.center, PLAYER_WIDTH // 2)

        center = self.rect.center
        pygame.draw.line(screen, LIGHT_GRAY,
                        (center[0] - 12, center[1] - 3),
                        (center[0] - 6, center[1] + 3), 2)
        pygame.draw.line(screen, LIGHT_GRAY,
                        (center[0] - 12, center[1] + 3),
                        (center[0] - 6, center[1] - 3), 2)
        pygame.draw.line(screen, LIGHT_GRAY,
                        (center[0] + 6, center[1] - 3),
                        (center[0] + 12, center[1] + 3), 2)
        pygame.draw.line(screen, LIGHT_GRAY,
                        (center[0] + 6, center[1] + 3),
                        (center[0] + 12, center[1] - 3), 2)

    def _draw_face(self, screen, color):
        """Draw face."""
        eye_y = self.rect.y + PLAYER_HEIGHT // 3
        eye_left_x = self.rect.x + 12
        eye_right_x = self.rect.right - 12

        if self.facing_right:
            eye_left_x += 2
            eye_right_x += 2
        else:
            eye_left_x -= 2
            eye_right_x -= 2

        eye_color = BLACK if self.hit_flash_timer <= 0 else color
        pygame.draw.circle(screen, eye_color, (eye_left_x, eye_y), 3)
        pygame.draw.circle(screen, eye_color, (eye_right_x, eye_y), 3)

    def _draw_attack(self, screen):
        """Draw attack animation with weapon image."""
        if self.attack_hitbox:
            # Use AI-generated weapon image if available
            if self.weapon_image:
                weapon_img = self.weapon_image

                # Scale weapon image
                weapon_img = pygame.transform.scale(weapon_img,
                                                    (self.attack_hitbox.width,
                                                     self.attack_hitbox.height))

                # Flip if attacking left
                if not self.facing_right:
                    weapon_img = pygame.transform.flip(weapon_img, True, False)

                # Add glow effect
                glow_surface = pygame.Surface((self.attack_hitbox.width,
                                              self.attack_hitbox.height),
                                             pygame.SRCALPHA)
                glow_surface.fill((*self.color, 100))
                screen.blit(glow_surface, self.attack_hitbox)

                # Draw weapon image
                screen.blit(weapon_img, self.attack_hitbox)
            else:
                # Fallback: semi-transparent attack arc
                attack_surface = pygame.Surface((self.attack_hitbox.width,
                                                self.attack_hitbox.height),
                                               pygame.SRCALPHA)

                if self.attack_state == self.ATTACK_SWING:
                    # Draw swing arc
                    arc_color = (*self.color, 150)
                    pygame.draw.ellipse(attack_surface, arc_color,
                                      attack_surface.get_rect(), 3)
                else:
                    # Draw thrust
                    thrust_color = (*self.color, 120)
                    pygame.draw.rect(attack_surface, thrust_color,
                                   attack_surface.get_rect())

                screen.blit(attack_surface, self.attack_hitbox)

    def _draw_health_bar(self, screen):
        """Draw health bar."""
        bar_width = PLAYER_WIDTH
        bar_height = 5
        bar_x = self.rect.x
        bar_y = self.rect.y - 10

        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))

        health_percent = self.health / self.max_health
        fill_width = int(bar_width * health_percent)

        if health_percent > 0.6:
            bar_color = SUCCESS_GREEN
        elif health_percent > 0.3:
            bar_color = WARNING_YELLOW
        else:
            bar_color = DANGER_RED

        if fill_width > 0:
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_width, bar_height))

        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

    def _draw_player_id(self, screen):
        """Draw player ID."""
        font = pygame.font.Font(None, 16)
        id_text = font.render(f"P{self.player_id + 1}", True, WHITE)
        text_rect = id_text.get_rect(center=(self.rect.centerx, self.rect.bottom + 8))

        badge_rect = text_rect.inflate(6, 3)
        pygame.draw.rect(screen, self.color, badge_rect, border_radius=3)
        pygame.draw.rect(screen, WHITE, badge_rect, 1, border_radius=3)

        screen.blit(id_text, text_rect)

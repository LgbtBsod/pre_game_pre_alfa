"""
Movement system (SRP): updates entity positions from inputs and time.
"""

from typing import Tuple, Optional


class MovementSystem:
    def __init__(self, base_speed_pixels_per_sec: float = 120.0):
        self.base_speed = base_speed_pixels_per_sec

    def update_player_from_inputs(self, player, keys: Optional[object], delta_time: float) -> Tuple[float, float]:
        """
        Computes movement delta in world space from input state and applies it to player's EntityPosition.

        Returns (dx, dy) applied in world units.
        """
        if keys is None or player is None:
            return 0.0, 0.0

        dx = 0.0
        dy = 0.0

        try:
            import pygame
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= 1.0
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += 1.0
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= 1.0
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += 1.0
        except Exception:
            pass

        if dx == 0.0 and dy == 0.0:
            return 0.0, 0.0

        # Normalize for diagonal movement
        length = (dx * dx + dy * dy) ** 0.5
        if length > 0:
            dx /= length
            dy /= length

        speed_multiplier = getattr(player.stats, 'speed', 1.0)
        speed = self.base_speed * speed_multiplier
        applied_dx = dx * speed * delta_time
        applied_dy = dy * speed * delta_time

        # Apply to EntityPosition
        player.position.x += applied_dx
        player.position.y += applied_dy

        return applied_dx, applied_dy



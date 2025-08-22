"""
Камера: свободное движение и центрирование на точке (изометрические координаты)
"""

from typing import Tuple


class Camera:
    def __init__(self, view_width: int, view_height: int):
        self.x = 0.0
        self.y = 0.0
        self.view_width = float(view_width)
        self.view_height = float(view_height)

    def set_view_size(self, width: int, height: int) -> None:
        self.view_width = float(width)
        self.view_height = float(height)

    def pan(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

    def center_on_iso(self, iso_x: float, iso_y: float) -> None:
        self.x = iso_x - self.view_width / 2.0
        self.y = iso_y - self.view_height / 2.0

    def update_from_inputs(self, keys, speed_pixels_per_sec: float, delta_time: float) -> None:
        dx = dy = 0.0
        if keys is not None:
            # arrows and WASD
            try:
                import pygame
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    dx -= speed_pixels_per_sec * delta_time
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    dx += speed_pixels_per_sec * delta_time
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    dy -= speed_pixels_per_sec * delta_time
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    dy += speed_pixels_per_sec * delta_time
            except Exception:
                pass
        self.pan(dx, dy)

    def world_iso_to_screen(self, iso_x: float, iso_y: float) -> Tuple[int, int]:
        sx = int(iso_x - self.x)
        sy = int(iso_y - self.y)
        return sx, sy



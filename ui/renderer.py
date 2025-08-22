"""
Game rendering helpers (SRP): world, entities, beacons, grid.
"""

from typing import List, Dict, Tuple, Any


class GameRenderer:
    def __init__(self, screen, fonts, projection, camera, colors):
        self.screen = screen
        self.fonts = fonts
        self.projection = projection
        self.camera = camera
        self.colors = colors

    def render_grid(self, size: int = 10) -> None:
        # simple checker grid
        for x in range(-size, size + 1):
            for y in range(-size, size + 1):
                if (x + y) % 2 == 0:
                    self._draw_iso_tile(x, y, (60, 60, 60))
                else:
                    self._draw_iso_tile(x, y, (50, 50, 50))

    def _draw_iso_tile(self, wx: int, wy: int, color: Tuple[int, int, int]):
        iso_x, iso_y = self.projection.world_to_iso(wx, wy)
        sx, sy = self.camera.world_iso_to_screen(iso_x, iso_y)
        # diamond
        try:
            import pygame
            tile_w, tile_h = 64, 32
            points = [
                (sx, sy - tile_h // 2),
                (sx + tile_w // 2, sy),
                (sx, sy + tile_h // 2),
                (sx - tile_w // 2, sy),
            ]
            pygame.draw.polygon(self.screen, color, points)
            pygame.draw.polygon(self.screen, (0, 0, 0), points, 1)
        except Exception:
            pass

    def render_player_marker(self, player) -> None:
        if not player:
            return
        px, py = self.projection.world_to_iso(player.position.x, player.position.y)
        sx, sy = self.camera.world_iso_to_screen(px, py)
        try:
            import pygame
            pygame.draw.circle(self.screen, self.colors.GREEN, (sx, sy), 16)
            pygame.draw.circle(self.screen, (0, 0, 0), (sx, sy), 16, 2)
        except Exception:
            pass

    def render_enemies(self, enemies: List[Any]) -> None:
        try:
            import pygame
            for e in enemies:
                if hasattr(e, 'position'):
                    ex, ey = self.projection.world_to_iso(e.position.x, e.position.y)
                    sx, sy = self.camera.world_iso_to_screen(ex, ey)
                    pygame.draw.circle(self.screen, self.colors.RED, (sx, sy), 12)
                    pygame.draw.circle(self.screen, (0, 0, 0), (sx, sy), 12, 2)
        except Exception:
            pass

    def render_obstacles(self, obstacles: List[Dict[str, Any]]) -> None:
        try:
            import pygame
            for ob in obstacles:
                if 'position' not in ob:
                    continue
                iso_x, iso_y = self.projection.world_to_iso(*ob['position'])
                sx, sy = self.camera.world_iso_to_screen(iso_x, iso_y)
                if ob.get('type') == 'trap':
                    points = [(sx, sy - 8), (sx + 8, sy), (sx, sy + 8), (sx - 8, sy)]
                    pygame.draw.polygon(self.screen, self.colors.ORANGE, points)
                elif ob.get('type') == 'geo_barrier':
                    pygame.draw.rect(self.screen, self.colors.GRAY, (sx - 12, sy - 8, 24, 16))
                    pygame.draw.rect(self.screen, (0, 0, 0), (sx - 12, sy - 8, 24, 16), 1)
        except Exception:
            pass

    def render_items(self, items: List[Dict[str, Any]]) -> None:
        try:
            import pygame
            for it in items:
                if 'position' not in it:
                    continue
                iso_x, iso_y = self.projection.world_to_iso(*it['position'])
                sx, sy = self.camera.world_iso_to_screen(iso_x, iso_y)
                pygame.draw.circle(self.screen, self.colors.BLUE, (sx, sy), 6)
        except Exception:
            pass

    def render_chests(self, chests: List[Dict[str, Any]]) -> None:
        try:
            import pygame
            for chest in chests:
                if 'position' not in chest:
                    continue
                iso_x, iso_y = self.projection.world_to_iso(*chest['position'])
                sx, sy = self.camera.world_iso_to_screen(iso_x, iso_y)
                color = self.colors.YELLOW if not chest.get('opened', False) else self.colors.GRAY
                pygame.draw.rect(self.screen, color, (sx - 12, sy - 8, 24, 16))
                pygame.draw.rect(self.screen, (0, 0, 0), (sx - 12, sy - 8, 24, 16), 1)
        except Exception:
            pass



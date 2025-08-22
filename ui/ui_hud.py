"""
UI HUD: lightweight debug overlay renderer extracted from game loop (SRP).
"""

from typing import Dict, Any


class UIHud:
    def __init__(self, screen):
        self.screen = screen

    def render_debug(self, stats: Dict[str, Any], is_paused: bool) -> None:
        try:
            import pygame
            if not self.screen:
                return

            # FPS
            fps = stats.get('fps', 0)
            if fps and fps > 0:
                font = pygame.font.Font(None, 24)
                fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
                self.screen.blit(fps_text, (10, 10))

            # World info
            world_info = stats.get('world', {}) or {}
            if world_info:
                font = pygame.font.Font(None, 20)
                world_text = font.render(
                    f"Мир: {world_info.get('name', 'Unknown')} | "
                    f"День: {world_info.get('day_cycle', 0)} | "
                    f"Погода: {world_info.get('weather', 'Unknown')}",
                    True, (255, 255, 255)
                )
                self.screen.blit(world_text, (10, 40))

            # Entities
            entity_stats = stats.get('entities', {}) or {}
            font = pygame.font.Font(None, 20)
            entity_text = font.render(
                f"Сущности: {entity_stats.get('total_entities', 0)}",
                True, (255, 255, 255)
            )
            self.screen.blit(entity_text, (10, 70))

            # Pause banner
            if is_paused:
                font = pygame.font.Font(None, 36)
                pause_text = font.render("ПАУЗА", True, (255, 255, 0))
                text_rect = pause_text.get_rect(center=(self.screen.get_width() // 2, 50))
                self.screen.blit(pause_text, text_rect)
        except Exception:
            # UI HUD is best-effort; avoid crashing the loop
            pass



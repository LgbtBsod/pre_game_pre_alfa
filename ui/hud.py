"""
HUD панели: статус, инвентарь с подсказками, гены, ИИ-обучение
Объединенный компонент с debug overlay
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any


class StatusHUD:
    def __init__(self, screen: pygame.Surface, fonts: Dict[str, pygame.font.Font], panel_rect: pygame.Rect, colors):
        self.screen = screen
        self.fonts = fonts
        self.panel = panel_rect
        self.colors = colors

    def render(self, player) -> None:
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, self.panel)
        pygame.draw.rect(self.screen, self.colors.WHITE, self.panel, 2)

        title = self.fonts["main"].render("СТАТУС", True, self.colors.WHITE)
        self.screen.blit(title, (self.panel.x + 10, self.panel.y + 10))

        if not player:
            return

        y = self.panel.y + 40
        small = self.fonts["small"]

        try:
            hp = getattr(player.stats, "health", 100)
            hp_max = getattr(player.stats, "max_health", 100)
            self.screen.blit(small.render(f"Здоровье: {hp:.0f}/{hp_max:.0f}", True, self.colors.HEALTH_COLOR), (self.panel.x + 10, y))
            y += 20
        except Exception:
            pass

        try:
            mana = getattr(player.stats, "mana", 100)
            mana_max = getattr(player.stats, "max_mana", 100)
            self.screen.blit(small.render(f"Мана: {mana:.0f}/{mana_max:.0f}", True, self.colors.ENERGY_COLOR), (self.panel.x + 10, y))
            y += 20
        except Exception:
            pass

        try:
            sta = getattr(player.stats, "stamina", 100)
            sta_max = getattr(player.stats, "max_stamina", 100)
            self.screen.blit(small.render(f"Выносливость: {sta:.0f}/{sta_max:.0f}", True, self.colors.STAMINA_COLOR), (self.panel.x + 10, y))
            y += 20
        except Exception:
            pass

        level_value = getattr(player, "level", getattr(player.stats, "level", 1))
        self.screen.blit(small.render(f"Уровень: {level_value}", True, self.colors.WHITE), (self.panel.x + 10, y))


class InventoryHUD:
    def __init__(self, screen: pygame.Surface, fonts: Dict[str, pygame.font.Font], panel_rect: pygame.Rect, colors):
        self.screen = screen
        self.fonts = fonts
        self.panel = panel_rect
        self.colors = colors
        self._item_rects: List[Tuple[pygame.Rect, str]] = []

    def render(self, player, db) -> None:
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, self.panel)
        pygame.draw.rect(self.screen, self.colors.WHITE, self.panel, 2)
        title = self.fonts["main"].render("ИНВЕНТАРЬ", True, self.colors.WHITE)
        self.screen.blit(title, (self.panel.centerx - title.get_width() // 2, self.panel.y + 10))

        if not player or not hasattr(player, "inventory_system"):
            return

        inventory = player.inventory_system.get_inventory_data()
        self._item_rects.clear()
        y = self.panel.y + 40
        small = self.fonts["small"]

        for i, (item_id, qty) in enumerate(list(inventory.items())[:8]):
            info = db.get_item(item_id) or db.get_weapon(item_id) or {}
            name = info.get("name", item_id)
            surf = small.render(f"{name} x{qty}", True, self.colors.WHITE)
            self.screen.blit(surf, (self.panel.x + 10, y))
            rect = surf.get_rect(topleft=(self.panel.x + 10, y))
            self._item_rects.append((rect, item_id))
            y += 22

        # tooltip
        mx, my = pygame.mouse.get_pos()
        for rect, item_id in self._item_rects:
            if rect.collidepoint((mx, my)):
                info = db.get_item(item_id) or db.get_weapon(item_id) or {}
                lines: List[str] = []
                if "name" in info:
                    lines.append(info["name"])
                if "rarity" in info:
                    lines.append(f"Редкость: {info['rarity']}")
                if "value" in info:
                    lines.append(f"Цена: {info['value']}")
                if "damage" in info:
                    lines.append(f"Урон: {info['damage']}")
                if info.get("effects"):
                    lines.append(f"Эффекты: {', '.join(info['effects'])}")
                self._render_tooltip((mx, my), lines)

    def _render_tooltip(self, pos: Tuple[int, int], lines: List[str]) -> None:
        if not lines:
            return
        padding = 8
        small = self.fonts["small"]
        surfaces = [small.render(str(t), True, self.colors.WHITE) for t in lines]
        width = max(s.get_width() for s in surfaces) + padding * 2
        height = sum(s.get_height() for s in surfaces) + padding * 2
        x, y = pos
        rect = pygame.Rect(x + 16, y + 16, width, height)
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, rect)
        pygame.draw.rect(self.screen, self.colors.WHITE, rect, 1)
        cy = rect.y + padding
        for s in surfaces:
            self.screen.blit(s, (rect.x + padding, cy))
            cy += s.get_height()


class GeneticsHUD:
    def __init__(self, screen: pygame.Surface, fonts: Dict[str, pygame.font.Font], panel_rect: pygame.Rect, colors):
        self.screen = screen
        self.fonts = fonts
        self.panel = panel_rect
        self.colors = colors

    def render(self, player) -> None:
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, self.panel)
        pygame.draw.rect(self.screen, self.colors.WHITE, self.panel, 2)
        title = self.fonts["main"].render("ГЕНЕТИКА", True, self.colors.GENETIC_COLOR)
        self.screen.blit(title, (self.panel.centerx - title.get_width() // 2, self.panel.y + 10))

        if not player:
            return
        small = self.fonts["small"]
        y = self.panel.y + 40
        try:
            active_genes = getattr(player.genetic_system, "active_genes", [])
            self.screen.blit(small.render(f"Активные гены: {len(active_genes)}", True, self.colors.GENETIC_COLOR), (self.panel.x + 10, y))
            y += 20
            for i, gene in enumerate(active_genes[:4]):
                self.screen.blit(small.render(f"{i+1}. {gene}", True, self.colors.LIGHT_GRAY), (self.panel.x + 10, y))
                y += 16
            y += 4
            mutation_level = getattr(player, "mutation_level", 0.0)
            self.screen.blit(small.render(f"Мутации: {mutation_level:.2f}", True, self.colors.GENETIC_COLOR), (self.panel.x + 10, y))
            y += 18
            stability = getattr(player, "genetic_stability", 1.0)
            self.screen.blit(small.render(f"Стабильность: {stability:.2f}", True, self.colors.GENETIC_COLOR), (self.panel.x + 10, y))
        except Exception:
            pass


class AILearningHUD:
    def __init__(self, screen: pygame.Surface, fonts: Dict[str, pygame.font.Font], panel_rect: pygame.Rect, colors):
        self.screen = screen
        self.fonts = fonts
        self.panel = panel_rect
        self.colors = colors

    def render(self, player) -> None:
        pygame.draw.rect(self.screen, self.colors.DARK_GRAY, self.panel)
        pygame.draw.rect(self.screen, self.colors.WHITE, self.panel, 2)

        title = self.fonts["main"].render("ИИ / ОБУЧЕНИЕ", True, self.colors.WHITE)
        self.screen.blit(title, (self.panel.centerx - title.get_width() // 2, self.panel.y + 10))

        if not player or not hasattr(player, 'ai_system'):
            return

        small = self.fonts["small"]
        y = self.panel.y + 40
        try:
            level = getattr(player.ai_system, 'level', 1)
            episodes = getattr(player.ai_system, 'episodes_trained', 0)
            epsilon = getattr(player.ai_system, 'epsilon', 0.0)
            last_reward = getattr(player.ai_system, 'last_reward', 0.0)

            self.screen.blit(small.render(f"Уровень обучения: {level}", True, self.colors.LIGHT_GRAY), (self.panel.x + 10, y)); y += 18
            self.screen.blit(small.render(f"Эпизоды: {episodes}", True, self.colors.LIGHT_GRAY), (self.panel.x + 10, y)); y += 36
            self.screen.blit(small.render(f"Эпсилон: {epsilon:.2f}", True, self.colors.LIGHT_GRAY), (self.panel.x + 10, y)); y += 54
            self.screen.blit(small.render(f"Последняя награда: {last_reward:.2f}", True, self.colors.LIGHT_GRAY), (self.panel.x + 10, y)); y += 72
        except Exception:
            pass


class DebugHUD:
    """Debug overlay для отображения технической информации"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def render_debug(self, stats: Dict[str, Any], is_paused: bool) -> None:
        """Отображение debug информации"""
        try:
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
            # Debug HUD is best-effort; avoid crashing the loop
            pass


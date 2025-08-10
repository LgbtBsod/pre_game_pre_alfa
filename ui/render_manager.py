"""
Менеджер рендеринга - управляет отрисовкой всех игровых элементов
"""
import time
from typing import Dict, List, Optional, Any, Tuple
from tkinter import Canvas

from core.game_state_manager import GameStateManager
from map.tiled_map import TiledMap
from config.game_constants import PLAYER_COLOR, TEXT_COLOR
from utils.game_utils import rgb_to_hex


# Функция rgb_to_hex теперь импортируется из utils.game_utils


class RenderManager:
    """Управляет рендерингом всех игровых элементов"""
    
    def __init__(self, canvas: Canvas, game_state: GameStateManager):
        self.canvas = canvas
        self.game_state = game_state
        self.width = canvas.winfo_reqwidth()
        self.height = canvas.winfo_reqheight()
        
        # Позиция камеры
        self.map_view_x = 0
        self.map_view_y = 0
        
        # Карта
        self.tiled_map: Optional[TiledMap] = None
        
    def set_tiled_map(self, tiled_map: TiledMap) -> None:
        """Установка карты для рендеринга"""
        self.tiled_map = tiled_map
        self._center_initial_camera()
        
    def _center_initial_camera(self) -> None:
        """Центрирование камеры на игроке при инициализации"""
        if not self.tiled_map or not self.game_state.player:
            return
            
        px, py = self.game_state.player.position
        map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
        map_px_h = self.tiled_map.height * self.tiled_map.tileheight
        
        self.map_view_x = max(0, min(px - self.width // 2, max(0, map_px_w - self.width)))
        self.map_view_y = max(0, min(py - self.height // 2, max(0, map_px_h - self.height)))
        
    def center_camera_on_player(self) -> None:
        """Центрирование камеры на игроке"""
        if not self.game_state.player:
            return
            
        px, py = self.game_state.player.position
        
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
            map_px_h = self.tiled_map.height * self.tiled_map.tileheight
            self.map_view_x = max(0, min(px - self.width // 2, max(0, map_px_w - self.width)))
            self.map_view_y = max(0, min(py - self.height // 2, max(0, map_px_h - self.height)))
        else:
            self.map_view_x = max(0, px - self.width // 2)
            self.map_view_y = max(0, py - self.height // 2)
            
    def render_frame(self) -> None:
        """Отрисовка полного кадра"""
        self.canvas.delete("all")
        
        # Рендер карты
        self._render_map()
        
        # Рендер сущностей
        self._render_entities()
        
        # Рендер UI
        self._render_ui()
        
        # Рендер пользовательских объектов
        self._render_user_objects()
        
        # Рендер подсказок
        self._render_hints()
        
    def _render_map(self) -> None:
        """Отрисовка карты"""
        if self.tiled_map:
            self.tiled_map.draw_to_canvas(
                self.canvas,
                self.map_view_x,
                self.map_view_y,
                self.width,
                self.height,
                tag="map",
            )
            
    def _render_entities(self) -> None:
        """Отрисовка игровых сущностей"""
        # Игрок
        if self.game_state.player:
            self._render_player(self.game_state.player)
            
        # Враги
        for enemy in self.game_state.enemies:
            if enemy.alive:
                self._render_enemy(enemy)
                
        # Босс
        if self.game_state.boss and self.game_state.boss.alive:
            self._render_boss(self.game_state.boss)
            
    def _render_player(self, player) -> None:
        """Отрисовка игрока"""
        px, py = player.position
        spx, spy = px - self.map_view_x, py - self.map_view_y
        
        color = rgb_to_hex(PLAYER_COLOR) if player.alive else rgb_to_hex((50, 50, 50))
        self._draw_circle(spx, spy, 20, fill=color)
        
    def _render_enemy(self, enemy) -> None:
        """Отрисовка врага"""
        ex, ey = enemy.position
        sex, sey = ex - self.map_view_x, ey - self.map_view_y
        
        # Цвет в зависимости от типа врага
        if enemy.enemy_type == "warrior":
            color = rgb_to_hex((255, 50, 50))
        elif enemy.enemy_type == "archer":
            color = rgb_to_hex((200, 50, 150))
        else:
            color = rgb_to_hex((50, 150, 255))
            
        self._draw_circle(sex, sey, 15, fill=color)
        
    def _render_boss(self, boss) -> None:
        """Отрисовка босса"""
        bx, by = boss.position
        sbx, sby = bx - self.map_view_x, by - self.map_view_y
        
        self._draw_circle(sbx, sby, 30, fill=rgb_to_hex((255, 165, 0)))
        
        # Информация о фазе босса
        if hasattr(boss, 'phase'):
            self.canvas.create_text(
                sbx, sby - 40, 
                text=f"Фаза: {boss.phase}", 
                fill=rgb_to_hex((255, 255, 0))
            )
            
    def _render_ui(self) -> None:
        """Отрисовка пользовательского интерфейса"""
        if not self.game_state.player:
            return
            
        # Основная информация
        self._render_basic_info()
        
        # Информация об опыте
        self._render_experience_info()
        
        # Статистика
        self._render_statistics()
        
        # Информация о навыках
        self._render_skills_info()
        
        # Информация об эмоциях
        self._render_emotions_info()
        
        # Информация о карте
        self._render_map_info()
        
        # Информация о боссе
        self._render_boss_info()
        
    def _render_basic_info(self) -> None:
        """Отрисовка основной информации"""
        player = self.game_state.player
        leveling = self.game_state.leveling_system
        
        if leveling:
            level = leveling.level
        else:
            level = getattr(player, 'level', 1)
            
        self.canvas.create_text(
            10, 10, 
            text=f"Уровень: {level}", 
            fill=rgb_to_hex(TEXT_COLOR), 
            anchor="nw"
        )
        
        self.canvas.create_text(
            10, 40, 
            text=f"Здоровье: {int(player.health)}/{int(player.max_health)}", 
            fill=rgb_to_hex(TEXT_COLOR), 
            anchor="nw"
        )
        
    def _render_experience_info(self) -> None:
        """Отрисовка информации об опыте"""
        leveling = self.game_state.leveling_system
        if not leveling:
            return
            
        exp_progress = leveling.get_leveling_progress()
        
        self.canvas.create_text(
            10, 70, 
            text=f"Опыт: {exp_progress['current_exp']}/{exp_progress['exp_to_next']}", 
            fill=rgb_to_hex(TEXT_COLOR), 
            anchor="nw"
        )
        
        self.canvas.create_text(
            10, 100, 
            text=f"Очки хар-к: {exp_progress['attribute_points']}", 
            fill=rgb_to_hex(TEXT_COLOR), 
            anchor="nw"
        )
        
    def _render_statistics(self) -> None:
        """Отрисовка статистики"""
        stats = self.game_state.statistics
        
        self.canvas.create_text(
            10, 130, 
            text=f"Реинкарнации: {stats.reincarnation_count}", 
            fill=rgb_to_hex((220, 220, 180)), 
            anchor="nw"
        )
        
        self.canvas.create_text(
            10, 160, 
            text=f"Поколения: {stats.generation_count}", 
            fill=rgb_to_hex((220, 180, 220)), 
            anchor="nw"
        )
        
        # Время сессии
        session_time = time.time() - stats.session_start_time
        self.canvas.create_text(
            10, 190, 
            text=f"Время сессии: {int(session_time // 60)}:{int(session_time % 60):02d}", 
            fill=rgb_to_hex((180, 220, 180)), 
            anchor="nw"
        )
        
        # Скорость обучения
        if self.game_state.player:
            self.canvas.create_text(
                10, 220, 
                text=f"Скорость обучения: {self.game_state.player.learning_rate:.3f}", 
                fill=rgb_to_hex((220, 180, 180)), 
                anchor="nw"
            )
            
    def _render_skills_info(self) -> None:
        """Отрисовка информации о навыках"""
        if not self.game_state.skill_system:
            return
            
        y_offset = 250
        skills = self.game_state.skill_system.get_learned_skills()
        
        for i, skill in enumerate(skills[:3]):  # Показываем первые 3 навыка
            y_pos = y_offset + i * 30
            cooldown_text = f" (КД: {skill.current_cooldown:.1f}s)" if skill.current_cooldown > 0 else ""
            
            self.canvas.create_text(
                10, y_pos, 
                text=f"{i+1}: {skill.name}{cooldown_text}", 
                fill=rgb_to_hex(config.TEXT_COLOR), 
                anchor="nw"
            )
            
    def _render_emotions_info(self) -> None:
        """Отрисовка информации об эмоциях"""
        if not self.game_state.emotion_synthesizer:
            return
            
        y_offset = 350
        current_emotion = getattr(self.game_state.player, 'emotion', 'NEUTRAL')
        emotion_power = getattr(self.game_state.emotion_synthesizer, 'emotion_power', 1.0)
        
        self.canvas.create_text(
            10, y_offset, 
            text=f"Эмоция: {current_emotion}", 
            fill=rgb_to_hex(TEXT_COLOR), 
            anchor="nw"
        )
        
        self.canvas.create_text(
            10, y_offset + 30, 
            text=f"Сила эмоции: {emotion_power:.2f}", 
            fill=rgb_to_hex(TEXT_COLOR), 
            anchor="nw"
        )
        
    def _render_map_info(self) -> None:
        """Отрисовка информации о карте"""
        if self.tiled_map:
            self.canvas.create_text(
                10, 450, 
                text=f"Карта: {self.tiled_map.width}x{self.tiled_map.height} (tile {self.tiled_map.tilewidth}x{self.tiled_map.tileheight})", 
                fill=rgb_to_hex((180, 200, 255)), 
                anchor="nw"
            )
            
    def _render_boss_info(self) -> None:
        """Отрисовка информации о боссе"""
        if self.game_state.boss and self.game_state.boss.alive:
            self.canvas.create_text(
                self.width - 220, 10, 
                text=f"Босс: {int(self.game_state.boss.health)}/{int(self.game_state.boss.max_health)}", 
                fill=rgb_to_hex((255, 100, 100)), 
                anchor="nw"
            )
            
    def _render_user_objects(self) -> None:
        """Отрисовка пользовательских объектов"""
        if not self.tiled_map:
            return
            
        tw, th = self.tiled_map.tilewidth, self.tiled_map.tileheight
        
        # Препятствия
        for (tx, ty) in self.game_state.user_obstacles:
            x0 = tx * tw - self.map_view_x
            y0 = ty * th - self.map_view_y
            self.canvas.create_rectangle(
                x0, y0, x0 + tw, y0 + th, 
                outline="#88a", width=2
            )
            
        # Сундуки
        for chest in self.game_state.chests:
            tx, ty = chest["tx"], chest["ty"]
            x0 = tx * tw - self.map_view_x + tw * 0.25
            y0 = ty * th - self.map_view_y + th * 0.25
            x1 = x0 + tw * 0.5
            y1 = y0 + th * 0.5
            
            fill = "#d4a017" if not chest.get("opened") else "#8b7d5b"
            self.canvas.create_rectangle(
                x0, y0, x1, y1, 
                fill=fill, outline="#553"
            )
            
    def _render_hints(self) -> None:
        """Отрисовка подсказок"""
        self.canvas.create_text(
            10, self.height - 24, 
            text="Space: новое поколение | P: пауза | ЛКМ: препятствие | ПКМ: сундук", 
            fill=rgb_to_hex((200, 220, 240)), 
            anchor="sw"
        )
        
    def _draw_circle(self, x: float, y: float, radius: float, fill: str = "#ffffff") -> None:
        """Отрисовка круга"""
        self.canvas.create_oval(
            x - radius, y - radius, 
            x + radius, y + radius, 
            fill=fill, width=0
        )
        
    def draw_banner(self, text: str) -> None:
        """Отрисовка баннера"""
        self.canvas.create_rectangle(
            0, 0, self.width, self.height, 
            fill="#000000", stipple="gray25"
        )
        
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=text,
            fill=rgb_to_hex((255, 215, 0)),
            font=("Arial", 24, "bold"),
        )
        
    def get_world_position(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Получение мировой позиции из экранных координат"""
        world_x = screen_x + self.map_view_x
        world_y = screen_y + self.map_view_y
        return world_x, world_y
        
    def get_tile_position(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Получение позиции тайла из мировых координат"""
        if not self.tiled_map:
            return 0, 0
            
        tw, th = self.tiled_map.tilewidth, self.tiled_map.tileheight
        tx, ty = int(world_x // tw), int(world_y // th)
        return tx, ty

"""
Менеджер рендеринга - управляет отрисовкой всех игровых элементов
Оптимизированная версия с улучшенной производительностью
"""
import time
import math
from typing import Dict, List, Optional, Any, Tuple
from tkinter import Canvas
from dataclasses import dataclass

from core.game_state_manager import game_state_manager
from config.game_constants import PLAYER_COLOR, TEXT_COLOR
from utils.game_utils import rgb_to_hex


@dataclass
class RenderStats:
    """Статистика рендеринга"""
    frames_rendered: int = 0
    entities_rendered: int = 0
    render_time: float = 0.0
    last_fps_time: float = 0.0
    fps: int = 0


class RenderManager:
    """Управляет рендерингом всех игровых элементов с оптимизацией"""
    
    def __init__(self, canvas: Canvas, game_state: game_state_manager):
        self.canvas = canvas
        self.game_state = game_state
        self.width = canvas.winfo_reqwidth()
        self.height = canvas.winfo_reqheight()
        
        # Позиция камеры
        self.camera_x = 0
        self.camera_y = 0
        self.camera_zoom = 1.0
        
        # Статистика рендеринга
        self.stats = RenderStats()
        self.stats.last_fps_time = time.time()
        
        # Кэш для оптимизации
        self._cached_entities: Dict[int, Dict] = {}
        self._last_render_time = 0
        self._render_interval = 1.0 / 60  # 60 FPS
        
        # Настройки рендеринга
        self.show_fps = True
        self.show_debug_info = False
        self.show_health_bars = True
        self.show_names = True
        
        # Цвета и стили
        self.colors = {
            'background': '#1a1a1a',
            'border': '#333333',
            'text': rgb_to_hex(TEXT_COLOR),
            'player': rgb_to_hex(PLAYER_COLOR),
            'enemy_warrior': '#ff3333',
            'enemy_archer': '#ff66cc',
            'enemy_mage': '#3399ff',
            'health_good': '#00ff00',
            'health_warning': '#ffff00',
            'health_critical': '#ff0000',
            'health_bg': '#333333',
            'health_border': '#666666'
        }
        
        # Шрифты
        self.fonts = {
            'title': ('Arial', 16, 'bold'),
            'normal': ('Arial', 10),
            'small': ('Arial', 8),
            'debug': ('Consolas', 8)
        }
        
    def clear(self):
        """Очистка canvas"""
        self.canvas.delete("all")
        
    def update(self):
        """Обновление экрана"""
        self.canvas.update()
        
    def set_camera(self, x: float, y: float, zoom: float = 1.0):
        """Установка позиции камеры"""
        self.camera_x = x
        self.camera_y = y
        self.camera_zoom = max(0.1, min(3.0, zoom))  # Ограничиваем зум
        
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Преобразование мировых координат в экранные"""
        screen_x = int((world_x - self.camera_x) * self.camera_zoom + self.width // 2)
        screen_y = int((world_y - self.camera_y) * self.camera_zoom + self.height // 2)
        return screen_x, screen_y
        
    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Преобразование экранных координат в мировые"""
        world_x = (screen_x - self.width // 2) / self.camera_zoom + self.camera_x
        world_y = (screen_y - self.height // 2) / self.camera_zoom + self.camera_y
        return world_x, world_y
        
    def render_area(self, area_name: str):
        """Рендеринг игровой области с оптимизацией"""
        # Фон
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill=self.colors['background'],
            outline=self.colors['border'],
            width=2,
            tags="background"
        )
        
        # Сетка (опционально)
        if self.show_debug_info:
            self._render_grid()
        
        # Название области
        self.canvas.create_text(
            self.width // 2, 30,
            text=f"Область: {area_name}",
            fill=self.colors['text'],
            font=self.fonts['title'],
            tags="ui"
        )
        
    def _render_grid(self, grid_size: int = 50):
        """Отрисовка сетки для отладки"""
        # Вертикальные линии
        for x in range(0, self.width, grid_size):
            self.canvas.create_line(
                x, 0, x, self.height,
                fill='#333333',
                width=1,
                tags="debug"
            )
        
        # Горизонтальные линии
        for y in range(0, self.height, grid_size):
            self.canvas.create_line(
                0, y, self.width, y,
                fill='#333333',
                width=1,
                tags="debug"
            )
        
    def render_entity(self, entity):
        """Рендеринг игровой сущности с оптимизацией"""
        if not hasattr(entity, 'position'):
            return
            
        # Проверяем, нужно ли рендерить
        if not self._should_render_entity(entity):
            return
            
        x, y = entity.position
        
        # Определяем тип сущности и стиль
        entity_style = self._get_entity_style(entity)
        
        # Отрисовываем сущность
        self._render_entity_shape(x, y, entity_style)
        
        # Отрисовываем имя
        if self.show_names:
            self._render_entity_name(x, y, entity, entity_style)
        
        # Отрисовываем полоску здоровья
        if self.show_health_bars and hasattr(entity, 'health') and hasattr(entity, 'max_health'):
            self._render_health_bar(x, y, entity, entity_style)
        
        # Обновляем статистику
        self.stats.entities_rendered += 1
        
    def _should_render_entity(self, entity) -> bool:
        """Проверка, нужно ли рендерить сущность (оптимизация)"""
        if not hasattr(entity, 'position'):
            return False
            
        # Проверяем видимость (простая проверка по расстоянию)
        x, y = entity.position
        center_x, center_y = self.width // 2, self.height // 2
        
        # Если сущность слишком далеко от центра экрана, не рендерим
        distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_distance = max(self.width, self.height) * 0.8
        
        return distance <= max_distance
        
    def _get_entity_style(self, entity) -> Dict:
        """Получение стиля для сущности"""
        if hasattr(entity, 'name') and 'player' in entity.name.lower():
            return {
                'color': self.colors['player'],
                'size': 20,
                'shape': 'circle',
                'outline': '#ffffff',
                'outline_width': 2
            }
        elif hasattr(entity, 'enemy_type'):
            enemy_colors = {
                'warrior': self.colors['enemy_warrior'],
                'archer': self.colors['enemy_archer'],
                'mage': self.colors['enemy_mage']
            }
            return {
                'color': enemy_colors.get(entity.enemy_type, self.colors['enemy_warrior']),
                'size': 15,
                'shape': 'circle',
                'outline': '#ffffff',
                'outline_width': 1
            }
        else:
            return {
                'color': '#ffffff',
                'size': 10,
                'shape': 'circle',
                'outline': '#666666',
                'outline_width': 1
            }
        
    def _render_entity_shape(self, x: float, y: float, style: Dict):
        """Отрисовка формы сущности"""
        size = style['size']
        
        if style['shape'] == 'circle':
            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=style['color'],
                outline=style['outline'],
                width=style['outline_width'],
                tags="entity"
            )
        elif style['shape'] == 'square':
            self.canvas.create_rectangle(
                x - size, y - size,
                x + size, y + size,
                fill=style['color'],
                outline=style['outline'],
                width=style['outline_width'],
                tags="entity"
            )
        
    def _render_entity_name(self, x: float, y: float, entity, style: Dict):
        """Отрисовка имени сущности"""
        name = getattr(entity, 'name', getattr(entity, 'enemy_type', 'Unknown'))
        size = style['size']
        
        self.canvas.create_text(
            x, y - size - 10,
            text=name,
            fill=self.colors['text'],
            font=self.fonts['normal'],
            tags="ui"
        )
        
    def _render_health_bar(self, x: float, y: float, entity, style: Dict):
        """Отрисовка полоски здоровья"""
        health_percent = entity.health / entity.max_health
        size = style['size']
        
        # Размеры полоски здоровья
        health_width = 30
        health_height = 4
        
        # Позиция полоски
        bar_x = x - health_width // 2
        bar_y = y + size + 5
        
        # Фон полоски здоровья
        self.canvas.create_rectangle(
            bar_x, bar_y,
            bar_x + health_width, bar_y + health_height,
            fill=self.colors['health_bg'],
            outline=self.colors['health_border'],
            tags="ui"
        )
        
        # Полоска здоровья
        current_width = int(health_width * health_percent)
        if current_width > 0:
            # Определяем цвет в зависимости от здоровья
            if health_percent > 0.5:
                health_color = self.colors['health_good']
            elif health_percent > 0.25:
                health_color = self.colors['health_warning']
            else:
                health_color = self.colors['health_critical']
            
            self.canvas.create_rectangle(
                bar_x, bar_y,
                bar_x + current_width, bar_y + health_height,
                fill=health_color,
                tags="ui"
            )
        
    def render_ui(self):
        """Рендеринг пользовательского интерфейса"""
        # Время игры
        game_time = time.time()
        time_str = f"Время: {int(game_time // 60)}:{int(game_time % 60):02d}"
        
        self.canvas.create_text(
            10, 10,
            text=time_str,
            fill=self.colors['text'],
            font=self.fonts['normal'],
            anchor='nw',
            tags="ui"
        )
        
        # FPS
        if self.show_fps:
            self._update_fps()
            fps_text = f"FPS: {self.stats.fps}"
            self.canvas.create_text(
                self.width - 10, 10,
                text=fps_text,
                fill=self.colors['text'],
                font=self.fonts['normal'],
                anchor='ne',
                tags="ui"
            )
        
        # Инструкции
        instructions = [
            "Управление:",
            "ЛКМ - перемещение игрока",
            "ESC - меню",
            "P - пауза",
            "F5 - сохранение"
        ]
        
        y_offset = 60
        for instruction in instructions:
            self.canvas.create_text(
                10, y_offset,
                text=instruction,
                fill=self.colors['text'],
                font=self.fonts['small'],
                anchor='nw',
                tags="ui"
            )
            y_offset += 20
            
        # Отладочная информация
        if self.show_debug_info:
            self._render_debug_info()
            
    def _update_fps(self):
        """Обновление FPS счетчика"""
        current_time = time.time()
        self.stats.frames_rendered += 1
        
        if current_time - self.stats.last_fps_time >= 1.0:
            self.stats.fps = self.stats.frames_rendered
            self.stats.frames_rendered = 0
            self.stats.last_fps_time = current_time
            
    def _render_debug_info(self):
        """Отрисовка отладочной информации"""
        debug_info = [
            f"Камера: ({self.camera_x:.1f}, {self.camera_y:.1f})",
            f"Зум: {self.camera_zoom:.2f}",
            f"Сущностей: {self.stats.entities_rendered}",
            f"Время рендера: {self.stats.render_time:.3f}ms"
        ]
        
        y_offset = self.height - 100
        for info in debug_info:
            self.canvas.create_text(
                10, y_offset,
                text=info,
                fill=self.colors['text'],
                font=self.fonts['debug'],
                anchor='nw',
                tags="debug"
            )
            y_offset += 15
            
    def render_frame(self):
        """Отрисовка полного кадра с оптимизацией"""
        start_time = time.time()
        
        # Очищаем canvas
        self.clear()
        
        # Рендер области
        self.render_area("current_area")
        
        # Рендер UI
        self.render_ui()
        
        # Обновляем статистику
        self.stats.render_time = (time.time() - start_time) * 1000
        self.stats.entities_rendered = 0
        
    def center_camera_on_player(self, player):
        """Центрирование камеры на игроке"""
        if not player or not hasattr(player, 'position'):
            return
            
        px, py = player.position
        self.camera_x = px
        self.camera_y = py
        
    def get_world_position(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Получение мировой позиции из экранных координат"""
        return self.screen_to_world(screen_x, screen_y)
        
    def draw_banner(self, text: str, color: str = None):
        """Отрисовка баннера"""
        if color is None:
            color = '#ffd700'  # Золотой цвет по умолчанию
            
        # Полупрозрачный фон
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill='#000000',
            stipple='gray25',
            tags="banner"
        )
        
        # Текст баннера
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=text,
            fill=color,
            font=self.fonts['title'],
            tags="banner"
        )
        
    def draw_minimap(self, entities: List, player, size: int = 150):
        """Отрисовка миникарты"""
        if not entities and not player:
            return
            
        # Позиция миникарты
        map_x = self.width - size - 10
        map_y = 10
        
        # Фон миникарты
        self.canvas.create_rectangle(
            map_x, map_y,
            map_x + size, map_y + size,
            fill='#000000',
            outline='#ffffff',
            width=2,
            tags="minimap"
        )
        
        # Масштаб для миникарты
        scale = size / 800  # Предполагаем, что игровая область 800x800
        
        # Отрисовываем игрока
        if player and hasattr(player, 'position'):
            px, py = player.position
            player_x = map_x + int(px * scale)
            player_y = map_y + int(py * scale)
            
            self.canvas.create_oval(
                player_x - 3, player_y - 3,
                player_x + 3, player_y + 3,
                fill=self.colors['player'],
                tags="minimap"
            )
        
        # Отрисовываем сущности
        for entity in entities:
            if hasattr(entity, 'position'):
                ex, ey = entity.position
                entity_x = map_x + int(ex * scale)
                entity_y = map_y + int(ey * scale)
                
                # Цвет сущности
                if hasattr(entity, 'enemy_type'):
                    color = self.colors.get(f'enemy_{entity.enemy_type}', '#ffffff')
                else:
                    color = '#ffffff'
                
                self.canvas.create_oval(
                    entity_x - 2, entity_y - 2,
                    entity_x + 2, entity_y + 2,
                    fill=color,
                    tags="minimap"
                )
                
    def toggle_debug_info(self):
        """Переключение отладочной информации"""
        self.show_debug_info = not self.show_debug_info
        
    def toggle_fps_display(self):
        """Переключение отображения FPS"""
        self.show_fps = not self.show_fps
        
    def toggle_health_bars(self):
        """Переключение отображения полосок здоровья"""
        self.show_health_bars = not self.show_health_bars
        
    def toggle_names(self):
        """Переключение отображения имен"""
        self.show_names = not self.show_names
        
    def get_render_stats(self) -> RenderStats:
        """Получение статистики рендеринга"""
        return self.stats

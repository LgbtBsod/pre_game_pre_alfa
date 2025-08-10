"""
Менеджер рендеринга - управляет отрисовкой всех игровых элементов
"""
import time
from typing import Dict, List, Optional, Any, Tuple
from tkinter import Canvas

from core.game_state_manager import game_state_manager
from config.game_constants import PLAYER_COLOR, TEXT_COLOR
from utils.game_utils import rgb_to_hex


class RenderManager:
    """Управляет рендерингом всех игровых элементов"""
    
    def __init__(self, canvas: Canvas, game_state: game_state_manager):
        self.canvas = canvas
        self.game_state = game_state
        self.width = canvas.winfo_reqwidth()
        self.height = canvas.winfo_reqheight()
        
        # Позиция камеры
        self.map_view_x = 0
        self.map_view_y = 0
        
    def clear(self):
        """Очистка canvas"""
        self.canvas.delete("all")
        
    def update(self):
        """Обновление экрана"""
        self.canvas.update()
        
    def render_area(self, area_name: str):
        """Рендеринг игровой области"""
        # Простая отрисовка фона
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill='#1a1a1a',
            outline='#333333',
            width=2
        )
        
        # Отображаем название области
        self.canvas.create_text(
            self.width // 2, 30,
            text=f"Область: {area_name}",
            fill=rgb_to_hex(TEXT_COLOR),
            font=('Arial', 16, 'bold')
        )
        
    def render_entity(self, entity):
        """Рендеринг игровой сущности"""
        if not hasattr(entity, 'position'):
            return
            
        x, y = entity.position
        
        # Определяем цвет в зависимости от типа сущности
        if hasattr(entity, 'name') and 'player' in entity.name.lower():
            color = rgb_to_hex(PLAYER_COLOR)
            size = 20
        elif hasattr(entity, 'enemy_type'):
            if entity.enemy_type == "warrior":
                color = "#ff3333"
            elif entity.enemy_type == "archer":
                color = "#ff66cc"
            else:
                color = "#3399ff"
            size = 15
        else:
            color = "#ffffff"
            size = 10
            
        # Отрисовываем сущность как круг
        self.canvas.create_oval(
            x - size, y - size,
            x + size, y + size,
            fill=color,
            outline='#ffffff',
            width=2
        )
        
        # Отображаем имя или тип
        name = getattr(entity, 'name', getattr(entity, 'enemy_type', 'Unknown'))
        self.canvas.create_text(
            x, y - size - 10,
            text=name,
            fill=rgb_to_hex(TEXT_COLOR),
            font=('Arial', 10)
        )
        
        # Отображаем здоровье
        if hasattr(entity, 'health') and hasattr(entity, 'max_health'):
            health_percent = entity.health / entity.max_health
            health_width = 30
            health_height = 4
            
            # Фон полоски здоровья
            self.canvas.create_rectangle(
                x - health_width//2, y + size + 5,
                x + health_width//2, y + size + 5 + health_height,
                fill='#333333',
                outline='#666666'
            )
            
            # Полоска здоровья
            current_width = int(health_width * health_percent)
            health_color = '#00ff00' if health_percent > 0.5 else '#ffff00' if health_percent > 0.25 else '#ff0000'
            
            if current_width > 0:
                self.canvas.create_rectangle(
                    x - health_width//2, y + size + 5,
                    x - health_width//2 + current_width, y + size + 5 + health_height,
                    fill=health_color
                )
                
    def render_ui(self):
        """Рендеринг пользовательского интерфейса"""
        # Информация о времени игры
        game_time = time.time()
        time_str = f"Время: {int(game_time // 60)}:{int(game_time % 60):02d}"
        
        self.canvas.create_text(
            10, 10,
            text=time_str,
            fill=rgb_to_hex(TEXT_COLOR),
            font=('Arial', 12),
            anchor='nw'
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
                fill=rgb_to_hex(TEXT_COLOR),
                font=('Arial', 10),
                anchor='nw'
            )
            y_offset += 20
            
    def render_frame(self):
        """Отрисовка полного кадра"""
        self.clear()
        
        # Рендер области
        self.render_area("current_area")
        
        # Рендер UI
        self.render_ui()
        
    def center_camera_on_player(self):
        """Центрирование камеры на игроке"""
        if not self.game_state.player:
            return
            
        px, py = self.game_state.player.position
        self.map_view_x = max(0, px - self.width // 2)
        self.map_view_y = max(0, py - self.height // 2)
        
    def get_world_position(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Получение мировой позиции из экранных координат"""
        world_x = screen_x + self.map_view_x
        world_y = screen_y + self.map_view_y
        return world_x, world_y
        
    def draw_banner(self, text: str):
        """Отрисовка баннера"""
        # Полупрозрачный фон
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill='#000000',
            stipple='gray25'
        )
        
        # Текст баннера
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=text,
            fill=rgb_to_hex((255, 215, 0)),
            font=('Arial', 24, 'bold')
        )

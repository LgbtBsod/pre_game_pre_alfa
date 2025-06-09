# UI/ui_buff.py

from ursina import Entity, Text, color, Vec3, camera
from typing import List, Dict
import time


class BuffUI(Entity):
    def __init__(self, buff_manager):
        super().__init__(parent=camera.ui)
        self.buff_manager = buff_manager
        self.buff_icons = []  # Для хранения иконок баффов
        self.last_update_time = 0
        self.update_interval = 0.2  # Обновлять UI каждые 0.2 секунды
        
        # Основной текст с баффами
        self.buff_text = Text(
            text='',
            position=Vec3(-0.85, 0.3, -1),
            scale=0.8,
            color=color.gold,
            background=True,
            background_color=color.black66,
            background_padding=Vec3(0.5, 0.3, 0)
        )
        
        # Заголовок
        self.title = Text(
            text="Active Buffs:",
            position=Vec3(-0.85, 0.4, -1),
            scale=1.0,
            color=color.white,
            parent=self
        )

    def update(self):
        # Оптимизация: не обновлять каждый кадр
        if time.time() - self.last_update_time < self.update_interval:
            return
            
        self.last_update_time = time.time()
        self._update_buff_display()

    def _update_buff_display(self):
        """Обновляет отображение активных баффов"""
        buffs = self.buff_manager.get_active_buffs()
        
        if not buffs:
            self.buff_text.text = "No active buffs"
            self.buff_text.color = color.gray
            return
            
        self.buff_text.color = color.gold
        lines = []
        
        for buff in buffs:
            line = self._format_buff_line(buff)
            lines.append(line)
            
        self.buff_text.text = '\n'.join(lines)
        
        # Обновляем позицию текста относительно количества баффов
        self._adjust_ui_position(len(buffs))

    def _format_buff_line(self, buff: Dict) -> str:
        """Форматирует строку для отображения баффа"""
        stat_name = buff['stat'].replace('_', ' ').title()
        value = buff['value']
        time_left = buff.get('time_left')
        
        # Форматирование значения в зависимости от типа
        if buff['type'] == 'percent':
            value_str = f"+{value*100:.0f}%"
        elif buff['type'] == 'flat':
            value_str = f"+{value:.0f}"
        else:  # multiply
            value_str = f"x{value:.1f}"
        
        # Добавляем оставшееся время, если есть
        if time_left and time_left > 0:
            return f"{stat_name}: {value_str} ({max(0, time_left):.1f}s)"
        return f"{stat_name}: {value_str}"

    def _adjust_ui_position(self, buff_count: int):
        """Регулирует позицию UI в зависимости от количества баффов"""
        # Смещаем вниз при большом количестве баффов
        vertical_offset = min(0.3, 0.3 - (buff_count * 0.02))
        self.buff_text.position = Vec3(-0.85, vertical_offset, -1)
        self.title.position = Vec3(-0.85, vertical_offset + 0.1, -1)

    def flash_important_buff(self, stat: str):
        """Визуально выделяет важный бафф"""
        original_color = self.buff_text.color
        self.buff_text.color = color.orange
        invoke(setattr, self.buff_text, 'color', original_color, delay=0.5)
#!/usr/bin/env python3
"""
Inventory Widget Module - Модуль инвентаря UI
Современный неоновый дизайн с полупрозрачностью
"""

import logging
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton

from .panel import NeonPanel, PanelStyle
from .button import NeonButton, ButtonStyle

logger = logging.getLogger(__name__)

@dataclass
class InventorySlotStyle:
    """Стиль слота инвентаря"""
    # Размеры
    width: float = 0.08
    height: float = 0.08
    
    # Цвета
    empty_color: Tuple[float, float, float, float] = (0.3, 0.3, 0.3, 0.5)
    filled_color: Tuple[float, float, float, float] = (0.5, 0.5, 0.5, 0.8)
    border_color: Tuple[float, float, float, float] = (0.0, 1.0, 1.0, 0.6)
    highlight_color: Tuple[float, float, float, float] = (1.0, 1.0, 0.0, 0.8)
    
    # Эффекты
    border_width: float = 0.002
    show_tooltip: bool = True

@dataclass
class InventoryStyle:
    """Стиль инвентаря"""
    # Размеры
    width: float = 0.8
    height: float = 0.6
    
    # Слоты
    slots_per_row: int = 8
    slots_per_column: int = 6
    slot_spacing: float = 0.01
    
    # Цвета
    background_color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.8)
    border_color: Tuple[float, float, float, float] = (0.0, 1.0, 1.0, 0.8)
    
    # Заголовок
    title_color: Tuple[float, float, float, float] = (0.0, 1.0, 1.0, 1.0)
    title_scale: float = 0.05

class InventorySlot:
    """Слот инвентаря"""
    
    def __init__(self, 
                 slot_id: int,
                 style: Optional[InventorySlotStyle] = None,
                 parent=None):
        self.slot_id = slot_id
        self.style = style or InventorySlotStyle()
        self.parent = parent
        
        # UI элементы
        self.background_frame = None
        self.border_frame = None
        self.item_label = None
        self.count_label = None
        
        # Состояние
        self.item_data: Optional[Dict[str, Any]] = None
        self.is_highlighted = False
        self.is_selected = False
        
        logger.debug(f"Создан слот инвентаря: {slot_id}")
    
    def create(self, pos: Tuple[float, float, float] = (0, 0, 0)) -> DirectFrame:
        """Создание слота Panda3D"""
        try:
            # Основной контейнер
            main_frame = DirectFrame(
                frameColor=(0, 0, 0, 0),
                frameSize=(-self.style.width/2, self.style.width/2, 
                          -self.style.height/2, self.style.height/2),
                parent=self.parent
            )
            main_frame.setPos(*pos)
            
            # Фон слота
            self.background_frame = DirectFrame(
                frameColor=self.style.empty_color,
                frameSize=(-self.style.width/2, self.style.width/2, 
                          -self.style.height/2, self.style.height/2),
                parent=main_frame
            )
            
            # Граница слота
            self.border_frame = DirectFrame(
                frameColor=self.style.border_color,
                frameSize=(-self.style.width/2 - self.style.border_width, 
                          self.style.width/2 + self.style.border_width,
                          -self.style.height/2 - self.style.border_width, 
                          self.style.height/2 + self.style.border_width),
                parent=main_frame
            )
            
            # Метка предмета
            self.item_label = DirectLabel(
                text="",
                scale=0.03,
                pos=(0, 0, 0),
                frameColor=(0, 0, 0, 0),
                text_fg=(1.0, 1.0, 1.0, 1.0),
                parent=main_frame
            )
            
            # Счетчик предметов
            self.count_label = DirectLabel(
                text="",
                scale=0.02,
                pos=(self.style.width/2 - 0.01, 0, -self.style.height/2 + 0.01),
                frameColor=(0, 0, 0, 0),
                text_fg=(1.0, 1.0, 1.0, 1.0),
                parent=main_frame
            )
            
            logger.debug(f"Слот инвентаря {self.slot_id} создан успешно")
            return main_frame
            
        except Exception as e:
            logger.error(f"Ошибка создания слота инвентаря {self.slot_id}: {e}")
            return None
    
    def set_item(self, item_data: Optional[Dict[str, Any]]):
        """Установка предмета в слот"""
        try:
            self.item_data = item_data
            
            if item_data:
                # Предмет есть
                self.background_frame['frameColor'] = self.style.filled_color
                self.item_label['text'] = item_data.get('name', 'Unknown')
                
                # Показываем количество если больше 1
                count = item_data.get('count', 1)
                if count > 1:
                    self.count_label['text'] = str(count)
                    self.count_label.setVisible(True)
                else:
                    self.count_label.setVisible(False)
                
                logger.debug(f"Предмет {item_data.get('name', 'Unknown')} помещен в слот {self.slot_id}")
            else:
                # Слот пустой
                self.background_frame['frameColor'] = self.style.empty_color
                self.item_label['text'] = ""
                self.count_label.setVisible(False)
                
                logger.debug(f"Слот {self.slot_id} очищен")
                
        except Exception as e:
            logger.error(f"Ошибка установки предмета в слот {self.slot_id}: {e}")
    
    def highlight(self, highlighted: bool):
        """Подсветка слота"""
        try:
            self.is_highlighted = highlighted
            if highlighted:
                self.border_frame['frameColor'] = self.style.highlight_color
            else:
                self.border_frame['frameColor'] = self.style.border_color
                
        except Exception as e:
            logger.error(f"Ошибка подсветки слота {self.slot_id}: {e}")
    
    def select(self, selected: bool):
        """Выбор слота"""
        try:
            self.is_selected = selected
            if selected:
                self.border_frame['frameColor'] = self.style.highlight_color
            else:
                self.border_frame['frameColor'] = self.style.border_color
                
        except Exception as e:
            logger.error(f"Ошибка выбора слота {self.slot_id}: {e}")
    
    def get_item(self) -> Optional[Dict[str, Any]]:
        """Получение предмета из слота"""
        return self.item_data
    
    def is_empty(self) -> bool:
        """Проверка, пуст ли слот"""
        return self.item_data is None
    
    def destroy(self):
        """Уничтожение слота"""
        if self.background_frame:
            self.background_frame.destroy()
            self.background_frame = None
        if self.border_frame:
            self.border_frame.destroy()
            self.border_frame = None
        if self.item_label:
            self.item_label.destroy()
            self.item_label = None
        if self.count_label:
            self.count_label.destroy()
            self.count_label = None
        
        logger.debug(f"Слот инвентаря {self.slot_id} уничтожен")

class NeonInventory:
    """Неоновый инвентарь с современным дизайном"""
    
    def __init__(self, 
                 title: str = "INVENTORY",
                 style: Optional[InventoryStyle] = None,
                 parent=None):
        self.title = title
        self.style = style or InventoryStyle()
        self.parent = parent
        
        # UI элементы
        self.background_panel = None
        self.title_label = None
        self.slots_frame = None
        
        # Слоты
        self.slots: List[InventorySlot] = []
        self.selected_slot: Optional[int] = None
        
        # Кнопки
        self.use_button = None
        self.drop_button = None
        self.sort_button = None
        
        logger.debug(f"Создан неоновый инвентарь: {title}")
    
    def create(self, pos: Tuple[float, float, float] = (0, 0, 0)) -> DirectFrame:
        """Создание инвентаря Panda3D"""
        try:
            # Основная панель
            panel_style = PanelStyle(
                width=self.style.width,
                height=self.style.height,
                background_color=self.style.background_color,
                border_color=self.style.border_color,
                title_color=self.style.title_color,
                title_scale=self.style.title_scale
            )
            self.background_panel = NeonPanel(self.title, panel_style, self.parent)
            self.background_panel.create(pos)
            
            # Создаем слоты
            self._create_slots()
            
            # Создаем кнопки управления
            self._create_control_buttons()
            
            logger.debug(f"Инвентарь {self.title} создан успешно")
            return self.background_panel.background_frame
            
        except Exception as e:
            logger.error(f"Ошибка создания инвентаря {self.title}: {e}")
            return None
    
    def _create_slots(self):
        """Создание слотов инвентаря"""
        try:
            # Контейнер для слотов
            self.slots_frame = DirectFrame(
                frameColor=(0, 0, 0, 0),
                frameSize=(-self.style.width/2 + 0.05, self.style.width/2 - 0.05,
                          -self.style.height/2 + 0.1, self.style.height/2 - 0.1),
                parent=self.background_panel.content_frame
            )
            
            # Создаем слоты в сетке
            slot_style = InventorySlotStyle()
            slot_index = 0
            
            for row in range(self.style.slots_per_column):
                for col in range(self.style.slots_per_row):
                    # Позиция слота
                    x = (col - (self.style.slots_per_row - 1) / 2) * (self.style.width + self.style.slot_spacing)
                    z = (row - (self.style.slots_per_column - 1) / 2) * (self.style.height + self.style.slot_spacing)
                    pos = (x, 0, z)
                    
                    # Создаем слот
                    slot = InventorySlot(slot_index, slot_style, self.slots_frame)
                    slot.create(pos)
                    self.slots.append(slot)
                    
                    slot_index += 1
            
            logger.debug(f"Создано {len(self.slots)} слотов инвентаря")
            
        except Exception as e:
            logger.error(f"Ошибка создания слотов инвентаря: {e}")
    
    def _create_control_buttons(self):
        """Создание кнопок управления"""
        try:
            # Кнопка использования
            self.use_button = NeonButton("USE", None, parent=self.background_panel.content_frame)
            self.use_button.create((0.2, 0, -self.style.height/2 + 0.05))
            
            # Кнопка выброса
            self.drop_button = NeonButton("DROP", None, parent=self.background_panel.content_frame)
            self.drop_button.create((0.0, 0, -self.style.height/2 + 0.05))
            
            # Кнопка сортировки
            self.sort_button = NeonButton("SORT", None, parent=self.background_panel.content_frame)
            self.sort_button.create((-0.2, 0, -self.style.height/2 + 0.05))
            
            logger.debug("Кнопки управления инвентарем созданы")
            
        except Exception as e:
            logger.error(f"Ошибка создания кнопок управления: {e}")
    
    def add_item(self, item_data: Dict[str, Any], slot_id: Optional[int] = None) -> bool:
        """Добавление предмета в инвентарь"""
        try:
            if slot_id is None:
                # Ищем свободный слот
                for i, slot in enumerate(self.slots):
                    if slot.is_empty():
                        slot_id = i
                        break
            
            if slot_id is not None and 0 <= slot_id < len(self.slots):
                self.slots[slot_id].set_item(item_data)
                logger.debug(f"Предмет {item_data.get('name', 'Unknown')} добавлен в слот {slot_id}")
                return True
            else:
                logger.warning(f"Не удалось найти свободный слот для предмета {item_data.get('name', 'Unknown')}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка добавления предмета: {e}")
            return False
    
    def remove_item(self, slot_id: int) -> Optional[Dict[str, Any]]:
        """Удаление предмета из инвентаря"""
        try:
            if 0 <= slot_id < len(self.slots):
                item_data = self.slots[slot_id].get_item()
                self.slots[slot_id].set_item(None)
                
                if self.selected_slot == slot_id:
                    self.selected_slot = None
                
                logger.debug(f"Предмет удален из слота {slot_id}")
                return item_data
            else:
                logger.warning(f"Неверный ID слота: {slot_id}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка удаления предмета: {e}")
            return None
    
    def select_slot(self, slot_id: int):
        """Выбор слота"""
        try:
            # Снимаем выделение с предыдущего слота
            if self.selected_slot is not None and 0 <= self.selected_slot < len(self.slots):
                self.slots[self.selected_slot].select(False)
            
            # Выделяем новый слот
            if 0 <= slot_id < len(self.slots):
                self.slots[slot_id].select(True)
                self.selected_slot = slot_id
                logger.debug(f"Выбран слот {slot_id}")
            else:
                self.selected_slot = None
                
        except Exception as e:
            logger.error(f"Ошибка выбора слота: {e}")
    
    def get_selected_item(self) -> Optional[Dict[str, Any]]:
        """Получение выбранного предмета"""
        if self.selected_slot is not None and 0 <= self.selected_slot < len(self.slots):
            return self.slots[self.selected_slot].get_item()
        return None
    
    def sort_inventory(self):
        """Сортировка инвентаря"""
        try:
            # Собираем все предметы
            items = []
            for slot in self.slots:
                if not slot.is_empty():
                    items.append(slot.get_item())
                    slot.set_item(None)
            
            # Сортируем по типу и имени
            items.sort(key=lambda x: (x.get('type', ''), x.get('name', '')))
            
            # Распределяем обратно по слотам
            for i, item in enumerate(items):
                if i < len(self.slots):
                    self.slots[i].set_item(item)
            
            logger.debug("Инвентарь отсортирован")
            
        except Exception as e:
            logger.error(f"Ошибка сортировки инвентаря: {e}")
    
    def clear_inventory(self):
        """Очистка инвентаря"""
        try:
            for slot in self.slots:
                slot.set_item(None)
            
            self.selected_slot = None
            logger.debug("Инвентарь очищен")
            
        except Exception as e:
            logger.error(f"Ошибка очистки инвентаря: {e}")
    
    def set_visible(self, visible: bool):
        """Показать/скрыть инвентарь"""
        if self.background_panel:
            self.background_panel.set_visible(visible)
    
    def destroy(self):
        """Уничтожение инвентаря"""
        # Уничтожаем слоты
        for slot in self.slots:
            slot.destroy()
        self.slots.clear()
        
        # Уничтожаем кнопки
        if self.use_button:
            self.use_button.destroy()
        if self.drop_button:
            self.drop_button.destroy()
        if self.sort_button:
            self.sort_button.destroy()
        
        # Уничтожаем панель
        if self.background_panel:
            self.background_panel.destroy()
        
        logger.debug(f"Инвентарь {self.title} уничтожен")

def create_neon_inventory(title: str = "INVENTORY",
                         style: Optional[InventoryStyle] = None,
                         parent=None,
                         pos: Tuple[float, float, float] = (0, 0, 0)) -> NeonInventory:
    """Фабричная функция для создания неонового инвентаря"""
    inventory = NeonInventory(title, style, parent)
    inventory.create(pos)
    return inventory

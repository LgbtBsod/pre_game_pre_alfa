# UI/inventory.py
from ursina import *
from typing import List, Dict, Optional
from equip.items_data import ItemsData

class InventoryUI(Entity):
    def __init__(self, player, equipment, rows=5, cols=6):
        super().__init__(
            parent=camera.ui,
            model=Quad(radius=0.02),
            scale=(cols * 0.1 + 0.05, rows * 0.1 + 0.05),
            position=(0.6, 0.1),
            color=color.rgba(20, 20, 30, 220),
            enabled=False
        )
        self.player = player
        self.equipment = equipment
        self.items_data = ItemsData()
        
        # UI элементы
        self.cells: List[Button] = []
        self._init_cells(rows, cols)
        self._init_tooltip()
        self._init_context_menu()
        
        # Состояние
        self.selected_item: Optional[str] = None
    
    def _init_cells(self, rows: int, cols: int):
        """Создает сетку ячеек инвентаря"""
        start_x = -((cols - 1) * 0.1) / 2
        start_y = ((rows - 1) * 0.1) / 2
        
        for row in range(rows):
            for col in range(cols):
                btn = Button(
                    parent=self,
                    model=Quad(radius=0.02),
                    position=(start_x + col * 0.1, start_y - row * 0.1),
                    scale=0.09,
                    color=color.rgba(50, 50, 60, 200),
                    highlight_color=color.rgba(80, 80, 90, 200),
                    on_click=self._on_cell_click
                )
                btn.item_icon = Entity(parent=btn, scale=0.7)
                btn.item_name = ""
                self.cells.append(btn)
    
    def _init_tooltip(self):
        """Инициализирует подсказку для предметов"""
        self.tooltip = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.25, 0.15),
            color=color.rgba(10, 10, 20, 240),
            enabled=False
        )

        # Имя предмета
        self.tooltip_name = Text(
            parent=self.tooltip,
            text='',
            position=Vec3(-0.45, 0.35, -1),
            scale=1.2,
            color=color.orange
        )

        # Статы
        self.tooltip_stats = Text(
            parent=self.tooltip,
            text='',
            position=Vec3(-0.45, 0.2, -1),
            scale=0.9,
            color=color.white
        )

        # Описание
        self.tooltip_desc = Text(
            parent=self.tooltip,
            text='',
            position=Vec3(-0.45, 0.05, -1),
            scale=0.8,
            color=color.lime
        )
        
    
    def _init_context_menu(self):
        """Инициализирует контекстное меню"""
        self.context_menu = Panel(
            parent=camera.ui,
            scale=(0.15, 0.1),
            color=color.rgba(30, 30, 40, 240),
            enabled=False
        )
        self.context_menu.use_btn = Button(
            parent=self.context_menu,
            text="Use",
            scale=(0.9, 0.3),
            position=(0, 0.15),
            on_click=self._use_item
        )
        self.context_menu.equip_btn = Button(
            parent=self.context_menu,
            text="Equip",
            scale=(0.9, 0.3),
            position=(0, -0.15),
            on_click=self._equip_item
        )
    
    def update_inventory(self):
        """Обновляет отображение инвентаря"""
        for i, cell in enumerate(self.cells):
            cell.item_icon.texture = None
            cell.item_name = ""
            
            if i < len(self.player.inventory):
                item_name = self.player.inventory[i]
                if item_data := self.items_data.get_item(item_name):
                    cell.item_name = item_name
                    
                    # Установка иконки
                    if item_data['icon']:
                        cell.item_icon.texture = item_data['icon']
                    
                    # Подсветка экипированных предметов
                    if item_name in self.equipment.equipped_items:
                        cell.color = color.rgba(100, 80, 50, 220)
    
    def _on_cell_click(self):
        """Обрабатывает клик по ячейке"""
        if hasattr(self.hovered_entity, 'item_name') and self.hovered_entity.item_name:
            self.selected_item = self.hovered_entity.item_name
            self._show_context_menu()
    
    def _show_context_menu(self):
        """Показывает контекстное меню для выбранного предмета"""
        if not self.selected_item:
            return
            
        item_data = self.items_data.get_item(self.selected_item)
        if not item_data:
            return
            
        # Позиционируем меню рядом с курсором
        self.context_menu.position = mouse.position + Vec2(0.1, -0.1)
        
        # Настраиваем доступные действия
        self.context_menu.use_btn.enabled = item_data['trigger'] == 'active'
        self.context_menu.equip_btn.enabled = item_data['type'] == 'artifact'
        
        self.context_menu.enabled = True
    
    def _use_item(self):
        """Использует выбранный предмет"""
        if self.selected_item and self.selected_item in self.player.inventory:
            self.equipment.use_item_effect(self.selected_item)
            self._close_context_menu()
    
    def _equip_item(self):
        """Экипирует или снимает выбранный предмет"""
        if not self.selected_item:
            return
            
        if self.selected_item in self.equipment.equipped_items:
            self.equipment.unequip_item(self.selected_item)
        else:
            self.equipment.equip_item(self.selected_item)
        
        self.update_inventory()
        self._close_context_menu()
    
    def _close_context_menu(self):
        """Закрывает контекстное меню"""
        self.context_menu.enabled = False
        self.selected_item = None
    
    def input(self, key):
        """Обрабатывает ввод"""
        if key == 'i':
            self.enabled = not self.enabled
            if self.enabled:
                self.update_inventory()
            else:
                self._close_context_menu()
        elif key == 'escape' and self.enabled:
            self.enabled = False
            self._close_context_menu()
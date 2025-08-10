import tkinter as tk
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MenuItem:
    """Элемент меню"""
    label: str
    action: Callable
    icon: Optional[str] = None
    shortcut: Optional[str] = None
    enabled: bool = True


class GameMenu:
    """Игровое меню, вызываемое во время игры"""
    
    def __init__(self, parent_canvas: tk.Canvas, width: int, height: int):
        self.parent_canvas = parent_canvas
        self.width = width
        self.height = height
        self.visible = False
        self.menu_items: Dict[str, MenuItem] = {}
        self.current_submenu: Optional[str] = None
        self.submenus: Dict[str, Dict[str, MenuItem]] = {}
        
        # Создаем canvas для меню
        self.menu_canvas = tk.Canvas(
            parent_canvas.master,
            width=400,
            height=500,
            bg='#2a2a2a',
            highlightthickness=0,
            relief='flat'
        )
        
        # Стили
        self.colors = {
            'bg': '#2a2a2a',
            'bg_hover': '#3a3a3a',
            'text': '#ffffff',
            'text_disabled': '#666666',
            'accent': '#4a9eff',
            'border': '#555555'
        }
        
        self.fonts = {
            'title': ('Arial', 18, 'bold'),
            'menu': ('Arial', 12),
            'submenu': ('Arial', 10)
        }
        
        # Привязываем события
        self.menu_canvas.bind('<Button-1>', self._on_click)
        self.menu_canvas.bind('<Motion>', self._on_mouse_move)
        self.menu_canvas.bind('<Key>', self._on_key)
        self.menu_canvas.bind('<Escape>', self.hide)
        
        # Инициализируем меню
        self._init_main_menu()
        self._init_submenus()
    
    def _init_main_menu(self):
        """Инициализация главного меню"""
        self.menu_items = {
            'resume': MenuItem("Продолжить", self.hide, shortcut="ESC"),
            'inventory': MenuItem("Инвентарь", lambda: self.show_submenu('inventory'), shortcut="I"),
            'character': MenuItem("Персонаж", lambda: self.show_submenu('character'), shortcut="C"),
            'skills': MenuItem("Умения", lambda: self.show_submenu('skills'), shortcut="K"),
            'settings': MenuItem("Настройки", lambda: self.show_submenu('settings'), shortcut="S"),
            'save': MenuItem("Сохранить", lambda: None, shortcut="F5"),
            'quit': MenuItem("Выйти в главное меню", lambda: None, shortcut="Q")
        }
    
    def _init_submenus(self):
        """Инициализация подменю"""
        self.submenus = {
            'inventory': {
                'weapons': MenuItem("Оружие", lambda: None),
                'armor': MenuItem("Броня", lambda: None),
                'consumables': MenuItem("Расходники", lambda: None),
                'materials': MenuItem("Материалы", lambda: None)
            },
            'character': {
                'attributes': MenuItem("Характеристики", lambda: None),
                'stats': MenuItem("Статистика", lambda: None),
                'equipment': MenuItem("Экипировка", lambda: None),
                'leveling': MenuItem("Прокачка", lambda: None)
            },
            'skills': {
                'combat': MenuItem("Боевые", lambda: None),
                'passive': MenuItem("Пассивные", lambda: None),
                'special': MenuItem("Особые", lambda: None)
            },
            'settings': {
                'graphics': MenuItem("Графика", lambda: None),
                'audio': MenuItem("Звук", lambda: None),
                'controls': MenuItem("Управление", lambda: None),
                'gameplay': MenuItem("Игровой процесс", lambda: None)
            }
        }
    
    def show(self, x: int = None, y: int = None):
        """Показать меню"""
        if self.visible:
            return
        
        self.visible = True
        self.current_submenu = None
        
        # Позиционируем меню по центру или по указанным координатам
        if x is None:
            x = (self.width - 400) // 2
        if y is None:
            y = (self.height - 500) // 2
        
        self.menu_canvas.place(x=x, y=y)
        self.menu_canvas.focus_set()
        self._draw_menu()
    
    def hide(self):
        """Скрыть меню"""
        if not self.visible:
            return
        
        self.visible = False
        self.current_submenu = None
        self.menu_canvas.place_forget()
        self.parent_canvas.focus_set()
    
    def toggle(self):
        """Переключить видимость меню"""
        if self.visible:
            self.hide()
        else:
            self.show()
    
    def _draw_menu(self):
        """Отрисовка меню"""
        self.menu_canvas.delete("all")
        
        if self.current_submenu:
            self._draw_submenu()
        else:
            self._draw_main_menu()
    
    def _draw_main_menu(self):
        """Отрисовка главного меню"""
        # Заголовок
        self.menu_canvas.create_text(
            200, 30,
            text="ИГРОВОЕ МЕНЮ",
            font=self.fonts['title'],
            fill=self.colors['text']
        )
        
        # Разделитель
        self.menu_canvas.create_line(20, 60, 380, 60, fill=self.colors['border'], width=2)
        
        # Элементы меню
        y_start = 100
        item_height = 40
        spacing = 10
        
        for i, (key, item) in enumerate(self.menu_items.items()):
            y = y_start + i * (item_height + spacing)
            
            # Фон элемента
            bg_color = self.colors['bg_hover'] if key == 'resume' else self.colors['bg']
            self.menu_canvas.create_rectangle(
                20, y, 380, y + item_height,
                fill=bg_color,
                outline=self.colors['border'],
                tags=f"menu_item_{key}"
            )
            
            # Текст
            text_color = self.colors['text'] if item.enabled else self.colors['text_disabled']
            self.menu_canvas.create_text(
                40, y + item_height // 2,
                text=item.label,
                font=self.fonts['menu'],
                fill=text_color,
                anchor='w'
            )
            
            # Горячая клавиша
            if item.shortcut:
                self.menu_canvas.create_text(
                    360, y + item_height // 2,
                    text=item.shortcut,
                    font=self.fonts['submenu'],
                    fill=self.colors['accent'],
                    anchor='e'
                )
    
    def _draw_submenu(self):
        """Отрисовка подменю"""
        # Кнопка "Назад"
        self.menu_canvas.create_rectangle(20, 20, 100, 50, fill=self.colors['bg'], outline=self.colors['border'])
        self.menu_canvas.create_text(60, 35, text="← Назад", font=self.fonts['submenu'], fill=self.colors['text'])
        
        # Заголовок подменю
        submenu_name = self.current_submenu.title()
        self.menu_canvas.create_text(
            200, 30,
            text=submenu_name,
            font=self.fonts['title'],
            fill=self.colors['text']
        )
        
        # Разделитель
        self.menu_canvas.create_line(20, 60, 380, 60, fill=self.colors['border'], width=2)
        
        # Элементы подменю
        y_start = 100
        item_height = 40
        spacing = 10
        
        for i, (key, item) in enumerate(self.submenus[self.current_submenu].items()):
            y = y_start + i * (item_height + spacing)
            
            self.menu_canvas.create_rectangle(
                20, y, 380, y + item_height,
                fill=self.colors['bg'],
                outline=self.colors['border'],
                tags=f"submenu_item_{key}"
            )
            
            text_color = self.colors['text'] if item.enabled else self.colors['text_disabled']
            self.menu_canvas.create_text(
                40, y + item_height // 2,
                text=item.label,
                font=self.fonts['menu'],
                fill=text_color,
                anchor='w'
            )
    
    def show_submenu(self, submenu_name: str):
        """Показать подменю"""
        if submenu_name in self.submenus:
            self.current_submenu = submenu_name
            self._draw_menu()
    
    def _on_click(self, event):
        """Обработка клика мыши"""
        x, y = event.x, event.y
        
        if self.current_submenu:
            # Проверяем клик по кнопке "Назад"
            if 20 <= x <= 100 and 20 <= y <= 50:
                self.current_submenu = None
                self._draw_menu()
                return
            
            # Проверяем клик по элементам подменю
            for key, item in self.submenus[self.current_submenu].items():
                item_y = 100 + list(self.submenus[self.current_submenu].keys()).index(key) * 50
                if 20 <= x <= 380 and item_y <= y <= item_y + 40:
                    if item.enabled and item.action:
                        item.action()
                    return
        else:
            # Проверяем клик по элементам главного меню
            for key, item in self.menu_items.items():
                item_y = 100 + list(self.menu_items.keys()).index(key) * 50
                if 20 <= x <= 380 and item_y <= y <= item_y + 40:
                    if item.enabled and item.action:
                        item.action()
                    return
    
    def _on_mouse_move(self, event):
        """Обработка движения мыши для hover эффектов"""
        # Можно добавить hover эффекты для элементов меню
        pass
    
    def _on_key(self, event):
        """Обработка нажатий клавиш"""
        key = event.keysym.lower()
        
        # Проверяем горячие клавиши
        for menu_key, item in self.menu_items.items():
            if item.shortcut and item.shortcut.lower() == key:
                if item.enabled and item.action:
                    item.action()
                return
        
        # ESC для закрытия
        if key == 'escape':
            self.hide()
            return
        
        # Enter для подтверждения выбора
        if key == 'return':
            # Можно добавить логику выбора текущего выделенного элемента
            pass
    
    def update_menu_items(self, new_items: Dict[str, MenuItem]):
        """Обновить элементы меню"""
        self.menu_items.update(new_items)
        if self.visible:
            self._draw_menu()
    
    def set_callback(self, menu_key: str, callback: Callable):
        """Установить callback для элемента меню"""
        if menu_key in self.menu_items:
            self.menu_items[menu_key].action = callback
        elif menu_key in self.submenus:
            for submenu_key, item in self.submenus[menu_key].items():
                if submenu_key == menu_key:
                    item.action = callback
                    break

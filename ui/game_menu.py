"""
Игровое меню с оптимизированной архитектурой для pygame
"""

import pygame
from typing import Callable, Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class MenuState(Enum):
    """Состояния меню"""
    MAIN = "main"
    SUBMENU = "submenu"
    HIDDEN = "hidden"


@dataclass
class MenuItem:
    """Элемент меню"""
    label: str
    action: Callable
    icon: Optional[str] = None
    shortcut: Optional[str] = None
    enabled: bool = True
    description: Optional[str] = None
    category: Optional[str] = None


class GameMenu:
    """Игровое меню с оптимизированной архитектурой для pygame"""

    def __init__(self, screen: pygame.Surface, width: int, height: int):
        self.screen = screen
        self.width = width
        self.height = height
        self.state = MenuState.HIDDEN
        self.visible = False

        # Элементы меню
        self.menu_items: Dict[str, MenuItem] = {}
        self.submenus: Dict[str, Dict[str, MenuItem]] = {}
        self.current_submenu: Optional[str] = None

        # Навигация
        self.selected_index = 0
        self.hover_index = -1

        # Стили
        self.colors = {
            "bg": (42, 42, 42),
            "bg_hover": (58, 58, 58),
            "bg_selected": (74, 74, 74),
            "text": (255, 255, 255),
            "text_disabled": (102, 102, 102),
            "accent": (74, 158, 255),
            "border": (85, 85, 85),
            "overlay": (0, 0, 0, 128),
        }

        # Шрифты
        self.fonts = {
            "title": pygame.font.Font(None, 36),
            "menu": pygame.font.Font(None, 24),
            "submenu": pygame.font.Font(None, 20),
            "description": pygame.font.Font(None, 18),
        }

        # Размеры
        self.layout = {
            "menu_width": 400,
            "menu_height": 500,
            "item_height": 40,
            "item_spacing": 10,
            "padding": 20,
        }

        # Инициализируем меню
        self._init_main_menu()
        self._init_submenus()

    def _init_main_menu(self):
        """Инициализация главного меню"""
        self.menu_items = {
            "resume": MenuItem(
                "Продолжить", self.hide, shortcut="ESC", description="Вернуться к игре"
            ),
            "inventory": MenuItem(
                "Инвентарь",
                lambda: self.show_submenu("inventory"),
                description="Управление предметами"
            ),
            "genetics": MenuItem(
                "Генетика",
                lambda: self.show_submenu("genetics"),
                description="Генетические модификации"
            ),
            "ai_learning": MenuItem(
                "ИИ Обучение",
                lambda: self.show_submenu("ai_learning"),
                description="Настройки ИИ"
            ),
            "settings": MenuItem(
                "Настройки",
                lambda: self.show_submenu("settings"),
                description="Параметры игры"
            ),
            "save": MenuItem(
                "Сохранить", self._save_game, shortcut="F5", description="Сохранить игру"
            ),
            "load": MenuItem(
                "Загрузить", self._load_game, shortcut="F9", description="Загрузить игру"
            ),
            "quit": MenuItem(
                "Выход", self._quit_game, shortcut="F10", description="Выйти из игры"
            ),
        }

    def _init_submenus(self):
        """Инициализация подменю"""
        self.submenus = {
            "inventory": {
                "view": MenuItem("Просмотр", lambda: None, description="Просмотр инвентаря"),
                "sort": MenuItem("Сортировка", lambda: None, description="Сортировка предметов"),
                "use": MenuItem("Использовать", lambda: None, description="Использовать предмет"),
                "drop": MenuItem("Выбросить", lambda: None, description="Выбросить предмет"),
                "back": MenuItem("Назад", lambda: self.show_main_menu(), description="Вернуться в главное меню"),
            },
            "genetics": {
                "view": MenuItem("Просмотр генов", lambda: None, description="Просмотр активных генов"),
                "modify": MenuItem("Модификация", lambda: None, description="Изменение генов"),
                "stability": MenuItem("Стабильность", lambda: None, description="Управление стабильностью"),
                "back": MenuItem("Назад", lambda: self.show_main_menu(), description="Вернуться в главное меню"),
            },
            "ai_learning": {
                "status": MenuItem("Статус", lambda: None, description="Статус обучения ИИ"),
                "parameters": MenuItem("Параметры", lambda: None, description="Настройки ИИ"),
                "training": MenuItem("Обучение", lambda: None, description="Управление обучением"),
                "back": MenuItem("Назад", lambda: self.show_main_menu(), description="Вернуться в главное меню"),
            },
            "settings": {
                "graphics": MenuItem("Графика", lambda: None, description="Настройки графики"),
                "audio": MenuItem("Звук", lambda: None, description="Настройки звука"),
                "controls": MenuItem("Управление", lambda: None, description="Настройки управления"),
                "back": MenuItem("Назад", lambda: self.show_main_menu(), description="Вернуться в главное меню"),
            },
        }

    def show(self):
        """Показать меню"""
        self.visible = True
        self.state = MenuState.MAIN
        self.selected_index = 0

    def hide(self):
        """Скрыть меню"""
        self.visible = False
        self.state = MenuState.HIDDEN

    def show_main_menu(self):
        """Показать главное меню"""
        self.state = MenuState.MAIN
        self.current_submenu = None
        self.selected_index = 0

    def show_submenu(self, submenu_name: str):
        """Показать подменю"""
        if submenu_name in self.submenus:
            self.state = MenuState.SUBMENU
            self.current_submenu = submenu_name
            self.selected_index = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий pygame"""
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_click(event)
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event)

        return False

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Обработка нажатий клавиш"""
        if event.key == pygame.K_ESCAPE:
            if self.state == MenuState.SUBMENU:
                self.show_main_menu()
            else:
                self.hide()
            return True
        elif event.key == pygame.K_UP:
            self._move_selection(-1)
            return True
        elif event.key == pygame.K_DOWN:
            self._move_selection(1)
            return True
        elif event.key == pygame.K_RETURN:
            self._execute_selected_item()
            return True

        return False

    def _handle_mouse_click(self, event: pygame.event.Event) -> bool:
        """Обработка кликов мыши"""
        if event.button == 1:  # Левый клик
            mouse_pos = pygame.mouse.get_pos()
            clicked_item = self._get_item_at_position(mouse_pos)
            if clicked_item:
                self._execute_item(clicked_item)
                return True
        return False

    def _handle_mouse_motion(self, event: pygame.event.Event) -> bool:
        """Обработка движения мыши"""
        mouse_pos = pygame.mouse.get_pos()
        hover_item = self._get_item_at_position(mouse_pos)
        if hover_item:
            self.hover_index = hover_item
        else:
            self.hover_index = -1
        return False

    def _move_selection(self, direction: int):
        """Перемещение выбора"""
        if self.state == MenuState.MAIN:
            items = list(self.menu_items.values())
        else:
            items = list(self.submenus[self.current_submenu].values())

        if items:
            self.selected_index = (self.selected_index + direction) % len(items)

    def _execute_selected_item(self):
        """Выполнение выбранного элемента"""
        if self.state == MenuState.MAIN:
            items = list(self.menu_items.values())
        else:
            items = list(self.submenus[self.current_submenu].values())

        if 0 <= self.selected_index < len(items):
            self._execute_item(items[self.selected_index])

    def _execute_item(self, item: MenuItem):
        """Выполнение элемента меню"""
        if item.enabled and item.action:
            try:
                item.action()
            except Exception as e:
                print(f"Ошибка выполнения действия меню: {e}")

    def _get_item_at_position(self, pos: tuple) -> Optional[int]:
        """Получение элемента по позиции мыши"""
        x, y = pos
        
        # Вычисляем позицию меню
        menu_x = (self.width - self.layout["menu_width"]) // 2
        menu_y = (self.height - self.layout["menu_height"]) // 2
        
        if not (menu_x <= x <= menu_x + self.layout["menu_width"] and
                menu_y <= y <= menu_y + self.layout["menu_height"]):
            return None

        # Вычисляем индекс элемента
        item_y = y - menu_y - self.layout["padding"]
        if item_y < 0:
            return None

        item_index = item_y // (self.layout["item_height"] + self.layout["item_spacing"])
        
        if self.state == MenuState.MAIN:
            items = list(self.menu_items.values())
        else:
            items = list(self.submenus[self.current_submenu].values())

        if 0 <= item_index < len(items):
            return item_index
        return None

    def render(self):
        """Отрисовка меню"""
        if not self.visible:
            return

        # Создаем поверхность для меню
        menu_surface = pygame.Surface((self.layout["menu_width"], self.layout["menu_height"]))
        menu_surface.set_alpha(230)  # Полупрозрачность
        menu_surface.fill(self.colors["bg"])

        # Позиция меню
        menu_x = (self.width - self.layout["menu_width"]) // 2
        menu_y = (self.height - self.layout["menu_height"]) // 2

        # Заголовок
        title_text = "МЕНЮ ИГРЫ" if self.state == MenuState.MAIN else self.current_submenu.upper()
        title_surface = self.fonts["title"].render(title_text, True, self.colors["text"])
        title_rect = title_surface.get_rect(centerx=self.layout["menu_width"]//2, y=self.layout["padding"])
        menu_surface.blit(title_surface, title_rect)

        # Элементы меню
        if self.state == MenuState.MAIN:
            items = list(self.menu_items.values())
        else:
            items = list(self.submenus[self.current_submenu].values())

        y = self.layout["padding"] + 50
        for i, item in enumerate(items):
            # Фон элемента
            item_rect = pygame.Rect(10, y, self.layout["menu_width"] - 20, self.layout["item_height"])
            
            if i == self.selected_index:
                pygame.draw.rect(menu_surface, self.colors["bg_selected"], item_rect)
            elif i == self.hover_index:
                pygame.draw.rect(menu_surface, self.colors["bg_hover"], item_rect)
            
            pygame.draw.rect(menu_surface, self.colors["border"], item_rect, 1)

            # Текст элемента
            color = self.colors["text"] if item.enabled else self.colors["text_disabled"]
            text_surface = self.fonts["menu"].render(item.label, True, color)
            text_rect = text_surface.get_rect(x=20, centery=y + self.layout["item_height"]//2)
            menu_surface.blit(text_surface, text_rect)

            # Горячая клавиша
            if item.shortcut:
                shortcut_surface = self.fonts["description"].render(f"[{item.shortcut}]", True, self.colors["accent"])
                shortcut_rect = shortcut_surface.get_rect(right=self.layout["menu_width"] - 20, centery=y + self.layout["item_height"]//2)
                menu_surface.blit(shortcut_surface, shortcut_rect)

            y += self.layout["item_height"] + self.layout["item_spacing"]

        # Отображаем меню на экране
        self.screen.blit(menu_surface, (menu_x, menu_y))

    def _save_game(self):
        """Сохранение игры"""
        print("Сохранение игры...")
        # Здесь будет логика сохранения

    def _load_game(self):
        """Загрузка игры"""
        print("Загрузка игры...")
        # Здесь будет логика загрузки

    def _quit_game(self):
        """Выход из игры"""
        print("Выход из игры...")
        pygame.quit()
        import sys
        sys.exit(0)

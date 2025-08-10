"""
Игровое меню с оптимизированной архитектурой
"""

import tkinter as tk
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
    """Игровое меню с оптимизированной архитектурой"""

    def __init__(self, parent_canvas: tk.Canvas, width: int, height: int):
        self.parent_canvas = parent_canvas
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
        self.styles = {
            "colors": {
                "bg": "#2a2a2a",
                "bg_hover": "#3a3a3a",
                "bg_selected": "#4a4a4a",
                "text": "#ffffff",
                "text_disabled": "#666666",
                "accent": "#4a9eff",
                "border": "#555555",
                "overlay": "#000000",
            },
            "fonts": {
                "title": ("Arial", 18, "bold"),
                "menu": ("Arial", 12),
                "submenu": ("Arial", 10),
                "description": ("Arial", 9),
            },
            "layout": {
                "menu_width": 400,
                "menu_height": 500,
                "item_height": 40,
                "item_spacing": 10,
                "padding": 20,
            },
        }

        # Привязываем события
        self._bind_events()

        # Инициализируем меню
        self._init_main_menu()
        self._init_submenus()

    def _bind_events(self):
        """Привязка событий к canvas"""
        self.parent_canvas.bind("<Button-1>", self._on_click)
        self.parent_canvas.bind("<Motion>", self._on_mouse_move)
        self.parent_canvas.bind("<Key>", self._on_key)
        self.parent_canvas.bind("<Escape>", self.hide)

    def _init_main_menu(self):
        """Инициализация главного меню"""
        self.menu_items = {
            "resume": MenuItem(
                "Продолжить", self.hide, shortcut="ESC", description="Вернуться к игре"
            ),
            "inventory": MenuItem(
                "Инвентарь",
                lambda: self.show_submenu("inventory"),
                shortcut="I",
                description="Управление предметами",
            ),
            "character": MenuItem(
                "Персонаж",
                lambda: self.show_submenu("character"),
                shortcut="C",
                description="Характеристики персонажа",
            ),
            "skills": MenuItem(
                "Умения",
                lambda: self.show_submenu("skills"),
                shortcut="K",
                description="Управление способностями",
            ),
            "settings": MenuItem(
                "Настройки",
                lambda: self.show_submenu("settings"),
                shortcut="S",
                description="Настройки игры",
            ),
            "save": MenuItem(
                "Сохранить",
                lambda: None,
                shortcut="F5",
                description="Сохранить прогресс",
            ),
            "quit": MenuItem(
                "Выйти в главное меню",
                lambda: None,
                shortcut="Q",
                description="Вернуться в главное меню",
            ),
        }

    def _init_submenus(self):
        """Инициализация подменю"""
        self.submenus = {
            "inventory": {
                "weapons": MenuItem(
                    "Оружие", lambda: None, description="Боевое снаряжение"
                ),
                "armor": MenuItem(
                    "Броня", lambda: None, description="Защитное снаряжение"
                ),
                "consumables": MenuItem(
                    "Расходники", lambda: None, description="Зелья и свитки"
                ),
                "materials": MenuItem(
                    "Материалы", lambda: None, description="Крафтовые ресурсы"
                ),
            },
            "character": {
                "attributes": MenuItem(
                    "Характеристики", lambda: None, description="Основные параметры"
                ),
                "stats": MenuItem(
                    "Статистика", lambda: None, description="Игровая статистика"
                ),
                "equipment": MenuItem(
                    "Экипировка", lambda: None, description="Надетые предметы"
                ),
                "leveling": MenuItem(
                    "Прокачка", lambda: None, description="Развитие персонажа"
                ),
            },
            "skills": {
                "combat": MenuItem(
                    "Боевые", lambda: None, description="Атакующие способности"
                ),
                "passive": MenuItem(
                    "Пассивные", lambda: None, description="Постоянные эффекты"
                ),
                "special": MenuItem(
                    "Особые", lambda: None, description="Уникальные умения"
                ),
            },
            "settings": {
                "graphics": MenuItem(
                    "Графика", lambda: None, description="Настройки отображения"
                ),
                "audio": MenuItem("Звук", lambda: None, description="Аудио настройки"),
                "controls": MenuItem(
                    "Управление", lambda: None, description="Настройки управления"
                ),
                "gameplay": MenuItem(
                    "Игровой процесс", lambda: None, description="Игровые настройки"
                ),
            },
        }

    def show(self, x: int = None, y: int = None):
        """Показать меню"""
        if self.visible:
            return

        self.visible = True
        self.state = MenuState.MAIN
        self.current_submenu = None
        self.selected_index = 0
        self.hover_index = -1

        # Позиционируем меню по центру или по указанным координатам
        if x is None:
            x = (self.width - self.styles["layout"]["menu_width"]) // 2
        if y is None:
            y = (self.height - self.styles["layout"]["menu_height"]) // 2

        self._draw_menu()

    def hide(self):
        """Скрыть меню"""
        if not self.visible:
            return

        self.visible = False
        self.state = MenuState.HIDDEN
        self.current_submenu = None
        self.selected_index = 0
        self.hover_index = -1

        # Очищаем меню с canvas
        self.parent_canvas.delete("menu")

    def toggle(self):
        """Переключить видимость меню"""
        if self.visible:
            self.hide()
        else:
            self.show()

    def _draw_menu(self):
        """Отрисовка меню с оптимизацией"""
        # Очищаем предыдущее меню
        self.parent_canvas.delete("menu")

        if not self.visible:
            return

        # Отрисовываем полупрозрачный фон
        self._draw_overlay()

        # Отрисовываем основное меню или подменю
        if self.state == MenuState.MAIN:
            self._draw_main_menu()
        elif self.state == MenuState.SUBMENU:
            self._draw_submenu()

    def _draw_overlay(self):
        """Отрисовка полупрозрачного фона"""
        self.parent_canvas.create_rectangle(
            0,
            0,
            self.width,
            self.height,
            fill=self.styles["colors"]["overlay"],
            stipple="gray25",
            tags="menu",
        )

    def _draw_main_menu(self):
        """Отрисовка главного меню"""
        layout = self.styles["layout"]
        colors = self.styles["colors"]
        fonts = self.styles["fonts"]

        # Позиция меню
        menu_x = (self.width - layout["menu_width"]) // 2
        menu_y = (self.height - layout["menu_height"]) // 2

        # Фон меню
        self.parent_canvas.create_rectangle(
            menu_x,
            menu_y,
            menu_x + layout["menu_width"],
            menu_y + layout["menu_height"],
            fill=colors["bg"],
            outline=colors["border"],
            width=2,
            tags="menu",
        )

        # Заголовок
        self.parent_canvas.create_text(
            menu_x + layout["menu_width"] // 2,
            menu_y + 30,
            text="ИГРОВОЕ МЕНЮ",
            font=fonts["title"],
            fill=colors["text"],
            tags="menu",
        )

        # Разделитель
        self.parent_canvas.create_line(
            menu_x + layout["padding"],
            menu_y + 60,
            menu_x + layout["menu_width"] - layout["padding"],
            menu_y + 60,
            fill=colors["border"],
            width=2,
            tags="menu",
        )

        # Элементы меню
        self._draw_menu_items(
            menu_x,
            menu_y + 80,
            self.menu_items,
            layout["item_height"],
            layout["item_spacing"],
        )

    def _draw_submenu(self):
        """Отрисовка подменю"""
        if not self.current_submenu or self.current_submenu not in self.submenus:
            return

        layout = self.styles["layout"]
        colors = self.styles["colors"]
        fonts = self.styles["fonts"]

        # Позиция меню
        menu_x = (self.width - layout["menu_width"]) // 2
        menu_y = (self.height - layout["menu_height"]) // 2

        # Фон меню
        self.parent_canvas.create_rectangle(
            menu_x,
            menu_y,
            menu_x + layout["menu_width"],
            menu_y + layout["menu_height"],
            fill=colors["bg"],
            outline=colors["border"],
            width=2,
            tags="menu",
        )

        # Кнопка "Назад"
        back_btn_x = menu_x + layout["padding"]
        back_btn_y = menu_y + layout["padding"]
        back_btn_width = 80
        back_btn_height = 30

        self.parent_canvas.create_rectangle(
            back_btn_x,
            back_btn_y,
            back_btn_x + back_btn_width,
            back_btn_y + back_btn_height,
            fill=colors["bg_hover"],
            outline=colors["border"],
            tags="menu",
        )

        self.parent_canvas.create_text(
            back_btn_x + back_btn_width // 2,
            back_btn_y + back_btn_height // 2,
            text="← Назад",
            font=fonts["submenu"],
            fill=colors["text"],
            tags="menu",
        )

        # Заголовок подменю
        submenu_name = self.current_submenu.title()
        self.parent_canvas.create_text(
            menu_x + layout["menu_width"] // 2,
            menu_y + 30,
            text=submenu_name,
            font=fonts["title"],
            fill=colors["text"],
            tags="menu",
        )

        # Разделитель
        self.parent_canvas.create_line(
            menu_x + layout["padding"],
            menu_y + 60,
            menu_x + layout["menu_width"] - layout["padding"],
            menu_y + 60,
            fill=colors["border"],
            width=2,
            tags="menu",
        )

        # Элементы подменю
        self._draw_menu_items(
            menu_x,
            menu_y + 80,
            self.submenus[self.current_submenu],
            layout["item_height"],
            layout["item_spacing"],
        )

    def _draw_menu_items(
        self, x: int, y: int, items: Dict[str, MenuItem], item_height: int, spacing: int
    ):
        """Отрисовка элементов меню"""
        colors = self.styles["colors"]
        fonts = self.styles["fonts"]
        layout = self.styles["layout"]

        items_list = list(items.items())

        for i, (key, item) in enumerate(items_list):
            item_y = y + i * (item_height + spacing)

            # Определяем цвет фона
            if i == self.selected_index:
                bg_color = colors["bg_selected"]
            elif i == self.hover_index:
                bg_color = colors["bg_hover"]
            else:
                bg_color = colors["bg"]

            # Фон элемента
            self.parent_canvas.create_rectangle(
                x + layout["padding"],
                item_y,
                x + layout["menu_width"] - layout["padding"],
                item_y + item_height,
                fill=bg_color,
                outline=colors["border"],
                tags=f"menu_item_{key}",
            )

            # Текст
            text_color = colors["text"] if item.enabled else colors["text_disabled"]
            self.parent_canvas.create_text(
                x + layout["padding"] + 10,
                item_y + item_height // 2,
                text=item.label,
                font=fonts["menu"],
                fill=text_color,
                anchor="w",
                tags="menu",
            )

            # Описание (если есть)
            if item.description:
                self.parent_canvas.create_text(
                    x + layout["padding"] + 10,
                    item_y + item_height // 2 + 15,
                    text=item.description,
                    font=fonts["description"],
                    fill=colors["text_disabled"],
                    anchor="w",
                    tags="menu",
                )

            # Горячая клавиша
            if item.shortcut:
                self.parent_canvas.create_text(
                    x + layout["menu_width"] - layout["padding"] - 10,
                    item_y + item_height // 2,
                    text=item.shortcut,
                    font=fonts["submenu"],
                    fill=colors["accent"],
                    anchor="e",
                    tags="menu",
                )

    def show_submenu(self, submenu_name: str):
        """Показать подменю"""
        if submenu_name in self.submenus:
            self.current_submenu = submenu_name
            self.state = MenuState.SUBMENU
            self.selected_index = 0
            self.hover_index = -1
            self._draw_menu()

    def _on_click(self, event):
        """Обработка клика мыши"""
        if not self.visible:
            return

        x, y = event.x, event.y
        layout = self.styles["layout"]

        # Позиция меню
        menu_x = (self.width - layout["menu_width"]) // 2
        menu_y = (self.height - layout["menu_height"]) // 2

        if self.state == MenuState.SUBMENU:
            # Проверяем клик по кнопке "Назад"
            back_btn_x = menu_x + layout["padding"]
            back_btn_y = menu_y + layout["padding"]
            if (
                back_btn_x <= x <= back_btn_x + 80
                and back_btn_y <= y <= back_btn_y + 30
            ):
                self.current_submenu = None
                self.state = MenuState.MAIN
                self.selected_index = 0
                self._draw_menu()
                return

            # Проверяем клик по элементам подменю
            items = self.submenus[self.current_submenu]
            self._handle_item_click(x, y, menu_x, menu_y, items, 80)
        else:
            # Проверяем клик по элементам главного меню
            self._handle_item_click(x, y, menu_x, menu_y, self.menu_items, 80)

    def _handle_item_click(
        self,
        x: int,
        y: int,
        menu_x: int,
        menu_y: int,
        items: Dict[str, MenuItem],
        start_y: int,
    ):
        """Обработка клика по элементам меню"""
        layout = self.styles["layout"]
        items_list = list(items.items())

        for i, (key, item) in enumerate(items_list):
            item_y = (
                menu_y + start_y + i * (layout["item_height"] + layout["item_spacing"])
            )

            if (
                menu_x + layout["padding"]
                <= x
                <= menu_x + layout["menu_width"] - layout["padding"]
                and item_y <= y <= item_y + layout["item_height"]
            ):
                if item.enabled and item.action:
                    item.action()
                return

    def _on_mouse_move(self, event):
        """Обработка движения мыши для hover эффектов"""
        if not self.visible:
            return

        x, y = event.x, event.y
        layout = self.styles["layout"]

        # Позиция меню
        menu_x = (self.width - layout["menu_width"]) // 2
        menu_y = (self.height - layout["menu_height"]) // 2

        # Определяем, над каким элементом находится мышь
        if self.state == MenuState.SUBMENU:
            items = self.submenus[self.current_submenu]
            start_y = 80
        else:
            items = self.menu_items
            start_y = 80

        items_list = list(items.items())
        new_hover_index = -1

        for i, (key, item) in enumerate(items_list):
            item_y = (
                menu_y + start_y + i * (layout["item_height"] + layout["item_spacing"])
            )

            if (
                menu_x + layout["padding"]
                <= x
                <= menu_x + layout["menu_width"] - layout["padding"]
                and item_y <= y <= item_y + layout["item_height"]
            ):
                new_hover_index = i
                break

        # Обновляем hover индекс только если он изменился
        if new_hover_index != self.hover_index:
            self.hover_index = new_hover_index
            self._draw_menu()

    def _on_key(self, event):
        """Обработка нажатий клавиш"""
        if not self.visible:
            return

        key = event.keysym.lower()

        # Навигация по меню
        if key == "up":
            self._navigate_up()
        elif key == "down":
            self._navigate_down()
        elif key == "return" or key == "space":
            self._select_current_item()
        elif key == "escape":
            if self.state == MenuState.SUBMENU:
                self.show_submenu(self.current_submenu)  # Возврат в главное меню
            else:
                self.hide()
        elif key == "left" and self.state == MenuState.SUBMENU:
            self.current_submenu = None
            self.state = MenuState.MAIN
            self.selected_index = 0
            self._draw_menu()
        elif key == "right" and self.state == MenuState.MAIN:
            # Можно добавить логику для быстрого перехода в подменю
            pass

        # Проверяем горячие клавиши
        self._check_hotkeys(key)

    def _navigate_up(self):
        """Навигация вверх по меню"""
        if self.state == MenuState.MAIN:
            items_count = len(self.menu_items)
        else:
            items_count = len(self.submenus[self.current_submenu])

        self.selected_index = (self.selected_index - 1) % items_count
        self._draw_menu()

    def _navigate_down(self):
        """Навигация вниз по меню"""
        if self.state == MenuState.MAIN:
            items_count = len(self.menu_items)
        else:
            items_count = len(self.submenus[self.current_submenu])

        self.selected_index = (self.selected_index + 1) % items_count
        self._draw_menu()

    def _select_current_item(self):
        """Выбор текущего элемента меню"""
        if self.state == MenuState.MAIN:
            items_list = list(self.menu_items.items())
        else:
            items_list = list(self.submenus[self.current_submenu].items())

        if 0 <= self.selected_index < len(items_list):
            key, item = items_list[self.selected_index]
            if item.enabled and item.action:
                item.action()

    def _check_hotkeys(self, key: str):
        """Проверка горячих клавиш"""
        # Проверяем горячие клавиши главного меню
        for menu_key, item in self.menu_items.items():
            if item.shortcut and item.shortcut.lower() == key:
                if item.enabled and item.action:
                    item.action()
                return

        # Проверяем горячие клавиши подменю
        if self.state == MenuState.SUBMENU:
            for submenu_key, item in self.submenus[self.current_submenu].items():
                if item.shortcut and item.shortcut.lower() == key:
                    if item.enabled and item.action:
                        item.action()
                    return

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

    def add_menu_item(self, key: str, item: MenuItem):
        """Добавить новый элемент меню"""
        self.menu_items[key] = item
        if self.visible:
            self._draw_menu()

    def remove_menu_item(self, key: str):
        """Удалить элемент меню"""
        if key in self.menu_items:
            del self.menu_items[key]
            if self.visible:
                self._draw_menu()

    def render(self, render_manager):
        """Рендеринг меню (для совместимости)"""
        if self.visible:
            self._draw_menu()

    def get_current_state(self) -> MenuState:
        """Получение текущего состояния меню"""
        return self.state

    def is_visible(self) -> bool:
        """Проверка видимости меню"""
        return self.visible

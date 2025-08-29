"""
Система UI - базовый интерфейс для отображения всех игровых систем
"""

import time
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from src.core.architecture import BaseComponent, ComponentType, Priority


class UIElementType(Enum):
    """Типы UI элементов"""
    BUTTON = "button"
    LABEL = "label"
    PROGRESS_BAR = "progress_bar"
    PANEL = "panel"
    MENU = "menu"
    HUD = "hud"
    TOOLTIP = "tooltip"


class UIState(Enum):
    """Состояния UI"""
    HIDDEN = "hidden"
    VISIBLE = "visible"
    DISABLED = "disabled"
    ACTIVE = "active"


@dataclass
class UIElement:
    """Базовый UI элемент"""
    element_id: str
    element_type: UIElementType
    position: tuple = (0, 0)
    size: tuple = (100, 100)
    text: str = ""
    state: UIState = UIState.VISIBLE
    visible: bool = True
    enabled: bool = True
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    callbacks: Dict[str, Callable] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    
    def is_visible(self) -> bool:
        """Проверить, видим ли элемент"""
        if not self.visible:
            return False
        if self.state == UIState.HIDDEN:
            return False
        return True
    
    def is_enabled(self) -> bool:
        """Проверить, активен ли элемент"""
        if not self.enabled:
            return False
        if self.state == UIState.DISABLED:
            return False
        return True


@dataclass
class HUDData:
    """Данные для HUD"""
    health_percentage: float = 100.0
    mana_percentage: float = 100.0
    energy_percentage: float = 100.0
    stamina_percentage: float = 100.0
    shield_percentage: float = 0.0
    experience: int = 0
    level: int = 1
    active_effects: List[str] = field(default_factory=list)
    combat_state: str = "idle"
    position: tuple = (0, 0, 0)


class UISystem(BaseComponent):
    """
    Система UI
    Управляет всеми элементами интерфейса и их отображением
    """
    
    def __init__(self):
        super().__init__(
            name="UISystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.MEDIUM
        )
        
        # UI элементы
        self.ui_elements: Dict[str, UIElement] = {}
        self.element_hierarchy: Dict[str, List[str]] = {}
        
        # HUD данные
        self.hud_data: Dict[str, HUDData] = {}
        
        # Активные панели
        self.active_panels: List[str] = []
        self.panel_stack: List[str] = []
        
        # Обработчики событий
        self.event_handlers: Dict[str, Callable] = {}
        
        # Настройки
        self.auto_update_interval = 0.1  # секунды
        self.last_update_time = 0.0
        
    def _on_initialize(self) -> bool:
        """Инициализация UI системы"""
        try:
            # Регистрация базовых UI элементов
            self._register_basic_elements()
            
            # Настройка обработчиков событий
            self._setup_event_handlers()
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации UISystem: {e}")
            return False
    
    def _register_basic_elements(self):
        """Регистрация базовых UI элементов"""
        # Создаем основной HUD
        self.create_hud("main_hud")
        
        # Создаем основные панели
        self.create_panel("main_menu", "Главное меню")
        self.create_panel("game_hud", "Игровой HUD")
        self.create_panel("inventory_panel", "Инвентарь")
        self.create_panel("skills_panel", "Навыки")
        self.create_panel("combat_panel", "Бой")
        
        # Создаем кнопки
        self.create_button("start_game", "Начать игру", self._on_start_game)
        self.create_button("load_game", "Загрузить игру", self._on_load_game)
        self.create_button("settings", "Настройки", self._on_settings)
        self.create_button("exit_game", "Выход", self._on_exit_game)
    
    def _setup_event_handlers(self):
        """Настройка обработчиков событий"""
        self.event_handlers["ui_update"] = self._handle_ui_update
        self.event_handlers["hud_update"] = self._handle_hud_update
        self.event_handlers["panel_show"] = self._handle_panel_show
        self.event_handlers["panel_hide"] = self._handle_panel_hide
    
    # Создание UI элементов
    def create_element(self, element_id: str, element_type: UIElementType, **kwargs) -> UIElement:
        """Создать UI элемент"""
        if element_id in self.ui_elements:
            return self.ui_elements[element_id]
        
        element = UIElement(
            element_id=element_id,
            element_type=element_type,
            **kwargs
        )
        
        self.ui_elements[element_id] = element
        
        # Добавляем в иерархию
        if element.parent:
            if element.parent not in self.element_hierarchy:
                self.element_hierarchy[element.parent] = []
            self.element_hierarchy[element.parent].append(element_id)
        
        return element
    
    def create_button(self, button_id: str, text: str, callback: Callable, **kwargs) -> UIElement:
        """Создать кнопку"""
        return self.create_element(
            button_id, 
            UIElementType.BUTTON, 
            text=text,
            callbacks={"click": callback},
            **kwargs
        )
    
    def create_label(self, label_id: str, text: str, **kwargs) -> UIElement:
        """Создать текстовую метку"""
        return self.create_element(
            label_id,
            UIElementType.LABEL,
            text=text,
            **kwargs
        )
    
    def create_progress_bar(self, bar_id: str, **kwargs) -> UIElement:
        """Создать полосу прогресса"""
        return self.create_element(
            bar_id,
            UIElementType.PROGRESS_BAR,
            **kwargs
        )
    
    def create_panel(self, panel_id: str, title: str, **kwargs) -> UIElement:
        """Создать панель"""
        return self.create_element(
            panel_id,
            UIElementType.PANEL,
            text=title,
            **kwargs
        )
    
    def create_hud(self, hud_id: str, **kwargs) -> UIElement:
        """Создать HUD"""
        return self.create_element(
            hud_id,
            UIElementType.HUD,
            **kwargs
        )
    
    # Управление HUD
    def create_hud_data(self, entity_id: str, **kwargs) -> HUDData:
        """Создать данные HUD для сущности"""
        if entity_id in self.hud_data:
            return self.hud_data[entity_id]
        
        hud_data = HUDData(**kwargs)
        self.hud_data[entity_id] = hud_data
        return hud_data
    
    def update_hud_data(self, entity_id: str, **kwargs):
        """Обновить данные HUD"""
        if entity_id not in self.hud_data:
            self.create_hud_data(entity_id)
        
        hud_data = self.hud_data[entity_id]
        
        for key, value in kwargs.items():
            if hasattr(hud_data, key):
                setattr(hud_data, key, value)
    
    def get_hud_data(self, entity_id: str) -> Optional[HUDData]:
        """Получить данные HUD"""
        return self.hud_data.get(entity_id)
    
    # Управление панелями
    def show_panel(self, panel_id: str):
        """Показать панель"""
        if panel_id not in self.ui_elements:
            return
        
        panel = self.ui_elements[panel_id]
        if panel.element_type != UIElementType.PANEL:
            return
        
        # Добавляем в стек активных панелей
        if panel_id not in self.panel_stack:
            self.panel_stack.append(panel_id)
        
        # Показываем панель
        panel.state = UIState.ACTIVE
        panel.visible = True
        
        # Показываем дочерние элементы
        for child_id in panel.children:
            if child_id in self.ui_elements:
                child = self.ui_elements[child_id]
                child.visible = True
                child.state = UIState.VISIBLE
    
    def hide_panel(self, panel_id: str):
        """Скрыть панель"""
        if panel_id not in self.ui_elements:
            return
        
        panel = self.ui_elements[panel_id]
        if panel.element_type != UIElementType.PANEL:
            return
        
        # Убираем из стека
        if panel_id in self.panel_stack:
            self.panel_stack.remove(panel_id)
        
        # Скрываем панель
        panel.state = UIState.HIDDEN
        panel.visible = False
        
        # Скрываем дочерние элементы
        for child_id in panel.children:
            if child_id in self.ui_elements:
                child = self.ui_elements[child_id]
                child.visible = False
                child.state = UIState.HIDDEN
    
    def is_panel_visible(self, panel_id: str) -> bool:
        """Проверить, видима ли панель"""
        if panel_id not in self.ui_elements:
            return False
        
        panel = self.ui_elements[panel_id]
        return panel.is_visible()
    
    # Управление элементами
    def show_element(self, element_id: str):
        """Показать элемент"""
        if element_id in self.ui_elements:
            element = self.ui_elements[element_id]
            element.visible = True
            element.state = UIState.VISIBLE
    
    def hide_element(self, element_id: str):
        """Скрыть элемент"""
        if element_id in self.ui_elements:
            element = self.ui_elements[element_id]
            element.visible = False
            element.state = UIState.HIDDEN
    
    def enable_element(self, element_id: str):
        """Включить элемент"""
        if element_id in self.ui_elements:
            element = self.ui_elements[element_id]
            element.enabled = True
            element.state = UIState.ACTIVE
    
    def disable_element(self, element_id: str):
        """Отключить элемент"""
        if element_id in self.ui_elements:
            element = self.ui_elements[element_id]
            element.enabled = False
            element.state = UIState.DISABLED
    
    def set_element_text(self, element_id: str, text: str):
        """Установить текст элемента"""
        if element_id in self.ui_elements:
            element = self.ui_elements[element_id]
            element.text = text
    
    def set_element_position(self, element_id: str, position: tuple):
        """Установить позицию элемента"""
        if element_id in self.ui_elements:
            element = self.ui_elements[element_id]
            element.position = position
    
    def set_element_size(self, element_id: str, size: tuple):
        """Установить размер элемента"""
        if element_id in self.ui_elements:
            element = self.ui_elements[element_id]
            element.size = size
    
    # Обработка событий
    def handle_click(self, element_id: str):
        """Обработать клик по элементу"""
        if element_id not in self.ui_elements:
            return
        
        element = self.ui_elements[element_id]
        if not element.is_enabled():
            return
        
        # Вызываем callback для клика
        if "click" in element.callbacks:
            try:
                element.callbacks["click"]()
            except Exception as e:
                self.logger.error(f"Ошибка в callback клика для {element_id}: {e}")
    
    def add_callback(self, element_id: str, event_type: str, callback: Callable):
        """Добавить callback для элемента"""
        if element_id not in self.ui_elements:
            return
        
        element = self.ui_elements[element_id]
        element.callbacks[event_type] = callback
    
    # Обновление UI
    def update(self, delta_time: float):
        """Обновить UI систему"""
        current_time = time.time()
        
        # Проверяем, нужно ли обновлять UI
        if current_time - self.last_update_time < self.auto_update_interval:
            return
        
        # Обновляем все видимые элементы
        for element_id, element in self.ui_elements.items():
            if element.is_visible():
                self._update_element(element, delta_time)
        
        self.last_update_time = current_time
    
    def _update_element(self, element: UIElement, delta_time: float):
        """Обновить отдельный элемент"""
        # Обновляем прогресс-бары
        if element.element_type == UIElementType.PROGRESS_BAR:
            self._update_progress_bar(element, delta_time)
        
        # Обновляем HUD
        elif element.element_type == UIElementType.HUD:
            self._update_hud(element, delta_time)
    
    def _update_progress_bar(self, element: UIElement, delta_time: float):
        """Обновить прогресс-бар"""
        # TODO: Анимация прогресс-бара
        pass
    
    def _update_hud(self, element: UIElement, delta_time: float):
        """Обновить HUD"""
        # TODO: Обновление данных HUD
        pass
    
    # Обработчики событий
    def _handle_ui_update(self, event_data: Dict[str, Any]):
        """Обработчик обновления UI"""
        # TODO: Обработка событий обновления UI
        pass
    
    def _handle_hud_update(self, event_data: Dict[str, Any]):
        """Обработчик обновления HUD"""
        entity_id = event_data.get("entity_id")
        if not entity_id:
            return
        
        # Обновляем данные HUD
        if entity_id in self.hud_data:
            hud_data = self.hud_data[entity_id]
            
            # Обновляем отображение
            self._update_hud_display(entity_id, hud_data)
    
    def _handle_panel_show(self, event_data: Dict[str, Any]):
        """Обработчик показа панели"""
        panel_id = event_data.get("panel_id")
        if panel_id:
            self.show_panel(panel_id)
    
    def _handle_panel_hide(self, event_data: Dict[str, Any]):
        """Обработчик скрытия панели"""
        panel_id = event_data.get("panel_id")
        if panel_id:
            self.hide_panel(panel_id)
    
    def _update_hud_display(self, entity_id: str, hud_data: HUDData):
        """Обновить отображение HUD"""
        # Обновляем прогресс-бары здоровья
        health_bar_id = f"{entity_id}_health_bar"
        if health_bar_id in self.ui_elements:
            self._update_health_bar(health_bar_id, hud_data.health_percentage)
        
        # Обновляем прогресс-бары ресурсов
        mana_bar_id = f"{entity_id}_mana_bar"
        if mana_bar_id in self.ui_elements:
            self._update_mana_bar(mana_bar_id, hud_data.mana_percentage)
        
        # Обновляем метки
        level_label_id = f"{entity_id}_level_label"
        if level_label_id in self.ui_elements:
            self.set_element_text(level_label_id, f"Уровень: {hud_data.level}")
        
        exp_label_id = f"{entity_id}_exp_label"
        if exp_label_id in self.ui_elements:
            self.set_element_text(exp_label_id, f"Опыт: {hud_data.experience}")
    
    def _update_health_bar(self, bar_id: str, percentage: float):
        """Обновить полосу здоровья"""
        if bar_id not in self.ui_elements:
            return
        
        bar = self.ui_elements[bar_id]
        bar.data["current_value"] = percentage
        bar.data["max_value"] = 100.0
        
        # Обновляем цвет в зависимости от процента
        if percentage > 50:
            bar.data["color"] = (0, 1, 0)  # Зеленый
        elif percentage > 25:
            bar.data["color"] = (1, 1, 0)  # Желтый
        else:
            bar.data["color"] = (1, 0, 0)  # Красный
    
    def _update_mana_bar(self, bar_id: str, percentage: float):
        """Обновить полосу маны"""
        if bar_id not in self.ui_elements:
            return
        
        bar = self.ui_elements[bar_id]
        bar.data["current_value"] = percentage
        bar.data["max_value"] = 100.0
        bar.data["color"] = (0, 0, 1)  # Синий
    
    # Callback функции для кнопок
    def _on_start_game(self):
        """Callback для кнопки 'Начать игру'"""
        self.logger.info("Нажата кнопка 'Начать игру'")
        # TODO: Запуск игры
    
    def _on_load_game(self):
        """Callback для кнопки 'Загрузить игру'"""
        self.logger.info("Нажата кнопка 'Загрузить игру'")
        # TODO: Загрузка игры
    
    def _on_settings(self):
        """Callback для кнопки 'Настройки'"""
        self.logger.info("Нажата кнопка 'Настройки'")
        # TODO: Открытие настроек
    
    def _on_exit_game(self):
        """Callback для кнопки 'Выход'"""
        self.logger.info("Нажата кнопка 'Выход'")
        # TODO: Выход из игры
    
    # Публичные методы
    def get_element(self, element_id: str) -> Optional[UIElement]:
        """Получить UI элемент"""
        return self.ui_elements.get(element_id)
    
    def get_visible_elements(self) -> List[UIElement]:
        """Получить все видимые элементы"""
        return [e for e in self.ui_elements.values() if e.is_visible()]
    
    def get_active_panels(self) -> List[str]:
        """Получить активные панели"""
        return self.panel_stack.copy()
    
    def clear_all_panels(self):
        """Очистить все панели"""
        for panel_id in self.panel_stack.copy():
            self.hide_panel(panel_id)
    
    def refresh_ui(self):
        """Обновить весь UI"""
        self.last_update_time = 0.0  # Принудительное обновление
        self.update(0.0)

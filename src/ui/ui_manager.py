#!/usr/bin/env python3
"""UI менеджер - управление пользовательским интерфейсом
Интеграция с системой атрибутов для визуализации характеристик"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState
from src.core.state_manager import StateManager, StateType
from src.systems.attributes.attribute_system import AttributeSystem, AttributeSet, AttributeModifier, StatModifier, BaseAttribute, DerivedStat

logger = logging.getLogger(__name__)

# = ТИПЫ UI ЭЛЕМЕНТОВ

class UIElementType(Enum):
    """Типы UI элементов"""
    WINDOW = "window"
    PANEL = "panel"
    BUTTON = "button"
    LABEL = "label"
    TEXTBOX = "textbox"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    DROPDOWN = "dropdown"
    PROGRESS_BAR = "progress_bar"
    INVENTORY_GRID = "inventory_grid"
    SKILL_TREE = "skill_tree"
    STATS_PANEL = "stats_panel"

class UITheme(Enum):
    """Темы UI"""
    DARK = "dark"
    LIGHT = "light"
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    MINIMAL = "minimal"

class UIState(Enum):
    """Состояния UI"""
    HIDDEN = "hidden"
    VISIBLE = "visible"
    DISABLED = "disabled"
    ACTIVE = "active"
    HOVERED = "hovered"
    PRESSED = "pressed"

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class UIPosition:
    """Позиция UI элемента"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    anchor: str = "top_left"  # top_left, top_right, bottom_left, bottom_right, center

@dataclass
class UISize:
    """Размер UI элемента"""
    width: float = 100.0
    height: float = 100.0
    min_width: float = 50.0
    min_height: float = 50.0
    max_width: float = 1000.0
    max_height: float = 1000.0

@dataclass
class UIStyle:
    """Стиль UI элемента"""
    background_color: Tuple[float, float, float, float] = (0.2, 0.2, 0.2, 0.8)
    border_color: Tuple[float, float, float, float] = (0.5, 0.5, 0.5, 1.0)
    text_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    border_width: float = 2.0
    corner_radius: float = 5.0
    font_size: int = 14
    font_family: str = "Arial"
    padding: Tuple[float, float, float, float] = (5.0, 5.0, 5.0, 5.0)  # top, right, bottom, left

@dataclass
class UIElement:
    """Базовый UI элемент"""
    element_id: str
    element_type: UIElementType
    position: UIPosition
    size: UISize
    style: UIStyle
    state: UIState = UIState.VISIBLE
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)  # element_ids
    visible: bool = True
    enabled: bool = True
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StatsPanel(UIElement):
    """Панель характеристик"""
    entity_id: Optional[str] = None
    show_attributes: bool = True
    show_stats: bool = True
    show_modifiers: bool = True
    auto_update: bool = True
    update_interval: float = 1.0
    last_update: float = 0.0

@dataclass
class ModifierDisplay:
    """Отображение модификатора"""
    modifier_id: str
    source: str
    target: str
    value: float
    is_percentage: bool
    duration: float
    remaining_time: float
    color: Tuple[float, float, float, float]

class UIManager(BaseComponent):
    """Менеджер пользовательского интерфейса"""
    
    def __init__(self):
        super().__init__(
            component_id="ui_manager",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Архитектурные компоненты
        self.state_manager: Optional[StateManager] = None
        self.attribute_system: Optional[AttributeSystem] = None
        
        # UI элементы
        self.ui_elements: Dict[str, UIElement] = {}
        self.active_windows: List[str] = []
        self.modal_windows: List[str] = []
        
        # Тема и стили
        self.current_theme: UITheme = UITheme.DARK
        self.theme_styles: Dict[UITheme, Dict[str, UIStyle]] = {}
        
        # Интеграция с системой атрибутов
        self.stats_panels: Dict[str, StatsPanel] = {}
        self.modifier_displays: Dict[str, ModifierDisplay] = {}
        
        # Настройки системы
        self.system_settings = {
            'enable_ui_animations': True,
            'enable_tooltips': True,
            'enable_context_menus': True,
            'auto_hide_inactive_panels': True,
            'show_fps_counter': False,
            'show_debug_info': False,
            'ui_scale': 1.0,
            'language': 'en'
        }
        
        # Статистика
        self.system_stats = {
            'total_ui_elements': 0,
            'active_windows': 0,
            'stats_panels': 0,
            'modifier_displays': 0,
            'update_time': 0.0,
            'render_time': 0.0
        }
        
        # Callbacks
        self.on_element_created: Optional[Callable] = None
        self.on_element_destroyed: Optional[Callable] = None
        self.on_element_clicked: Optional[Callable] = None
        self.on_window_opened: Optional[Callable] = None
        self.on_window_closed: Optional[Callable] = None
        
        logger.info("UI менеджер инициализирован")
    
    def set_architecture_components(self, state_manager: StateManager, attribute_system: AttributeSystem):
        """Установка архитектурных компонентов"""
        self.state_manager = state_manager
        self.attribute_system = attribute_system
        logger.info("Архитектурные компоненты установлены в UIManager")
    
    def _register_system_states(self):
        """Регистрация состояний системы"""
        if self.state_manager:
            self.state_manager.set_state(
                f"{self.component_id}_settings",
                self.system_settings,
                StateType.SETTINGS
            )
            
            self.state_manager.set_state(
                f"{self.component_id}_stats",
                self.system_stats,
                StateType.STATISTICS
            )
            
            self.state_manager.set_state(
                f"{self.component_id}_state",
                self.system_state,
                StateType.SYSTEM_STATE
            )
    
    def initialize(self) -> bool:
        """Инициализация UI менеджера"""
        try:
            logger.info("Инициализация UIManager...")
            
            self._register_system_states()
            
            # Создание тем UI
            self._create_ui_themes()
            
            # Создание базовых UI элементов
            self._create_base_ui_elements()
            
            self.system_state = LifecycleState.READY
            logger.info("UIManager инициализирован успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации UIManager: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def start(self) -> bool:
        """Запуск UI менеджера"""
        try:
            logger.info("Запуск UIManager...")
            
            if self.system_state != LifecycleState.READY:
                logger.error("UIManager не готов к запуску")
                return False
            
            self.system_state = LifecycleState.RUNNING
            logger.info("UIManager запущен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска UIManager: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def update(self, delta_time: float):
        """Обновление UI менеджера"""
        if self.system_state != LifecycleState.RUNNING:
            return
        
        try:
            start_time = time.time()
            
            # Обновление панелей характеристик
            self._update_stats_panels(delta_time)
            
            # Обновление отображения модификаторов
            self._update_modifier_displays(delta_time)
            
            # Обновление анимаций UI
            if self.system_settings['enable_ui_animations']:
                self._update_ui_animations(delta_time)
            
            self.system_stats['update_time'] = time.time() - start_time
            
            # Обновляем состояние в менеджере состояний
            if self.state_manager:
                self.state_manager.set_state(
                    f"{self.system_name}_stats",
                    self.system_stats,
                    StateType.STATISTICS
                )
                
        except Exception as e:
            logger.error(f"Ошибка обновления UIManager: {e}")
    
    def stop(self) -> bool:
        """Остановка UI менеджера"""
        try:
            logger.info("Остановка UIManager...")
            
            self.system_state = LifecycleState.STOPPED
            logger.info("UIManager остановлен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки UIManager: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение UI менеджера"""
        try:
            logger.info("Уничтожение UIManager...")
            
            # Очистка всех UI элементов
            self._clear_all_ui_elements()
            
            self.ui_elements.clear()
            self.active_windows.clear()
            self.modal_windows.clear()
            self.stats_panels.clear()
            self.modifier_displays.clear()
            self.theme_styles.clear()
            
            self.system_state = LifecycleState.DESTROYED
            logger.info("UIManager уничтожен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения UIManager: {e}")
            return False
    
    def _clear_all_ui_elements(self):
        """Очистка всех UI элементов"""
        for element_id in list(self.ui_elements.keys()):
            self.destroy_ui_element(element_id)
    
    def _create_ui_themes(self):
        """Создание тем UI"""
        try:
            # Темная тема
            dark_theme = {
                'window': UIStyle(
                    background_color=(0.1, 0.1, 0.1, 0.9),
                    border_color=(0.3, 0.3, 0.3, 1.0),
                    text_color=(1.0, 1.0, 1.0, 1.0)
                ),
                'panel': UIStyle(
                    background_color=(0.15, 0.15, 0.15, 0.8),
                    border_color=(0.4, 0.4, 0.4, 1.0),
                    text_color=(0.9, 0.9, 0.9, 1.0)
                ),
                'button': UIStyle(
                    background_color=(0.2, 0.2, 0.2, 0.8),
                    border_color=(0.5, 0.5, 0.5, 1.0),
                    text_color=(1.0, 1.0, 1.0, 1.0)
                ),
                'stats_panel': UIStyle(
                    background_color=(0.1, 0.1, 0.1, 0.8),
                    border_color=(0.3, 0.3, 0.3, 1.0),
                    text_color=(0.8, 0.8, 0.8, 1.0)
                )
            }
            
            # Светлая тема
            light_theme = {
                'window': UIStyle(
                    background_color=(0.9, 0.9, 0.9, 0.9),
                    border_color=(0.7, 0.7, 0.7, 1.0),
                    text_color=(0.1, 0.1, 0.1, 1.0)
                ),
                'panel': UIStyle(
                    background_color=(0.85, 0.85, 0.85, 0.8),
                    border_color=(0.6, 0.6, 0.6, 1.0),
                    text_color=(0.2, 0.2, 0.2, 1.0)
                ),
                'button': UIStyle(
                    background_color=(0.8, 0.8, 0.8, 0.8),
                    border_color=(0.5, 0.5, 0.5, 1.0),
                    text_color=(0.1, 0.1, 0.1, 1.0)
                ),
                'stats_panel': UIStyle(
                    background_color=(0.9, 0.9, 0.9, 0.8),
                    border_color=(0.7, 0.7, 0.7, 1.0),
                    text_color=(0.2, 0.2, 0.2, 1.0)
                )
            }
            
            self.theme_styles[UITheme.DARK] = dark_theme
            self.theme_styles[UITheme.LIGHT] = light_theme
            
            logger.info(f"Создано {len(self.theme_styles)} тем UI")
            
        except Exception as e:
            logger.error(f"Ошибка создания тем UI: {e}")
    
    def _create_base_ui_elements(self):
        """Создание базовых UI элементов"""
        try:
            # Главное меню
            main_menu = UIElement(
                element_id="main_menu",
                element_type=UIElementType.WINDOW,
                position=UIPosition(x=10, y=10, anchor="top_left"),
                size=UISize(width=200, height=300),
                style=self.theme_styles[self.current_theme]['window'],
                state=UIState.VISIBLE
            )
            
            # Панель характеристик игрока
            player_stats_panel = StatsPanel(
                element_id="player_stats_panel",
                element_type=UIElementType.STATS_PANEL,
                position=UIPosition(x=10, y=320, anchor="top_left"),
                size=UISize(width=250, height=400),
                style=self.theme_styles[self.current_theme]['stats_panel'],
                entity_id="player",
                show_attributes=True,
                show_stats=True,
                show_modifiers=True,
                auto_update=True
            )
            
            # Добавляем элементы в систему
            self.ui_elements["main_menu"] = main_menu
            self.ui_elements["player_stats_panel"] = player_stats_panel
            self.stats_panels["player_stats_panel"] = player_stats_panel
            
            # Обновляем статистику
            self.system_stats['total_ui_elements'] = len(self.ui_elements)
            self.system_stats['stats_panels'] = len(self.stats_panels)
            
            logger.info(f"Создано {len(self.ui_elements)} базовых UI элементов")
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых UI элементов: {e}")
    
    def _update_stats_panels(self, delta_time: float):
        """Обновление панелей характеристик"""
        current_time = time.time()
        
        for panel_id, panel in self.stats_panels.items():
            if not panel.auto_update:
                continue
            
            if current_time - panel.last_update < panel.update_interval:
                continue
            
            # Обновляем данные панели
            self._update_stats_panel_data(panel)
            panel.last_update = current_time
    
    def _update_stats_panel_data(self, panel: StatsPanel):
        """Обновление данных панели характеристик"""
        try:
            if not panel.entity_id or not self.attribute_system:
                return
            
            # Получаем данные сущности из системы атрибутов
            # Здесь должна быть интеграция с системой атрибутов для получения
            # базовых атрибутов, характеристик и модификаторов
            
            # Обновляем отображаемые данные
            panel.data['last_update'] = time.time()
            
        except Exception as e:
            logger.error(f"Ошибка обновления данных панели характеристик: {e}")
    
    def _update_modifier_displays(self, delta_time: float):
        """Обновление отображения модификаторов"""
        current_time = time.time()
        
        expired_modifiers = []
        for modifier_id, modifier_display in self.modifier_displays.items():
            if modifier_display.duration > 0:
                modifier_display.remaining_time -= delta_time
                
                if modifier_display.remaining_time <= 0:
                    expired_modifiers.append(modifier_id)
        
        # Удаляем истекшие модификаторы
        for modifier_id in expired_modifiers:
            del self.modifier_displays[modifier_id]
        
        # Обновляем статистику
        self.system_stats['modifier_displays'] = len(self.modifier_displays)
    
    def _update_ui_animations(self, delta_time: float):
        """Обновление анимаций UI"""
        # Здесь должна быть логика анимаций UI элементов
        pass
    
    def create_stats_panel(self, entity_id: str, position: UIPosition, 
                          size: UISize = None, show_attributes: bool = True,
                          show_stats: bool = True, show_modifiers: bool = True) -> str:
        """Создание панели характеристик для сущности"""
        try:
            if size is None:
                size = UISize(width=250, height=400)
            
            panel_id = f"stats_panel_{entity_id}"
            
            stats_panel = StatsPanel(
                element_id=panel_id,
                element_type=UIElementType.STATS_PANEL,
                position=position,
                size=size,
                style=self.theme_styles[self.current_theme]['stats_panel'],
                entity_id=entity_id,
                show_attributes=show_attributes,
                show_stats=show_stats,
                show_modifiers=show_modifiers,
                auto_update=True
            )
            
            # Добавляем в систему
            self.ui_elements[panel_id] = stats_panel
            self.stats_panels[panel_id] = stats_panel
            
            # Обновляем статистику
            self.system_stats['total_ui_elements'] = len(self.ui_elements)
            self.system_stats['stats_panels'] = len(self.stats_panels)
            
            # Вызываем callback
            if self.on_element_created:
                self.on_element_created(stats_panel)
            
            logger.info(f"Создана панель характеристик для сущности {entity_id}")
            return panel_id
            
        except Exception as e:
            logger.error(f"Ошибка создания панели характеристик для сущности {entity_id}: {e}")
            return ""
    
    def update_stats_panel(self, panel_id: str, base_attributes: AttributeSet = None,
                          attribute_modifiers: List[AttributeModifier] = None,
                          stat_modifiers: List[StatModifier] = None):
        """Обновление данных панели характеристик"""
        try:
            if panel_id not in self.stats_panels:
                logger.warning(f"Панель характеристик {panel_id} не найдена")
                return
            
            panel = self.stats_panels[panel_id]
            
            # Обновляем данные панели
            panel.data['base_attributes'] = base_attributes
            panel.data['attribute_modifiers'] = attribute_modifiers or []
            panel.data['stat_modifiers'] = stat_modifiers or []
            panel.data['last_update'] = time.time()
            
            # Рассчитываем финальные характеристики
            if base_attributes and self.attribute_system:
                calculated_stats = self.attribute_system.calculate_stats_for_entity(
                    entity_id=panel.entity_id or "temp",
                    base_attributes=base_attributes,
                    attribute_modifiers=attribute_modifiers,
                    stat_modifiers=stat_modifiers
                )
                panel.data['calculated_stats'] = calculated_stats
            
            logger.debug(f"Обновлены данные панели характеристик {panel_id}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления панели характеристик {panel_id}: {e}")
    
    def add_modifier_display(self, modifier_id: str, source: str, target: str,
                           value: float, is_percentage: bool, duration: float,
                           color: Tuple[float, float, float, float] = None):
        """Добавление отображения модификатора"""
        try:
            if color is None:
                # Определяем цвет на основе типа модификатора
                if value > 0:
                    color = (0.2, 0.8, 0.2, 1.0)  # Зеленый для положительных
                else:
                    color = (0.8, 0.2, 0.2, 1.0)  # Красный для отрицательных
            
            modifier_display = ModifierDisplay(
                modifier_id=modifier_id,
                source=source,
                target=target,
                value=value,
                is_percentage=is_percentage,
                duration=duration,
                remaining_time=duration,
                color=color
            )
            
            self.modifier_displays[modifier_id] = modifier_display
            
            # Обновляем статистику
            self.system_stats['modifier_displays'] = len(self.modifier_displays)
            
            logger.debug(f"Добавлено отображение модификатора {modifier_id}")
            
        except Exception as e:
            logger.error(f"Ошибка добавления отображения модификатора {modifier_id}: {e}")
    
    def remove_modifier_display(self, modifier_id: str):
        """Удаление отображения модификатора"""
        try:
            if modifier_id in self.modifier_displays:
                del self.modifier_displays[modifier_id]
                
                # Обновляем статистику
                self.system_stats['modifier_displays'] = len(self.modifier_displays)
                
                logger.debug(f"Удалено отображение модификатора {modifier_id}")
            
        except Exception as e:
            logger.error(f"Ошибка удаления отображения модификатора {modifier_id}: {e}")
    
    def create_ui_element(self, element_type: UIElementType, position: UIPosition,
                         size: UISize, style: UIStyle = None, parent_id: str = None) -> str:
        """Создание UI элемента"""
        try:
            element_id = f"{element_type.value}_{int(time.time() * 1000)}"
            
            if style is None:
                style = self.theme_styles[self.current_theme].get(element_type.value, UIStyle())
            
            ui_element = UIElement(
                element_id=element_id,
                element_type=element_type,
                position=position,
                size=size,
                style=style,
                parent_id=parent_id
            )
            
            # Добавляем в систему
            self.ui_elements[element_id] = ui_element
            
            # Добавляем к родителю
            if parent_id and parent_id in self.ui_elements:
                self.ui_elements[parent_id].children.append(element_id)
            
            # Обновляем статистику
            self.system_stats['total_ui_elements'] = len(self.ui_elements)
            
            # Вызываем callback
            if self.on_element_created:
                self.on_element_created(ui_element)
            
            logger.info(f"Создан UI элемент {element_id}")
            return element_id
            
        except Exception as e:
            logger.error(f"Ошибка создания UI элемента: {e}")
            return ""
    
    def destroy_ui_element(self, element_id: str) -> bool:
        """Уничтожение UI элемента"""
        try:
            if element_id not in self.ui_elements:
                logger.warning(f"UI элемент {element_id} не найден")
                return False
            
            ui_element = self.ui_elements[element_id]
            
            # Удаляем дочерние элементы
            for child_id in ui_element.children:
                self.destroy_ui_element(child_id)
            
            # Удаляем из родителя
            if ui_element.parent_id and ui_element.parent_id in self.ui_elements:
                parent = self.ui_elements[ui_element.parent_id]
                if element_id in parent.children:
                    parent.children.remove(element_id)
            
            # Удаляем из специальных коллекций
            if element_id in self.stats_panels:
                del self.stats_panels[element_id]
            
            # Удаляем элемент
            del self.ui_elements[element_id]
            
            # Обновляем статистику
            self.system_stats['total_ui_elements'] = len(self.ui_elements)
            self.system_stats['stats_panels'] = len(self.stats_panels)
            
            # Вызываем callback
            if self.on_element_destroyed:
                self.on_element_destroyed(ui_element)
            
            logger.info(f"Уничтожен UI элемент {element_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения UI элемента {element_id}: {e}")
            return False
    
    def set_ui_theme(self, theme: UITheme):
        """Установка темы UI"""
        try:
            if theme not in self.theme_styles:
                logger.warning(f"Тема {theme} не найдена")
                return
            
            self.current_theme = theme
            
            # Обновляем стили всех элементов
            for element in self.ui_elements.values():
                if element.element_type.value in self.theme_styles[theme]:
                    element.style = self.theme_styles[theme][element.element_type.value]
            
            logger.info(f"Установлена тема UI: {theme}")
            
        except Exception as e:
            logger.error(f"Ошибка установки темы UI: {e}")
    
    def get_ui_element(self, element_id: str) -> Optional[UIElement]:
        """Получение UI элемента"""
        return self.ui_elements.get(element_id)
    
    def get_stats_panel(self, panel_id: str) -> Optional[StatsPanel]:
        """Получение панели характеристик"""
        return self.stats_panels.get(panel_id)
    
    def get_modifier_displays(self) -> Dict[str, ModifierDisplay]:
        """Получение всех отображений модификаторов"""
        return self.modifier_displays.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'current_theme': self.current_theme.value,
            'total_ui_elements': self.system_stats['total_ui_elements'],
            'active_windows': self.system_stats['active_windows'],
            'stats_panels': self.system_stats['stats_panels'],
            'modifier_displays': self.system_stats['modifier_displays'],
            'update_time': self.system_stats['update_time'],
            'render_time': self.system_stats['render_time']
        }
    
    def reset_stats(self):
        """Сброс статистики"""
        self.system_stats = {
            'total_ui_elements': len(self.ui_elements),
            'active_windows': len(self.active_windows),
            'stats_panels': len(self.stats_panels),
            'modifier_displays': len(self.modifier_displays),
            'update_time': 0.0,
            'render_time': 0.0
        }

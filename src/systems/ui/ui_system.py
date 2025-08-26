#!/usr/bin/env python3
"""
Система пользовательского интерфейса - режим "Творец мира"
Пользователь создает препятствия, ловушки, сундуки и врагов
"""

import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from collections import deque
from dataclasses import dataclass, field
from enum import Enum

from ...core.interfaces import ISystem, SystemPriority, SystemState
from ...core.constants import (
    UIElementType, UIState, StatType, BASE_STATS,
    PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS,
    WorldObjectType, ObjectCategory, ObjectState, CreatorMode, ToolType,
    WORLD_SETTINGS, UI_SETTINGS, DEFAULT_OBJECT_TEMPLATES, UI_COLORS
)

logger = logging.getLogger(__name__)

# Используем константы из модуля constants
WorldObjectType = WorldObjectType
ObjectCategory = ObjectCategory

@dataclass
class WorldObjectTemplate:
    """Шаблон объекта для создания"""
    template_id: str
    name: str
    object_type: WorldObjectType
    category: ObjectCategory
    description: str
    icon: str
    cost: int = 0
    unlock_level: int = 1
    properties: Dict[str, Any] = field(default_factory=dict)
    is_available: bool = True

@dataclass
class UIElement:
    """Элемент пользовательского интерфейса"""
    element_id: str
    element_type: UIElementType
    name: str = ""
    position: tuple = (0.0, 0.0)
    size: tuple = (100.0, 100.0)
    visible: bool = True
    enabled: bool = True
    state: UIState = UIState.NORMAL
    text: str = ""
    icon: str = ""
    color: tuple = (255, 255, 255, 255)
    background_color: tuple = (0, 0, 0, 128)
    border_color: tuple = (128, 128, 128, 255)
    font_size: int = 14
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    event_handlers: Dict[str, str] = field(default_factory=dict)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    last_update: float = field(default_factory=time.time)
    animation_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CreatorMode:
    """Режим создания объектов"""
    mode_id: str
    name: str
    description: str
    active: bool = False
    selected_template: Optional[str] = None
    placement_mode: bool = False
    last_placed_position: Optional[Tuple[float, float, float]] = None

@dataclass
class UILayout:
    """Макет UI элементов"""
    layout_id: str
    name: str = ""
    layout_type: str = "vertical"  # vertical, horizontal, grid, absolute
    spacing: float = 5.0
    padding: tuple = (10.0, 10.0)
    auto_size: bool = True
    elements: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    last_update: float = field(default_factory=time.time)

@dataclass
class UITheme:
    """Тема пользовательского интерфейса"""
    theme_id: str
    name: str = ""
    colors: Dict[str, tuple] = field(default_factory=dict)
    fonts: Dict[str, str] = field(default_factory=dict)
    sizes: Dict[str, float] = field(default_factory=dict)
    styles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    is_active: bool = False
    last_update: float = field(default_factory=time.time)

class UISystem(ISystem):
    """Система пользовательского интерфейса - режим творца мира"""
    
    def __init__(self):
        self._system_name = "ui"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # UI элементы
        self.ui_elements: Dict[str, UIElement] = {}
        self.ui_layouts: Dict[str, UILayout] = {}
        self.ui_themes: Dict[str, UITheme] = {}
        self.active_screens: List[str] = []

        # Очередь событий UI и троттлинг обновлений (декуплинг от основного цикла)
        self._event_queue: deque = deque()
        self._max_events_per_tick: int = 64
        self._last_update_time: float = 0.0
        self._update_interval: float = 1.0 / 30.0  # 30 Гц по умолчанию
        
        # Шаблоны объектов для создания
        self.object_templates: Dict[str, WorldObjectTemplate] = {}
        
        # Режимы создания
        self.creator_modes: Dict[str, CreatorMode] = {}
        
        # Активный режим
        self.active_mode: Optional[str] = None
        
        # Выбранный шаблон для размещения
        self.selected_template: Optional[WorldObjectTemplate] = None
        
        # Статистика создания
        self.creation_stats = {
            'objects_created': 0,
            'obstacles_placed': 0,
            'traps_placed': 0,
            'chests_placed': 0,
            'enemies_spawned': 0,
            'total_cost': 0
        }
        
        # Настройки системы
        self.system_settings = UI_SETTINGS.copy()
        self.system_settings.update({
            'max_ui_elements': SYSTEM_LIMITS["max_ui_elements"],
            'max_layers': SYSTEM_LIMITS["max_ui_layers"],
            'grid_snap': WORLD_SETTINGS["grid_snap"],
            'grid_size': WORLD_SETTINGS["grid_size"],
            'show_preview': WORLD_SETTINGS["show_preview"],
            'ui_update_hz': 30,
            'max_events_per_tick': 64,
            'animation_enabled': True
        })
        
        # Статистика системы
        self.system_stats = {
            'total_elements': 0,
            'visible_elements': 0,
            'active_modes': 0,
            'available_templates': 0,
            'events_processed': 0,
            'update_time': 0.0
        }
        
        # Panda3D GUI компоненты
        self.gui_frame = None
        self.gui_root = None
        
        logger.info("Система UI творца мира инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы UI"""
        try:
            logger.info("Инициализация системы UI...")
            
            # Настраиваем систему
            self._setup_ui_system()
            # Применяем частоту обновления и лимиты очереди
            self._apply_runtime_settings()
            
            # Создаем шаблоны объектов
            self._create_object_templates()
            
            # Создаем базовые UI элементы (если нужно)
            # self._create_base_ui_elements()
            
            self._system_state = SystemState.READY
            logger.info("Система UI успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы UI: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы UI"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            # Троттлинг частоты обновления UI для декуплинга от основного цикла
            self._last_update_time += delta_time
            if self._last_update_time < self._update_interval:
                # Даже если пропускаем тяжелое обновление, обработаем ограниченное число событий
                self._drain_event_queue(budget_only=True)
                return True
            self._last_update_time = 0.0
            
            # Обрабатываем очередь событий с бюджетом
            self._drain_event_queue()

            # Обновляем UI элементы
            self._update_ui_elements(delta_time)
            
            # Обновляем макеты
            self._update_layouts(delta_time)
            
            # Обновляем анимации
            self._update_animations(delta_time)
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы UI: {e}")
            return False

    def _apply_runtime_settings(self) -> None:
        """Применение настроек частоты обновления и лимита очереди"""
        try:
            hz = int(self.system_settings.get('ui_update_hz', 30))
            self._update_interval = 1.0 / max(1, hz)
            self._max_events_per_tick = int(self.system_settings.get('max_events_per_tick', 64))
        except Exception as e:
            logger.warning(f"Некорректные параметры UI настроек: {e}")
    
    def pause(self) -> bool:
        """Приостановка системы UI"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система UI приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы UI: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы UI"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система UI возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы UI: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы UI"""
        try:
            logger.info("Очистка системы UI...")
            
            # Очищаем все данные
            self.ui_elements.clear()
            self.object_templates.clear()
            self.creator_modes.clear()
            self.selected_template = None
            self.active_mode = None
            
            # Сбрасываем статистику
            self.system_stats = {
                'total_elements': 0,
                'visible_elements': 0,
                'active_modes': 0,
                'available_templates': 0,
                'events_processed': 0,
                'update_time': 0.0
            }
            
            # Сбрасываем статистику создания
            self.reset_creation_stats()
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система UI очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы UI: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'total_elements': len(self.ui_elements),
            'active_modes': len(self.creator_modes),
            'available_templates': len(self.object_templates),
            'stats': self.system_stats
        }
    
    def get_available_templates(self, category: ObjectCategory) -> List[WorldObjectTemplate]:
        """Получение доступных шаблонов по категории"""
        try:
            return [template for template in self.object_templates.values() 
                   if template.category == category and template.is_available]
        except Exception as e:
            logger.error(f"Ошибка получения шаблонов для категории {category}: {e}")
            return []
    
    def get_templates_by_type(self, object_type: WorldObjectType) -> List[WorldObjectTemplate]:
        """Получение шаблонов по типу объекта"""
        try:
            return [template for template in self.object_templates.values() 
                   if template.object_type == object_type and template.is_available]
        except Exception as e:
            logger.error(f"Ошибка получения шаблонов для типа {object_type}: {e}")
            return []
    
    def select_template(self, template_id: str) -> bool:
        """Выбор шаблона для размещения"""
        try:
            if template_id in self.object_templates:
                self.selected_template = self.object_templates[template_id]
                logger.info(f"Выбран шаблон: {self.selected_template.name}")
                return True
            else:
                logger.warning(f"Шаблон {template_id} не найден")
                return False
        except Exception as e:
            logger.error(f"Ошибка выбора шаблона {template_id}: {e}")
            return False
    
    def get_template_by_id(self, template_id: str) -> Optional[WorldObjectTemplate]:
        """Получение шаблона по ID"""
        try:
            return self.object_templates.get(template_id)
        except Exception as e:
            logger.error(f"Ошибка получения шаблона {template_id}: {e}")
            return None
    
    def unlock_template(self, template_id: str) -> bool:
        """Разблокировка шаблона"""
        try:
            if template_id in self.object_templates:
                self.object_templates[template_id].is_available = True
                logger.info(f"Разблокирован шаблон: {self.object_templates[template_id].name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка разблокировки шаблона {template_id}: {e}")
            return False
    
    def lock_template(self, template_id: str) -> bool:
        """Блокировка шаблона"""
        try:
            if template_id in self.object_templates:
                self.object_templates[template_id].is_available = False
                logger.info(f"Заблокирован шаблон: {self.object_templates[template_id].name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка блокировки шаблона {template_id}: {e}")
            return False
    
    def get_creation_stats(self) -> Dict[str, Any]:
        """Получение статистики создания"""
        return self.creation_stats.copy()
    
    def reset_creation_stats(self) -> None:
        """Сброс статистики создания"""
        self.creation_stats = {
            'objects_created': 0,
            'obstacles_placed': 0,
            'traps_placed': 0,
            'chests_placed': 0,
            'enemies_spawned': 0,
            'total_cost': 0
        }
    
    def increment_creation_stat(self, stat_name: str, value: int = 1) -> None:
        """Увеличение статистики создания"""
        if stat_name in self.creation_stats:
            self.creation_stats[stat_name] += value
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            # Добавляем в очередь для безопасной обработки в такт UI
            self._event_queue.append((event_type, event_data))
            return True
        except Exception as e:
            logger.error(f"Ошибка постановки события {event_type} в очередь: {e}")
            return False

    def _process_event(self, event_type: str, event_data: Any) -> bool:
        """Немедленная обработка одного события из очереди"""
        try:
            if event_type == "ui_element_created":
                return self._handle_ui_element_created(event_data)
            elif event_type == "ui_element_updated":
                return self._handle_ui_element_updated(event_data)
            elif event_type == "ui_element_destroyed":
                return self._handle_ui_element_destroyed(event_data)
            elif event_type == "screen_changed":
                return self._handle_screen_changed(event_data)
            elif event_type == "theme_changed":
                return self._handle_theme_changed(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False

    def _drain_event_queue(self, budget_only: bool = False) -> None:
        """Обработка очереди событий с бюджетом на тик"""
        try:
            processed = 0
            budget = self._max_events_per_tick if not budget_only else max(1, self._max_events_per_tick // 4)
            while self._event_queue and processed < budget:
                event_type, event_data = self._event_queue.popleft()
                self._process_event(event_type, event_data)
                processed += 1
            self.system_stats['events_processed'] = self.system_stats.get('events_processed', 0) + processed
        except Exception as e:
            logger.warning(f"Ошибка обработки очереди событий UI: {e}")
    
    def _setup_ui_system(self) -> None:
        """Настройка системы UI"""
        try:
            # Здесь должна быть инициализация Panda3D GUI
            # Пока просто логируем
            logger.debug("Система UI настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему UI: {e}")
    
    def _create_base_themes(self) -> None:
        """Создание базовых тем"""
        try:
            # Светлая тема
            light_theme = UITheme(
                theme_id="light_theme",
                name="Светлая тема",
                colors={
                    'primary': (51, 122, 183, 255),
                    'secondary': (92, 184, 92, 255),
                    'success': (92, 184, 92, 255),
                    'warning': (240, 173, 78, 255),
                    'danger': (217, 83, 79, 255),
                    'info': (91, 192, 222, 255),
                    'light': (248, 249, 250, 255),
                    'dark': (52, 58, 64, 255),
                    'white': (255, 255, 255, 255),
                    'black': (0, 0, 0, 255)
                },
                fonts={
                    'default': 'Arial',
                    'heading': 'Arial Bold',
                    'monospace': 'Courier New'
                },
                sizes={
                    'font_small': 12.0,
                    'font_normal': 14.0,
                    'font_large': 16.0,
                    'font_xlarge': 20.0,
                    'spacing_small': 5.0,
                    'spacing_normal': 10.0,
                    'spacing_large': 20.0
                },
                is_active=True
            )
            
            # Темная тема
            dark_theme = UITheme(
                theme_id="dark_theme",
                name="Темная тема",
                colors={
                    'primary': (0, 123, 255, 255),
                    'secondary': (108, 117, 125, 255),
                    'success': (40, 167, 69, 255),
                    'warning': (255, 193, 7, 255),
                    'danger': (220, 53, 69, 255),
                    'info': (23, 162, 184, 255),
                    'light': (248, 249, 250, 255),
                    'dark': (52, 58, 64, 255),
                    'white': (33, 37, 41, 255),
                    'black': (255, 255, 255, 255)
                },
                fonts={
                    'default': 'Arial',
                    'heading': 'Arial Bold',
                    'monospace': 'Courier New'
                },
                sizes={
                    'font_small': 12.0,
                    'font_normal': 14.0,
                    'font_large': 16.0,
                    'font_xlarge': 20.0,
                    'spacing_small': 5.0,
                    'spacing_normal': 10.0,
                    'spacing_large': 20.0
                },
                is_active=False
            )
            
            # Добавляем темы
            self.ui_themes["light_theme"] = light_theme
            self.ui_themes["dark_theme"] = dark_theme
            
            logger.info("Созданы базовые темы")
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых тем: {e}")
    
    def _create_base_layouts(self) -> None:
        """Создание базовых макетов"""
        try:
            # Главное меню
            main_menu_layout = UILayout(
                layout_id="main_menu_layout",
                name="Главное меню",
                layout_type="vertical",
                spacing=10.0,
                padding=(20.0, 20.0),
                auto_size=True
            )
            
            # Игровое меню
            game_menu_layout = UILayout(
                layout_id="game_menu_layout",
                name="Игровое меню",
                layout_type="horizontal",
                spacing=15.0,
                padding=(10.0, 10.0),
                auto_size=False
            )
            
            # Настройки
            settings_layout = UILayout(
                layout_id="settings_layout",
                name="Настройки",
                layout_type="grid",
                spacing=8.0,
                padding=(15.0, 15.0),
                auto_size=True
            )
            
            # Добавляем макеты
            self.ui_layouts["main_menu_layout"] = main_menu_layout
            self.ui_layouts["game_menu_layout"] = game_menu_layout
            self.ui_layouts["settings_layout"] = settings_layout
            
            logger.info("Созданы базовые макеты")
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых макетов: {e}")
    
    def _create_object_templates(self) -> None:
        """Создание шаблонов объектов для создания"""
        try:
            # Создаем шаблоны из констант
            for template_id, template_data in DEFAULT_OBJECT_TEMPLATES.items():
                self.object_templates[template_id] = WorldObjectTemplate(
                    template_id=template_id,
                    name=template_data["name"],
                    object_type=template_data["type"],
                    category=template_data["category"],
                    description=template_data["description"],
                    icon=template_data["icon"],
                    cost=template_data["cost"],
                    unlock_level=template_data["unlock_level"],
                    properties=template_data["properties"]
                )
            
            # Добавляем дополнительные шаблоны
            additional_templates = {
                "poison_pit": {
                    "name": "Яма с ядом",
                    "type": WorldObjectType.TRAP,
                    "category": ObjectCategory.COMBAT,
                    "description": "Ловушка с ядовитым газом",
                    "icon": "☠️",
                    "cost": 35,
                    "unlock_level": 3,
                    "properties": {
                        'width': 2.0,
                        'height': 0.1,
                        'depth': 2.0,
                        'color': (0.2, 0.8, 0.2, 0.8),
                        'damage': 5,
                        'damage_type': 'poison',
                        'duration': 10.0,
                        'trigger_type': 'step'
                    }
                },
                "golden_chest": {
                    "name": "Золотой сундук",
                    "type": WorldObjectType.CHEST,
                    "category": ObjectCategory.REWARDS,
                    "description": "Содержит редкие награды",
                    "icon": "💎",
                    "cost": 150,
                    "unlock_level": 5,
                    "properties": {
                        'width': 1.2,
                        'height': 1.2,
                        'depth': 1.2,
                        'color': (1.0, 0.8, 0.0, 1.0),
                        'loot_quality': 'rare',
                        'loot_count': 5,
                        'locked': True,
                        'trap_chance': 0.3
                    }
                },
                "troll": {
                    "name": "Тролль",
                    "type": WorldObjectType.ENEMY,
                    "category": ObjectCategory.COMBAT,
                    "description": "Сильный и медленный враг",
                    "icon": "👺",
                    "cost": 80,
                    "unlock_level": 4,
                    "properties": {
                        'width': 1.5,
                        'height': 2.5,
                        'depth': 1.5,
                        'color': (0.8, 0.4, 0.2, 1.0),
                        'health': 120,
                        'damage': 25,
                        'speed': 1.5,
                        'ai_type': 'defensive',
                        'loot_drop': True,
                        'regeneration': True
                    }
                },
                "mountain": {
                    "name": "Гора",
                    "type": WorldObjectType.GEO_OBSTACLE,
                    "category": ObjectCategory.ENVIRONMENT,
                    "description": "Непроходимое географическое препятствие",
                    "icon": "⛰️",
                    "cost": 20,
                    "unlock_level": 1,
                    "properties": {
                        'width': 5.0,
                        'height': 8.0,
                        'depth': 5.0,
                        'color': (0.4, 0.3, 0.2, 1.0),
                        'collision': True,
                        'climbable': False,
                        'weather_effect': 'wind'
                    }
                },
                "river": {
                    "name": "Река",
                    "type": WorldObjectType.GEO_OBSTACLE,
                    "category": ObjectCategory.ENVIRONMENT,
                    "description": "Замедляет движение",
                    "icon": "🌊",
                    "cost": 15,
                    "unlock_level": 1,
                    "properties": {
                        'width': 3.0,
                        'height': 0.5,
                        'depth': 10.0,
                        'color': (0.2, 0.4, 0.8, 0.7),
                        'collision': False,
                        'movement_penalty': 0.5,
                        'swimmable': True
                    }
                },
                "tree": {
                    "name": "Дерево",
                    "type": WorldObjectType.DECORATION,
                    "category": ObjectCategory.ENVIRONMENT,
                    "description": "Декоративный элемент",
                    "icon": "🌳",
                    "cost": 5,
                    "unlock_level": 1,
                    "properties": {
                        'width': 1.0,
                        'height': 4.0,
                        'depth': 1.0,
                        'color': (0.2, 0.6, 0.2, 1.0),
                        'collision': False,
                        'provides_shade': True,
                        'seasonal_changes': True
                    }
                }
            }
            
            # Добавляем дополнительные шаблоны
            for template_id, template_data in additional_templates.items():
                self.object_templates[template_id] = WorldObjectTemplate(
                    template_id=template_id,
                    name=template_data["name"],
                    object_type=template_data["type"],
                    category=template_data["category"],
                    description=template_data["description"],
                    icon=template_data["icon"],
                    cost=template_data["cost"],
                    unlock_level=template_data["unlock_level"],
                    properties=template_data["properties"]
                )
            
            logger.info(f"Создано {len(self.object_templates)} шаблонов объектов")
            
        except Exception as e:
            logger.error(f"Ошибка создания шаблонов объектов: {e}")
    
    def _create_base_ui_elements(self) -> None:
        """Создание базовых UI элементов"""
        try:
            # Главное меню
            main_menu = UIElement(
                element_id="main_menu",
                element_type=UIElementType.PANEL,
                name="Главное меню",
                position=(0.0, 0.0),
                size=(800.0, 600.0),
                visible=True,
                enabled=True,
                state=UIState.NORMAL,
                text="Главное меню",
                background_color=(0, 0, 0, 200),
                border_color=(128, 128, 128, 255)
            )
            
            # Кнопка старта
            start_button = UIElement(
                element_id="start_button",
                element_type=UIElementType.BUTTON,
                name="Старт",
                position=(0.0, 100.0),
                size=(200.0, 50.0),
                visible=True,
                enabled=True,
                state=UIState.NORMAL,
                text="Старт",
                background_color=(51, 122, 183, 255),
                border_color=(46, 109, 164, 255),
                parent_id="main_menu"
            )
            
            # Кнопка настроек
            settings_button = UIElement(
                element_id="settings_button",
                element_type=UIElementType.BUTTON,
                name="Настройки",
                position=(0.0, 50.0),
                size=(200.0, 50.0),
                visible=True,
                enabled=True,
                state=UIState.NORMAL,
                text="Настройки",
                background_color=(92, 184, 92, 255),
                border_color=(76, 175, 80, 255),
                parent_id="main_menu"
            )
            
            # Кнопка выхода
            exit_button = UIElement(
                element_id="exit_button",
                element_type=UIElementType.BUTTON,
                name="Выход",
                position=(0.0, 0.0),
                size=(200.0, 50.0),
                visible=True,
                enabled=True,
                state=UIState.NORMAL,
                text="Выход",
                background_color=(217, 83, 79, 255),
                border_color=(212, 63, 58, 255),
                parent_id="main_menu"
            )
            
            # Добавляем элементы
            self.ui_elements["main_menu"] = main_menu
            self.ui_elements["start_button"] = start_button
            self.ui_elements["settings_button"] = settings_button
            self.ui_elements["exit_button"] = exit_button
            
            # Обновляем связи
            main_menu.children = ["start_button", "settings_button", "exit_button"]
            
            # Добавляем в макет
            main_menu_layout = self.ui_layouts["main_menu_layout"]
            main_menu_layout.elements = ["main_menu", "start_button", "settings_button", "exit_button"]
            
            logger.info("Созданы базовые UI элементы")
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых UI элементов: {e}")
    
    def _update_ui_elements(self, delta_time: float) -> None:
        """Обновление UI элементов"""
        try:
            current_time = time.time()
            
            for element_id, ui_element in self.ui_elements.items():
                # Обновляем время последнего обновления
                ui_element.last_update = current_time
                
                # Здесь должна быть логика обновления Panda3D GUI элементов
                # Пока просто обновляем состояние
                if ui_element.visible and ui_element.enabled:
                    ui_element.custom_data['last_updated'] = current_time
                
        except Exception as e:
            logger.warning(f"Ошибка обновления UI элементов: {e}")
    
    def _update_layouts(self, delta_time: float) -> None:
        """Обновление макетов"""
        try:
            current_time = time.time()
            
            for layout_id, layout in self.ui_layouts.items():
                # Обновляем время последнего обновления
                layout.last_update = current_time
                
                # Здесь должна быть логика обновления макетов
                # Пока просто обновляем статистику
                if layout.elements:
                    layout.custom_data = {'last_updated': current_time}
                
        except Exception as e:
            logger.warning(f"Ошибка обновления макетов: {e}")
    
    def _update_animations(self, delta_time: float) -> None:
        """Обновление анимаций"""
        try:
            if not self.system_settings['animation_enabled']:
                return
            
            current_time = time.time()
            
            for element_id, ui_element in self.ui_elements.items():
                if ui_element.animation_data:
                    # Здесь должна быть логика обновления анимаций
                    # Пока просто обновляем время
                    ui_element.animation_data['last_update'] = current_time
                
        except Exception as e:
            logger.warning(f"Ошибка обновления анимаций: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['total_elements'] = len(self.ui_elements)
            self.system_stats['visible_elements'] = len([e for e in self.ui_elements.values() if e.visible])
            self.system_stats['active_layouts'] = len(self.ui_layouts)
            self.system_stats['active_themes'] = len([t for t in self.ui_themes.values() if t.is_active])
            self.system_stats['active_screens'] = len(self.active_screens)
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_ui_element_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания UI элемента"""
        try:
            element_id = event_data.get('element_id')
            element_data = event_data.get('element_data', {})
            
            if element_id and element_data:
                return self.create_ui_element(element_id, element_data)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания UI элемента: {e}")
            return False
    
    def _handle_ui_element_updated(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события обновления UI элемента"""
        try:
            element_id = event_data.get('element_id')
            update_data = event_data.get('update_data', {})
            
            if element_id and update_data:
                return self.update_ui_element(element_id, update_data)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события обновления UI элемента: {e}")
            return False
    
    def _handle_ui_element_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения UI элемента"""
        try:
            element_id = event_data.get('element_id')
            
            if element_id:
                return self.destroy_ui_element(element_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения UI элемента: {e}")
            return False
    
    def _handle_screen_changed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события смены экрана"""
        try:
            screen_id = event_data.get('screen_id')
            action = event_data.get('action', 'show')  # show, hide, switch
            
            if screen_id:
                if action == "show":
                    return self.show_screen(screen_id)
                elif action == "hide":
                    return self.hide_screen(screen_id)
                elif action == "switch":
                    return self.switch_screen(screen_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события смены экрана: {e}")
            return False
    
    def _handle_theme_changed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события смены темы"""
        try:
            theme_id = event_data.get('theme_id')
            
            if theme_id:
                return self.switch_theme(theme_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события смены темы: {e}")
            return False
    
    def create_ui_element(self, element_id: str, element_data: Dict[str, Any]) -> bool:
        """Создание UI элемента"""
        try:
            if element_id in self.ui_elements:
                logger.warning(f"UI элемент {element_id} уже существует")
                return False
            
            # Создаем UI элемент
            ui_element = UIElement(
                element_id=element_id,
                element_type=UIElementType(element_data.get('element_type', UIElementType.PANEL.value)),
                name=element_data.get('name', ''),
                position=element_data.get('position', (0.0, 0.0)),
                size=element_data.get('size', (100.0, 100.0)),
                visible=element_data.get('visible', True),
                enabled=element_data.get('enabled', True),
                state=UIState(element_data.get('state', UIState.NORMAL.value)),
                text=element_data.get('text', ''),
                icon=element_data.get('icon', ''),
                color=element_data.get('color', (255, 255, 255, 255)),
                background_color=element_data.get('background_color', (0, 0, 0, 128)),
                border_color=element_data.get('border_color', (128, 128, 128, 255)),
                font_size=element_data.get('font_size', 14),
                parent_id=element_data.get('parent_id'),
                event_handlers=element_data.get('event_handlers', {}),
                custom_data=element_data.get('custom_data', {})
            )
            
            # Добавляем в систему
            self.ui_elements[element_id] = ui_element
            
            # Обновляем связи с родителем
            if ui_element.parent_id and ui_element.parent_id in self.ui_elements:
                parent = self.ui_elements[ui_element.parent_id]
                parent.children.append(element_id)
            
            # Здесь должна быть логика создания Panda3D GUI элемента
            # Пока просто логируем
            
            logger.info(f"Создан UI элемент {element_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания UI элемента {element_id}: {e}")
            return False
    
    def update_ui_element(self, element_id: str, update_data: Dict[str, Any]) -> bool:
        """Обновление UI элемента"""
        try:
            if element_id not in self.ui_elements:
                return False
            
            ui_element = self.ui_elements[element_id]
            
            # Обновляем свойства
            for key, value in update_data.items():
                if hasattr(ui_element, key):
                    setattr(ui_element, key, value)
            
            ui_element.last_update = time.time()
            
            # Здесь должна быть логика обновления Panda3D GUI элемента
            # Пока просто логируем
            
            logger.debug(f"Обновлен UI элемент {element_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления UI элемента {element_id}: {e}")
            return False
    
    def destroy_ui_element(self, element_id: str) -> bool:
        """Уничтожение UI элемента"""
        try:
            if element_id not in self.ui_elements:
                return False
            
            ui_element = self.ui_elements[element_id]
            
            # Удаляем связи с родителем
            if ui_element.parent_id and ui_element.parent_id in self.ui_elements:
                parent = self.ui_elements[ui_element.parent_id]
                if element_id in parent.children:
                    parent.children.remove(element_id)
            
            # Удаляем дочерние элементы
            for child_id in ui_element.children[:]:
                self.destroy_ui_element(child_id)
            
            # Здесь должна быть логика удаления Panda3D GUI элемента
            # Пока просто удаляем из системы
            
            del self.ui_elements[element_id]
            
            logger.info(f"UI элемент {element_id} уничтожен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения UI элемента {element_id}: {e}")
            return False
    
    def show_screen(self, screen_id: str) -> bool:
        """Показать экран"""
        try:
            if screen_id not in self.active_screens:
                self.active_screens.append(screen_id)
                
                # Показываем все элементы экрана
                for element_id, ui_element in self.ui_elements.items():
                    if element_id.startswith(f"{screen_id}_"):
                        ui_element.visible = True
                
                logger.info(f"Показан экран {screen_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка показа экрана {screen_id}: {e}")
            return False
    
    def hide_screen(self, screen_id: str) -> bool:
        """Скрыть экран"""
        try:
            if screen_id in self.active_screens:
                self.active_screens.remove(screen_id)
                
                # Скрываем все элементы экрана
                for element_id, ui_element in self.ui_elements.items():
                    if element_id.startswith(f"{screen_id}_"):
                        ui_element.visible = False
                
                logger.info(f"Скрыт экран {screen_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка скрытия экрана {screen_id}: {e}")
            return False
    
    def switch_screen(self, screen_id: str) -> bool:
        """Переключить экран"""
        try:
            # Скрываем все экраны
            for active_screen in self.active_screens[:]:
                self.hide_screen(active_screen)
            
            # Показываем нужный экран
            return self.show_screen(screen_id)
            
        except Exception as e:
            logger.error(f"Ошибка переключения на экран {screen_id}: {e}")
            return False
    
    def switch_theme(self, theme_id: str) -> bool:
        """Переключить тему"""
        try:
            if not self.system_settings['theme_switching_enabled']:
                return False
            
            if theme_id not in self.ui_themes:
                return False
            
            # Деактивируем все темы
            for theme in self.ui_themes.values():
                theme.is_active = False
            
            # Активируем нужную тему
            target_theme = self.ui_themes[theme_id]
            target_theme.is_active = True
            target_theme.last_update = time.time()
            
            # Применяем тему ко всем элементам
            self._apply_theme_to_elements(target_theme)
            
            logger.info(f"Переключена тема {theme_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка переключения темы {theme_id}: {e}")
            return False
    
    def _apply_theme_to_elements(self, theme: UITheme) -> None:
        """Применение темы к элементам"""
        try:
            for element_id, ui_element in self.ui_elements.items():
                # Применяем цвета темы
                if 'primary' in theme.colors:
                    ui_element.background_color = theme.colors['primary']
                
                if 'text' in theme.colors:
                    ui_element.color = theme.colors['text']
                
                # Применяем размеры темы
                if 'font_normal' in theme.sizes:
                    ui_element.font_size = int(theme.sizes['font_normal'])
                
        except Exception as e:
            logger.warning(f"Ошибка применения темы к элементам: {e}")
    
    def get_ui_element_info(self, element_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о UI элементе"""
        try:
            if element_id not in self.ui_elements:
                return None
            
            ui_element = self.ui_elements[element_id]
            
            return {
                'element_id': ui_element.element_id,
                'element_type': ui_element.element_type.value,
                'name': ui_element.name,
                'position': ui_element.position,
                'size': ui_element.size,
                'visible': ui_element.visible,
                'enabled': ui_element.enabled,
                'state': ui_element.state.value,
                'text': ui_element.text,
                'icon': ui_element.icon,
                'color': ui_element.color,
                'background_color': ui_element.background_color,
                'border_color': ui_element.border_color,
                'font_size': ui_element.font_size,
                'parent_id': ui_element.parent_id,
                'children': ui_element.children,
                'event_handlers': ui_element.event_handlers,
                'custom_data': ui_element.custom_data,
                'last_update': ui_element.last_update,
                'animation_data': ui_element.animation_data
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о UI элементе {element_id}: {e}")
            return None
    
    def get_layout_info(self, layout_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о макете"""
        try:
            if layout_id not in self.ui_layouts:
                return None
            
            layout = self.ui_layouts[layout_id]
            
            return {
                'layout_id': layout.layout_id,
                'name': layout.name,
                'layout_type': layout.layout_type,
                'spacing': layout.spacing,
                'padding': layout.padding,
                'auto_size': layout.auto_size,
                'elements': layout.elements,
                'constraints': layout.constraints,
                'last_update': layout.last_update
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о макете {layout_id}: {e}")
            return None
    
    def get_theme_info(self, theme_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о теме"""
        try:
            if theme_id not in self.ui_themes:
                return None
            
            theme = self.ui_themes[theme_id]
            
            return {
                'theme_id': theme.theme_id,
                'name': theme.name,
                'colors': theme.colors,
                'fonts': theme.fonts,
                'sizes': theme.sizes,
                'styles': theme.styles,
                'is_active': theme.is_active,
                'last_update': theme.last_update
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о теме {theme_id}: {e}")
            return None
    
    def toggle_ui_element_visibility(self, element_id: str) -> bool:
        """Переключение видимости UI элемента"""
        try:
            if element_id not in self.ui_elements:
                return False
            
            ui_element = self.ui_elements[element_id]
            ui_element.visible = not ui_element.visible
            ui_element.last_update = time.time()
            
            # Здесь должна быть логика обновления Panda3D GUI элемента
            # Пока просто логируем
            
            logger.debug(f"Переключена видимость UI элемента {element_id}: {ui_element.visible}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка переключения видимости UI элемента {element_id}: {e}")
            return False
    
    def get_visible_elements_count(self) -> int:
        """Получение количества видимых элементов"""
        try:
            return len([e for e in self.ui_elements.values() if e.visible])
        except Exception as e:
            logger.error(f"Ошибка получения количества видимых элементов: {e}")
            return 0
    
    def get_elements_by_type(self, element_type: UIElementType) -> List[str]:
        """Получение элементов по типу"""
        try:
            return [
                element_id for element_id, element in self.ui_elements.items()
                if element.element_type == element_type
            ]
        except Exception as e:
            logger.error(f"Ошибка получения элементов по типу {element_type.value}: {e}")
            return []
    
    def get_elements_by_screen(self, screen_id: str) -> List[str]:
        """Получение элементов экрана"""
        try:
            return [
                element_id for element_id in self.ui_elements.keys()
                if element_id.startswith(f"{screen_id}_")
            ]
        except Exception as e:
            logger.error(f"Ошибка получения элементов экрана {screen_id}: {e}")
            return []

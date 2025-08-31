#!/usr/bin/env python3
"""Система UI - расширенный интерфейс пользователя
HUD, инвентарь, диалоги, карта, настройки и уведомления"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import math
import time
import random

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState

logger = logging.getLogger(__name__)

# = ТИПЫ UI

class UIType(Enum):
    """Типы UI элементов"""
    HUD = "hud"                    # Игровой интерфейс
    INVENTORY = "inventory"        # Инвентарь
    DIALOGUE = "dialogue"          # Диалоги
    MAP = "map"                    # Карта
    SETTINGS = "settings"          # Настройки
    NOTIFICATION = "notification"  # Уведомления
    MENU = "menu"                  # Меню

class UILayout(Enum):
    """Типы расположения UI"""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    FULLSCREEN = "fullscreen"

class NotificationType(Enum):
    """Типы уведомлений"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    QUEST = "quest"
    COMBAT = "combat"

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class UIElement:
    """Базовый UI элемент"""
    element_id: str
    ui_type: UIType
    layout: UILayout
    position: Tuple[float, float] = (0.0, 0.0)
    size: Tuple[float, float] = (100.0, 100.0)
    visible: bool = True
    enabled: bool = True
    z_index: int = 0
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)

@dataclass
class HUDElement(UIElement):
    """Элемент HUD"""
    health_bar: bool = False
    mana_bar: bool = False
    stamina_bar: bool = False
    experience_bar: bool = False
    skill_cooldowns: bool = False
    minimap: bool = False
    quest_tracker: bool = False

@dataclass
class InventoryElement(UIElement):
    """Элемент инвентаря"""
    grid_size: Tuple[int, int] = (8, 6)
    item_slots: List[Optional[str]] = field(default_factory=list)
    equipped_items: Dict[str, str] = field(default_factory=dict)
    currency_display: bool = True
    weight_display: bool = True

@dataclass
class DialogueElement(UIElement):
    """Элемент диалога"""
    speaker_name: str = ""
    dialogue_text: str = ""
    options: List[str] = field(default_factory=list)
    portrait_path: Optional[str] = None
    auto_advance: bool = False
    typing_speed: float = 0.05

@dataclass
class MapElement(UIElement):
    """Элемент карты"""
    map_scale: float = 1.0
    player_marker: bool = True
    quest_markers: bool = True
    poi_markers: bool = True
    fog_of_war: bool = True
    zoom_levels: List[float] = field(default_factory=lambda: [0.5, 1.0, 2.0, 4.0])

@dataclass
class Notification:
    """Уведомление"""
    notification_id: str
    title: str
    message: str
    notification_type: NotificationType
    duration: float = 5.0
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    dismissed: bool = False
    action_callback: Optional[Callable] = None

@dataclass
class UITheme:
    """Тема UI"""
    theme_id: str
    name: str
    primary_color: Tuple[float, float, float, float] = (0.2, 0.2, 0.2, 0.9)
    secondary_color: Tuple[float, float, float, float] = (0.3, 0.3, 0.3, 0.9)
    accent_color: Tuple[float, float, float, float] = (0.1, 0.6, 0.9, 1.0)
    text_color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    font_path: str = "fonts/arial.ttf"
    font_size: int = 14

class UISystem(BaseComponent):
    """Система UI"""
    
    def __init__(self):
        super().__init__(
            component_id="ui_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # UI элементы
        self.ui_elements: Dict[str, UIElement] = {}
        self.active_elements: Dict[str, UIElement] = {}
        
        # Уведомления
        self.notifications: List[Notification] = []
        self.notification_queue: List[Notification] = []
        
        # Темы
        self.themes: Dict[str, UITheme] = {}
        self.current_theme: Optional[UITheme] = None
        
        # Интеграция с другими системами
        self.player_entity = None
        self.inventory_system = None
        self.dialogue_system = None
        self.quest_system = None
        self.combat_system = None
        
        # Статистика
        self.total_notifications: int = 0
        self.ui_interactions: int = 0
        
        # Callbacks
        self.on_ui_element_created: Optional[Callable] = None
        self.on_ui_element_updated: Optional[Callable] = None
        self.on_notification_created: Optional[Callable] = None
        self.on_notification_dismissed: Optional[Callable] = None
        
        logger.info("Система UI инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы UI"""
        try:
            logger.info("Инициализация системы UI...")
            
            # Создание базовых тем
            if not self._create_base_themes():
                return False
            
            # Создание базовых UI элементов
            if not self._create_base_ui_elements():
                return False
            
            self.state = LifecycleState.READY
            logger.info("Система UI успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы UI: {e}")
            self.state = LifecycleState.ERROR
            return False
    
    def _create_base_themes(self) -> bool:
        """Создание базовых тем UI"""
        try:
            # Темная тема
            dark_theme = UITheme(
                theme_id="dark_theme",
                name="Темная тема",
                primary_color=(0.1, 0.1, 0.1, 0.95),
                secondary_color=(0.2, 0.2, 0.2, 0.9),
                accent_color=(0.1, 0.6, 0.9, 1.0),
                text_color=(0.9, 0.9, 0.9, 1.0),
                font_path="fonts/arial.ttf",
                font_size=14
            )
            
            # Светлая тема
            light_theme = UITheme(
                theme_id="light_theme",
                name="Светлая тема",
                primary_color=(0.9, 0.9, 0.9, 0.95),
                secondary_color=(0.8, 0.8, 0.8, 0.9),
                accent_color=(0.2, 0.4, 0.8, 1.0),
                text_color=(0.1, 0.1, 0.1, 1.0),
                font_path="fonts/arial.ttf",
                font_size=14
            )
            
            # Игровая тема
            game_theme = UITheme(
                theme_id="game_theme",
                name="Игровая тема",
                primary_color=(0.15, 0.15, 0.2, 0.9),
                secondary_color=(0.25, 0.25, 0.3, 0.85),
                accent_color=(0.8, 0.6, 0.2, 1.0),
                text_color=(0.9, 0.9, 0.8, 1.0),
                font_path="fonts/game_font.ttf",
                font_size=16
            )
            
            self.themes[dark_theme.theme_id] = dark_theme
            self.themes[light_theme.theme_id] = light_theme
            self.themes[game_theme.theme_id] = game_theme
            
            # Установка темы по умолчанию
            self.current_theme = game_theme
            
            logger.info(f"Создано {len(self.themes)} тем UI")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых тем: {e}")
            return False
    
    def _create_base_ui_elements(self) -> bool:
        """Создание базовых UI элементов"""
        try:
            # HUD элементы
            health_bar = HUDElement(
                element_id="health_bar",
                ui_type=UIType.HUD,
                layout=UILayout.TOP_LEFT,
                position=(10.0, 10.0),
                size=(200.0, 20.0),
                health_bar=True
            )
            
            mana_bar = HUDElement(
                element_id="mana_bar",
                ui_type=UIType.HUD,
                layout=UILayout.TOP_LEFT,
                position=(10.0, 35.0),
                size=(200.0, 20.0),
                mana_bar=True
            )
            
            experience_bar = HUDElement(
                element_id="experience_bar",
                ui_type=UIType.HUD,
                layout=UILayout.BOTTOM_LEFT,
                position=(10.0, 10.0),
                size=(300.0, 15.0),
                experience_bar=True
            )
            
            skill_bar = HUDElement(
                element_id="skill_bar",
                ui_type=UIType.HUD,
                layout=UILayout.BOTTOM_CENTER,
                position=(0.0, 10.0),
                size=(400.0, 60.0),
                skill_cooldowns=True
            )
            
            minimap = HUDElement(
                element_id="minimap",
                ui_type=UIType.HUD,
                layout=UILayout.TOP_RIGHT,
                position=(10.0, 10.0),
                size=(150.0, 150.0),
                minimap=True
            )
            
            quest_tracker = HUDElement(
                element_id="quest_tracker",
                ui_type=UIType.HUD,
                layout=UILayout.TOP_RIGHT,
                position=(10.0, 170.0),
                size=(200.0, 100.0),
                quest_tracker=True
            )
            
            # Инвентарь
            inventory = InventoryElement(
                element_id="inventory",
                ui_type=UIType.INVENTORY,
                layout=UILayout.CENTER,
                position=(0.0, 0.0),
                size=(600.0, 400.0),
                visible=False,
                grid_size=(8, 6),
                currency_display=True,
                weight_display=True
            )
            
            # Диалог
            dialogue = DialogueElement(
                element_id="dialogue",
                ui_type=UIType.DIALOGUE,
                layout=UILayout.BOTTOM_CENTER,
                position=(0.0, 50.0),
                size=(800.0, 150.0),
                visible=False,
                typing_speed=0.05
            )
            
            # Карта
            world_map = MapElement(
                element_id="world_map",
                ui_type=UIType.MAP,
                layout=UILayout.FULLSCREEN,
                position=(0.0, 0.0),
                size=(1920.0, 1080.0),
                visible=False,
                map_scale=1.0,
                player_marker=True,
                quest_markers=True,
                poi_markers=True,
                fog_of_war=True
            )
            
            # Настройки
            settings = UIElement(
                element_id="settings",
                ui_type=UIType.SETTINGS,
                layout=UILayout.CENTER,
                position=(0.0, 0.0),
                size=(500.0, 600.0),
                visible=False
            )
            
            # Добавление элементов
            elements = [
                health_bar, mana_bar, experience_bar, skill_bar,
                minimap, quest_tracker, inventory, dialogue,
                world_map, settings
            ]
            
            for element in elements:
                self.ui_elements[element.element_id] = element
                if element.visible:
                    self.active_elements[element.element_id] = element
            
            logger.info(f"Создано {len(self.ui_elements)} базовых UI элементов")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых UI элементов: {e}")
            return False
    
    def set_system_integrations(self, player_entity=None, inventory_system=None,
                               dialogue_system=None, quest_system=None, combat_system=None):
        """Установка интеграций с другими системами"""
        try:
            self.player_entity = player_entity
            self.inventory_system = inventory_system
            self.dialogue_system = dialogue_system
            self.quest_system = quest_system
            self.combat_system = combat_system
            
            logger.info("Интеграции с другими системами установлены")
            
        except Exception as e:
            logger.error(f"Ошибка установки интеграций: {e}")
    
    def create_ui_element(self, element: UIElement) -> bool:
        """Создание UI элемента"""
        try:
            if element.element_id in self.ui_elements:
                logger.warning(f"UI элемент {element.element_id} уже существует")
                return False
            
            self.ui_elements[element.element_id] = element
            
            if element.visible:
                self.active_elements[element.element_id] = element
            
            # Вызов callback
            if self.on_ui_element_created:
                self.on_ui_element_created(element)
            
            logger.info(f"UI элемент {element.element_id} создан")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания UI элемента: {e}")
            return False
    
    def show_ui_element(self, element_id: str) -> bool:
        """Показать UI элемент"""
        try:
            if element_id not in self.ui_elements:
                logger.error(f"UI элемент {element_id} не найден")
                return False
            
            element = self.ui_elements[element_id]
            element.visible = True
            self.active_elements[element_id] = element
            
            # Вызов callback
            if self.on_ui_element_updated:
                self.on_ui_element_updated(element)
            
            logger.info(f"UI элемент {element_id} показан")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка показа UI элемента: {e}")
            return False
    
    def hide_ui_element(self, element_id: str) -> bool:
        """Скрыть UI элемент"""
        try:
            if element_id not in self.ui_elements:
                logger.error(f"UI элемент {element_id} не найден")
                return False
            
            element = self.ui_elements[element_id]
            element.visible = False
            
            if element_id in self.active_elements:
                del self.active_elements[element_id]
            
            # Вызов callback
            if self.on_ui_element_updated:
                self.on_ui_element_updated(element)
            
            logger.info(f"UI элемент {element_id} скрыт")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка скрытия UI элемента: {e}")
            return False
    
    def update_hud(self):
        """Обновление HUD"""
        try:
            if not self.player_entity:
                return
            
            # Обновление полос здоровья/маны/опыта
            health_element = self.ui_elements.get("health_bar")
            if health_element and isinstance(health_element, HUDElement):
                # Здесь должна быть логика обновления полосы здоровья
                pass
            
            mana_element = self.ui_elements.get("mana_bar")
            if mana_element and isinstance(mana_element, HUDElement):
                # Здесь должна быть логика обновления полосы маны
                pass
            
            experience_element = self.ui_elements.get("experience_bar")
            if experience_element and isinstance(experience_element, HUDElement):
                # Здесь должна быть логика обновления полосы опыта
                pass
            
            # Обновление навыков
            skill_element = self.ui_elements.get("skill_bar")
            if skill_element and isinstance(skill_element, HUDElement):
                # Здесь должна быть логика обновления кулдаунов навыков
                pass
            
        except Exception as e:
            logger.error(f"Ошибка обновления HUD: {e}")
    
    def update_inventory(self):
        """Обновление инвентаря"""
        try:
            if not self.inventory_system:
                return
            
            inventory_element = self.ui_elements.get("inventory")
            if not inventory_element or not isinstance(inventory_element, InventoryElement):
                return
            
            # Обновление слотов предметов
            # Здесь должна быть логика обновления инвентаря
            
            # Обновление экипировки
            # Здесь должна быть логика обновления экипировки
            
            # Обновление валюты и веса
            # Здесь должна быть логика обновления валюты и веса
            
        except Exception as e:
            logger.error(f"Ошибка обновления инвентаря: {e}")
    
    def update_dialogue(self, speaker_name: str = "", dialogue_text: str = "", 
                       options: List[str] = None):
        """Обновление диалога"""
        try:
            dialogue_element = self.ui_elements.get("dialogue")
            if not dialogue_element or not isinstance(dialogue_element, DialogueElement):
                return
            
            dialogue_element.speaker_name = speaker_name
            dialogue_element.dialogue_text = dialogue_text
            dialogue_element.options = options or []
            
            # Показать диалог если есть текст
            if dialogue_text:
                self.show_ui_element("dialogue")
            else:
                self.hide_ui_element("dialogue")
            
            # Вызов callback
            if self.on_ui_element_updated:
                self.on_ui_element_updated(dialogue_element)
            
        except Exception as e:
            logger.error(f"Ошибка обновления диалога: {e}")
    
    def update_map(self, player_position: Tuple[float, float] = None,
                   quest_markers: List[Tuple[float, float]] = None,
                   poi_markers: List[Tuple[float, float]] = None):
        """Обновление карты"""
        try:
            map_element = self.ui_elements.get("world_map")
            if not map_element or not isinstance(map_element, MapElement):
                return
            
            # Обновление позиции игрока
            if player_position:
                # Здесь должна быть логика обновления маркера игрока
                pass
            
            # Обновление маркеров квестов
            if quest_markers:
                # Здесь должна быть логика обновления маркеров квестов
                pass
            
            # Обновление точек интереса
            if poi_markers:
                # Здесь должна быть логика обновления точек интереса
                pass
            
        except Exception as e:
            logger.error(f"Ошибка обновления карты: {e}")
    
    def create_notification(self, title: str, message: str, 
                           notification_type: NotificationType = NotificationType.INFO,
                           duration: float = 5.0, priority: int = 0,
                           action_callback: Optional[Callable] = None) -> str:
        """Создание уведомления"""
        try:
            notification_id = f"notification_{int(time.time())}_{random.randint(1000, 9999)}"
            
            notification = Notification(
                notification_id=notification_id,
                title=title,
                message=message,
                notification_type=notification_type,
                duration=duration,
                priority=priority,
                action_callback=action_callback
            )
            
            # Добавление в очередь по приоритету
            self._add_notification_to_queue(notification)
            
            # Обновление статистики
            self.total_notifications += 1
            
            # Вызов callback
            if self.on_notification_created:
                self.on_notification_created(notification)
            
            logger.info(f"Уведомление {notification_id} создано: {title}")
            return notification_id
            
        except Exception as e:
            logger.error(f"Ошибка создания уведомления: {e}")
            return ""
    
    def _add_notification_to_queue(self, notification: Notification):
        """Добавление уведомления в очередь"""
        try:
            # Вставка по приоритету
            insert_index = 0
            for i, existing_notification in enumerate(self.notification_queue):
                if notification.priority > existing_notification.priority:
                    insert_index = i
                    break
                insert_index = i + 1
            
            self.notification_queue.insert(insert_index, notification)
            
            # Ограничение количества уведомлений
            if len(self.notification_queue) > 10:
                self.notification_queue = self.notification_queue[:10]
            
        except Exception as e:
            logger.error(f"Ошибка добавления уведомления в очередь: {e}")
    
    def dismiss_notification(self, notification_id: str) -> bool:
        """Отклонение уведомления"""
        try:
            # Поиск в активных уведомлениях
            for i, notification in enumerate(self.notifications):
                if notification.notification_id == notification_id:
                    dismissed_notification = self.notifications.pop(i)
                    dismissed_notification.dismissed = True
                    
                    # Вызов callback
                    if self.on_notification_dismissed:
                        self.on_notification_dismissed(dismissed_notification)
                    
                    logger.info(f"Уведомление {notification_id} отклонено")
                    return True
            
            # Поиск в очереди
            for i, notification in enumerate(self.notification_queue):
                if notification.notification_id == notification_id:
                    dismissed_notification = self.notification_queue.pop(i)
                    dismissed_notification.dismissed = True
                    
                    # Вызов callback
                    if self.on_notification_dismissed:
                        self.on_notification_dismissed(dismissed_notification)
                    
                    logger.info(f"Уведомление {notification_id} отклонено из очереди")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка отклонения уведомления: {e}")
            return False
    
    def set_theme(self, theme_id: str) -> bool:
        """Установка темы UI"""
        try:
            if theme_id not in self.themes:
                logger.error(f"Тема {theme_id} не найдена")
                return False
            
            self.current_theme = self.themes[theme_id]
            
            # Применение темы ко всем элементам
            for element in self.ui_elements.values():
                # Здесь должна быть логика применения темы
                pass
            
            logger.info(f"Тема {theme_id} установлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка установки темы: {e}")
            return False
    
    def get_ui_element(self, element_id: str) -> Optional[UIElement]:
        """Получение UI элемента"""
        try:
            return self.ui_elements.get(element_id)
            
        except Exception as e:
            logger.error(f"Ошибка получения UI элемента: {e}")
            return None
    
    def get_active_elements(self) -> List[UIElement]:
        """Получение активных UI элементов"""
        try:
            return list(self.active_elements.values())
            
        except Exception as e:
            logger.error(f"Ошибка получения активных элементов: {e}")
            return []
    
    def get_notifications(self) -> List[Notification]:
        """Получение активных уведомлений"""
        try:
            return self.notifications.copy()
            
        except Exception as e:
            logger.error(f"Ошибка получения уведомлений: {e}")
            return []
    
    def update(self, delta_time: float):
        """Обновление системы UI"""
        try:
            # Обновление HUD
            self.update_hud()
            
            # Обновление инвентаря
            self.update_inventory()
            
            # Обработка уведомлений
            self._process_notifications(delta_time)
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы UI: {e}")
    
    def _process_notifications(self, delta_time: float):
        """Обработка уведомлений"""
        try:
            current_time = time.time()
            
            # Удаление истекших уведомлений
            self.notifications = [
                notification for notification in self.notifications
                if current_time - notification.created_at < notification.duration
            ]
            
            # Добавление новых уведомлений из очереди
            while self.notification_queue and len(self.notifications) < 5:
                notification = self.notification_queue.pop(0)
                self.notifications.append(notification)
            
        except Exception as e:
            logger.error(f"Ошибка обработки уведомлений: {e}")
    
    def get_ui_statistics(self) -> Dict[str, Any]:
        """Получение статистики UI"""
        try:
            return {
                "total_ui_elements": len(self.ui_elements),
                "active_ui_elements": len(self.active_elements),
                "total_notifications": self.total_notifications,
                "active_notifications": len(self.notifications),
                "queued_notifications": len(self.notification_queue),
                "ui_interactions": self.ui_interactions,
                "current_theme": self.current_theme.theme_id if self.current_theme else None
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики UI: {e}")
            return {}
    
    def cleanup(self):
        """Очистка системы UI"""
        try:
            # Очистка UI элементов
            self.ui_elements.clear()
            self.active_elements.clear()
            
            # Очистка уведомлений
            self.notifications.clear()
            self.notification_queue.clear()
            
            # Очистка тем
            self.themes.clear()
            self.current_theme = None
            
            logger.info("Система UI очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы UI: {e}")

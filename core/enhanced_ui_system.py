#!/usr/bin/env python3
"""
Расширенная система пользовательского интерфейса.
Вдохновлено UI из Hades, Darkest Dungeon, Risk of Rain 2, Returnal.
Включает адаптивный интерфейс, эмоциональную обратную связь и мета-прогрессию.
"""

import pygame
import math
import time
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class UITheme(Enum):
    """Темы интерфейса"""
    CLASSIC = "classic"                 # Классическая тема
    HADES = "hades"                     # Стиль Hades
    DARKEST_DUNGEON = "darkest_dungeon" # Стиль Darkest Dungeon
    RETURNAL = "returnal"               # Стиль Returnal
    BLOODBORNE = "bloodborne"           # Стиль Bloodborne
    CYBERPUNK = "cyberpunk"             # Киберпанк стиль
    MINIMALIST = "minimalist"           # Минималистичный


class UIState(Enum):
    """Состояния интерфейса"""
    MAIN_MENU = "main_menu"
    IN_GAME = "in_game"
    INVENTORY = "inventory"
    CHARACTER_SHEET = "character_sheet"
    SETTINGS = "settings"
    PAUSE = "pause"
    DIALOGUE = "dialogue"
    EVOLUTION = "evolution"
    META_PROGRESSION = "meta_progression"
    DEATH_SCREEN = "death_screen"


class AnimationType(Enum):
    """Типы анимаций"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_IN = "slide_in"
    SLIDE_OUT = "slide_out"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    PULSE = "pulse"
    SHAKE = "shake"
    GLOW = "glow"
    PARTICLE_BURST = "particle_burst"


@dataclass
class UIAnimation:
    """Анимация UI элемента"""
    animation_type: AnimationType
    duration: float
    start_time: float
    start_value: float
    end_value: float
    easing_function: str = "linear"
    loop: bool = False
    
    def get_current_value(self, current_time: float) -> float:
        """Получение текущего значения анимации"""
        elapsed = current_time - self.start_time
        progress = min(1.0, elapsed / self.duration)
        
        # Применение функции сглаживания
        if self.easing_function == "ease_in":
            progress = progress * progress
        elif self.easing_function == "ease_out":
            progress = 1 - (1 - progress) * (1 - progress)
        elif self.easing_function == "ease_in_out":
            if progress < 0.5:
                progress = 2 * progress * progress
            else:
                progress = 1 - 2 * (1 - progress) * (1 - progress)
        
        current_value = self.start_value + (self.end_value - self.start_value) * progress
        
        # Обработка зацикливания
        if self.loop and elapsed >= self.duration:
            self.start_time = current_time
        
        return current_value
    
    def is_finished(self, current_time: float) -> bool:
        """Проверка завершения анимации"""
        if self.loop:
            return False
        return (current_time - self.start_time) >= self.duration


@dataclass
class UIElement:
    """Базовый UI элемент"""
    id: str
    x: float
    y: float
    width: float
    height: float
    visible: bool = True
    interactive: bool = False
    
    # Стиль
    background_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
    border_color: Tuple[int, int, int, int] = (255, 255, 255, 255)
    border_width: int = 0
    
    # Анимации
    animations: List[UIAnimation] = field(default_factory=list)
    
    # Callbacks
    on_click: Optional[Callable] = None
    on_hover: Optional[Callable] = None
    
    def update(self, delta_time: float):
        """Обновление элемента"""
        current_time = time.time()
        
        # Обновление анимаций
        for animation in list(self.animations):
            if animation.is_finished(current_time):
                self.animations.remove(animation)
    
    def add_animation(self, animation: UIAnimation):
        """Добавление анимации"""
        animation.start_time = time.time()
        self.animations.append(animation)
    
    def is_point_inside(self, point: Tuple[float, float]) -> bool:
        """Проверка попадания точки в элемент"""
        px, py = point
        return (self.x <= px <= self.x + self.width and
                self.y <= py <= self.y + self.height)


@dataclass
class UIText(UIElement):
    """Текстовый UI элемент"""
    text: str = ""
    font_size: int = 16
    font_color: Tuple[int, int, int] = (255, 255, 255)
    font_name: str = "Arial"
    alignment: str = "left"  # left, center, right
    
    # Эффекты текста
    shadow: bool = False
    shadow_offset: Tuple[int, int] = (2, 2)
    shadow_color: Tuple[int, int, int] = (0, 0, 0)
    
    outline: bool = False
    outline_width: int = 1
    outline_color: Tuple[int, int, int] = (0, 0, 0)


@dataclass
class UIButton(UIElement):
    """Кнопка"""
    text: str = ""
    font_size: int = 16
    
    # Состояния кнопки
    normal_color: Tuple[int, int, int, int] = (100, 100, 100, 255)
    hover_color: Tuple[int, int, int, int] = (150, 150, 150, 255)
    pressed_color: Tuple[int, int, int, int] = (50, 50, 50, 255)
    disabled_color: Tuple[int, int, int, int] = (50, 50, 50, 128)
    
    enabled: bool = True
    pressed: bool = False
    hovered: bool = False


@dataclass
class UIProgressBar(UIElement):
    """Прогресс-бар"""
    current_value: float = 0.0
    max_value: float = 100.0
    
    # Цвета
    fill_color: Tuple[int, int, int, int] = (0, 255, 0, 255)
    background_color: Tuple[int, int, int, int] = (50, 50, 50, 255)
    
    # Стиль
    show_text: bool = True
    text_format: str = "{current}/{max}"
    
    # Анимированное заполнение
    animated: bool = True
    animation_speed: float = 2.0
    display_value: float = 0.0
    
    def update(self, delta_time: float):
        """Обновление прогресс-бара"""
        super().update(delta_time)
        
        if self.animated:
            # Плавное изменение отображаемого значения
            diff = self.current_value - self.display_value
            if abs(diff) > 0.1:
                self.display_value += diff * self.animation_speed * delta_time
            else:
                self.display_value = self.current_value
    
    def get_fill_percentage(self) -> float:
        """Получение процента заполнения"""
        if self.max_value == 0:
            return 0.0
        return min(1.0, max(0.0, self.display_value / self.max_value))


class EnhancedUISystem:
    """Расширенная система пользовательского интерфейса"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Состояние UI
        self.current_state = UIState.MAIN_MENU
        self.previous_state = None
        
        # Элементы интерфейса
        self.ui_elements: Dict[str, List[UIElement]] = {state.value: [] for state in UIState}
        
        # Система тем
        self.current_theme = UITheme.CLASSIC
        self.theme_configs: Dict[UITheme, Dict[str, Any]] = {}
        
        # Система анимаций
        self.animation_system = UIAnimationSystem()
        
        # Система частиц для UI
        self.particle_system = UIParticleSystem()
        
        # Система обратной связи
        self.feedback_system = UIFeedbackSystem()
        
        # Адаптивный интерфейс
        self.adaptive_ui = AdaptiveUISystem()
        
        # Инициализация
        self._init_themes()
        self._init_ui_elements()
        
        logger.info("Расширенная система UI инициализирована")
    
    def update(self, delta_time: float, input_events: List[Any]):
        """Обновление системы UI"""
        # Обновление элементов текущего состояния
        current_elements = self.ui_elements.get(self.current_state.value, [])
        for element in current_elements:
            element.update(delta_time)
        
        # Обработка ввода
        self._handle_input_events(input_events)
        
        # Обновление систем
        self.animation_system.update(delta_time)
        self.particle_system.update(delta_time)
        self.feedback_system.update(delta_time)
        self.adaptive_ui.update(delta_time)
    
    def render(self, screen: pygame.Surface):
        """Отрисовка UI"""
        # Отрисовка элементов текущего состояния
        current_elements = self.ui_elements.get(self.current_state.value, [])
        for element in current_elements:
            if element.visible:
                self._render_element(screen, element)
        
        # Отрисовка частиц
        self.particle_system.render(screen)
        
        # Отрисовка системы обратной связи
        self.feedback_system.render(screen)
    
    def change_state(self, new_state: UIState, transition_type: str = "fade"):
        """Изменение состояния UI"""
        if new_state == self.current_state:
            return
        
        self.previous_state = self.current_state
        
        # Анимация перехода
        if transition_type == "fade":
            self._fade_transition(new_state)
        elif transition_type == "slide":
            self._slide_transition(new_state)
        
        self.current_state = new_state
        logger.info(f"UI состояние изменено на: {new_state.value}")
    
    def add_element(self, state: UIState, element: UIElement):
        """Добавление UI элемента"""
        if state.value not in self.ui_elements:
            self.ui_elements[state.value] = []
        
        self.ui_elements[state.value].append(element)
    
    def remove_element(self, state: UIState, element_id: str):
        """Удаление UI элемента"""
        if state.value in self.ui_elements:
            self.ui_elements[state.value] = [
                elem for elem in self.ui_elements[state.value] 
                if elem.id != element_id
            ]
    
    def get_element(self, state: UIState, element_id: str) -> Optional[UIElement]:
        """Получение UI элемента"""
        if state.value in self.ui_elements:
            for element in self.ui_elements[state.value]:
                if element.id == element_id:
                    return element
        return None
    
    def show_notification(self, message: str, notification_type: str = "info", 
                         duration: float = 3.0):
        """Показ уведомления"""
        self.feedback_system.show_notification(message, notification_type, duration)
    
    def show_damage_number(self, damage: float, position: Tuple[float, float], 
                          damage_type: str = "normal"):
        """Показ числа урона"""
        self.feedback_system.show_damage_number(damage, position, damage_type)
    
    def trigger_screen_shake(self, intensity: float, duration: float):
        """Активация тряски экрана"""
        self.feedback_system.trigger_screen_shake(intensity, duration)
    
    def set_theme(self, theme: UITheme):
        """Установка темы интерфейса"""
        self.current_theme = theme
        self._apply_theme()
        logger.info(f"Тема UI изменена на: {theme.value}")
    
    def _init_themes(self):
        """Инициализация тем интерфейса"""
        self.theme_configs = {
            UITheme.HADES: {
                "primary_color": (139, 69, 19),      # Коричневый
                "secondary_color": (255, 215, 0),    # Золотой
                "accent_color": (255, 69, 0),        # Красно-оранжевый
                "background_color": (25, 25, 25),    # Тёмно-серый
                "text_color": (255, 255, 255),       # Белый
                "font_family": "serif",
                "ui_style": "ornate"
            },
            UITheme.DARKEST_DUNGEON: {
                "primary_color": (139, 0, 0),        # Тёмно-красный
                "secondary_color": (105, 105, 105),  # Тёмно-серый
                "accent_color": (255, 215, 0),       # Золотой
                "background_color": (0, 0, 0),       # Чёрный
                "text_color": (255, 255, 255),       # Белый
                "font_family": "serif",
                "ui_style": "gothic"
            },
            UITheme.RETURNAL: {
                "primary_color": (0, 255, 255),      # Голубой
                "secondary_color": (255, 0, 255),    # Пурпурный
                "accent_color": (255, 255, 0),       # Жёлтый
                "background_color": (10, 10, 20),    # Тёмно-синий
                "text_color": (255, 255, 255),       # Белый
                "font_family": "futuristic",
                "ui_style": "sci_fi"
            },
            UITheme.BLOODBORNE: {
                "primary_color": (128, 0, 0),        # Тёмно-красный
                "secondary_color": (64, 64, 64),     # Серый
                "accent_color": (255, 215, 0),       # Золотой
                "background_color": (0, 0, 0),       # Чёрный
                "text_color": (200, 200, 200),       # Светло-серый
                "font_family": "gothic",
                "ui_style": "horror"
            }
        }
    
    def _init_ui_elements(self):
        """Инициализация UI элементов"""
        # Главное меню
        self._init_main_menu()
        
        # Игровой интерфейс
        self._init_in_game_ui()
        
        # Инвентарь
        self._init_inventory_ui()
        
        # Лист персонажа
        self._init_character_sheet()
        
        # Мета-прогрессия
        self._init_meta_progression_ui()
    
    def _init_main_menu(self):
        """Инициализация главного меню"""
        # Заголовок игры
        title = UIText(
            id="game_title",
            x=self.screen_width // 2 - 200,
            y=100,
            width=400,
            height=80,
            text="AI EVOLVE: Enhanced Edition",
            font_size=32,
            font_color=(255, 215, 0),
            alignment="center"
        )
        self.add_element(UIState.MAIN_MENU, title)
        
        # Кнопки меню
        button_width = 200
        button_height = 50
        button_x = self.screen_width // 2 - button_width // 2
        
        buttons = [
            ("new_game", "Новая игра", 300),
            ("continue", "Продолжить", 370),
            ("meta_progression", "Мета-прогрессия", 440),
            ("settings", "Настройки", 510),
            ("exit", "Выход", 580)
        ]
        
        for button_id, text, y in buttons:
            button = UIButton(
                id=button_id,
                x=button_x,
                y=y,
                width=button_width,
                height=button_height,
                text=text,
                interactive=True,
                on_click=self._create_button_callback(button_id)
            )
            self.add_element(UIState.MAIN_MENU, button)
    
    def _init_in_game_ui(self):
        """Инициализация игрового интерфейса"""
        # Полоса здоровья
        health_bar = UIProgressBar(
            id="health_bar",
            x=20,
            y=20,
            width=200,
            height=20,
            current_value=100,
            max_value=100,
            fill_color=(255, 0, 0, 255),
            show_text=True,
            text_format="HP: {current}/{max}"
        )
        self.add_element(UIState.IN_GAME, health_bar)
        
        # Полоса энергии
        energy_bar = UIProgressBar(
            id="energy_bar",
            x=20,
            y=50,
            width=200,
            height=20,
            current_value=50,
            max_value=100,
            fill_color=(0, 0, 255, 255),
            show_text=True,
            text_format="Energy: {current}/{max}"
        )
        self.add_element(UIState.IN_GAME, energy_bar)
        
        # Индикатор эволюции
        evolution_bar = UIProgressBar(
            id="evolution_bar",
            x=20,
            y=80,
            width=200,
            height=15,
            current_value=25,
            max_value=100,
            fill_color=(0, 255, 0, 255),
            show_text=True,
            text_format="Evolution: {current}%"
        )
        self.add_element(UIState.IN_GAME, evolution_bar)
        
        # Мини-карта
        minimap = UIElement(
            id="minimap",
            x=self.screen_width - 220,
            y=20,
            width=200,
            height=200,
            background_color=(0, 0, 0, 128),
            border_color=(255, 255, 255, 255),
            border_width=2
        )
        self.add_element(UIState.IN_GAME, minimap)
    
    def _init_inventory_ui(self):
        """Инициализация интерфейса инвентаря"""
        # Сетка инвентаря (5x4)
        slot_size = 60
        start_x = 100
        start_y = 100
        
        for row in range(4):
            for col in range(5):
                slot_id = f"inventory_slot_{row}_{col}"
                slot = UIElement(
                    id=slot_id,
                    x=start_x + col * (slot_size + 5),
                    y=start_y + row * (slot_size + 5),
                    width=slot_size,
                    height=slot_size,
                    background_color=(50, 50, 50, 255),
                    border_color=(100, 100, 100, 255),
                    border_width=2,
                    interactive=True
                )
                self.add_element(UIState.INVENTORY, slot)
    
    def _init_character_sheet(self):
        """Инициализация листа персонажа"""
        # Характеристики
        stats = [
            ("Уровень", "level", 1),
            ("Здоровье", "health", 100),
            ("Атака", "attack", 25),
            ("Защита", "defense", 10),
            ("Скорость", "speed", 2.0),
            ("Эволюция", "evolution", 15)
        ]
        
        for i, (name, stat_id, value) in enumerate(stats):
            stat_text = UIText(
                id=f"stat_{stat_id}",
                x=50,
                y=100 + i * 30,
                width=200,
                height=25,
                text=f"{name}: {value}",
                font_size=18
            )
            self.add_element(UIState.CHARACTER_SHEET, stat_text)
    
    def _init_meta_progression_ui(self):
        """Инициализация интерфейса мета-прогрессии"""
        # Валюты
        currencies = [
            ("Эссенция", "essence", 1250),
            ("Фрагменты памяти", "memory_fragments", 45),
            ("Очки эволюции", "evolution_points", 78),
            ("Кристаллы мудрости", "wisdom_crystals", 12)
        ]
        
        for i, (name, currency_id, amount) in enumerate(currencies):
            currency_text = UIText(
                id=f"currency_{currency_id}",
                x=50,
                y=50 + i * 30,
                width=250,
                height=25,
                text=f"{name}: {amount}",
                font_size=16,
                font_color=(255, 215, 0)
            )
            self.add_element(UIState.META_PROGRESSION, currency_text)
    
    def _handle_input_events(self, events: List[Any]):
        """Обработка событий ввода"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if hasattr(event, 'type'):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_click(mouse_pos, event.button)
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_mouse_hover(mouse_pos)
                elif event.type == pygame.KEYDOWN:
                    self._handle_key_press(event.key)
    
    def _handle_mouse_click(self, pos: Tuple[int, int], button: int):
        """Обработка клика мыши"""
        current_elements = self.ui_elements.get(self.current_state.value, [])
        
        for element in current_elements:
            if element.interactive and element.is_point_inside(pos):
                if element.on_click:
                    element.on_click(element, pos, button)
                
                # Анимация клика
                click_animation = UIAnimation(
                    animation_type=AnimationType.SCALE_DOWN,
                    duration=0.1,
                    start_time=time.time(),
                    start_value=1.0,
                    end_value=0.95,
                    easing_function="ease_out"
                )
                element.add_animation(click_animation)
                break
    
    def _handle_mouse_hover(self, pos: Tuple[int, int]):
        """Обработка наведения мыши"""
        current_elements = self.ui_elements.get(self.current_state.value, [])
        
        for element in current_elements:
            if element.interactive:
                is_hovered = element.is_point_inside(pos)
                
                if isinstance(element, UIButton):
                    if is_hovered and not element.hovered:
                        element.hovered = True
                        if element.on_hover:
                            element.on_hover(element, pos, True)
                    elif not is_hovered and element.hovered:
                        element.hovered = False
                        if element.on_hover:
                            element.on_hover(element, pos, False)
    
    def _handle_key_press(self, key: int):
        """Обработка нажатия клавиш"""
        # Глобальные горячие клавиши
        if key == pygame.K_ESCAPE:
            if self.current_state == UIState.IN_GAME:
                self.change_state(UIState.PAUSE)
            elif self.current_state == UIState.PAUSE:
                self.change_state(UIState.IN_GAME)
        elif key == pygame.K_i:
            if self.current_state == UIState.IN_GAME:
                self.change_state(UIState.INVENTORY)
            elif self.current_state == UIState.INVENTORY:
                self.change_state(UIState.IN_GAME)
        elif key == pygame.K_c:
            if self.current_state == UIState.IN_GAME:
                self.change_state(UIState.CHARACTER_SHEET)
            elif self.current_state == UIState.CHARACTER_SHEET:
                self.change_state(UIState.IN_GAME)
    
    def _render_element(self, screen: pygame.Surface, element: UIElement):
        """Отрисовка UI элемента"""
        # Фон элемента
        if element.background_color[3] > 0:
            bg_surface = pygame.Surface((element.width, element.height), pygame.SRCALPHA)
            bg_surface.fill(element.background_color)
            screen.blit(bg_surface, (element.x, element.y))
        
        # Граница элемента
        if element.border_width > 0:
            pygame.draw.rect(screen, element.border_color[:3], 
                           (element.x, element.y, element.width, element.height), 
                           element.border_width)
        
        # Специфичная отрисовка для разных типов элементов
        if isinstance(element, UIText):
            self._render_text(screen, element)
        elif isinstance(element, UIButton):
            self._render_button(screen, element)
        elif isinstance(element, UIProgressBar):
            self._render_progress_bar(screen, element)
    
    def _render_text(self, screen: pygame.Surface, text_element: UIText):
        """Отрисовка текста"""
        if not text_element.text:
            return
        
        # Создание шрифта (упрощённая версия)
        font = pygame.font.Font(None, text_element.font_size)
        
        # Отрисовка тени
        if text_element.shadow:
            shadow_surface = font.render(text_element.text, True, text_element.shadow_color)
            shadow_x = text_element.x + text_element.shadow_offset[0]
            shadow_y = text_element.y + text_element.shadow_offset[1]
            screen.blit(shadow_surface, (shadow_x, shadow_y))
        
        # Отрисовка основного текста
        text_surface = font.render(text_element.text, True, text_element.font_color)
        
        # Выравнивание
        if text_element.alignment == "center":
            text_x = text_element.x + (text_element.width - text_surface.get_width()) // 2
        elif text_element.alignment == "right":
            text_x = text_element.x + text_element.width - text_surface.get_width()
        else:  # left
            text_x = text_element.x
        
        text_y = text_element.y + (text_element.height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def _render_button(self, screen: pygame.Surface, button: UIButton):
        """Отрисовка кнопки"""
        # Выбор цвета в зависимости от состояния
        if not button.enabled:
            color = button.disabled_color
        elif button.pressed:
            color = button.pressed_color
        elif button.hovered:
            color = button.hover_color
        else:
            color = button.normal_color
        
        # Фон кнопки
        button_surface = pygame.Surface((button.width, button.height), pygame.SRCALPHA)
        button_surface.fill(color)
        screen.blit(button_surface, (button.x, button.y))
        
        # Текст кнопки
        if button.text:
            font = pygame.font.Font(None, button.font_size)
            text_surface = font.render(button.text, True, (255, 255, 255))
            text_x = button.x + (button.width - text_surface.get_width()) // 2
            text_y = button.y + (button.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
    
    def _render_progress_bar(self, screen: pygame.Surface, progress_bar: UIProgressBar):
        """Отрисовка прогресс-бара"""
        # Фон
        bg_surface = pygame.Surface((progress_bar.width, progress_bar.height))
        bg_surface.fill(progress_bar.background_color[:3])
        screen.blit(bg_surface, (progress_bar.x, progress_bar.y))
        
        # Заполнение
        fill_width = int(progress_bar.width * progress_bar.get_fill_percentage())
        if fill_width > 0:
            fill_surface = pygame.Surface((fill_width, progress_bar.height))
            fill_surface.fill(progress_bar.fill_color[:3])
            screen.blit(fill_surface, (progress_bar.x, progress_bar.y))
        
        # Текст
        if progress_bar.show_text:
            text = progress_bar.text_format.format(
                current=int(progress_bar.display_value),
                max=int(progress_bar.max_value)
            )
            font = pygame.font.Font(None, 16)
            text_surface = font.render(text, True, (255, 255, 255))
            text_x = progress_bar.x + (progress_bar.width - text_surface.get_width()) // 2
            text_y = progress_bar.y + (progress_bar.height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
    
    def _create_button_callback(self, button_id: str) -> Callable:
        """Создание callback для кнопки"""
        def callback(element, pos, button):
            if button_id == "new_game":
                self.change_state(UIState.IN_GAME)
            elif button_id == "continue":
                self.change_state(UIState.IN_GAME)
            elif button_id == "meta_progression":
                self.change_state(UIState.META_PROGRESSION)
            elif button_id == "settings":
                self.change_state(UIState.SETTINGS)
            elif button_id == "exit":
                pygame.quit()
        
        return callback
    
    def _fade_transition(self, new_state: UIState):
        """Переход с затуханием"""
        # Добавление анимации затухания для текущих элементов
        current_elements = self.ui_elements.get(self.current_state.value, [])
        for element in current_elements:
            fade_out = UIAnimation(
                animation_type=AnimationType.FADE_OUT,
                duration=0.3,
                start_time=time.time(),
                start_value=1.0,
                end_value=0.0
            )
            element.add_animation(fade_out)
    
    def _slide_transition(self, new_state: UIState):
        """Переход со скольжением"""
        # Анимация скольжения для элементов
        pass
    
    def _apply_theme(self):
        """Применение текущей темы"""
        if self.current_theme in self.theme_configs:
            config = self.theme_configs[self.current_theme]
            
            # Применение цветовой схемы ко всем элементам
            for state_elements in self.ui_elements.values():
                for element in state_elements:
                    if isinstance(element, UIText):
                        element.font_color = config.get("text_color", (255, 255, 255))
                    elif isinstance(element, UIButton):
                        primary = config.get("primary_color", (100, 100, 100))
                        element.normal_color = (*primary, 255)


class UIAnimationSystem:
    """Система анимаций UI"""
    
    def __init__(self):
        self.global_animations: List[UIAnimation] = []
    
    def update(self, delta_time: float):
        """Обновление анимаций"""
        current_time = time.time()
        
        # Удаление завершённых анимаций
        self.global_animations = [
            anim for anim in self.global_animations 
            if not anim.is_finished(current_time)
        ]


class UIParticleSystem:
    """Система частиц для UI"""
    
    def __init__(self):
        self.particles: List[Dict[str, Any]] = []
    
    def update(self, delta_time: float):
        """Обновление частиц"""
        for particle in list(self.particles):
            particle["life"] -= delta_time
            if particle["life"] <= 0:
                self.particles.remove(particle)
    
    def render(self, screen: pygame.Surface):
        """Отрисовка частиц"""
        for particle in self.particles:
            # Простая отрисовка частицы
            alpha = int(255 * (particle["life"] / particle["max_life"]))
            color = (*particle["color"][:3], alpha)
            
            particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            particle_surface.fill(color)
            screen.blit(particle_surface, (particle["x"], particle["y"]))


class UIFeedbackSystem:
    """Система обратной связи UI"""
    
    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []
        self.damage_numbers: List[Dict[str, Any]] = []
        self.screen_shake_intensity = 0.0
        self.screen_shake_duration = 0.0
    
    def update(self, delta_time: float):
        """Обновление системы обратной связи"""
        # Обновление уведомлений
        for notification in list(self.notifications):
            notification["duration"] -= delta_time
            if notification["duration"] <= 0:
                self.notifications.remove(notification)
        
        # Обновление чисел урона
        for damage_number in list(self.damage_numbers):
            damage_number["duration"] -= delta_time
            damage_number["y"] -= 50 * delta_time  # Движение вверх
            if damage_number["duration"] <= 0:
                self.damage_numbers.remove(damage_number)
        
        # Обновление тряски экрана
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= delta_time
            if self.screen_shake_duration <= 0:
                self.screen_shake_intensity = 0.0
    
    def render(self, screen: pygame.Surface):
        """Отрисовка обратной связи"""
        # Отрисовка уведомлений
        for i, notification in enumerate(self.notifications):
            y_pos = 50 + i * 30
            font = pygame.font.Font(None, 24)
            text_surface = font.render(notification["message"], True, (255, 255, 255))
            screen.blit(text_surface, (50, y_pos))
        
        # Отрисовка чисел урона
        for damage_number in self.damage_numbers:
            font = pygame.font.Font(None, 32)
            color = (255, 0, 0) if damage_number["type"] == "damage" else (0, 255, 0)
            text_surface = font.render(str(int(damage_number["value"])), True, color)
            screen.blit(text_surface, (damage_number["x"], damage_number["y"]))
    
    def show_notification(self, message: str, notification_type: str, duration: float):
        """Показ уведомления"""
        self.notifications.append({
            "message": message,
            "type": notification_type,
            "duration": duration
        })
    
    def show_damage_number(self, damage: float, position: Tuple[float, float], 
                          damage_type: str):
        """Показ числа урона"""
        self.damage_numbers.append({
            "value": damage,
            "x": position[0],
            "y": position[1],
            "type": damage_type,
            "duration": 1.5
        })
    
    def trigger_screen_shake(self, intensity: float, duration: float):
        """Активация тряски экрана"""
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration


class AdaptiveUISystem:
    """Система адаптивного интерфейса"""
    
    def __init__(self):
        self.user_preferences: Dict[str, Any] = {}
        self.usage_statistics: Dict[str, int] = {}
    
    def update(self, delta_time: float):
        """Обновление адаптивной системы"""
        # Анализ использования UI элементов
        pass
    
    def adapt_ui_layout(self, screen_resolution: Tuple[int, int]):
        """Адаптация макета под разрешение"""
        # Масштабирование элементов под разрешение
        pass

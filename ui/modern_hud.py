#!/usr/bin/env python3
"""
Современный HUD и UI система
Обновленный интерфейс с современным дизайном и улучшенной функциональностью
"""

import pygame
import math
import time
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HUDPanelType(Enum):
    """Типы панелей HUD"""
    STATUS = "status"
    INVENTORY = "inventory"
    EMOTIONS = "emotions"
    GENETICS = "genetics"
    AI_LEARNING = "ai_learning"
    DEBUG = "debug"
    MINIMAP = "minimap"
    QUESTS = "quests"
    SKILLS = "skills"


@dataclass
class HUDPanel:
    """Панель HUD"""
    panel_type: HUDPanelType
    rect: pygame.Rect
    visible: bool = True
    alpha: int = 255
    background_color: Tuple[int, int, int] = (20, 20, 30)
    border_color: Tuple[int, int, int] = (60, 60, 80)
    title: str = ""
    title_color: Tuple[int, int, int] = (255, 255, 255)


class ModernProgressBar:
    """Современная полоса прогресса"""
    
    def __init__(self, rect: pygame.Rect, max_value: float = 100.0, 
                 current_value: float = 0.0, color: Tuple[int, int, int] = (0, 255, 0)):
        self.rect = rect
        self.max_value = max_value
        self.current_value = current_value
        self.color = color
        self.background_color = (40, 40, 50)
        self.border_color = (80, 80, 100)
        self.glow_color = (*color, 100)
        
        # Анимация
        self.target_value = current_value
        self.animation_speed = 5.0
        
    def update(self, delta_time: float):
        """Обновление анимации"""
        if abs(self.current_value - self.target_value) > 0.1:
            diff = self.target_value - self.current_value
            self.current_value += diff * self.animation_speed * delta_time
    
    def set_value(self, value: float):
        """Установка значения"""
        self.target_value = max(0, min(value, self.max_value))
    
    def render(self, screen: pygame.Surface):
        """Рендеринг полосы прогресса"""
        # Фон
        pygame.draw.rect(screen, self.background_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Прогресс
        if self.max_value > 0:
            progress_ratio = self.current_value / self.max_value
            progress_width = int(self.rect.width * progress_ratio)
            
            if progress_width > 0:
                progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
                
                # Основной цвет
                pygame.draw.rect(screen, self.color, progress_rect)
                
                # Градиент
                for i in range(min(5, progress_width)):
                    alpha = 100 - i * 20
                    if alpha > 0:
                        gradient_color = (*self.color, alpha)
                        gradient_surface = pygame.Surface((1, self.rect.height), pygame.SRCALPHA)
                        gradient_surface.fill(gradient_color)
                        screen.blit(gradient_surface, (progress_rect.x + i, progress_rect.y))


class ModernButton:
    """Современная кнопка"""
    
    def __init__(self, rect: pygame.Rect, text: str, callback=None, 
                 color: Tuple[int, int, int] = (60, 60, 80)):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = tuple(min(255, c + 30) for c in color)
        self.pressed_color = tuple(max(0, c - 30) for c in color)
        self.text_color = (255, 255, 255)
        self.border_color = (100, 100, 120)
        
        # Состояние
        self.hovered = False
        self.pressed = False
        self.enabled = True
        
        # Анимация
        self.hover_animation = 0.0
        self.press_animation = 0.0
        
    def update(self, delta_time: float):
        """Обновление анимации"""
        target_hover = 1.0 if self.hovered else 0.0
        self.hover_animation += (target_hover - self.hover_animation) * 10 * delta_time
        
        target_press = 1.0 if self.pressed else 0.0
        self.press_animation += (target_press - self.press_animation) * 15 * delta_time
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обработка событий"""
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.pressed:
                self.pressed = False
                if self.rect.collidepoint(event.pos) and self.callback:
                    self.callback()
                return True
                
        return False
    
    def render(self, screen: pygame.Surface, font: pygame.font.Font):
        """Рендеринг кнопки"""
        # Цвет с учетом состояния
        current_color = self.color
        if self.pressed:
            current_color = self.pressed_color
        elif self.hovered:
            current_color = self.hover_color
        
        # Фон
        pygame.draw.rect(screen, current_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # Эффект нажатия
        if self.pressed:
            offset = 2
            pressed_rect = self.rect.inflate(-offset, -offset)
            pygame.draw.rect(screen, (0, 0, 0, 50), pressed_rect)
        
        # Текст
        if font:
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            
            # Смещение при нажатии
            if self.pressed:
                text_rect.y += 1
            
            screen.blit(text_surface, text_rect)


class EmotionIndicator:
    """Индикатор эмоций"""
    
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.emotions = {}
        self.animation_time = 0.0
        
    def update_emotions(self, emotions: Dict[str, float]):
        """Обновление эмоций"""
        self.emotions = emotions
    
    def update(self, delta_time: float):
        """Обновление анимации"""
        self.animation_time += delta_time
    
    def render(self, screen: pygame.Surface):
        """Рендеринг индикатора эмоций"""
        # Фон
        pygame.draw.rect(screen, (20, 20, 30), self.rect)
        pygame.draw.rect(screen, (60, 60, 80), self.rect, 2)
        
        # Заголовок
        title_font = pygame.font.Font(None, 20)
        title_surface = title_font.render("Эмоции", True, (255, 255, 255))
        screen.blit(title_surface, (self.rect.x + 10, self.rect.y + 10))
        
        # Эмоции
        y_offset = 40
        for emotion_name, intensity in self.emotions.items():
            if intensity > 0.1:  # Показываем только активные эмоции
                # Цвет эмоции
                emotion_colors = {
                    'happy': (255, 255, 0),
                    'sad': (0, 0, 255),
                    'angry': (255, 0, 0),
                    'fear': (128, 0, 128),
                    'surprise': (255, 165, 0),
                    'love': (255, 192, 203),
                    'curiosity': (0, 255, 255),
                    'confidence': (255, 215, 0)
                }
                
                color = emotion_colors.get(emotion_name, (128, 128, 128))
                
                # Индикатор
                indicator_rect = pygame.Rect(
                    self.rect.x + 10,
                    self.rect.y + y_offset,
                    int(100 * intensity),
                    15
                )
                
                # Пульсация
                pulse = 1.0 + 0.2 * math.sin(self.animation_time * 3)
                pulse_color = tuple(int(c * pulse) for c in color)
                
                pygame.draw.rect(screen, pulse_color, indicator_rect)
                pygame.draw.rect(screen, (100, 100, 100), indicator_rect, 1)
                
                # Текст
                font = pygame.font.Font(None, 16)
                text_surface = font.render(emotion_name, True, (255, 255, 255))
                screen.blit(text_surface, (indicator_rect.right + 10, indicator_rect.y))
                
                y_offset += 25


class ModernHUD:
    """Современный HUD"""
    
    def __init__(self, screen: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        self.screen = screen
        self.fonts = fonts
        self.panels: Dict[HUDPanelType, HUDPanel] = {}
        self.buttons: List[ModernButton] = []
        self.progress_bars: Dict[str, ModernProgressBar] = {}
        self.emotion_indicator = None
        
        # Состояние
        self.visible = True
        self.alpha = 255
        
        # Данные
        self.player_data = {}
        self.game_stats = {}
        self.emotions = {}
        
        # Создание панелей
        self._create_panels()
        self._create_ui_elements()
        
        logger.info("Современный HUD инициализирован")
    
    def _create_panels(self):
        """Создание панелей HUD"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # Статус панель (левая верхняя)
        self.panels[HUDPanelType.STATUS] = HUDPanel(
            panel_type=HUDPanelType.STATUS,
            rect=pygame.Rect(10, 10, 300, 200),
            title="Статус",
            background_color=(20, 30, 40),
            border_color=(60, 80, 100)
        )
        
        # Инвентарь (правая верхняя)
        self.panels[HUDPanelType.INVENTORY] = HUDPanel(
            panel_type=HUDPanelType.INVENTORY,
            rect=pygame.Rect(screen_width - 310, 10, 300, 200),
            title="Инвентарь",
            background_color=(30, 20, 40),
            border_color=(80, 60, 100)
        )
        
        # Эмоции (левая нижняя)
        emotion_rect = pygame.Rect(10, screen_height - 210, 300, 200)
        self.panels[HUDPanelType.EMOTIONS] = HUDPanel(
            panel_type=HUDPanelType.EMOTIONS,
            rect=emotion_rect,
            title="Эмоции",
            background_color=(40, 20, 30),
            border_color=(100, 60, 80)
        )
        
        # Индикатор эмоций
        self.emotion_indicator = EmotionIndicator(emotion_rect)
        
        # Генетика (правая нижняя)
        self.panels[HUDPanelType.GENETICS] = HUDPanel(
            panel_type=HUDPanelType.GENETICS,
            rect=pygame.Rect(screen_width - 310, screen_height - 210, 300, 200),
            title="Генетика",
            background_color=(20, 40, 30),
            border_color=(60, 100, 80)
        )
        
        # Мини-карта (правый верхний угол)
        minimap_size = 150
        self.panels[HUDPanelType.MINIMAP] = HUDPanel(
            panel_type=HUDPanelType.MINIMAP,
            rect=pygame.Rect(screen_width - minimap_size - 10, 220, minimap_size, minimap_size),
            title="Карта",
            background_color=(15, 15, 25),
            border_color=(50, 50, 70)
        )
    
    def _create_ui_elements(self):
        """Создание UI элементов"""
        # Кнопки управления
        button_width = 80
        button_height = 30
        button_y = self.screen.get_height() - 40
        
        # Кнопка инвентаря
        self.buttons.append(ModernButton(
            pygame.Rect(10, button_y, button_width, button_height),
            "Инвентарь",
            lambda: self._toggle_panel(HUDPanelType.INVENTORY),
            (60, 60, 80)
        ))
        
        # Кнопка эмоций
        self.buttons.append(ModernButton(
            pygame.Rect(100, button_y, button_width, button_height),
            "Эмоции",
            lambda: self._toggle_panel(HUDPanelType.EMOTIONS),
            (80, 60, 80)
        ))
        
        # Кнопка генетики
        self.buttons.append(ModernButton(
            pygame.Rect(190, button_y, button_width, button_height),
            "Генетика",
            lambda: self._toggle_panel(HUDPanelType.GENETICS),
            (60, 80, 60)
        ))
        
        # Полосы прогресса
        status_panel = self.panels[HUDPanelType.STATUS]
        
        # Здоровье
        self.progress_bars['health'] = ModernProgressBar(
            pygame.Rect(status_panel.rect.x + 10, status_panel.rect.y + 40, 200, 20),
            max_value=100.0,
            current_value=100.0,
            color=(255, 50, 50)
        )
        
        # Энергия
        self.progress_bars['energy'] = ModernProgressBar(
            pygame.Rect(status_panel.rect.x + 10, status_panel.rect.y + 70, 200, 20),
            max_value=100.0,
            current_value=100.0,
            color=(50, 150, 255)
        )
        
        # Опыт
        self.progress_bars['experience'] = ModernProgressBar(
            pygame.Rect(status_panel.rect.x + 10, status_panel.rect.y + 100, 200, 20),
            max_value=100.0,
            current_value=0.0,
            color=(255, 215, 0)
        )
        
        # Уровень
        self.progress_bars['level'] = ModernProgressBar(
            pygame.Rect(status_panel.rect.x + 10, status_panel.rect.y + 130, 200, 20),
            max_value=100.0,
            current_value=1.0,
            color=(150, 50, 255)
        )
    
    def _toggle_panel(self, panel_type: HUDPanelType):
        """Переключение видимости панели"""
        if panel_type in self.panels:
            self.panels[panel_type].visible = not self.panels[panel_type].visible
    
    def update(self, delta_time: float):
        """Обновление HUD"""
        # Обновление кнопок
        for button in self.buttons:
            button.update(delta_time)
        
        # Обновление полос прогресса
        for progress_bar in self.progress_bars.values():
            progress_bar.update(delta_time)
        
        # Обновление индикатора эмоций
        if self.emotion_indicator:
            self.emotion_indicator.update(delta_time)
    
    def handle_event(self, event: pygame.event.Event):
        """Обработка событий"""
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False
    
    def update_player_data(self, player_data: Dict[str, Any]):
        """Обновление данных игрока"""
        self.player_data = player_data
        
        # Обновление полос прогресса
        if 'health' in player_data:
            self.progress_bars['health'].set_value(player_data['health'])
        
        if 'energy' in player_data:
            self.progress_bars['energy'].set_value(player_data['energy'])
        
        if 'experience' in player_data:
            self.progress_bars['experience'].set_value(player_data['experience'])
        
        if 'level' in player_data:
            self.progress_bars['level'].set_value(player_data['level'])
    
    def update_emotions(self, emotions: Dict[str, float]):
        """Обновление эмоций"""
        self.emotions = emotions
        if self.emotion_indicator:
            self.emotion_indicator.update_emotions(emotions)
    
    def update_game_stats(self, stats: Dict[str, Any]):
        """Обновление игровой статистики"""
        self.game_stats = stats
    
    def render(self):
        """Рендеринг HUD"""
        if not self.visible:
            return
        
        # Рендеринг панелей
        for panel in self.panels.values():
            if panel.visible:
                self._render_panel(panel)
        
        # Рендеринг полос прогресса
        for progress_bar in self.progress_bars.values():
            progress_bar.render(self.screen)
        
        # Рендеринг индикатора эмоций
        if self.emotion_indicator:
            self.emotion_indicator.render(self.screen)
        
        # Рендеринг кнопок
        for button in self.buttons:
            button.render(self.screen, self.fonts.get('small', None))
        
        # Рендеринг текста
        self._render_text()
    
    def _render_panel(self, panel: HUDPanel):
        """Рендеринг панели"""
        # Фон
        pygame.draw.rect(self.screen, panel.background_color, panel.rect)
        pygame.draw.rect(self.screen, panel.border_color, panel.rect, 2)
        
        # Заголовок
        if panel.title and 'small' in self.fonts:
            title_surface = self.fonts['small'].render(panel.title, True, panel.title_color)
            self.screen.blit(title_surface, (panel.rect.x + 10, panel.rect.y + 10))
    
    def _render_text(self):
        """Рендеринг текста"""
        if 'small' not in self.fonts:
            return
        
        font = self.fonts['small']
        
        # Статус панель
        status_panel = self.panels[HUDPanelType.STATUS]
        
        # Здоровье
        health_text = f"Здоровье: {int(self.progress_bars['health'].current_value)}"
        health_surface = font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (status_panel.rect.x + 220, status_panel.rect.y + 45))
        
        # Энергия
        energy_text = f"Энергия: {int(self.progress_bars['energy'].current_value)}"
        energy_surface = font.render(energy_text, True, (255, 255, 255))
        self.screen.blit(energy_surface, (status_panel.rect.x + 220, status_panel.rect.y + 75))
        
        # Опыт
        exp_text = f"Опыт: {int(self.progress_bars['experience'].current_value)}%"
        exp_surface = font.render(exp_text, True, (255, 255, 255))
        self.screen.blit(exp_surface, (status_panel.rect.x + 220, status_panel.rect.y + 105))
        
        # Уровень
        level_text = f"Уровень: {int(self.progress_bars['level'].current_value)}"
        level_surface = font.render(level_text, True, (255, 255, 255))
        self.screen.blit(level_surface, (status_panel.rect.x + 220, status_panel.rect.y + 135))
        
        # Игровая статистика
        if self.game_stats:
            stats_panel = self.panels[HUDPanelType.INVENTORY]
            y_offset = 40
            
            for key, value in self.game_stats.items():
                if isinstance(value, (int, float)):
                    stat_text = f"{key}: {value}"
                    stat_surface = font.render(stat_text, True, (255, 255, 255))
                    self.screen.blit(stat_surface, (stats_panel.rect.x + 10, stats_panel.rect.y + y_offset))
                    y_offset += 20


# Глобальный экземпляр HUD
modern_hud: Optional[ModernHUD] = None


def create_modern_hud(screen: pygame.Surface, fonts: Dict[str, pygame.font.Font]) -> ModernHUD:
    """Создание современного HUD"""
    global modern_hud
    modern_hud = ModernHUD(screen, fonts)
    return modern_hud


def get_modern_hud() -> Optional[ModernHUD]:
    """Получение глобального экземпляра HUD"""
    return modern_hud

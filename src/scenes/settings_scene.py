#!/usr/bin/env python3
"""
Settings Scene - Сцена настроек
Отвечает только за отображение и изменение настроек игры
"""

import logging
import pygame
import math
from typing import List, Optional, Dict, Any
from ..core.scene_manager import Scene

logger = logging.getLogger(__name__)

class SettingsScene(Scene):
    """Сцена настроек"""
    
    def __init__(self):
        super().__init__("settings")
        
        # UI элементы
        self.buttons: List[dict] = []
        self.selected_button = 0
        self.settings_options: List[dict] = []
        self.selected_option = 0
        
        # Графика
        self.background: Optional[pygame.Surface] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.button_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        
        # Анимация
        self.animation_timer = 0.0
        
        # Цвета
        self.colors = {
            'background': (30, 30, 50),
            'title': (255, 255, 255),
            'button_normal': (80, 80, 120),
            'button_selected': (120, 120, 180),
            'button_text': (255, 255, 255),
            'button_text_selected': (255, 255, 0),
            'option_normal': (60, 60, 100),
            'option_selected': (100, 100, 140),
            'text': (200, 200, 200)
        }
        
        logger.info("Сцена настроек создана")
    
    def initialize(self) -> bool:
        """Инициализация сцены настроек"""
        try:
            logger.info("Инициализация сцены настроек...")
            
            # Создание шрифтов
            self._create_fonts()
            
            # Создание кнопок
            self._create_buttons()
            
            # Создание опций настроек
            self._create_settings_options()
            
            # Создание фона
            self._create_background()
            
            self.initialized = True
            logger.info("Сцена настроек успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцены настроек: {e}")
            return False
    
    def _create_fonts(self):
        """Создание шрифтов"""
        try:
            self.title_font = pygame.font.Font(None, 56)
            self.button_font = pygame.font.Font(None, 32)
            self.text_font = pygame.font.Font(None, 24)
            logger.debug("Шрифты созданы")
        except Exception as e:
            logger.warning(f"Не удалось создать шрифты: {e}")
            self.title_font = pygame.font.SysFont(None, 56)
            self.button_font = pygame.font.SysFont(None, 32)
            self.text_font = pygame.font.SysFont(None, 24)
    
    def _create_buttons(self):
        """Создание кнопок"""
        button_configs = [
            {"text": "Применить", "action": "apply"},
            {"text": "Сбросить", "action": "reset"},
            {"text": "Назад", "action": "back"}
        ]
        
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = 700
        
        for i, config in enumerate(button_configs):
            button = {
                "text": config["text"],
                "action": config["action"],
                "rect": pygame.Rect(
                    200 + i * (button_width + button_spacing),
                    start_y,
                    button_width,
                    button_height
                ),
                "selected": False
            }
            self.buttons.append(button)
    
    def _create_settings_options(self):
        """Создание опций настроек"""
        self.settings_options = [
            {
                "name": "Разрешение экрана",
                "type": "select",
                "options": ["1024x768", "1280x720", "1600x900", "1920x1080"],
                "current": 2,
                "key": "resolution"
            },
            {
                "name": "Полноэкранный режим",
                "type": "toggle",
                "value": False,
                "key": "fullscreen"
            },
            {
                "name": "Громкость музыки",
                "type": "slider",
                "value": 0.7,
                "min": 0.0,
                "max": 1.0,
                "key": "music_volume"
            },
            {
                "name": "Громкость звуков",
                "type": "slider",
                "value": 0.8,
                "min": 0.0,
                "max": 1.0,
                "key": "sound_volume"
            },
            {
                "name": "Качество графики",
                "type": "select",
                "options": ["Низкое", "Среднее", "Высокое", "Ультра"],
                "current": 2,
                "key": "graphics_quality"
            },
            {
                "name": "Вертикальная синхронизация",
                "type": "toggle",
                "value": True,
                "key": "vsync"
            }
        ]
    
    def _create_background(self):
        """Создание фона"""
        try:
            self.background = pygame.Surface((1600, 900))
            self.background.fill(self.colors['background'])
            
            # Добавляем декоративные элементы
            for i in range(50):
                x = i * 40
                y = 50 + (i % 3) * 20
                color = (40, 40, 60)
                pygame.draw.circle(self.background, color, (x, y), 3)
                
        except Exception as e:
            logger.warning(f"Не удалось создать фон: {e}")
            self.background = None
    
    def update(self, delta_time: float):
        """Обновление сцены настроек"""
        self.animation_timer += delta_time
        
        # Обновление состояния кнопок
        self._update_buttons()
    
    def _update_buttons(self):
        """Обновление состояния кнопок"""
        mouse_pos = pygame.mouse.get_pos()
        
        for i, button in enumerate(self.buttons):
            button["selected"] = (i == self.selected_button or 
                                button["rect"].collidepoint(mouse_pos))
    
    def render(self, screen: pygame.Surface):
        """Отрисовка сцены настроек"""
        # Отрисовка фона
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(self.colors['background'])
        
        # Отрисовка заголовка
        self._render_title(screen)
        
        # Отрисовка опций настроек
        self._render_settings_options(screen)
        
        # Отрисовка кнопок
        self._render_buttons(screen)
        
        # Отрисовка инструкций
        self._render_instructions(screen)
    
    def _render_title(self, screen: pygame.Surface):
        """Отрисовка заголовка"""
        if not self.title_font:
            return
        
        title_text = "НАСТРОЙКИ"
        title_surface = self.title_font.render(title_text, True, self.colors['title'])
        title_rect = title_surface.get_rect()
        title_rect.centerx = 800
        title_rect.y = 50
        
        screen.blit(title_surface, title_rect)
    
    def _render_settings_options(self, screen: pygame.Surface):
        """Отрисовка опций настроек"""
        if not self.text_font or not self.button_font:
            return
        
        start_y = 150
        option_height = 80
        
        for i, option in enumerate(self.settings_options):
            y = start_y + i * option_height
            selected = (i == self.selected_option)
            
            # Фон опции
            bg_color = self.colors['option_selected'] if selected else self.colors['option_normal']
            pygame.draw.rect(screen, bg_color, (100, y, 1400, option_height - 10))
            
            # Название опции
            name_surface = self.button_font.render(option["name"], True, self.colors['text'])
            screen.blit(name_surface, (120, y + 10))
            
            # Значение опции
            if option["type"] == "toggle":
                value_text = "ВКЛ" if option["value"] else "ВЫКЛ"
                color = (0, 255, 0) if option["value"] else (255, 0, 0)
            elif option["type"] == "select":
                value_text = option["options"][option["current"]]
                color = self.colors['text']
            elif option["type"] == "slider":
                value_text = f"{int(option['value'] * 100)}%"
                color = self.colors['text']
                
                # Отрисовка слайдера
                slider_x = 1200
                slider_y = y + 25
                slider_width = 200
                slider_height = 20
                
                # Фон слайдера
                pygame.draw.rect(screen, (50, 50, 50), (slider_x, slider_y, slider_width, slider_height))
                
                # Заполнение слайдера
                fill_width = int(slider_width * option["value"])
                pygame.draw.rect(screen, (0, 150, 255), (slider_x, slider_y, fill_width, slider_height))
                
                # Ползунок
                handle_x = slider_x + fill_width - 5
                pygame.draw.circle(screen, (255, 255, 255), (handle_x, slider_y + slider_height // 2), 8)
            
            if option["type"] != "slider":
                value_surface = self.text_font.render(value_text, True, color)
                screen.blit(value_surface, (1200, y + 20))
    
    def _render_buttons(self, screen: pygame.Surface):
        """Отрисовка кнопок"""
        if not self.button_font:
            return
        
        for button in self.buttons:
            if button["selected"]:
                button_color = self.colors['button_selected']
                text_color = self.colors['button_text_selected']
            else:
                button_color = self.colors['button_normal']
                text_color = self.colors['button_text']
            
            # Отрисовка фона кнопки
            pygame.draw.rect(screen, button_color, button["rect"])
            pygame.draw.rect(screen, (255, 255, 255), button["rect"], 2)
            
            # Отрисовка текста кнопки
            text_surface = self.button_font.render(button["text"], True, text_color)
            text_rect = text_surface.get_rect()
            text_rect.center = button["rect"].center
            
            screen.blit(text_surface, text_rect)
    
    def _render_instructions(self, screen: pygame.Surface):
        """Отрисовка инструкций"""
        if not self.text_font:
            return
        
        instructions = [
            "Используйте стрелки ↑↓ для навигации по опциям",
            "← → для изменения значений, Enter для переключения",
            "Tab для перехода к кнопкам, ESC для возврата"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_surface = self.text_font.render(instruction, True, (150, 150, 150))
            instruction_rect = instruction_surface.get_rect()
            instruction_rect.centerx = 800
            instruction_rect.y = 820 + i * 25
            
            screen.blit(instruction_surface, instruction_rect)
    
    def handle_event(self, event: pygame.event.Event):
        """Обработка событий"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event)
    
    def _handle_keydown(self, event: pygame.event.Event):
        """Обработка нажатий клавиш"""
        if event.key == pygame.K_ESCAPE:
            self._request_scene_change("menu")
        elif event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.settings_options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.settings_options)
        elif event.key == pygame.K_LEFT:
            self._change_option_value(-1)
        elif event.key == pygame.K_RIGHT:
            self._change_option_value(1)
        elif event.key == pygame.K_RETURN:
            self._toggle_option()
        elif event.key == pygame.K_TAB:
            # Переключение на кнопки
            self.selected_button = (self.selected_button + 1) % len(self.buttons)
    
    def _handle_mouse_click(self, event: pygame.event.Event):
        """Обработка кликов мыши"""
        if event.button == 1:  # Левый клик
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клик по кнопкам
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    self._execute_button_action(button["action"])
                    break
            
            # Проверяем клик по опциям
            start_y = 150
            option_height = 80
            
            for i, option in enumerate(self.settings_options):
                y = start_y + i * option_height
                if 100 <= mouse_pos[0] <= 1500 and y <= mouse_pos[1] <= y + option_height:
                    self.selected_option = i
                    if option["type"] == "toggle":
                        self._toggle_option()
                    break
    
    def _handle_mouse_motion(self, event: pygame.event.Event):
        """Обработка движения мыши"""
        pass
    
    def _change_option_value(self, direction: int):
        """Изменение значения опции"""
        if self.selected_option >= len(self.settings_options):
            return
        
        option = self.settings_options[self.selected_option]
        
        if option["type"] == "select":
            option["current"] = (option["current"] + direction) % len(option["options"])
        elif option["type"] == "slider":
            step = 0.1
            option["value"] = max(option["min"], min(option["max"], option["value"] + direction * step))
    
    def _toggle_option(self):
        """Переключение опции"""
        if self.selected_option >= len(self.settings_options):
            return
        
        option = self.settings_options[self.selected_option]
        
        if option["type"] == "toggle":
            option["value"] = not option["value"]
    
    def _execute_button_action(self, action: str):
        """Выполнение действия кнопки"""
        logger.info(f"Выполняется действие настроек: {action}")
        
        if action == "apply":
            self._apply_settings()
        elif action == "reset":
            self._reset_settings()
        elif action == "back":
            self._request_scene_change("menu")
    
    def _apply_settings(self):
        """Применение настроек"""
        logger.info("Настройки применены")
        # Здесь будет логика применения настроек
        
    def _reset_settings(self):
        """Сброс настроек"""
        logger.info("Настройки сброшены к значениям по умолчанию")
        # Здесь будет логика сброса настроек
        self._create_settings_options()  # Пересоздаем с дефолтными значениями
    
    def _request_scene_change(self, scene_name: str):
        """Запрос на смену сцены"""
        if self.scene_manager:
            logger.info(f"Запрошен переход к сцене: {scene_name}")
            self.scene_manager.switch_to_scene(scene_name, "instant")
        else:
            logger.warning(f"SceneManager недоступен для смены сцены на {scene_name}")
    
    def cleanup(self):
        """Очистка ресурсов сцены настроек"""
        logger.info("Очистка сцены настроек...")
        
        # Очистка графических ресурсов
        self.background = None
        self.title_font = None
        self.button_font = None
        self.text_font = None
        
        # Очистка кнопок и опций
        self.buttons.clear()
        self.settings_options.clear()
        
        super().cleanup()
        logger.info("Сцена настроек очищена")

#!/usr/bin/env python3
"""
Menu Scene - Сцена главного меню
Отвечает только за отображение и взаимодействие с главным меню
"""

import logging
import pygame
from typing import List, Optional
from ..core.scene_manager import Scene

logger = logging.getLogger(__name__)

class MenuScene(Scene):
    """Сцена главного меню"""
    
    def __init__(self):
        super().__init__("menu")
        
        # UI элементы
        self.buttons: List[dict] = []
        self.selected_button = 0
        
        # Графика
        self.background: Optional[pygame.Surface] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.button_font: Optional[pygame.font.Font] = None
        
        # Анимация
        self.animation_timer = 0.0
        self.title_alpha = 255
        
        # Цвета
        self.colors = {
            'background': (20, 20, 40),
            'title': (255, 255, 255),
            'button_normal': (100, 100, 150),
            'button_selected': (150, 150, 200),
            'button_text': (255, 255, 255),
            'button_text_selected': (255, 255, 0)
        }
        
        logger.info("Сцена главного меню создана")
    
    def initialize(self) -> bool:
        """Инициализация сцены меню"""
        try:
            logger.info("Инициализация сцены главного меню...")
            
            # Создание шрифтов
            self._create_fonts()
            
            # Создание кнопок
            self._create_buttons()
            
            # Создание фона
            self._create_background()
            
            self.initialized = True
            logger.info("Сцена главного меню успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцены меню: {e}")
            return False
    
    def _create_fonts(self):
        """Создание шрифтов"""
        try:
            # Основной шрифт для заголовка
            self.title_font = pygame.font.Font(None, 72)
            
            # Шрифт для кнопок
            self.button_font = pygame.font.Font(None, 36)
            
            logger.debug("Шрифты созданы")
            
        except Exception as e:
            logger.warning(f"Не удалось создать шрифты: {e}")
            # Используем системные шрифты
            self.title_font = pygame.font.SysFont(None, 72)
            self.button_font = pygame.font.SysFont(None, 36)
    
    def _create_buttons(self):
        """Создание кнопок меню"""
        button_configs = [
            {"text": "Новая игра", "action": "new_game"},
            {"text": "Загрузить игру", "action": "load_game"},
            {"text": "Настройки", "action": "settings"},
            {"text": "Об игре", "action": "about"},
            {"text": "Выход", "action": "quit"}
        ]
        
        button_width = 300
        button_height = 50
        button_spacing = 20
        start_y = 300
        
        for i, config in enumerate(button_configs):
            button = {
                "text": config["text"],
                "action": config["action"],
                "rect": pygame.Rect(
                    800 - button_width // 2,  # Центрируем по горизонтали
                    start_y + i * (button_height + button_spacing),
                    button_width,
                    button_height
                ),
                "hover": False
            }
            self.buttons.append(button)
        
        logger.debug(f"Создано {len(self.buttons)} кнопок")
    
    def _create_background(self):
        """Создание фона меню"""
        try:
            # Создаем градиентный фон
            self.background = pygame.Surface((1600, 900))
            
            # Градиент от темно-синего к черному
            for y in range(900):
                alpha = int(255 * (1 - y / 900))
                color = (20, 20, 40 + alpha // 10)
                pygame.draw.line(self.background, color, (0, y), (1600, y))
            
            logger.debug("Фон меню создан")
            
        except Exception as e:
            logger.warning(f"Не удалось создать фон: {e}")
            self.background = None
    
    def update(self, delta_time: float):
        """Обновление сцены меню"""
        # Обновление анимации
        self.animation_timer += delta_time
        
        # Пульсация заголовка
        import math
        self.title_alpha = 200 + int(55 * (1 + math.sin(self.animation_timer * 2) / 2))
        
        # Обновление состояния кнопок
        self._update_buttons()
    
    def _update_buttons(self):
        """Обновление состояния кнопок"""
        mouse_pos = pygame.mouse.get_pos()
        
        for i, button in enumerate(self.buttons):
            # Проверка наведения мыши
            button["hover"] = button["rect"].collidepoint(mouse_pos)
            
            # Если мышь на кнопке, выбираем её
            if button["hover"]:
                self.selected_button = i
    
    def render(self, screen: pygame.Surface):
        """Отрисовка сцены меню"""
        # Отрисовка фона
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(self.colors['background'])
        
        # Отрисовка заголовка
        self._render_title(screen)
        
        # Отрисовка кнопок
        self._render_buttons(screen)
        
        # Отрисовка дополнительной информации
        self._render_info(screen)
    
    def _render_title(self, screen: pygame.Surface):
        """Отрисовка заголовка"""
        if not self.title_font:
            return
        
        title_text = "AI-EVOLVE Enhanced Edition"
        title_surface = self.title_font.render(title_text, True, self.colors['title'])
        
        # Простая пульсация без альфа-канала
        pass
        
        # Центрируем заголовок
        title_rect = title_surface.get_rect()
        title_rect.centerx = 800
        title_rect.centery = 150
        
        screen.blit(title_surface, title_rect)
    
    def _render_buttons(self, screen: pygame.Surface):
        """Отрисовка кнопок"""
        if not self.button_font:
            return
        
        for i, button in enumerate(self.buttons):
            # Выбор цвета кнопки
            if i == self.selected_button or button["hover"]:
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
    
    def _render_info(self, screen: pygame.Surface):
        """Отрисовка дополнительной информации"""
        if not self.button_font:
            return
        
        # Версия игры
        version_text = "v2.0.0 - Enhanced Edition"
        version_surface = self.button_font.render(version_text, True, (150, 150, 150))
        version_rect = version_surface.get_rect()
        version_rect.bottomright = (1580, 880)
        
        screen.blit(version_surface, version_rect)
        
        # Инструкции
        instructions = [
            "Используйте мышь или стрелки для навигации",
            "Enter для выбора, ESC для возврата"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_surface = self.button_font.render(instruction, True, (100, 100, 100))
            instruction_rect = instruction_surface.get_rect()
            instruction_rect.bottomleft = (20, 880 - (len(instructions) - 1 - i) * 25)
            
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
        if event.key == pygame.K_UP:
            self.selected_button = (self.selected_button - 1) % len(self.buttons)
        elif event.key == pygame.K_DOWN:
            self.selected_button = (self.selected_button + 1) % len(self.buttons)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self._execute_button_action(self.buttons[self.selected_button]["action"])
        elif event.key == pygame.K_ESCAPE:
            self._execute_button_action("quit")
    
    def _handle_mouse_click(self, event: pygame.event.Event):
        """Обработка кликов мыши"""
        if event.button == 1:  # Левый клик
            mouse_pos = pygame.mouse.get_pos()
            
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    self._execute_button_action(button["action"])
                    break
    
    def _handle_mouse_motion(self, event: pygame.event.Event):
        """Обработка движения мыши"""
        # Обновление состояния кнопок уже происходит в update()
        pass
    
    def _execute_button_action(self, action: str):
        """Выполнение действия кнопки"""
        logger.info(f"Выполняется действие: {action}")
        
        if action == "new_game":
            # Переход к игровой сцене
            self._request_scene_change("game")
        elif action == "load_game":
            # Переход к загрузке игры
            self._request_scene_change("load_game")
        elif action == "settings":
            # Переход к настройкам
            self._request_scene_change("settings")
        elif action == "about":
            # Показать информацию об игре
            self._show_about_info()
        elif action == "quit":
            # Выход из игры
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def _request_scene_change(self, scene_name: str):
        """Запрос на смену сцены"""
        if self.scene_manager:
            logger.info(f"Запрошен переход к сцене: {scene_name}")
            self.scene_manager.switch_to_scene(scene_name, "instant")
        else:
            logger.warning(f"SceneManager недоступен для смены сцены на {scene_name}")
    
    def _show_about_info(self):
        """Показать информацию об игре"""
        logger.info("Показана информация об игре")
        # Здесь можно добавить модальное окно с информацией
    
    def cleanup(self):
        """Очистка ресурсов сцены"""
        logger.info("Очистка сцены главного меню...")
        
        # Очистка графических ресурсов
        self.background = None
        self.title_font = None
        self.button_font = None
        
        # Очистка кнопок
        self.buttons.clear()
        
        super().cleanup()
        logger.info("Сцена главного меню очищена")

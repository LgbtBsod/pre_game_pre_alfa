#!/usr/bin/env python3
"""
Pause Scene - Сцена паузы
Отвечает только за отображение меню паузы и управление им
"""

import logging
import pygame
from typing import List, Optional
from ..core.scene_manager import Scene

logger = logging.getLogger(__name__)

class PauseScene(Scene):
    """Сцена паузы"""
    
    def __init__(self):
        super().__init__("pause")
        
        # UI элементы
        self.buttons: List[dict] = []
        self.selected_button = 0
        
        # Графика
        self.background: Optional[pygame.Surface] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.button_font: Optional[pygame.font.Font] = None
        
        # Анимация
        self.animation_timer = 0.0
        self.overlay_alpha = 128
        
        # Цвета
        self.colors = {
            'overlay': (0, 0, 0, 128),
            'title': (255, 255, 255),
            'button_normal': (100, 100, 150),
            'button_selected': (150, 150, 200),
            'button_text': (255, 255, 255),
            'button_text_selected': (255, 255, 0)
        }
        
        logger.info("Сцена паузы создана")
    
    def initialize(self) -> bool:
        """Инициализация сцены паузы"""
        try:
            logger.info("Инициализация сцены паузы...")
            
            # Создание шрифтов
            self._create_fonts()
            
            # Создание кнопок
            self._create_buttons()
            
            # Создание фона
            self._create_background()
            
            self.initialized = True
            logger.info("Сцена паузы успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцены паузы: {e}")
            return False
    
    def _create_fonts(self):
        """Создание шрифтов"""
        try:
            self.title_font = pygame.font.Font(None, 64)
            self.button_font = pygame.font.Font(None, 32)
            logger.debug("Шрифты созданы")
        except Exception as e:
            logger.warning(f"Не удалось создать шрифты: {e}")
            self.title_font = pygame.font.SysFont(None, 64)
            self.button_font = pygame.font.SysFont(None, 32)
    
    def _create_buttons(self):
        """Создание кнопок меню паузы"""
        button_configs = [
            {"text": "Продолжить", "action": "resume"},
            {"text": "Настройки", "action": "settings"},
            {"text": "Сохранить", "action": "save"},
            {"text": "Главное меню", "action": "main_menu"},
            {"text": "Выход", "action": "quit"}
        ]
        
        button_width = 300
        button_height = 50
        button_spacing = 20
        start_y = 350
        
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
        
        logger.debug(f"Создано {len(self.buttons)} кнопок паузы")
    
    def _create_background(self):
        """Создание фона паузы"""
        try:
            # Создаем полупрозрачный оверлей
            self.background = pygame.Surface((1600, 900), pygame.SRCALPHA)
            self.background.fill((0, 0, 0, 128))
            
            logger.debug("Фон паузы создан")
            
        except Exception as e:
            logger.warning(f"Не удалось создать фон паузы: {e}")
            self.background = None
    
    def update(self, delta_time: float):
        """Обновление сцены паузы"""
        # Обновление анимации
        self.animation_timer += delta_time
        
        # Пульсация оверлея
        import math
        self.overlay_alpha = 100 + int(28 * (1 + math.sin(self.animation_timer * 3) / 2))
        
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
        """Отрисовка сцены паузы"""
        # Отрисовка полупрозрачного оверлея
        if self.background:
            # Обновляем альфа-канал
            overlay = pygame.Surface((1600, 900), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.overlay_alpha))
            screen.blit(overlay, (0, 0))
        else:
            # Fallback - простой оверлей
            overlay = pygame.Surface((1600, 900), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
        
        # Отрисовка заголовка
        self._render_title(screen)
        
        # Отрисовка кнопок
        self._render_buttons(screen)
        
        # Отрисовка дополнительной информации
        self._render_info(screen)
    
    def _render_title(self, screen: pygame.Surface):
        """Отрисовка заголовка паузы"""
        if not self.title_font:
            return
        
        title_text = "ПАУЗА"
        title_surface = self.title_font.render(title_text, True, self.colors['title'])
        
        # Центрируем заголовок
        title_rect = title_surface.get_rect()
        title_rect.centerx = 800
        title_rect.centery = 200
        
        screen.blit(title_surface, title_rect)
    
    def _render_buttons(self, screen: pygame.Surface):
        """Отрисовка кнопок паузы"""
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
        
        # Инструкции
        instructions = [
            "ESC - Продолжить игру",
            "Стрелки - Навигация по меню",
            "Enter - Выбор"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_surface = self.button_font.render(instruction, True, (150, 150, 150))
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
        if event.key == pygame.K_ESCAPE:
            self._execute_button_action("resume")
        elif event.key == pygame.K_UP:
            self.selected_button = (self.selected_button - 1) % len(self.buttons)
        elif event.key == pygame.K_DOWN:
            self.selected_button = (self.selected_button + 1) % len(self.buttons)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self._execute_button_action(self.buttons[self.selected_button]["action"])
    
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
        logger.info(f"Выполняется действие паузы: {action}")
        
        if action == "resume":
            # Возврат к игре
            self._request_scene_change("game")
        elif action == "settings":
            # Переход к настройкам
            self._request_scene_change("settings")
        elif action == "save":
            # Сохранение игры
            self._save_game()
        elif action == "main_menu":
            # Переход в главное меню
            self._request_scene_change("menu")
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
    
    def _save_game(self):
        """Сохранение игры"""
        logger.info("Запрошено сохранение игры")
        # Здесь можно добавить логику сохранения
    
    def cleanup(self):
        """Очистка ресурсов сцены паузы"""
        logger.info("Очистка сцены паузы...")
        
        # Очистка графических ресурсов
        self.background = None
        self.title_font = None
        self.button_font = None
        
        # Очистка кнопок
        self.buttons.clear()
        
        super().cleanup()
        logger.info("Сцена паузы очищена")

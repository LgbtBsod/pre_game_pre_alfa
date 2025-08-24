#!/usr/bin/env python3
"""
Load Scene - Сцена загрузки игры
Отвечает только за загрузку сохраненных игр
"""

import logging
import pygame
import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..core.scene_manager import Scene

logger = logging.getLogger(__name__)

class LoadScene(Scene):
    """Сцена загрузки игры"""
    
    def __init__(self):
        super().__init__("load_game")
        
        # UI элементы
        self.buttons: List[dict] = []
        self.selected_button = 0
        self.save_slots: List[dict] = []
        self.selected_slot = 0
        
        # Графика
        self.background: Optional[pygame.Surface] = None
        self.title_font: Optional[pygame.font.Font] = None
        self.button_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        
        # Анимация
        self.animation_timer = 0.0
        
        # Цвета
        self.colors = {
            'background': (20, 30, 40),
            'title': (255, 255, 255),
            'button_normal': (70, 80, 100),
            'button_selected': (100, 120, 150),
            'button_text': (255, 255, 255),
            'button_text_selected': (255, 255, 0),
            'slot_normal': (40, 50, 60),
            'slot_selected': (80, 100, 120),
            'slot_empty': (30, 30, 30),
            'text': (200, 200, 200),
            'text_dim': (120, 120, 120)
        }
        
        logger.info("Сцена загрузки создана")
    
    def initialize(self) -> bool:
        """Инициализация сцены загрузки"""
        try:
            logger.info("Инициализация сцены загрузки...")
            
            # Создание шрифтов
            self._create_fonts()
            
            # Создание кнопок
            self._create_buttons()
            
            # Загрузка сохранений
            self._load_save_slots()
            
            # Создание фона
            self._create_background()
            
            self.initialized = True
            logger.info("Сцена загрузки успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцены загрузки: {e}")
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
            {"text": "Загрузить", "action": "load"},
            {"text": "Удалить", "action": "delete"},
            {"text": "Назад", "action": "back"}
        ]
        
        button_width = 200
        button_height = 50
        button_spacing = 30
        start_x = 200
        start_y = 750
        
        for i, config in enumerate(button_configs):
            button = {
                "text": config["text"],
                "action": config["action"],
                "rect": pygame.Rect(
                    start_x + i * (button_width + button_spacing),
                    start_y,
                    button_width,
                    button_height
                ),
                "selected": False
            }
            self.buttons.append(button)
    
    def _load_save_slots(self):
        """Загрузка слотов сохранений"""
        self.save_slots = []
        saves_dir = "saves"
        
        # Создаем папку сохранений если её нет
        if not os.path.exists(saves_dir):
            os.makedirs(saves_dir)
        
        # Загружаем до 10 слотов сохранений
        for i in range(10):
            slot_file = os.path.join(saves_dir, f"save_slot_{i}.json")
            
            if os.path.exists(slot_file):
                try:
                    with open(slot_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    slot = {
                        "id": i,
                        "exists": True,
                        "name": save_data.get("save_name", f"Сохранение {i+1}"),
                        "level": save_data.get("player_level", 1),
                        "location": save_data.get("location", "Неизвестно"),
                        "playtime": save_data.get("playtime", 0),
                        "date": save_data.get("save_date", "Неизвестно"),
                        "screenshot": save_data.get("screenshot", None)
                    }
                    
                except Exception as e:
                    logger.warning(f"Не удалось загрузить сохранение {i}: {e}")
                    slot = {
                        "id": i,
                        "exists": False,
                        "name": f"Слот {i+1}",
                        "level": 0,
                        "location": "",
                        "playtime": 0,
                        "date": "",
                        "screenshot": None
                    }
            else:
                slot = {
                    "id": i,
                    "exists": False,
                    "name": f"Слот {i+1}",
                    "level": 0,
                    "location": "",
                    "playtime": 0,
                    "date": "",
                    "screenshot": None
                }
            
            self.save_slots.append(slot)
    
    def _create_background(self):
        """Создание фона"""
        try:
            self.background = pygame.Surface((1600, 900))
            self.background.fill(self.colors['background'])
            
            # Добавляем декоративную сетку
            for x in range(0, 1600, 100):
                pygame.draw.line(self.background, (30, 40, 50), (x, 0), (x, 900), 1)
            for y in range(0, 900, 100):
                pygame.draw.line(self.background, (30, 40, 50), (0, y), (1600, y), 1)
                
        except Exception as e:
            logger.warning(f"Не удалось создать фон: {e}")
            self.background = None
    
    def update(self, delta_time: float):
        """Обновление сцены загрузки"""
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
        """Отрисовка сцены загрузки"""
        # Отрисовка фона
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(self.colors['background'])
        
        # Отрисовка заголовка
        self._render_title(screen)
        
        # Отрисовка слотов сохранений
        self._render_save_slots(screen)
        
        # Отрисовка кнопок
        self._render_buttons(screen)
        
        # Отрисовка инструкций
        self._render_instructions(screen)
    
    def _render_title(self, screen: pygame.Surface):
        """Отрисовка заголовка"""
        if not self.title_font:
            return
        
        title_text = "ЗАГРУЗКА ИГРЫ"
        title_surface = self.title_font.render(title_text, True, self.colors['title'])
        title_rect = title_surface.get_rect()
        title_rect.centerx = 800
        title_rect.y = 50
        
        screen.blit(title_surface, title_rect)
    
    def _render_save_slots(self, screen: pygame.Surface):
        """Отрисовка слотов сохранений"""
        if not self.text_font or not self.button_font:
            return
        
        slots_per_row = 2
        slot_width = 600
        slot_height = 120
        slot_spacing_x = 50
        slot_spacing_y = 20
        start_x = 200
        start_y = 150
        
        for i, slot in enumerate(self.save_slots):
            row = i // slots_per_row
            col = i % slots_per_row
            
            x = start_x + col * (slot_width + slot_spacing_x)
            y = start_y + row * (slot_height + slot_spacing_y)
            
            selected = (i == self.selected_slot)
            
            # Фон слота
            if slot["exists"]:
                bg_color = self.colors['slot_selected'] if selected else self.colors['slot_normal']
            else:
                bg_color = self.colors['slot_empty']
            
            pygame.draw.rect(screen, bg_color, (x, y, slot_width, slot_height))
            pygame.draw.rect(screen, (100, 100, 100), (x, y, slot_width, slot_height), 2)
            
            if slot["exists"]:
                # Информация о сохранении
                name_surface = self.button_font.render(slot["name"], True, self.colors['text'])
                screen.blit(name_surface, (x + 10, y + 10))
                
                level_text = f"Уровень: {slot['level']}"
                level_surface = self.text_font.render(level_text, True, self.colors['text'])
                screen.blit(level_surface, (x + 10, y + 40))
                
                location_text = f"Локация: {slot['location']}"
                location_surface = self.text_font.render(location_text, True, self.colors['text'])
                screen.blit(location_surface, (x + 10, y + 60))
                
                # Время игры
                hours = slot['playtime'] // 3600
                minutes = (slot['playtime'] % 3600) // 60
                time_text = f"Время: {hours:02d}:{minutes:02d}"
                time_surface = self.text_font.render(time_text, True, self.colors['text'])
                screen.blit(time_surface, (x + 300, y + 40))
                
                # Дата сохранения
                date_surface = self.text_font.render(slot['date'], True, self.colors['text_dim'])
                screen.blit(date_surface, (x + 300, y + 60))
                
                # Миниатюра (заглушка)
                thumbnail_rect = pygame.Rect(x + 450, y + 10, 140, 100)
                pygame.draw.rect(screen, (60, 60, 60), thumbnail_rect)
                pygame.draw.rect(screen, (80, 80, 80), thumbnail_rect, 1)
                
                thumb_text = "Скриншот"
                thumb_surface = self.text_font.render(thumb_text, True, self.colors['text_dim'])
                thumb_rect = thumb_surface.get_rect(center=thumbnail_rect.center)
                screen.blit(thumb_surface, thumb_rect)
                
            else:
                # Пустой слот
                empty_text = "ПУСТОЙ СЛОТ"
                empty_surface = self.button_font.render(empty_text, True, self.colors['text_dim'])
                empty_rect = empty_surface.get_rect()
                empty_rect.center = (x + slot_width // 2, y + slot_height // 2)
                screen.blit(empty_surface, empty_rect)
    
    def _render_buttons(self, screen: pygame.Surface):
        """Отрисовка кнопок"""
        if not self.button_font:
            return
        
        for button in self.buttons:
            # Проверяем доступность кнопки
            enabled = True
            if button["action"] in ["load", "delete"]:
                enabled = (self.selected_slot < len(self.save_slots) and 
                          self.save_slots[self.selected_slot]["exists"])
            
            if button["selected"] and enabled:
                button_color = self.colors['button_selected']
                text_color = self.colors['button_text_selected']
            else:
                button_color = self.colors['button_normal']
                text_color = self.colors['button_text']
                
                if not enabled:
                    button_color = (50, 50, 50)
                    text_color = (100, 100, 100)
            
            # Отрисовка фона кнопки
            pygame.draw.rect(screen, button_color, button["rect"])
            pygame.draw.rect(screen, (150, 150, 150), button["rect"], 2)
            
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
            "Используйте стрелки для навигации по слотам сохранений",
            "Enter для загрузки, Delete для удаления, ESC для возврата"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_surface = self.text_font.render(instruction, True, (150, 150, 150))
            instruction_rect = instruction_surface.get_rect()
            instruction_rect.centerx = 800
            instruction_rect.y = 850 + i * 25
            
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
            if self.selected_slot >= 2:
                self.selected_slot -= 2
        elif event.key == pygame.K_DOWN:
            if self.selected_slot < len(self.save_slots) - 2:
                self.selected_slot += 2
        elif event.key == pygame.K_LEFT:
            if self.selected_slot % 2 == 1:
                self.selected_slot -= 1
        elif event.key == pygame.K_RIGHT:
            if self.selected_slot % 2 == 0 and self.selected_slot < len(self.save_slots) - 1:
                self.selected_slot += 1
        elif event.key == pygame.K_RETURN:
            self._execute_button_action("load")
        elif event.key == pygame.K_DELETE:
            self._execute_button_action("delete")
        elif event.key == pygame.K_TAB:
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
            
            # Проверяем клик по слотам
            slots_per_row = 2
            slot_width = 600
            slot_height = 120
            slot_spacing_x = 50
            slot_spacing_y = 20
            start_x = 200
            start_y = 150
            
            for i, slot in enumerate(self.save_slots):
                row = i // slots_per_row
                col = i % slots_per_row
                
                x = start_x + col * (slot_width + slot_spacing_x)
                y = start_y + row * (slot_height + slot_spacing_y)
                
                if x <= mouse_pos[0] <= x + slot_width and y <= mouse_pos[1] <= y + slot_height:
                    self.selected_slot = i
                    break
    
    def _handle_mouse_motion(self, event: pygame.event.Event):
        """Обработка движения мыши"""
        pass
    
    def _execute_button_action(self, action: str):
        """Выполнение действия кнопки"""
        logger.info(f"Выполняется действие загрузки: {action}")
        
        if action == "load":
            self._load_game()
        elif action == "delete":
            self._delete_save()
        elif action == "back":
            self._request_scene_change("menu")
    
    def _load_game(self):
        """Загрузка игры"""
        if (self.selected_slot < len(self.save_slots) and 
            self.save_slots[self.selected_slot]["exists"]):
            
            slot = self.save_slots[self.selected_slot]
            logger.info(f"Загрузка сохранения: {slot['name']}")
            
            # Здесь будет логика загрузки игры
            # Пока что просто переходим к игровой сцене
            self._request_scene_change("game")
        else:
            logger.warning("Попытка загрузить пустой слот")
    
    def _delete_save(self):
        """Удаление сохранения"""
        if (self.selected_slot < len(self.save_slots) and 
            self.save_slots[self.selected_slot]["exists"]):
            
            slot = self.save_slots[self.selected_slot]
            logger.info(f"Удаление сохранения: {slot['name']}")
            
            # Удаляем файл сохранения
            save_file = f"saves/save_slot_{slot['id']}.json"
            try:
                if os.path.exists(save_file):
                    os.remove(save_file)
                
                # Обновляем слот
                slot["exists"] = False
                slot["name"] = f"Слот {slot['id']+1}"
                slot["level"] = 0
                slot["location"] = ""
                slot["playtime"] = 0
                slot["date"] = ""
                slot["screenshot"] = None
                
            except Exception as e:
                logger.error(f"Ошибка удаления сохранения: {e}")
        else:
            logger.warning("Попытка удалить пустой слот")
    
    def _request_scene_change(self, scene_name: str):
        """Запрос на смену сцены"""
        if self.scene_manager:
            logger.info(f"Запрошен переход к сцене: {scene_name}")
            self.scene_manager.switch_to_scene(scene_name, "instant")
        else:
            logger.warning(f"SceneManager недоступен для смены сцены на {scene_name}")
    
    def cleanup(self):
        """Очистка ресурсов сцены загрузки"""
        logger.info("Очистка сцены загрузки...")
        
        # Очистка графических ресурсов
        self.background = None
        self.title_font = None
        self.button_font = None
        self.text_font = None
        
        # Очистка данных
        self.buttons.clear()
        self.save_slots.clear()
        
        super().cleanup()
        logger.info("Сцена загрузки очищена")

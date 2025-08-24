#!/usr/bin/env python3
"""
Game Engine - Основной игровой движок
Отвечает только за координацию всех систем и управление жизненным циклом игры
"""

import time
import logging
import pygame
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .config_manager import ConfigManager
from .game_state import GameState
from .scene_manager import SceneManager
from .resource_manager import ResourceManager
from .performance_manager import PerformanceManager

logger = logging.getLogger(__name__)

class GameEngine:
    """
    Основной игровой движок
    Координирует все системы и управляет жизненным циклом игры
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        self.paused = False
        
        # Pygame компоненты
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        
        # Менеджеры систем
        self.scene_manager: Optional[SceneManager] = None
        self.resource_manager: Optional[ResourceManager] = None
        self.performance_manager: Optional[PerformanceManager] = None
        
        # Состояние игры
        self.current_state = GameState.INITIALIZING
        self.delta_time = 0.0
        self.last_frame_time = time.time()
        
        # Статистика
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        logger.info("Игровой движок инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация игрового движка"""
        try:
            logger.info("Начало инициализации игрового движка...")
            
            # Инициализация Pygame
            if not self._initialize_pygame():
                return False
            
            # Инициализация менеджеров
            if not self._initialize_managers():
                return False
            
            # Инициализация сцен
            if not self._initialize_scenes():
                return False
            
            self.current_state = GameState.MAIN_MENU
            logger.info("Игровой движок успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации игрового движка: {e}")
            return False
    
    def _initialize_pygame(self) -> bool:
        """Инициализация Pygame"""
        try:
            pygame.init()
            
            # Настройка дисплея
            display_config = self.config.get('display', {})
            width = display_config.get('window_width', 1600)
            height = display_config.get('window_height', 900)
            fullscreen = display_config.get('fullscreen', False)
            
            flags = pygame.FULLSCREEN if fullscreen else pygame.DOUBLEBUF
            if display_config.get('vsync', True):
                flags |= pygame.HWSURFACE
            
            self.screen = pygame.display.set_mode((width, height), flags)
            pygame.display.set_caption("AI-EVOLVE Enhanced Edition")
            
            # Инициализация часов
            self.clock = pygame.time.Clock()
            
            logger.info("Pygame успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Pygame: {e}")
            return False
    
    def _initialize_managers(self) -> bool:
        """Инициализация менеджеров систем"""
        try:
            # Менеджер ресурсов
            self.resource_manager = ResourceManager()
            if not self.resource_manager.initialize():
                logger.error("Не удалось инициализировать менеджер ресурсов")
                return False
            
            # Менеджер производительности
            self.performance_manager = PerformanceManager()
            if not self.performance_manager.initialize():
                logger.error("Не удалось инициализировать менеджер производительности")
                return False
            
            # Менеджер сцен
            self.scene_manager = SceneManager(self.screen, self.resource_manager)
            if not self.scene_manager.initialize():
                logger.error("Не удалось инициализировать менеджер сцен")
                return False
            
            logger.info("Все менеджеры успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджеров: {e}")
            return False
    
    def _initialize_scenes(self) -> bool:
        """Инициализация игровых сцен"""
        try:
            # Создание основных сцен
            try:
                from scenes.menu_scene import MenuScene
                from scenes.game_scene import GameScene
                from scenes.pause_scene import PauseScene
            except ImportError:
                from src.scenes.menu_scene import MenuScene
                from src.scenes.game_scene import GameScene
                from src.scenes.pause_scene import PauseScene
            
            # Регистрация сцен
            self.scene_manager.register_scene("menu", MenuScene())
            self.scene_manager.register_scene("game", GameScene())
            self.scene_manager.register_scene("pause", PauseScene())
            
            # Установка начальной сцены
            self.scene_manager.set_active_scene("menu")
            
            logger.info("Сцены успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцен: {e}")
            return False
    
    def run(self):
        """Основной игровой цикл"""
        if not self.initialize():
            logger.error("Не удалось инициализировать игровой движок")
            return
        
        self.running = True
        logger.info("Запуск игрового цикла")
        
        try:
            while self.running:
                # Обработка событий
                self._handle_events()
                
                # Обновление состояния
                if not self.paused:
                    self._update()
                
                # Отрисовка
                self._render()
                
                # Управление FPS
                self._limit_fps()
                
                # Обновление статистики
                self._update_stats()
                
        except Exception as e:
            logger.error(f"Критическая ошибка в игровом цикле: {e}")
            self._handle_critical_error(e)
        
        finally:
            self._cleanup()
    
    def _handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._toggle_pause()
                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()
            
            # Передача события в активную сцену
            if self.scene_manager and self.scene_manager.active_scene:
                self.scene_manager.active_scene.handle_event(event)
    
    def _update(self):
        """Обновление состояния игры"""
        current_time = time.time()
        self.delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Обновление активной сцены
        if self.scene_manager and self.scene_manager.active_scene:
            self.scene_manager.active_scene.update(self.delta_time)
        
        # Обновление менеджера производительности
        if self.performance_manager:
            self.performance_manager.update(self.delta_time)
    
    def _render(self):
        """Отрисовка игры"""
        if not self.screen:
            return
        
        # Очистка экрана
        self.screen.fill((0, 0, 0))
        
        # Отрисовка активной сцены
        if self.scene_manager and self.scene_manager.active_scene:
            self.scene_manager.active_scene.render(self.screen)
        
        # Обновление дисплея
        pygame.display.flip()
    
    def _limit_fps(self):
        """Ограничение FPS"""
        if self.clock:
            target_fps = self.config.get('display', {}).get('fps', 120)
            self.clock.tick(target_fps)
    
    def _update_stats(self):
        """Обновление статистики"""
        self.frame_count += 1
        current_time = time.time()
        
        # Обновление FPS каждую секунду
        if current_time - self.start_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.start_time = current_time
            
            # Логирование FPS каждые 10 секунд
            if int(current_time) % 10 == 0:
                logger.debug(f"FPS: {self.fps}")
    
    def _toggle_pause(self):
        """Переключение паузы"""
        self.paused = not self.paused
        if self.paused:
            self.current_state = GameState.PAUSED
            logger.info("Игра поставлена на паузу")
        else:
            self.current_state = GameState.PLAYING
            logger.info("Игра возобновлена")
    
    def _toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        if self.screen:
            pygame.display.toggle_fullscreen()
            logger.info("Переключен полноэкранный режим")
    
    def _handle_critical_error(self, error: Exception):
        """Обработка критических ошибок"""
        logger.critical(f"Критическая ошибка: {error}")
        # Здесь можно добавить логику сохранения состояния игры
        # и показа пользователю сообщения об ошибке
    
    def _cleanup(self):
        """Очистка ресурсов"""
        logger.info("Очистка ресурсов игрового движка...")
        
        try:
            # Очистка менеджеров
            if self.scene_manager:
                self.scene_manager.cleanup()
            
            if self.resource_manager:
                self.resource_manager.cleanup()
            
            if self.performance_manager:
                self.performance_manager.cleanup()
            
            # Завершение Pygame
            pygame.quit()
            
            logger.info("Ресурсы успешно очищены")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке ресурсов: {e}")
    
    def change_state(self, new_state: GameState):
        """Изменение состояния игры"""
        old_state = self.current_state
        self.current_state = new_state
        logger.info(f"Изменение состояния игры: {old_state} -> {new_state}")
        
        # Обработка изменения состояния
        if new_state == GameState.QUITTING:
            self.running = False
        elif new_state == GameState.PLAYING:
            self.paused = False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        return {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'delta_time': self.delta_time,
            'running_time': time.time() - self.start_time
        }

"""
Оптимизированный игровой цикл с использованием новой архитектуры
Применяет принцип единой ответственности и компонентную архитектуру
С оптимизацией производительности и управлением памятью
"""

import time
import pygame
import sys
from typing import Optional, Dict, Any
import logging
import gc
from collections import deque

from .game_systems import GameSystems
from .error_handler import error_handler, ErrorType, ErrorSeverity
from config.config_manager import config_manager
from ui.hud import DebugHUD

logger = logging.getLogger(__name__)


class RefactoredGameLoop:
    """
    Оптимизированный игровой цикл.
    Использует новую архитектуру с разделенными ответственностями.
    Включает оптимизацию производительности и управление памятью.
    """
    
    def __init__(self, use_pygame: bool = True):
        self.use_pygame = use_pygame
        self.is_running = False
        self.is_paused = False
        
        # Игровые системы
        self.game_systems = GameSystems()
        
        # Pygame компоненты
        self.screen = None
        self.clock = None
        self.debug_hud = None
        
        # Время и производительность
        self.last_frame_time = time.time()
        self.accumulated_time = 0.0
        self.frame_times = deque(maxlen=60)  # Храним время последних 60 кадров
        self.fps_counter = 0
        self.fps_timer = time.time()
        
        # Оптимизация памяти
        self.memory_cleanup_timer = 0
        self.memory_cleanup_interval = 300  # Очистка памяти каждые 5 секунд
        
        # Статистика производительности
        self.performance_stats = {
            'avg_fps': 0.0,
            'min_fps': float('inf'),
            'max_fps': 0.0,
            'frame_time_avg': 0.0,
            'memory_usage': 0.0
        }
        
        logger.info("Оптимизированный игровой цикл инициализирован")
    
    def _preload_resources(self):
        """Предзагрузка критически важных ресурсов с оптимизацией"""
        try:
            from .resource_manager import resource_manager
            
            # Список ресурсов для предзагрузки (приоритетные)
            resources_to_preload = [
                ("graphics/player/down/down_0.png", "image"),
                ("graphics/player/down/down_1.png", "image"),
                ("graphics/player/down/down_2.png", "image"),
                ("audio/hit.wav", "sound"),
                ("audio/heal.wav", "sound"),
                ("graphics/fonts/PixeloidSans.ttf", "font"),
            ]
            
            # Асинхронная предзагрузка
            resource_manager.preload_resources(resources_to_preload)
            logger.info("Ресурсы предзагружены")
            
        except Exception as e:
            logger.warning(f"Ошибка предзагрузки ресурсов: {e}")
    
    def _initialize_pygame(self) -> bool:
        """Инициализация Pygame с оптимизацией"""
        try:
            pygame.init()
            
            # Оптимизация Pygame
            pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN])
            
            # Настройка экрана
            display_info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (config_manager.get('game', 'display.window_width', 1280),
                 config_manager.get('game', 'display.window_height', 720)),
                pygame.DOUBLEBUF | pygame.HWSURFACE if config_manager.get('game', 'display.hardware_acceleration', True) else pygame.DOUBLEBUF
            )
            
            # Настройка заголовка и иконки
            pygame.display.set_caption("AI-EVOLVE: Enhanced Edition")
            
            # Настройка часов
            self.clock = pygame.time.Clock()
            target_fps = config_manager.get('game', 'display.render_fps', 60)
            self.clock.tick(target_fps)
            
            logger.info(f"Pygame инициализирован: {display_info.current_w}x{display_info.current_h}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Pygame: {e}")
            return False
    
    def initialize(self) -> bool:
        """Инициализация игрового цикла с оптимизацией"""
        try:
            # Инициализируем pygame если нужно
            if self.use_pygame:
                if not self._initialize_pygame():
                    return False
            
            # Предзагружаем ресурсы
            self._preload_resources()
            
            # Инициализируем игровые системы
            if not self.game_systems.initialize():
                logger.error("Ошибка инициализации игровых систем")
                return False
            
            # Настраиваем рендерер
            if self.screen:
                self.game_systems.render_system.set_screen(self.screen)
                self.debug_hud = DebugHUD(self.screen)
            
            # Инициализация производительности
            self._init_performance_monitoring()
            
            logger.info("Игровой цикл успешно инициализирован")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                ErrorType.UNKNOWN,
                f"Критическая ошибка инициализации игрового цикла: {str(e)}",
                exception=e,
                severity=ErrorSeverity.CRITICAL
            )
            return False
    
    def _init_performance_monitoring(self):
        """Инициализация мониторинга производительности"""
        try:
            import psutil
            self.process = psutil.Process()
            logger.info("Мониторинг производительности активирован")
        except ImportError:
            self.process = None
            logger.info("Мониторинг производительности недоступен (psutil не найден)")
    
    def _update_performance_stats(self, frame_time: float):
        """Обновление статистики производительности"""
        # Обновляем время кадров
        self.frame_times.append(frame_time)
        
        # Обновляем FPS
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_timer >= 1.0:
            fps = self.fps_counter / (current_time - self.fps_timer)
            self.performance_stats['avg_fps'] = fps
            self.performance_stats['min_fps'] = min(self.performance_stats['min_fps'], fps)
            self.performance_stats['max_fps'] = max(self.performance_stats['max_fps'], fps)
            
            # Обновляем среднее время кадра
            if self.frame_times:
                self.performance_stats['frame_time_avg'] = sum(self.frame_times) / len(self.frame_times)
            
            # Обновляем использование памяти
            if self.process:
                try:
                    memory_info = self.process.memory_info()
                    self.performance_stats['memory_usage'] = memory_info.rss / 1024 / 1024  # MB
                except Exception:
                    pass
            
            # Сброс счетчиков
            self.fps_counter = 0
            self.fps_timer = current_time
    
    def _cleanup_memory(self):
        """Очистка памяти для оптимизации"""
        current_time = time.time()
        if current_time - self.memory_cleanup_timer >= self.memory_cleanup_interval:
            # Принудительная сборка мусора
            collected = gc.collect()
            
            # Очистка кэша ресурсов
            try:
                from .resource_manager import resource_manager
                resource_manager.cleanup_unused_resources()
            except Exception:
                pass
            
            # Очистка кэша игровых систем
            self.game_systems.cleanup_cache()
            
            self.memory_cleanup_timer = current_time
            
            if collected > 0:
                logger.debug(f"Очистка памяти: освобождено {collected} объектов")
    
    def _handle_events(self):
        """Обработка событий с оптимизацией"""
        if not self.use_pygame:
            return
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                return
            
            # Передаем события в игровые системы
            self.game_systems.handle_event(event)
    
    def _update_game(self, delta_time: float):
        """Обновление игровой логики с оптимизацией"""
        try:
            # Обновляем игровые системы
            self.game_systems.update(delta_time)
            
            # Обновляем производительность
            self._update_performance_stats(delta_time)
            
            # Очистка памяти
            self._cleanup_memory()
            
        except Exception as e:
            error_handler.handle_error(
                ErrorType.GAME_UPDATE,
                f"Ошибка обновления игры: {str(e)}",
                exception=e,
                severity=ErrorSeverity.ERROR
            )
    
    def _render_frame(self):
        """Рендеринг кадра с оптимизацией"""
        try:
            if not self.use_pygame or not self.screen:
                return
            
            # Очищаем экран
            self.screen.fill((0, 0, 0))
            
            # Рендерим игровые системы
            self.game_systems.render(self.screen)
            
            # Рендерим HUD
            if self.debug_hud:
                self.debug_hud.render(self.performance_stats)
            
            # Обновляем экран
            pygame.display.flip()
            
        except Exception as e:
            error_handler.handle_error(
                ErrorType.RENDERING,
                f"Ошибка рендеринга: {str(e)}",
                exception=e,
                severity=ErrorSeverity.ERROR
            )
    
    def run(self):
        """Основной игровой цикл с оптимизацией"""
        if not self.is_running:
            self.is_running = True
            logger.info("Запуск игрового цикла")
        
        target_fps = config_manager.get('game', 'display.render_fps', 60)
        target_frame_time = 1.0 / target_fps
        
        try:
            while self.is_running:
                # Измеряем время кадра
                current_time = time.time()
                delta_time = current_time - self.last_frame_time
                
                # Ограничиваем delta_time для стабильности
                delta_time = min(delta_time, 0.1)  # Максимум 100ms
                
                # Обработка событий
                self._handle_events()
                
                if not self.is_running:
                    break
                
                # Обновление игры
                if not self.is_paused:
                    self._update_game(delta_time)
                
                # Рендеринг
                self._render_frame()
                
                # Ограничение FPS
                frame_time = time.time() - current_time
                if frame_time < target_frame_time:
                    time.sleep(target_frame_time - frame_time)
                
                # Обновляем время последнего кадра
                self.last_frame_time = time.time()
                
                # Обновляем часы Pygame
                if self.clock:
                    self.clock.tick(target_fps)
                
        except KeyboardInterrupt:
            logger.info("Игровой цикл прерван пользователем")
        except Exception as e:
            error_handler.handle_error(
                ErrorType.UNKNOWN,
                f"Критическая ошибка игрового цикла: {str(e)}",
                exception=e,
                severity=ErrorSeverity.CRITICAL
            )
        finally:
            self.cleanup()
    
    def pause(self):
        """Приостановка игры"""
        self.is_paused = True
        logger.info("Игра приостановлена")
    
    def resume(self):
        """Возобновление игры"""
        self.is_paused = False
        logger.info("Игра возобновлена")
    
    def stop(self):
        """Остановка игры"""
        self.is_running = False
        logger.info("Игра остановлена")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        return self.performance_stats.copy()
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            logger.info("Очистка ресурсов игрового цикла")
            
            # Очищаем игровые системы
            if hasattr(self.game_systems, 'cleanup'):
                self.game_systems.cleanup()
            
            # Очищаем Pygame
            if self.use_pygame:
                pygame.quit()
            
            # Принудительная очистка памяти
            gc.collect()
            
            logger.info("Очистка завершена")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке: {e}")
    
    def __del__(self):
        """Деструктор для автоматической очистки"""
        self.cleanup()

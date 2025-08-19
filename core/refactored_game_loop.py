"""
Обновленный игровой цикл с использованием новой архитектуры
Применяет принцип единой ответственности и компонентную архитектуру
"""

import time
import pygame
import sys
from typing import Optional
import logging

from .game_systems import GameSystems
from .error_handler import ErrorHandler, ErrorType, ErrorSeverity
from config.config_factory import config_factory, ConfigType

logger = logging.getLogger(__name__)


class RefactoredGameLoop:
    """
    Обновленный игровой цикл.
    Использует новую архитектуру с разделенными ответственностями.
    """
    
    def __init__(self, use_pygame: bool = True):
        self.use_pygame = use_pygame
        self.is_running = False
        self.is_paused = False
        
        # Игровые системы
        self.game_systems = GameSystems()
        
        # Обработчик ошибок
        self.error_handler = ErrorHandler()
        
        # Pygame компоненты
        self.screen = None
        self.clock = None
        
        # Время
        self.last_frame_time = time.time()
        self.accumulated_time = 0.0
        
        logger.info("Обновленный игровой цикл инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация игрового цикла"""
        try:
            # Инициализируем pygame если нужно
            if self.use_pygame:
                if not self._initialize_pygame():
                    return False
            
            # Инициализируем игровые системы
            if not self.game_systems.initialize():
                logger.error("Ошибка инициализации игровых систем")
                return False
            
            # Настраиваем рендерер
            if self.screen:
                self.game_systems.render_system.set_screen(self.screen)
            
            logger.info("Игровой цикл успешно инициализирован")
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.UNKNOWN,
                f"Критическая ошибка инициализации игрового цикла: {str(e)}",
                exception=e,
                severity=ErrorSeverity.CRITICAL
            )
            return False
    
    def _initialize_pygame(self) -> bool:
        """Инициализация pygame"""
        try:
            if not pygame.get_init():
                pygame.init()
            
            # Загружаем конфигурацию
            game_config = config_factory.create_config(ConfigType.GAME_SETTINGS)
            display_config = game_config.get('display', {})
            
            # Настройки окна
            window_width = display_config.get('window_width', 1280)
            window_height = display_config.get('window_height', 720)
            fullscreen = display_config.get('fullscreen', False)
            vsync = display_config.get('vsync', True)
            
            # Создаем окно
            flags = pygame.DOUBLEBUF
            if fullscreen:
                flags |= pygame.FULLSCREEN
            if vsync:
                flags |= pygame.HWSURFACE
            
            self.screen = pygame.display.set_mode((window_width, window_height), flags)
            pygame.display.set_caption("Эволюционная Адаптация: Генетический Резонанс")
            
            # Создаем часы
            self.clock = pygame.time.Clock()
            
            logger.info(f"Pygame инициализирован: {window_width}x{window_height}")
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.CONFIGURATION,
                f"Ошибка инициализации pygame: {str(e)}",
                exception=e,
                severity=ErrorSeverity.ERROR
            )
            return False
    
    def run(self) -> None:
        """Запуск игрового цикла"""
        if not self.is_running:
            self.is_running = True
            logger.info("Игровой цикл запущен")
        
        try:
            while self.is_running:
                # Обработка событий
                self._handle_events()
                
                # Обновление времени
                current_time = time.time()
                delta_time = current_time - self.last_frame_time
                self.last_frame_time = current_time
                
                # Ограничиваем delta_time для стабильности
                delta_time = min(delta_time, 0.1)  # Максимум 100ms
                
                # Обновление игры
                if not self.is_paused:
                    self._update(delta_time)
                
                # Отрисовка
                if self.use_pygame:
                    self._render()
                
                # Ограничение FPS
                if self.clock:
                    self.clock.tick(self.game_systems.target_fps)
                    
        except KeyboardInterrupt:
            logger.info("Игровой цикл прерван пользователем")
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.UNKNOWN,
                f"Критическая ошибка в игровом цикле: {str(e)}",
                exception=e,
                severity=ErrorSeverity.CRITICAL
            )
        finally:
            self.cleanup()
    
    def _handle_events(self) -> None:
        """Обработка событий"""
        if not self.use_pygame:
            return
        
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self._handle_keyup(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_mouse_down(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self._handle_mouse_up(event)
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_mouse_motion(event)
                    
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.UNKNOWN,
                f"Ошибка обработки событий: {str(e)}",
                exception=e,
                severity=ErrorSeverity.WARNING
            )
    
    def _handle_keydown(self, event) -> None:
        """Обработка нажатия клавиши"""
        if event.key == pygame.K_ESCAPE:
            self.is_running = False
        elif event.key == pygame.K_p:
            self.is_paused = not self.is_paused
            logger.info(f"Игра {'приостановлена' if self.is_paused else 'возобновлена'}")
        elif event.key == pygame.K_F1:
            self._show_debug_info()
        elif event.key == pygame.K_F2:
            self._save_debug_screenshot()
    
    def _handle_keyup(self, event) -> None:
        """Обработка отпускания клавиши"""
        pass
    
    def _handle_mouse_down(self, event) -> None:
        """Обработка нажатия мыши"""
        pass
    
    def _handle_mouse_up(self, event) -> None:
        """Обработка отпускания мыши"""
        pass
    
    def _handle_mouse_motion(self, event) -> None:
        """Обработка движения мыши"""
        pass
    
    def _update(self, delta_time: float) -> None:
        """Обновление игровой логики"""
        try:
            # Обновляем игровые системы
            self.game_systems.update(delta_time)
            
            # Обновляем накопленное время
            self.accumulated_time += delta_time
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.UNKNOWN,
                f"Ошибка обновления игровой логики: {str(e)}",
                exception=e,
                severity=ErrorSeverity.ERROR
            )
    
    def _render(self) -> None:
        """Отрисовка"""
        try:
            if not self.screen:
                return
            
            # Очищаем экран
            self.screen.fill((0, 0, 0))
            
            # Отрисовываем игровые системы
            self.game_systems.render()
            
            # Отрисовываем UI
            self._render_ui()
            
            # Обновляем экран
            pygame.display.flip()
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.RENDERING,
                f"Ошибка отрисовки: {str(e)}",
                exception=e,
                severity=ErrorSeverity.ERROR
            )
    
    def _render_ui(self) -> None:
        """Отрисовка пользовательского интерфейса"""
        try:
            if not self.screen:
                return
            
            # Получаем статистику
            stats = self.game_systems.get_statistics()
            
            # Отрисовываем FPS
            if stats.get('fps', 0) > 0:
                font = pygame.font.Font(None, 24)
                fps_text = font.render(f"FPS: {stats['fps']}", True, (255, 255, 255))
                self.screen.blit(fps_text, (10, 10))
            
            # Отрисовываем информацию о мире
            world_info = stats.get('world', {})
            if world_info:
                font = pygame.font.Font(None, 20)
                world_text = font.render(
                    f"Мир: {world_info.get('name', 'Unknown')} | "
                    f"День: {world_info.get('day_cycle', 0)} | "
                    f"Погода: {world_info.get('weather', 'Unknown')}", 
                    True, (255, 255, 255)
                )
                self.screen.blit(world_text, (10, 40))
            
            # Отрисовываем информацию о сущностях
            entity_stats = stats.get('entities', {})
            if entity_stats:
                font = pygame.font.Font(None, 20)
                entity_text = font.render(
                    f"Сущности: {entity_stats.get('total_entities', 0)}", 
                    True, (255, 255, 255)
                )
                self.screen.blit(entity_text, (10, 70))
            
            # Отрисовываем статус паузы
            if self.is_paused:
                font = pygame.font.Font(None, 36)
                pause_text = font.render("ПАУЗА", True, (255, 255, 0))
                text_rect = pause_text.get_rect(center=(self.screen.get_width() // 2, 50))
                self.screen.blit(pause_text, text_rect)
                
        except Exception as e:
            logger.error(f"Ошибка отрисовки UI: {e}")
    
    def _show_debug_info(self) -> None:
        """Показать отладочную информацию"""
        try:
            stats = self.game_systems.get_statistics()
            logger.info("=== ОТЛАДОЧНАЯ ИНФОРМАЦИЯ ===")
            logger.info(f"Время игры: {stats.get('game_time', 0):.2f} сек")
            logger.info(f"FPS: {stats.get('fps', 0)}")
            logger.info(f"Сущности: {stats.get('entities', {}).get('total_entities', 0)}")
            logger.info(f"Ошибки: {stats.get('errors', {}).get('total_errors', 0)}")
            logger.info("================================")
            
        except Exception as e:
            logger.error(f"Ошибка показа отладочной информации: {e}")
    
    def _save_debug_screenshot(self) -> None:
        """Сохранение отладочного скриншота"""
        try:
            if self.screen:
                import os
                from datetime import datetime
                
                # Создаем папку для скриншотов
                screenshots_dir = "screenshots"
                os.makedirs(screenshots_dir, exist_ok=True)
                
                # Генерируем имя файла
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{screenshots_dir}/debug_{timestamp}.png"
                
                # Сохраняем скриншот
                pygame.image.save(self.screen, filename)
                logger.info(f"Скриншот сохранен: {filename}")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения скриншота: {e}")
    
    def pause(self) -> None:
        """Приостановка игры"""
        self.is_paused = True
        logger.info("Игра приостановлена")
    
    def resume(self) -> None:
        """Возобновление игры"""
        self.is_paused = False
        logger.info("Игра возобновлена")
    
    def stop(self) -> None:
        """Остановка игры"""
        self.is_running = False
        logger.info("Игра остановлена")
    
    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            # Очищаем игровые системы
            self.game_systems.cleanup()
            
            # Очищаем pygame
            if self.use_pygame and pygame.get_init():
                pygame.quit()
            
            logger.info("Ресурсы игрового цикла очищены")
            
        except Exception as e:
            logger.error(f"Ошибка очистки ресурсов: {e}")
    
    def get_statistics(self) -> dict:
        """Получение статистики"""
        return self.game_systems.get_statistics()


def run_refactored_game():
    """Запуск обновленной игры"""
    try:
        # Создаем и инициализируем игровой цикл
        game_loop = RefactoredGameLoop(use_pygame=True)
        
        if not game_loop.initialize():
            logger.error("Ошибка инициализации игры")
            return False
        
        # Запускаем игровой цикл
        game_loop.run()
        
        return True
        
    except Exception as e:
        logger.error(f"Критическая ошибка запуска игры: {e}")
        return False


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Запуск игры
    success = run_refactored_game()
    
    if success:
        print("Игра завершена успешно")
    else:
        print("Игра завершена с ошибками")
        sys.exit(1)

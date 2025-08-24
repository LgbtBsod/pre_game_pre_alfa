#!/usr/bin/env python3
"""
Централизованный игровой движок AI-EVOLVE
Объединяет все системы в единую архитектуру с оптимизацией производительности
"""

import time
import logging
import traceback
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import pygame
import sys
from pathlib import Path

from .error_handler import error_handler, ErrorType, ErrorSeverity
from .performance_manager import performance_optimizer
from config.config_manager import config_manager

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Состояния игры"""
    INITIALIZING = "initializing"
    MAIN_MENU = "main_menu"
    LOADING = "loading"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    GENETICS = "genetics"
    EMOTIONS = "emotions"
    EVOLUTION = "evolution"
    SETTINGS = "settings"
    QUITTING = "quitting"


@dataclass
class GameConfig:
    """Конфигурация игры"""
    window_width: int = 1600
    window_height: int = 900
    fps: int = 120
    fullscreen: bool = False
    vsync: bool = True
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    difficulty: str = "normal"
    enable_enhanced_edition: bool = True
    enable_debug: bool = False
    
    @classmethod
    def from_config_manager(cls) -> 'GameConfig':
        """Создает конфигурацию из config_manager"""
        try:
            return cls(
                window_width=config_manager.get('display', 'window_width', 1600),
                window_height=config_manager.get('display', 'window_height', 900),
                fps=config_manager.get('display', 'render_fps', 120),
                fullscreen=config_manager.get('display', 'fullscreen', False),
                vsync=config_manager.get('display', 'vsync', True),
                music_volume=config_manager.get('audio', 'music_volume', 0.7),
                sfx_volume=config_manager.get('audio', 'sfx_volume', 0.8),
                difficulty=config_manager.get('gameplay', 'difficulty', 'normal'),
                enable_enhanced_edition=config_manager.get('enhanced', 'enabled', True),
                enable_debug=config_manager.get('debug', 'enabled', False)
            )
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            return cls()


class GameEngine:
    """
    Централизованный игровой движок
    Управляет всеми системами и жизненным циклом игры
    """
    
    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig.from_config_manager()
        self.state = GameState.INITIALIZING
        self.running = False
        
        # Pygame компоненты
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        
        # Системы
        self.systems: Dict[str, Any] = {}
        self.ui_manager = None
        self.scene_manager = None
        self.input_manager = None
        self.renderer = None
        
        # Производительность
        self.frame_times = []
        self.last_frame_time = time.time()
        self.fps_counter = 0
        self.fps_timer = time.time()
        
        # Статистика
        self.stats = {
            'total_frames': 0,
            'avg_fps': 0.0,
            'min_fps': float('inf'),
            'max_fps': 0.0,
            'total_play_time': 0.0
        }
        
        logger.info("Игровой движок инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация движка"""
        try:
            logger.info("Начало инициализации игрового движка...")
            
            # Инициализация Pygame
            if not self._initialize_pygame():
                return False
            
            # Инициализация систем
            if not self._initialize_systems():
                return False
            
            # Инициализация UI
            if not self._initialize_ui():
                return False
            
            # Инициализация сцен
            if not self._initialize_scenes():
                return False
            
            self.state = GameState.MAIN_MENU
            logger.info("Игровой движок успешно инициализирован")
            return True
            
        except Exception as e:
            error_handler.handle_error(
                ErrorType.INITIALIZATION_ERROR,
                ErrorSeverity.CRITICAL,
                f"Ошибка инициализации движка: {e}",
                traceback.format_exc()
            )
            return False
    
    def _initialize_pygame(self) -> bool:
        """Инициализация Pygame"""
        try:
            pygame.init()
            pygame.mixer.init()
            
            # Настройка экрана
            flags = pygame.DOUBLEBUF
            if self.config.fullscreen:
                flags |= pygame.FULLSCREEN
            if self.config.vsync:
                flags |= pygame.HWSURFACE
            
            self.screen = pygame.display.set_mode(
                (self.config.window_width, self.config.window_height),
                flags
            )
            
            pygame.display.set_caption("AI-EVOLVE: Enhanced Edition")
            
            # Настройка FPS
            self.clock = pygame.time.Clock()
            
            # Оптимизация событий
            pygame.event.set_allowed([
                pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP,
                pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                pygame.MOUSEMOTION
            ])
            
            logger.info("Pygame инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Pygame: {e}")
            return False
    
    def _initialize_systems(self) -> bool:
        """Инициализация игровых систем"""
        try:
            # Инициализация менеджера ресурсов
            from core.resource_manager import resource_manager
            self.systems['resource_manager'] = resource_manager
            
            # Предзагрузка критических ресурсов
            resource_manager.preload_critical_resources()
            
            # Инициализация системы простых объектов
            from core.simple_entity_system import entity_manager
            self.systems['entity_manager'] = entity_manager
            
            # Базовые системы
            self._load_system('effect_system', 'core.effect_system', 'EffectDatabase')
            self._load_system('genetic_system', 'core.genetic_system', 'AdvancedGeneticSystem')
            self._load_system('emotion_system', 'core.emotion_system', 'AdvancedEmotionSystem')
            self._load_system('ai_system', 'core.ai_system', 'AdaptiveAISystem')
            self._load_system('content_generator', 'core.content_generator', 'ContentGenerator')
            self._load_system('evolution_system', 'core.evolution_system', 'EvolutionCycleSystem')
            self._load_system('event_system', 'core.global_event_system', 'GlobalEventSystem')
            self._load_system('difficulty_system', 'core.dynamic_difficulty', 'DynamicDifficultySystem')
            
            # Enhanced Edition системы
            if self.config.enable_enhanced_edition:
                self._load_enhanced_systems()
            
            # Дополнительные системы
            self._load_system('computer_vision', 'core.computer_vision_system', 'ComputerVisionSystem')
            self._load_system('object_creation', 'core.object_creation_system', 'ObjectCreationSystem')
            self._load_system('session_manager', 'core.session_manager', 'SessionManager')
            
            # Предзагрузка UI и игровых ресурсов
            resource_manager.preload_ui_resources()
            resource_manager.preload_game_resources()
            
            # Инициализация мониторинга производительности
            from core.performance_manager import initialize_performance_monitoring
            initialize_performance_monitoring()
            
            logger.info("Игровые системы инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации систем: {e}")
            return False
    
    def _load_system(self, name: str, module_path: str, class_name: str) -> bool:
        """Безопасная загрузка системы"""
        try:
            module = __import__(module_path, fromlist=[class_name])
            system_class = getattr(module, class_name)
            
            # Специальная инициализация для систем, требующих параметры
            if name == 'genetic_system' and 'effect_system' in self.systems:
                self.systems[name] = system_class(self.systems['effect_system'])
            elif name == 'emotion_system' and 'effect_system' in self.systems:
                self.systems[name] = system_class(self.systems['effect_system'])
            elif name == 'ai_system':
                self.systems[name] = system_class("PLAYER_AI")
            elif name == 'computer_vision':
                self.systems[name] = system_class("PLAYER_VISION")
            else:
                self.systems[name] = system_class()
            
            logger.info(f"Система {name} загружена")
            return True
            
        except Exception as e:
            logger.warning(f"Не удалось загрузить систему {name}: {e}")
            self.systems[name] = None
            return False
    
    def _load_enhanced_systems(self) -> bool:
        """Загрузка Enhanced Edition систем"""
        try:
            # Enhanced Game Master
            self._load_system('enhanced_game_master', 'core.enhanced_game_master', 'EnhancedGameMaster')
            if self.systems['enhanced_game_master']:
                self.systems['enhanced_game_master'] = self.systems['enhanced_game_master'](
                    self.config.window_width, self.config.window_height
                )
            
            # Память поколений
            self._load_system('memory_system', 'core.generational_memory_system', 'GenerationalMemorySystem')
            if self.systems['memory_system']:
                self.systems['memory_system'] = self.systems['memory_system']("save")
            
            # Эмоциональный ИИ
            if self.systems['memory_system']:
                self._load_system('emotional_ai', 'core.emotional_ai_influence', 'EmotionalAIInfluenceSystem')
                if self.systems['emotional_ai']:
                    self.systems['emotional_ai'] = self.systems['emotional_ai'](self.systems['memory_system'])
            
            # Улучшенное боевое обучение
            if self.systems['memory_system'] and self.systems['emotional_ai']:
                self._load_system('enhanced_combat', 'core.enhanced_combat_learning', 'EnhancedCombatLearningSystem')
                if self.systems['enhanced_combat']:
                    self.systems['enhanced_combat'] = self.systems['enhanced_combat'](
                        self.systems['memory_system'], self.systems['emotional_ai']
                    )
            
            # Улучшенный генератор контента
            if self.systems['memory_system']:
                self._load_system('enhanced_content', 'core.enhanced_content_generator', 'EnhancedContentGenerator')
                if self.systems['enhanced_content']:
                    self.systems['enhanced_content'] = self.systems['enhanced_content'](self.systems['memory_system'])
            
            # Система навыков
            if self.systems['memory_system'] and self.systems['emotional_ai']:
                self._load_system('skill_manager', 'core.enhanced_skill_system', 'SkillManager')
                if self.systems['skill_manager']:
                    self.systems['skill_manager'] = self.systems['skill_manager'](
                        self.systems['memory_system'], self.systems['emotional_ai']
                    )
            
            logger.info("Enhanced Edition системы загружены")
            return True
            
        except Exception as e:
            logger.warning(f"Не удалось загрузить Enhanced Edition системы: {e}")
            return False
    
    def _initialize_ui(self) -> bool:
        """Инициализация UI"""
        try:
            from ui.renderer import GameRenderer
            from ui.camera import Camera
            from core.isometric_system import IsometricProjection
            
            # Изометрическая проекция
            isometric_projection = IsometricProjection(tile_width=64, tile_height=32)
            
            # Камера
            camera = Camera(self.config.window_width, self.config.window_height)
            
            # Рендерер
            self.renderer = GameRenderer(
                self.screen, 
                self._load_fonts(), 
                isometric_projection, 
                camera
            )
            
            # Менеджер ввода
            from core.input_manager import InputManager
            self.input_manager = InputManager()
            
            logger.info("UI инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации UI: {e}")
            return False
    
    def _initialize_scenes(self) -> bool:
        """Инициализация сцен"""
        try:
            from core.scene_manager import SceneManager
            from ui.menu_scene import MenuScene
            from ui.pause_scene import PauseScene
            from ui.game_scene import GameScene
            
            self.scene_manager = SceneManager()
            
            # Регистрация сцен
            self.scene_manager.register_scene('menu', MenuScene(self.scene_manager, self))
            self.scene_manager.register_scene('pause', PauseScene(self.scene_manager, self))
            self.scene_manager.register_scene('game', GameScene(self))
            
            # Переключение на главное меню
            self.scene_manager.switch_scene('menu')
            
            logger.info("Сцены инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцен: {e}")
            return False
    
    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        """Загрузка шрифтов"""
        fonts = {}
        try:
            font_path = Path("graphics/fonts/PixeloidSans.ttf")
            if font_path.exists():
                fonts["main"] = pygame.font.Font(str(font_path), 24)
                fonts["large"] = pygame.font.Font(str(font_path), 32)
                fonts["small"] = pygame.font.Font(str(font_path), 16)
            else:
                fonts["main"] = pygame.font.Font(None, 24)
                fonts["large"] = pygame.font.Font(None, 32)
                fonts["small"] = pygame.font.Font(None, 16)
        except Exception as e:
            logger.warning(f"Ошибка загрузки шрифтов: {e}")
            fonts["main"] = pygame.font.Font(None, 24)
            fonts["large"] = pygame.font.Font(None, 32)
            fonts["small"] = pygame.font.Font(None, 16)
        
        return fonts
    
    def run(self) -> int:
        """Главный цикл игры"""
        if not self.initialize():
            return 1
        
        self.running = True
        logger.info("Запуск главного игрового цикла")
        
        try:
            while self.running:
                # Обработка событий
                self._handle_events()
                
                # Обновление
                self._update()
                
                # Рендеринг
                self._render()
                
                # Ограничение FPS
                if self.clock:
                    self.clock.tick(self.config.fps)
                
                # Обновление статистики
                self._update_stats()
            
            return 0
            
        except KeyboardInterrupt:
            logger.info("Игра прервана пользователем")
            return 0
        except Exception as e:
            error_handler.handle_error(
                ErrorType.RUNTIME_ERROR,
                ErrorSeverity.CRITICAL,
                f"Критическая ошибка в игровом цикле: {e}",
                traceback.format_exc()
            )
            return 1
        finally:
            self.cleanup()
    
    def _handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            else:
                # Передача событий в активную сцену
                if self.scene_manager and self.scene_manager.current_scene:
                    self.scene_manager.current_scene.handle_event(event)
                
                # Обработка ввода
                if self.input_manager:
                    self.input_manager.handle_event(event)
    
    def _update(self):
        """Обновление игровой логики"""
        delta_time = time.time() - self.last_frame_time
        self.last_frame_time = time.time()
        
        # Ограничение delta_time для стабильности
        delta_time = min(delta_time, 0.1)
        
        # Обновление активной сцены
        if self.scene_manager and self.scene_manager.current_scene:
            self.scene_manager.current_scene.update(delta_time)
        
        # Обновление систем
        for system_name, system in self.systems.items():
            if system and hasattr(system, 'update'):
                try:
                    system.update(delta_time)
                except Exception as e:
                    logger.warning(f"Ошибка обновления системы {system_name}: {e}")
        
        # Обновление производительности
        performance_optimizer.update(delta_time)
    
    def _render(self):
        """Рендеринг"""
        if not self.screen:
            return
        
        # Очистка экрана
        self.screen.fill((0, 0, 0))
        
        # Рендеринг активной сцены
        if self.scene_manager and self.scene_manager.current_scene:
            self.scene_manager.current_scene.render(self.screen)
        
        # Обновление экрана
        pygame.display.flip()
    
    def _update_stats(self):
        """Обновление статистики"""
        self.stats['total_frames'] += 1
        
        # Обновление FPS
        current_time = time.time()
        if current_time - self.fps_timer >= 1.0:
            fps = self.fps_counter / (current_time - self.fps_timer)
            frame_time = (current_time - self.fps_timer) / self.fps_counter if self.fps_counter > 0 else 0
            
            self.stats['avg_fps'] = fps
            self.stats['min_fps'] = min(self.stats['min_fps'], fps)
            self.stats['max_fps'] = max(self.stats['max_fps'], fps)
            
            # Обновление метрик производительности
            from core.performance_manager import performance_monitor
            performance_monitor.update_frame_metrics(fps, frame_time * 1000)  # в миллисекундах
            
            self.fps_counter = 0
            self.fps_timer = current_time
        
        self.fps_counter += 1
    
    def get_system(self, name: str) -> Optional[Any]:
        """Получение системы по имени"""
        return self.systems.get(name)
    
    def set_state(self, state: GameState):
        """Изменение состояния игры"""
        logger.info(f"Изменение состояния игры: {self.state.value} -> {state.value}")
        self.state = state
    
    def quit(self):
        """Завершение игры"""
        logger.info("Завершение игры")
        self.running = False
        self.state = GameState.QUITTING
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            logger.info("Очистка ресурсов")
            
            # Очистка систем
            for system_name, system in self.systems.items():
                if system and hasattr(system, 'cleanup'):
                    try:
                        system.cleanup()
                    except Exception as e:
                        error_handler.handle_error(
                            ErrorType.SYSTEM_ERROR,
                            ErrorSeverity.MEDIUM,
                            f"Ошибка очистки системы {system_name}: {e}",
                            {'system_name': system_name}
                        )
            
            # Очистка менеджера ресурсов
            resource_manager = self.systems.get('resource_manager')
            if resource_manager:
                resource_manager.cleanup()
            
            # Очистка Pygame
            pygame.quit()
            
            logger.info("Ресурсы очищены")
            
        except Exception as e:
            error_handler.handle_error(
                ErrorType.SYSTEM_ERROR,
                ErrorSeverity.HIGH,
                f"Ошибка очистки ресурсов: {e}",
                {'cleanup_phase': 'final'}
            )


# Глобальный экземпляр движка
game_engine: Optional[GameEngine] = None


def get_game_engine() -> GameEngine:
    """Получение глобального экземпляра движка"""
    global game_engine
    if game_engine is None:
        game_engine = GameEngine()
    return game_engine

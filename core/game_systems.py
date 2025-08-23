"""
Оптимизированные системы игрового цикла
Разделение ответственностей из оригинального game_loop.py
С интеграцией всех модулей и оптимизацией производительности
"""

import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import gc
from collections import defaultdict

from .entity_system import EntityManager, EntityFactory
from .resource_loader import ResourceLoader
from .error_handler import error_handler, ErrorType, ErrorSeverity
from .components.transform_component import Vector3
from config.config_manager import config_manager
from .events import EventType
from .game_state import GameStateManager, GameState
from .performance_manager import performance_optimizer, initialize_performance_monitoring

from .event_system import event_system, GameEvents
from ui.renderer import GameRenderer

logger = logging.getLogger(__name__)


@dataclass
class WorldState:
    """Состояние игрового мира"""
    name: str
    seed: int
    weather: str = "clear"
    time_of_day: float = 0.0
    day_cycle: int = 0
    explored_areas: int = 0
    total_areas: int = 100
    
    @property
    def explored_percent(self) -> float:
        """Процент исследованной территории"""
        return self.explored_areas / self.total_areas if self.total_areas > 0 else 0.0


class WorldManager:
    """
    Менеджер игрового мира.
    Отвечает только за управление состоянием мира.
    """
    
    def __init__(self):
        self.current_world: Optional[WorldState] = None
        self.weather_options = ["clear", "cloudy", "rainy", "stormy", "foggy"]
        self.weather_weights = [0.4, 0.3, 0.15, 0.1, 0.05]
        self.day_length = 24 * 60  # 24 игровых часа = 24 реальных минуты
        
        # Экосистема
        self.ecosystem = {
            "predators": 0,
            "prey": 0,
            "neutral": 0,
            "balance": 1.0
        }
        
        # Глобальные события
        self.active_events = []
        self.event_history = []
    
    def create_world(self, name: str = None, seed: int = None) -> WorldState:
        """Создание нового мира"""
        if seed is None:
            seed = random.randint(1, 999999)
        
        if name is None:
            name = f"World_{seed}"
        
        self.current_world = WorldState(
            name=name,
            seed=seed
        )
        
        logger.info(f"Создан игровой мир: {name} (seed: {seed})")
        return self.current_world
    
    def update_world_time(self, delta_time: float) -> None:
        """Обновление времени в мире"""
        if not self.current_world:
            return
        
        self.current_world.time_of_day += delta_time
        
        # Цикл дня
        if self.current_world.time_of_day >= self.day_length:
            self.current_world.time_of_day = 0
            self.current_world.day_cycle += 1
            
            # Смена погоды
            self._change_weather()
            
            logger.info(f"Наступил день {self.current_world.day_cycle}")
    
    def _change_weather(self) -> None:
        """Смена погоды"""
        if not self.current_world:
            return
        
        # Выбираем новую погоду на основе весов
        new_weather = random.choices(
            self.weather_options, 
            weights=self.weather_weights, 
            k=1
        )[0]
        
        if new_weather != self.current_world.weather:
            self.current_world.weather = new_weather
            logger.info(f"Погода изменилась на: {new_weather}")
    
    def update_exploration(self, new_areas: int) -> None:
        """Обновление прогресса исследования"""
        if not self.current_world:
            return
        
        self.current_world.explored_areas = min(
            self.current_world.total_areas, 
            self.current_world.explored_areas + new_areas
        )
        
        logger.info(f"Прогресс исследования: {self.current_world.explored_percent:.1%}")
    
    def update_ecosystem(self, entity_type: str, change: int) -> None:
        """Обновление экосистемы"""
        if entity_type in self.ecosystem:
            self.ecosystem[entity_type] = max(0, self.ecosystem[entity_type] + change)
            self._update_ecosystem_balance()
    
    def _update_ecosystem_balance(self) -> None:
        """Обновление баланса экосистемы"""
        total_entities = sum(self.ecosystem.values()) - self.ecosystem["balance"]
        
        if total_entities > 0:
            predator_ratio = self.ecosystem["predators"] / total_entities
            prey_ratio = self.ecosystem["prey"] / total_entities
            
            # Идеальный баланс: 1 хищник на 3 жертвы
            ideal_ratio = 0.25
            self.ecosystem["balance"] = 1.0 - abs(predator_ratio - ideal_ratio)
        else:
            self.ecosystem["balance"] = 1.0
    
    def get_world_info(self) -> Dict[str, Any]:
        """Получение информации о мире"""
        if not self.current_world:
            return {}
        
        return {
            "name": self.current_world.name,
            "seed": self.current_world.seed,
            "weather": self.current_world.weather,
            "time_of_day": self.current_world.time_of_day,
            "day_cycle": self.current_world.day_cycle,
            "explored_percent": self.current_world.explored_percent,
            "ecosystem": self.ecosystem.copy()
        }


# EventSystem теперь импортируется из core.event_system
class RenderSystem:
    """
    Система рендеринга.
    Отвечает только за отрисовку.
    """
    
    def __init__(self, screen=None):
        self.screen = screen
        self.camera_offset = (0, 0)
        self.render_layers = {
            'background': [],
            'world': [],
            'entities': [],
            'ui': [],
            'overlay': []
        }
        self._game_renderer = None
    
    def set_screen(self, screen) -> None:
        """Установка экрана для отрисовки"""
        self.screen = screen
        # Recreate renderer if dependencies are resolvable by caller later
    
    def set_camera_offset(self, offset: Tuple[float, float]) -> None:
        """Установка смещения камеры"""
        self.camera_offset = offset

    def set_game_renderer(self, renderer: GameRenderer) -> None:
        """Подключить высокоуровневый рендерер сцен."""
        self._game_renderer = renderer
    
    def add_to_layer(self, layer: str, renderable) -> None:
        """Добавление объекта для отрисовки в слой"""
        if layer in self.render_layers:
            self.render_layers[layer].append(renderable)
    
    def clear_layer(self, layer: str) -> None:
        """Очистка слоя отрисовки"""
        if layer in self.render_layers:
            self.render_layers[layer].clear()
    
    def render(self) -> None:
        """Отрисовка всех слоев"""
        if not self.screen:
            return
        
        try:
            # Отрисовываем слои в порядке
            for layer_name, renderables in self.render_layers.items():
                for renderable in renderables:
                    if hasattr(renderable, 'render'):
                        renderable.render(self.screen, self.camera_offset)
                    elif callable(renderable):
                        renderable(self.screen, self.camera_offset)
            # Дополнительно: если подключен GameRenderer, можно вызвать преднастроенные группы
            if self._game_renderer and hasattr(self._game_renderer, 'render_grid'):
                # Ничего не вызываем по умолчанию, оставляем точку расширения
                pass
        except Exception as e:
            logger.error(f"Ошибка рендеринга: {e}")


class StateAdapter:
    """
    Адаптер над GameStateManager для совместимости с существующими обработчиками.
    """
    def __init__(self):
        self.manager = GameStateManager()
        self.state_handlers: Dict[GameState, callable] = {}
    
    def register_state_handler(self, state: str, handler: callable) -> None:
        # Принимаем строковые состояния и маппим на Enum
        enum_state = self._to_enum(state)
        self.state_handlers[enum_state] = handler
    
    def change_state(self, new_state: str, data: Any = None) -> None:
        enum_state = self._to_enum(new_state)
        self.manager.change_state(enum_state, data or {})
        logger.info(f"Состояние игры изменено: {enum_state.name}")
    
    def get_current_state(self) -> str:
        return self.manager.get_current_state().name.lower()
    
    def get_state_data(self, state: str = None) -> Any:
        current = self.manager.get_current_state() if state is None else self._to_enum(state)
        return self.manager.get_state_data(current)
    
    def update_state(self, delta_time: float) -> None:
        current = self.manager.get_current_state()
        handler = self.state_handlers.get(current)
        if handler:
            try:
                handler(delta_time)
            except Exception as e:
                logger.error(f"Ошибка обновления состояния {current.name}: {e}")
    
    def _to_enum(self, state: str) -> GameState:
        mapping = {
            'menu': GameState.MAIN_MENU,
            'playing': GameState.PLAYING,
            'paused': GameState.PAUSED,
            'inventory': GameState.INVENTORY,
        }
        return mapping.get(state, GameState.MAIN_MENU)


class GameSystems:
    """
    Центральный менеджер всех игровых систем.
    Координирует работу всех подсистем и обеспечивает их интеграцию.
    """
    
    def __init__(self):
        # Основные системы
        self.entity_manager = EntityManager()
        self.entity_factory = EntityFactory()
        self.resource_loader = ResourceLoader()
        self.game_state_manager = GameStateManager()
        self.render_system = GameRenderer()
        
        # Enhanced Edition системы
        self.enhanced_systems = {}
        self._init_enhanced_systems()
        
        # Дополнительные системы
        self.additional_systems = {}
        self._init_additional_systems()
        
        # Производительность
        self.performance_stats = defaultdict(float)
        self.last_update_time = time.time()
        
        # Кэш для оптимизации
        self._cache = {}
        self._cache_cleanup_timer = 0
        
        logger.info("Игровые системы инициализированы")
    
    def _init_enhanced_systems(self):
        """Инициализация Enhanced Edition систем"""
        enhanced_systems_list = [
            ('generational_memory', 'core.generational_memory_system', 'GenerationalMemorySystem'),
            ('emotional_ai', 'core.emotional_ai_influence', 'EmotionalAIInfluenceSystem'),
            ('enhanced_combat', 'core.enhanced_combat_learning', 'EnhancedCombatLearningSystem'),
            ('enhanced_content', 'core.enhanced_content_generator', 'EnhancedContentGenerator'),
            ('enhanced_skills', 'core.enhanced_skill_system', 'SkillManager'),
            ('enhanced_game_master', 'core.enhanced_game_master', 'EnhancedGameMaster'),
            ('curse_blessing', 'core.curse_blessing_system', 'CurseBlessingSystem'),
            ('risk_reward', 'core.risk_reward_system', 'RiskRewardSystem'),
            ('meta_progression', 'core.meta_progression_system', 'MetaProgressionSystem'),
            ('enhanced_inventory', 'core.enhanced_inventory_system', 'EnhancedInventorySystem'),
            ('enhanced_ui', 'core.enhanced_ui_system', 'EnhancedUISystem')
        ]
        
        for system_name, module_path, class_name in enhanced_systems_list:
            try:
                module = __import__(module_path, fromlist=[class_name])
                system_class = getattr(module, class_name)
                
                # Создаем экземпляр системы с базовыми параметрами
                if system_name == 'enhanced_game_master':
                    system_instance = system_class(1600, 900)
                elif system_name in ['generational_memory', 'emotional_ai', 'enhanced_combat']:
                    # Эти системы требуют зависимости
                    continue
                else:
                    system_instance = system_class()
                
                self.enhanced_systems[system_name] = system_instance
                logger.info(f"✅ Enhanced система {system_name} инициализирована")
                
            except ImportError as e:
                logger.debug(f"Enhanced система {system_name} недоступна: {e}")
            except Exception as e:
                logger.warning(f"Ошибка инициализации Enhanced системы {system_name}: {e}")
    
    def _init_additional_systems(self):
        """Инициализация дополнительных систем"""
        additional_systems_list = [
            ('trading', 'core.trading_system', 'TradingSystem'),
            ('social', 'core.social_system', 'SocialSystem'),
            ('quest', 'core.quest_system', 'QuestSystem'),
            ('crafting', 'core.crafting_system', 'CraftingSystem'),
            ('computer_vision', 'core.computer_vision_system', 'ComputerVisionSystem'),
            ('object_creation', 'core.object_creation_system', 'ObjectCreationSystem'),
            ('spatial', 'core.spatial_system', 'SpatialSystem'),
            ('session', 'core.session_manager', 'SessionManager'),
            ('ai', 'core.ai_system', 'AdaptiveAISystem'),
            ('genetic', 'core.genetic_system', 'AdvancedGeneticSystem'),
            ('emotion', 'core.emotion_system', 'AdvancedEmotionSystem'),
            ('evolution', 'core.evolution_system', 'EvolutionCycleSystem'),
            ('content_generator', 'core.content_generator', 'ContentGenerator'),
            ('global_events', 'core.global_event_system', 'GlobalEventSystem'),
            ('dynamic_difficulty', 'core.dynamic_difficulty', 'DynamicDifficultySystem'),
            ('isometric', 'core.isometric_system', 'IsometricProjection'),
            ('movement', 'core.movement_system', 'MovementSystem'),
            ('level_progression', 'core.level_progression', 'LevelProgressionSystem'),
            ('input_manager', 'core.input_manager', 'InputManager'),
            ('scene_manager', 'core.scene_manager', 'SceneManager')
        ]
        
        for system_name, module_path, class_name in additional_systems_list:
            try:
                module = __import__(module_path, fromlist=[class_name])
                system_class = getattr(module, class_name)
                
                # Создаем экземпляр системы
                if system_name in ['ai', 'genetic', 'emotion']:
                    # Эти системы требуют зависимости
                    continue
                else:
                    system_instance = system_class()
                
                self.additional_systems[system_name] = system_instance
                logger.info(f"✅ Дополнительная система {system_name} инициализирована")
                
            except ImportError as e:
                logger.debug(f"Дополнительная система {system_name} недоступна: {e}")
            except Exception as e:
                logger.warning(f"Ошибка инициализации дополнительной системы {system_name}: {e}")
    
    def initialize(self) -> bool:
        """Инициализация всех игровых систем"""
        try:
            # Инициализируем основные системы
            if not self.entity_manager.initialize():
                logger.error("Ошибка инициализации EntityManager")
                return False
            
            if not self.resource_loader.initialize():
                logger.error("Ошибка инициализации ResourceLoader")
                return False
            
            if not self.game_state_manager.initialize():
                logger.error("Ошибка инициализации GameStateManager")
                return False
            
            # Инициализируем Enhanced системы
            for system_name, system in self.enhanced_systems.items():
                if hasattr(system, 'initialize'):
                    try:
                        if not system.initialize():
                            logger.warning(f"Ошибка инициализации Enhanced системы {system_name}")
                    except Exception as e:
                        logger.warning(f"Ошибка инициализации Enhanced системы {system_name}: {e}")
            
            # Инициализируем дополнительные системы
            for system_name, system in self.additional_systems.items():
                if hasattr(system, 'initialize'):
                    try:
                        if not system.initialize():
                            logger.warning(f"Ошибка инициализации дополнительной системы {system_name}")
                    except Exception as e:
                        logger.warning(f"Ошибка инициализации дополнительной системы {system_name}: {e}")
            
            # Инициализируем производительность
            initialize_performance_monitoring()
            
            logger.info("Все игровые системы успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Критическая ошибка инициализации игровых систем: {e}")
            return False
    
    def handle_event(self, event) -> None:
        """Обработка событий всеми системами"""
        try:
            # Передаем событие в основные системы
            self.entity_manager.handle_event(event)
            self.game_state_manager.handle_event(event)
            
            # Передаем событие в Enhanced системы
            for system in self.enhanced_systems.values():
                if hasattr(system, 'handle_event'):
                    try:
                        system.handle_event(event)
                    except Exception as e:
                        logger.debug(f"Ошибка обработки события в Enhanced системе: {e}")
            
            # Передаем событие в дополнительные системы
            for system in self.additional_systems.values():
                if hasattr(system, 'handle_event'):
                    try:
                        system.handle_event(event)
                    except Exception as e:
                        logger.debug(f"Ошибка обработки события в дополнительной системе: {e}")
            
            # Глобальная система событий
            event_system.handle_event(event)
            
        except Exception as e:
            error_handler.handle_error(
                ErrorType.EVENT_HANDLING,
                f"Ошибка обработки события: {str(e)}",
                exception=e,
                severity=ErrorSeverity.WARNING
            )
    
    def update(self, delta_time: float) -> None:
        """Обновление всех игровых систем"""
        try:
            current_time = time.time()
            
            # Обновляем основные системы
            self.entity_manager.update(delta_time)
            self.game_state_manager.update(delta_time)
            
            # Обновляем Enhanced системы
            for system_name, system in self.enhanced_systems.items():
                if hasattr(system, 'update'):
                    try:
                        system.update(delta_time)
                    except Exception as e:
                        logger.debug(f"Ошибка обновления Enhanced системы {system_name}: {e}")
            
            # Обновляем дополнительные системы
            for system_name, system in self.additional_systems.items():
                if hasattr(system, 'update'):
                    try:
                        system.update(delta_time)
                    except Exception as e:
                        logger.debug(f"Ошибка обновления дополнительной системы {system_name}: {e}")
            
            # Обновляем производительность
            self._update_performance_stats(delta_time)
            
            # Очистка кэша
            self._cleanup_cache()
            
            self.last_update_time = current_time
            
        except Exception as e:
            error_handler.handle_error(
                ErrorType.GAME_UPDATE,
                f"Ошибка обновления игровых систем: {str(e)}",
                exception=e,
                severity=ErrorSeverity.ERROR
            )
    
    def render(self, screen) -> None:
        """Рендеринг всех игровых систем"""
        try:
            # Рендерим основные системы
            self.render_system.set_screen(screen)
            self.render_system.render()
            
            # Рендерим Enhanced системы
            for system in self.enhanced_systems.values():
                if hasattr(system, 'render'):
                    try:
                        system.render(screen)
                    except Exception as e:
                        logger.debug(f"Ошибка рендеринга Enhanced системы: {e}")
            
            # Рендерим дополнительные системы
            for system in self.additional_systems.values():
                if hasattr(system, 'render'):
                    try:
                        system.render(screen)
                    except Exception as e:
                        logger.debug(f"Ошибка рендеринга дополнительной системы: {e}")
            
        except Exception as e:
            error_handler.handle_error(
                ErrorType.RENDERING,
                f"Ошибка рендеринга игровых систем: {str(e)}",
                exception=e,
                severity=ErrorSeverity.ERROR
            )
    
    def _update_performance_stats(self, delta_time: float):
        """Обновление статистики производительности"""
        self.performance_stats['update_time'] += delta_time
        self.performance_stats['total_updates'] += 1
        self.performance_stats['avg_update_time'] = self.performance_stats['update_time'] / self.performance_stats['total_updates']
    
    def _cleanup_cache(self):
        """Очистка кэша для оптимизации памяти"""
        current_time = time.time()
        if current_time - self._cache_cleanup_timer >= 60:  # Каждую минуту
            # Очищаем старые записи кэша
            old_keys = [k for k, v in self._cache.items() if current_time - v.get('timestamp', 0) > 300]
            for key in old_keys:
                del self._cache[key]
            
            self._cache_cleanup_timer = current_time
    
    def get_system(self, system_name: str) -> Optional[Any]:
        """Получение системы по имени"""
        # Проверяем Enhanced системы
        if system_name in self.enhanced_systems:
            return self.enhanced_systems[system_name]
        
        # Проверяем дополнительные системы
        if system_name in self.additional_systems:
            return self.additional_systems[system_name]
        
        # Проверяем основные системы
        if hasattr(self, system_name):
            return getattr(self, system_name)
        
        return None
    
    def get_all_systems(self) -> Dict[str, Any]:
        """Получение всех систем"""
        all_systems = {}
        
        # Основные системы
        all_systems.update({
            'entity_manager': self.entity_manager,
            'entity_factory': self.entity_factory,
            'resource_loader': self.resource_loader,
            'game_state_manager': self.game_state_manager,
            'render_system': self.render_system
        })
        
        # Enhanced системы
        all_systems.update(self.enhanced_systems)
        
        # Дополнительные системы
        all_systems.update(self.additional_systems)
        
        return all_systems
    
    def get_system_status(self) -> Dict[str, str]:
        """Получение статуса всех систем"""
        status = {}
        
        # Основные системы
        status['entity_manager'] = 'active' if self.entity_manager else 'inactive'
        status['resource_loader'] = 'active' if self.resource_loader else 'inactive'
        status['game_state_manager'] = 'active' if self.game_state_manager else 'inactive'
        status['render_system'] = 'active' if self.render_system else 'inactive'
        
        # Enhanced системы
        for system_name, system in self.enhanced_systems.items():
            status[f'enhanced_{system_name}'] = 'active' if system else 'inactive'
        
        # Дополнительные системы
        for system_name, system in self.additional_systems.items():
            status[f'additional_{system_name}'] = 'active' if system else 'inactive'
        
        return status
    
    def cleanup_cache(self):
        """Очистка кэша всех систем"""
        try:
            # Очищаем локальный кэш
            self._cache.clear()
            
            # Очищаем кэш Enhanced систем
            for system in self.enhanced_systems.values():
                if hasattr(system, 'cleanup_cache'):
                    try:
                        system.cleanup_cache()
                    except Exception:
                        pass
            
            # Очищаем кэш дополнительных систем
            for system in self.additional_systems.values():
                if hasattr(system, 'cleanup_cache'):
                    try:
                        system.cleanup_cache()
                    except Exception:
                        pass
            
            logger.debug("Кэш всех систем очищен")
            
        except Exception as e:
            logger.warning(f"Ошибка при очистке кэша: {e}")
    
    def cleanup(self):
        """Очистка всех игровых систем"""
        try:
            logger.info("Очистка игровых систем")
            
            # Очищаем основные системы
            if hasattr(self.entity_manager, 'cleanup'):
                self.entity_manager.cleanup()
            if hasattr(self.resource_loader, 'cleanup'):
                self.resource_loader.cleanup()
            if hasattr(self.game_state_manager, 'cleanup'):
                self.game_state_manager.cleanup()
            
            # Очищаем Enhanced системы
            for system_name, system in self.enhanced_systems.items():
                if hasattr(system, 'cleanup'):
                    try:
                        system.cleanup()
                    except Exception as e:
                        logger.debug(f"Ошибка очистки Enhanced системы {system_name}: {e}")
            
            # Очищаем дополнительные системы
            for system_name, system in self.additional_systems.items():
                if hasattr(system, 'cleanup'):
                    try:
                        system.cleanup()
                    except Exception as e:
                        logger.debug(f"Ошибка очистки дополнительной системы {system_name}: {e}")
            
            # Очищаем кэш
            self.cleanup_cache()
            
            # Принудительная сборка мусора
            gc.collect()
            
            logger.info("Очистка игровых систем завершена")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке игровых систем: {e}")
    
    def __del__(self):
        """Деструктор для автоматической очистки"""
        self.cleanup()

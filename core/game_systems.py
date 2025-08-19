"""
Системы игрового цикла
Разделение ответственностей из оригинального game_loop.py
"""

import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

from .entity_system import EntityManager, EntityFactory
from .resource_loader import ResourceLoader
from .error_handler import ErrorHandler, ErrorType, ErrorSeverity
from .components.transform_component import Vector3
from config.config_factory import config_factory, ConfigType

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
        
        self.current_world.weather = random.choices(
            self.weather_options, 
            weights=self.weather_weights
        )[0]
        
        logger.info(f"Погода изменилась на: {self.current_world.weather}")
    
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
            "explored_percent": self.current_world.explored_percent,
            "weather": self.current_world.weather,
            "time_of_day": self.current_world.time_of_day,
            "day_cycle": self.current_world.day_cycle,
            "ecosystem": self.ecosystem.copy(),
            "active_events": len(self.active_events)
        }


class EventSystem:
    """
    Система событий.
    Отвечает только за управление событиями.
    """
    
    def __init__(self):
        self.event_handlers: Dict[str, List[callable]] = {}
        self.event_queue = []
        self.event_history = []
    
    def register_handler(self, event_type: str, handler: callable) -> None:
        """Регистрация обработчика события"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: str, data: Any = None) -> None:
        """Отправка события"""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }
        
        self.event_queue.append(event)
        logger.debug(f"Событие добавлено в очередь: {event_type}")
    
    def process_events(self) -> None:
        """Обработка событий в очереди"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            
            # Добавляем в историю
            self.event_history.append(event)
            
            # Вызываем обработчики
            if event['type'] in self.event_handlers:
                for handler in self.event_handlers[event['type']]:
                    try:
                        handler(event['data'])
                    except Exception as e:
                        logger.error(f"Ошибка в обработчике события {event['type']}: {e}")
            
            logger.debug(f"Событие обработано: {event['type']}")


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
    
    def set_screen(self, screen) -> None:
        """Установка экрана для отрисовки"""
        self.screen = screen
    
    def set_camera_offset(self, offset: Tuple[float, float]) -> None:
        """Установка смещения камеры"""
        self.camera_offset = offset
    
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
                        
        except Exception as e:
            logger.error(f"Ошибка рендеринга: {e}")


class GameStateManager:
    """
    Менеджер состояния игры.
    Отвечает только за управление состоянием игры.
    """
    
    def __init__(self):
        self.current_state = "menu"
        self.previous_state = None
        self.state_handlers = {}
        self.state_data = {}
    
    def register_state_handler(self, state: str, handler: callable) -> None:
        """Регистрация обработчика состояния"""
        self.state_handlers[state] = handler
    
    def change_state(self, new_state: str, data: Any = None) -> None:
        """Смена состояния игры"""
        self.previous_state = self.current_state
        self.current_state = new_state
        
        if data:
            self.state_data[new_state] = data
        
        logger.info(f"Состояние игры изменено: {self.previous_state} -> {new_state}")
    
    def get_current_state(self) -> str:
        """Получение текущего состояния"""
        return self.current_state
    
    def get_state_data(self, state: str = None) -> Any:
        """Получение данных состояния"""
        if state is None:
            state = self.current_state
        return self.state_data.get(state)
    
    def update_state(self, delta_time: float) -> None:
        """Обновление текущего состояния"""
        if self.current_state in self.state_handlers:
            try:
                self.state_handlers[self.current_state](delta_time)
            except Exception as e:
                logger.error(f"Ошибка обновления состояния {self.current_state}: {e}")


class GameSystems:
    """
    Объединяет все игровые системы.
    Координирует работу различных систем.
    """
    
    def __init__(self):
        # Инициализация систем
        self.world_manager = WorldManager()
        self.event_system = EventSystem()
        self.render_system = RenderSystem()
        self.state_manager = GameStateManager()
        
        # Системы сущностей
        self.resource_loader = ResourceLoader()
        self.entity_manager = EntityManager()
        self.entity_factory = EntityFactory(self.entity_manager, self.resource_loader)
        
        # Обработчик ошибок
        self.error_handler = ErrorHandler()
        
        # Время игры
        self.game_time = 0.0
        self.delta_time = 0.0
        self.last_update = time.time()
        
        # Статистика
        self.fps_counter = 0
        self.fps = 0
        self.last_fps_update = 0.0
        
        # Настройки
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps
        
        logger.info("Игровые системы инициализированы")
    
    def initialize(self) -> bool:
        """Инициализация всех систем"""
        try:
            # Загружаем конфигурацию
            game_config = config_factory.create_config(ConfigType.GAME_SETTINGS)
            self.target_fps = game_config.get('display', {}).get('render_fps', 60)
            self.frame_time = 1.0 / self.target_fps
            
            # Создаем мир
            self.world_manager.create_world()
            
            # Регистрируем обработчики событий
            self._register_event_handlers()
            
            # Регистрируем обработчики состояний
            self._register_state_handlers()
            
            logger.info("Все системы успешно инициализированы")
            return True
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.CONFIGURATION,
                f"Ошибка инициализации игровых систем: {str(e)}",
                exception=e,
                severity=ErrorSeverity.CRITICAL
            )
            return False
    
    def _register_event_handlers(self):
        """Регистрация обработчиков событий"""
        self.event_system.register_handler('entity_created', self._on_entity_created)
        self.event_system.register_handler('entity_destroyed', self._on_entity_destroyed)
        self.event_system.register_handler('world_changed', self._on_world_changed)
    
    def _register_state_handlers(self):
        """Регистрация обработчиков состояний"""
        self.state_manager.register_state_handler('menu', self._update_menu_state)
        self.state_manager.register_state_handler('playing', self._update_playing_state)
        self.state_manager.register_state_handler('paused', self._update_paused_state)
    
    def update(self, delta_time: float) -> None:
        """Обновление всех систем"""
        try:
            self.delta_time = delta_time
            self.game_time += delta_time
            
            # Обновляем время FPS
            self.fps_counter += 1
            if self.game_time - self.last_fps_update >= 1.0:
                self.fps = self.fps_counter
                self.fps_counter = 0
                self.last_fps_update = self.game_time
            
            # Обновляем системы
            self.world_manager.update_world_time(delta_time)
            self.event_system.process_events()
            self.entity_manager.update_entities(delta_time)
            self.state_manager.update_state(delta_time)
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.UNKNOWN,
                f"Ошибка обновления игровых систем: {str(e)}",
                exception=e,
                severity=ErrorSeverity.ERROR
            )
    
    def render(self) -> None:
        """Отрисовка всех систем"""
        try:
            self.render_system.render()
        except Exception as e:
            self.error_handler.handle_error(
                ErrorType.RENDERING,
                f"Ошибка рендеринга: {str(e)}",
                exception=e,
                severity=ErrorSeverity.ERROR
            )
    
    def _on_entity_created(self, entity_data):
        """Обработчик создания сущности"""
        entity_type = entity_data.get('type', 'unknown')
        self.world_manager.update_ecosystem(entity_type, 1)
    
    def _on_entity_destroyed(self, entity_data):
        """Обработчик уничтожения сущности"""
        entity_type = entity_data.get('type', 'unknown')
        self.world_manager.update_ecosystem(entity_type, -1)
    
    def _on_world_changed(self, world_data):
        """Обработчик изменения мира"""
        logger.info(f"Мир изменен: {world_data}")
    
    def _update_menu_state(self, delta_time: float):
        """Обновление состояния меню"""
        pass
    
    def _update_playing_state(self, delta_time: float):
        """Обновление состояния игры"""
        pass
    
    def _update_paused_state(self, delta_time: float):
        """Обновление состояния паузы"""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики всех систем"""
        return {
            'game_time': self.game_time,
            'fps': self.fps,
            'world': self.world_manager.get_world_info(),
            'entities': self.entity_manager.get_statistics(),
            'errors': self.error_handler.get_error_statistics()
        }
    
    def cleanup(self) -> None:
        """Очистка ресурсов"""
        try:
            # Очищаем сущности
            for entity_id in list(self.entity_manager.entities.keys()):
                self.entity_manager.destroy_entity(entity_id)
            
            # Очищаем кэш ресурсов
            self.resource_loader.clear_cache()
            
            logger.info("Ресурсы игровых систем очищены")
            
        except Exception as e:
            logger.error(f"Ошибка очистки ресурсов: {e}")

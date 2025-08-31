#!/usr/bin/env python3
"""Scene Manager - управление игровыми сценами"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState
from src.core.constants import constants_manager, SceneType, SceneState
from src.core.state_manager import StateManager, StateType

logger = logging.getLogger(__name__)

class SceneType(Enum):
    """Типы сцен"""
    MAIN_MENU = "main_menu"
    GAME_WORLD = "game_world"
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    INVENTORY = "inventory"
    SKILL_TREE = "skill_tree"
    MAP = "map"
    SETTINGS = "settings"
    LOADING = "loading"
    CREDITS = "credits"

class SceneState(Enum):
    """Состояния сцен"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    ACTIVE = "active"
    PAUSED = "paused"
    TRANSITIONING = "transitioning"
    UNLOADING = "unloading"

@dataclass
class SceneData:
    """Данные сцены"""
    scene_id: str
    scene_type: SceneType
    scene_name: str
    scene_file: str
    properties: Dict[str, Any] = field(default_factory=dict)
    entities: List[str] = field(default_factory=list)
    ui_elements: List[str] = field(default_factory=list)
    background_music: Optional[str] = None
    ambient_sounds: List[str] = field(default_factory=list)

@dataclass
class SceneTransition:
    """Переход между сценами"""
    from_scene: str
    to_scene: str
    transition_type: str = "fade"
    duration: float = 1.0
    callback: Optional[Callable] = None

class SceneManager(BaseComponent):
    """Менеджер игровых сцен"""
    
    def __init__(self):
        super().__init__(
            system_name="scene_manager",
            system_priority=Priority.HIGH,
            system_type=ComponentType.SYSTEM
        )
        
        # Архитектурные компоненты
        self.state_manager: Optional[StateManager] = None
        
        # Сцены и переходы
        self.scenes: Dict[str, SceneData] = {}
        self.active_scene: Optional[str] = None
        self.previous_scene: Optional[str] = None
        self.scene_stack: List[str] = []
        
        # Переходы
        self.current_transition: Optional[SceneTransition] = None
        self.transition_queue: List[SceneTransition] = []
        
        # Настройки сцен
        self.scene_settings = {
            'auto_save_on_scene_change': True,
            'preload_adjacent_scenes': True,
            'scene_transition_effects': True,
            'scene_loading_timeout': 30.0,
            'max_scene_stack_size': 10
        }
        
        # Статистика сцен
        self.scene_stats = {
            'total_scenes': 0,
            'scenes_loaded': 0,
            'scenes_unloaded': 0,
            'scene_transitions': 0,
            'current_scene_time': 0.0,
            'total_scene_time': 0.0,
            'update_time': 0.0
        }
    
    def set_architecture_components(self, state_manager: StateManager):
        """Установка архитектурных компонентов"""
        self.state_manager = state_manager
        logger.info("Архитектурные компоненты установлены в SceneManager")
    
    def _register_system_states(self):
        """Регистрация состояний системы"""
        if self.state_manager:
            # Регистрируем состояния сцен
            self.state_manager.set_state(
                f"{self.system_name}_settings",
                self.scene_settings,
                StateType.SETTINGS
            )
            
            self.state_manager.set_state(
                f"{self.system_name}_stats",
                self.scene_stats,
                StateType.STATISTICS
            )
            
            self.state_manager.set_state(
                f"{self.system_name}_state",
                self.system_state,
                StateType.SYSTEM_STATE
            )
    
    def initialize(self) -> bool:
        """Инициализация менеджера сцен"""
        try:
            logger.info("Инициализация SceneManager...")
            
            # Регистрируем состояния системы
            self._register_system_states()
            
            # Создаем базовые сцены
            self._create_default_scenes()
            
            # Загружаем настройки сцен
            self._load_scene_settings()
            
            self.system_state = LifecycleState.READY
            logger.info("SceneManager инициализирован успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации SceneManager: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def start(self) -> bool:
        """Запуск менеджера сцен"""
        try:
            logger.info("Запуск SceneManager...")
            
            if self.system_state != LifecycleState.READY:
                logger.error("SceneManager не готов к запуску")
                return False
            
            # Активируем начальную сцену
            if self.scenes:
                first_scene = list(self.scenes.keys())[0]
                self.load_scene(first_scene)
            
            self.system_state = LifecycleState.RUNNING
            logger.info("SceneManager запущен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска SceneManager: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def update(self, delta_time: float):
        """Обновление менеджера сцен"""
        if self.system_state != LifecycleState.RUNNING:
            return
        
        try:
            start_time = time.time()
            
            # Обновляем активную сцену
            self._update_active_scene(delta_time)
            
            # Обрабатываем переходы
            self._process_transitions(delta_time)
            
            # Обновляем статистику
            self.scene_stats['current_scene_time'] += delta_time
            self.scene_stats['total_scene_time'] += delta_time
            self.scene_stats['update_time'] = time.time() - start_time
            
            # Обновляем состояние в менеджере состояний
            if self.state_manager:
                self.state_manager.set_state(
                    f"{self.system_name}_stats",
                    self.scene_stats,
                    StateType.STATISTICS
                )
                
        except Exception as e:
            logger.error(f"Ошибка обновления SceneManager: {e}")
    
    def stop(self) -> bool:
        """Остановка менеджера сцен"""
        try:
            logger.info("Остановка SceneManager...")
            
            # Выгружаем все сцены
            for scene_id in list(self.scenes.keys()):
                self.unload_scene(scene_id)
            
            self.system_state = LifecycleState.STOPPED
            logger.info("SceneManager остановлен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки SceneManager: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение менеджера сцен"""
        try:
            logger.info("Уничтожение SceneManager...")
            
            # Очищаем все сцены
            self.scenes.clear()
            self.scene_stack.clear()
            self.transition_queue.clear()
            
            self.system_state = LifecycleState.DESTROYED
            logger.info("SceneManager уничтожен успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения SceneManager: {e}")
            return False
    
    def _create_default_scenes(self):
        """Создание базовых сцен"""
        # Создаем главное меню
        main_menu = SceneData(
            scene_id="main_menu",
            scene_type=SceneType.MAIN_MENU,
            scene_name="Главное меню",
            scene_file="scenes/main_menu.json",
            background_music="music/main_menu.ogg"
        )
        
        # Создаем игровой мир
        game_world = SceneData(
            scene_id="game_world",
            scene_type=SceneType.GAME_WORLD,
            scene_name="Игровой мир",
            scene_file="scenes/game_world.json",
            background_music="music/game_world.ogg",
            ambient_sounds=["sounds/ambient_forest.ogg", "sounds/ambient_wind.ogg"]
        )
        
        # Создаем сцену боя
        combat = SceneData(
            scene_id="combat",
            scene_type=SceneType.COMBAT,
            scene_name="Бой",
            scene_file="scenes/combat.json",
            background_music="music/combat.ogg"
        )
        
        # Добавляем сцены
        self.scenes["main_menu"] = main_menu
        self.scenes["game_world"] = game_world
        self.scenes["combat"] = combat
        
        self.scene_stats['total_scenes'] = len(self.scenes)
    
    def _load_scene_settings(self):
        """Загрузка настроек сцен"""
        try:
            # Загружаем настройки из менеджера констант
            scene_constants = constants_manager.get_scene_settings()
            if scene_constants:
                self.scene_settings.update(scene_constants)
            
            logger.info("Настройки сцен загружены")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек сцен: {e}")
    
    def _update_active_scene(self, delta_time: float):
        """Обновление активной сцены"""
        if self.active_scene and self.active_scene in self.scenes:
            # Обновляем активную сцену
            scene = self.scenes[self.active_scene]
            self._update_scene(scene, delta_time)
    
    def _update_scene(self, scene: SceneData, delta_time: float):
        """Обновление отдельной сцены"""
        # Здесь будет логика обновления сцены
        pass
    
    def _process_transitions(self, delta_time: float):
        """Обработка переходов между сценами"""
        if self.current_transition:
            # Обрабатываем текущий переход
            self._update_transition(self.current_transition, delta_time)
        elif self.transition_queue:
            # Начинаем следующий переход
            self.current_transition = self.transition_queue.pop(0)
            self._start_transition(self.current_transition)
    
    def _update_transition(self, transition: SceneTransition, delta_time: float):
        """Обновление перехода"""
        # Здесь будет логика обновления перехода
        pass
    
    def _start_transition(self, transition: SceneTransition):
        """Начало перехода"""
        try:
            logger.info(f"Начало перехода: {transition.from_scene} -> {transition.to_scene}")
            
            # Здесь будет логика начала перехода
            
        except Exception as e:
            logger.error(f"Ошибка начала перехода: {e}")
    
    def create_scene(self, scene_id: str, scene_type: SceneType, scene_name: str, 
                    scene_file: str) -> Optional[SceneData]:
        """Создание новой сцены"""
        try:
            if scene_id in self.scenes:
                logger.warning(f"Сцена с ID {scene_id} уже существует")
                return None
            
            scene = SceneData(
                scene_id=scene_id,
                scene_type=scene_type,
                scene_name=scene_name,
                scene_file=scene_file
            )
            
            self.scenes[scene_id] = scene
            self.scene_stats['total_scenes'] = len(self.scenes)
            
            logger.info(f"Создана сцена: {scene_id}")
            return scene
            
        except Exception as e:
            logger.error(f"Ошибка создания сцены {scene_id}: {e}")
            return None
    
    def load_scene(self, scene_id: str) -> bool:
        """Загрузка сцены"""
        try:
            if scene_id not in self.scenes:
                logger.warning(f"Сцена с ID {scene_id} не найдена")
                return False
            
            # Сохраняем предыдущую сцену
            if self.active_scene:
                self.previous_scene = self.active_scene
                self.scene_stack.append(self.active_scene)
                
                # Ограничиваем размер стека
                if len(self.scene_stack) > self.scene_settings['max_scene_stack_size']:
                    self.scene_stack.pop(0)
            
            # Активируем новую сцену
            self.active_scene = scene_id
            self.scene_stats['scenes_loaded'] += 1
            self.scene_stats['current_scene_time'] = 0.0
            
            logger.info(f"Загружена сцена: {scene_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки сцены {scene_id}: {e}")
            return False
    
    def unload_scene(self, scene_id: str) -> bool:
        """Выгрузка сцены"""
        try:
            if scene_id not in self.scenes:
                logger.warning(f"Сцена с ID {scene_id} не найдена")
                return False
            
            # Если это активная сцена, деактивируем её
            if self.active_scene == scene_id:
                self.active_scene = None
            
            # Удаляем из стека
            if scene_id in self.scene_stack:
                self.scene_stack.remove(scene_id)
            
            self.scene_stats['scenes_unloaded'] += 1
            
            logger.info(f"Выгружена сцена: {scene_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка выгрузки сцены {scene_id}: {e}")
            return False
    
    def transition_to_scene(self, to_scene: str, transition_type: str = "fade", 
                          duration: float = 1.0, callback: Optional[Callable] = None) -> bool:
        """Переход к сцене"""
        try:
            if to_scene not in self.scenes:
                logger.warning(f"Сцена с ID {to_scene} не найдена")
                return False
            
            transition = SceneTransition(
                from_scene=self.active_scene or "",
                to_scene=to_scene,
                transition_type=transition_type,
                duration=duration,
                callback=callback
            )
            
            self.transition_queue.append(transition)
            self.scene_stats['scene_transitions'] += 1
            
            logger.info(f"Добавлен переход к сцене: {to_scene}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания перехода к сцене {to_scene}: {e}")
            return False
    
    def go_back(self) -> bool:
        """Возврат к предыдущей сцене"""
        try:
            if not self.scene_stack:
                logger.warning("Нет предыдущих сцен для возврата")
                return False
            
            previous_scene = self.scene_stack.pop()
            return self.load_scene(previous_scene)
            
        except Exception as e:
            logger.error(f"Ошибка возврата к предыдущей сцене: {e}")
            return False
    
    def get_scene(self, scene_id: str) -> Optional[SceneData]:
        """Получение сцены"""
        return self.scenes.get(scene_id)
    
    def get_active_scene_data(self) -> Optional[SceneData]:
        """Получение данных активной сцены"""
        if self.active_scene:
            return self.scenes.get(self.active_scene)
        return None
    
    def get_all_scenes(self) -> Dict[str, SceneData]:
        """Получение всех сцен"""
        return self.scenes.copy()
    
    def get_scene_stack(self) -> List[str]:
        """Получение стека сцен"""
        return self.scene_stack.copy()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'total_scenes': self.scene_stats['total_scenes'],
            'scenes_loaded': self.scene_stats['scenes_loaded'],
            'scenes_unloaded': self.scene_stats['scenes_unloaded'],
            'scene_transitions': self.scene_stats['scene_transitions'],
            'active_scene': self.active_scene,
            'previous_scene': self.previous_scene,
            'scene_stack_size': len(self.scene_stack),
            'current_scene_time': self.scene_stats['current_scene_time'],
            'total_scene_time': self.scene_stats['total_scene_time'],
            'update_time': self.scene_stats['update_time']
        }
    
    def reset_stats(self):
        """Сброс статистики"""
        self.scene_stats = {
            'total_scenes': len(self.scenes),
            'scenes_loaded': 0,
            'scenes_unloaded': 0,
            'scene_transitions': 0,
            'current_scene_time': 0.0,
            'total_scene_time': 0.0,
            'update_time': 0.0
        }

#!/usr/bin/env python3
"""
Game Engine - Основной игровой движок на Panda3D
Упрощенная архитектура с четким разделением ответственности
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Panda3D imports
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import WindowProperties

# Новая архитектура
from .architecture import ComponentManager, EventBus, Priority, ComponentType, LifecycleState
from .state_manager import StateManager, StateType
from .repository import RepositoryManager, DataType, StorageType

logger = logging.getLogger(__name__)

class GameEngine(ShowBase):
    """
    Основной игровой движок на Panda3D
    Упрощенная архитектура с четким разделением ответственности
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Инициализация Panda3D ShowBase
        super().__init__()
        
        self.settings = config
        self.running = False
        self.paused = False
        
        # Состояние игры
        self.current_state = "initializing"
        self.delta_time = 0.0
        self.last_frame_time = time.time()
        
        # Статистика
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Новая архитектура - основные менеджеры
        self.component_manager: Optional[ComponentManager] = None
        self.event_bus: Optional[EventBus] = None
        self.state_manager: Optional[StateManager] = None
        self.repository_manager: Optional[RepositoryManager] = None
        
        # Адаптеры для существующих систем (только для совместимости)
        self._legacy_adapters = {}
        
        logger.info("Игровой движок Panda3D с упрощенной архитектурой инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация игрового движка"""
        try:
            logger.info("Начало инициализации игрового движка Panda3D...")
            
            # Инициализация Panda3D
            if not self._initialize_panda3d():
                return False
            
            # Инициализация менеджеров новой архитектуры
            if not self._initialize_new_architecture():
                return False
            
            # Создание адаптеров для существующих систем
            if not self._create_legacy_adapters():
                return False
            
            # Привязываем глобальные клавиши управления
            self._bind_global_inputs()
            
            # Настройка задач
            self._setup_tasks()
            
            self.current_state = "ready"
            logger.info("Игровой движок успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Критическая ошибка инициализации: {e}")
            self.current_state = "error"
            return False
    
    def _initialize_panda3d(self) -> bool:
        """Инициализация базового Panda3D"""
        try:
            # Настройка окна
            props = WindowProperties()
            props.setTitle("AI-EVOLVE: Эволюционная Адаптация")
            props.setSize(1280, 720)
            props.setCursorHidden(False)
            
            # Применяем настройки
            self.openMainWindow(props=props)
            
            # Настройка камеры
            self.camera.setPos(0, -20, 10)
            self.camera.lookAt(0, 0, 0)

            logger.info("Panda3D успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Panda3D: {e}")
            return False
    
    def _initialize_new_architecture(self) -> bool:
        """Инициализация новой архитектуры"""
        try:
            # Создаем менеджер компонентов
            self.component_manager = ComponentManager()
            
            # Создаем шину событий
            self.event_bus = EventBus()
            
            # Создаем менеджер состояний
            self.state_manager = StateManager()
            
            # Создаем менеджер репозиториев
            self.repository_manager = RepositoryManager()
            
            # Регистрируем основные компоненты
            self.component_manager.register_component(self.event_bus)
            self.component_manager.register_component(self.state_manager)
            self.component_manager.register_component(self.repository_manager)
            
            # Инициализируем все компоненты
            if not self.component_manager.initialize_all():
                logger.error("Ошибка инициализации компонентов")
                return False
            
            logger.info("Новая архитектура инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации новой архитектуры: {e}")
            return False
    
    def _create_legacy_adapters(self) -> bool:
        """Создание адаптеров для существующих систем"""
        try:
            # Адаптер для AI систем
            try:
                from ..systems.ai.ai_integration_system import AIIntegrationSystem
                ai_system = AIIntegrationSystem()
                self.component_manager.register_component(ai_system)
                self._legacy_adapters['ai'] = ai_system
                logger.info("Адаптер для AI систем создан")
            except ImportError as e:
                logger.warning(f"AI системы недоступны: {e}")
            
            # Адаптер для боевой системы
            try:
                from ..systems.combat.combat_system import CombatSystem
                combat_system = CombatSystem()
                self.component_manager.register_component(combat_system)
                self._legacy_adapters['combat'] = combat_system
                logger.info("Адаптер для боевой системы создан")
            except ImportError as e:
                logger.warning(f"Боевая система недоступна: {e}")
            
            # Адаптер для системы эффектов
            try:
                from ..systems.effects.effect_system import EffectSystem
                effect_system = EffectSystem()
                self.component_manager.register_component(effect_system)
                self._legacy_adapters['effects'] = effect_system
                logger.info("Адаптер для системы эффектов создан")
            except ImportError as e:
                logger.warning(f"Система эффектов недоступна: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания адаптеров: {e}")
            return False
    
    def _bind_global_inputs(self):
        """Привязка глобальных клавиш управления"""
        try:
            # Переключение сцен
            self.accept("escape", self.toggle_pause)
            self.accept("f1", self.show_debug_info)
            self.accept("f2", self.toggle_performance_monitor)
            
            logger.info("Глобальные клавиши привязаны")
            
        except Exception as e:
            logger.error(f"Ошибка привязки клавиш: {e}")
    
    def _setup_tasks(self):
        """Настройка игровых задач"""
        try:
            # Основной игровой цикл
            self.taskMgr.add(self._game_loop, "game_loop")
            
            # Обновление компонентов
            self.taskMgr.add(self._update_components, "update_components")
            
            # Обновление FPS
            self.taskMgr.add(self._update_fps, "update_fps")
            
            logger.info("Игровые задачи настроены")
            
        except Exception as e:
            logger.error(f"Ошибка настройки задач: {e}")
    
    def start(self) -> bool:
        """Запуск игрового движка"""
        try:
            if self.current_state != "ready":
                logger.error("Движок не готов к запуску")
                return False
            
            logger.info("Запуск игрового движка...")
            
            # Запускаем все компоненты
            if not self.component_manager.start_all():
                logger.error("Ошибка запуска компонентов")
                return False
            
            self.running = True
            self.current_state = "running"
            
            logger.info("Игровой движок запущен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска движка: {e}")
            return False
    
    def stop(self) -> bool:
        """Остановка игрового движка"""
        try:
            logger.info("Остановка игрового движка...")
            
            # Останавливаем все компоненты
            if self.component_manager:
                self.component_manager.stop_all()
            
            self.running = False
            self.current_state = "stopped"
            
            logger.info("Игровой движок остановлен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки движка: {e}")
            return False
    
    def toggle_pause(self):
        """Переключение паузы"""
        if self.running:
            if self.paused:
                self.resume()
            else:
                self.pause()
    
    def pause(self):
        """Приостановка игры"""
        if self.running and not self.paused:
            self.paused = True
            self.current_state = "paused"
            logger.info("Игра приостановлена")
    
    def resume(self):
        """Возобновление игры"""
        if self.running and self.paused:
            self.paused = False
            self.current_state = "running"
            logger.info("Игра возобновлена")
    
    def show_debug_info(self):
        """Показать отладочную информацию"""
        if self.component_manager:
            metrics = self._get_system_metrics()
            logger.info(f"Системные метрики: {metrics}")
    
    def toggle_performance_monitor(self):
        """Переключение монитора производительности"""
        # Реализация монитора производительности
        pass
    
    def _game_loop(self, task):
        """Основной игровой цикл"""
        try:
            if not self.running or self.paused:
                return Task.cont
            
            # Обновляем время
            current_time = time.time()
            self.delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Обновляем счетчик кадров
            self.frame_count += 1
            
            return Task.cont
            
        except Exception as e:
            logger.error(f"Ошибка в игровом цикле: {e}")
            return Task.cont
    
    def _update_components(self, task):
        """Обновление компонентов"""
        try:
            if not self.running or self.paused:
                return Task.cont
            
            # Обновляем компоненты с ограничением по времени
            start_time = time.time()
            max_update_time = 0.016  # 16ms max
            
            # Здесь будет обновление компонентов по приоритету
            
            return Task.cont
            
        except Exception as e:
            logger.error(f"Ошибка обновления компонентов: {e}")
            return Task.cont
    
    def _update_fps(self, task):
        """Обновление FPS"""
        try:
            current_time = time.time()
            elapsed = current_time - self.start_time
            
            if elapsed >= 1.0:  # Обновляем FPS раз в секунду
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.start_time = current_time
                
                # Логируем FPS каждые 5 секунд
                if int(current_time) % 5 == 0:
                    logger.debug(f"FPS: {self.fps:.1f}")
            
            return Task.cont
            
        except Exception as e:
            logger.error(f"Ошибка обновления FPS: {e}")
            return Task.cont
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Получение системных метрик"""
        metrics = {
            'game_state': self.current_state,
            'running': self.running,
            'paused': self.paused,
            'fps': self.fps,
            'frame_count': self.frame_count,
            'delta_time': self.delta_time
        }
        
        # Метрики компонентов
        if self.component_manager:
            component_metrics = {}
            for component_type in ComponentType:
                components = self.component_manager.get_components_by_type(component_type)
                component_metrics[component_type.value] = len(components)
            
            metrics['components'] = component_metrics
        
        return metrics
    
    def get_component(self, component_type: ComponentType, component_id: str = None):
        """Получение компонента по типу и ID"""
        if not self.component_manager:
            return None
        
        if component_id:
            return self.component_manager.get_component(component_id)
        else:
            components = self.component_manager.get_components_by_type(component_type)
            return components[0] if components else None
    
    def publish_event(self, event_type: str, data: Any = None):
        """Публикация события"""
        if self.event_bus:
            return self.event_bus.publish(event_type, data)
        return False
    
    def subscribe_to_event(self, event_type: str, callback):
        """Подписка на событие"""
        if self.event_bus:
            return self.event_bus.subscribe(event_type, callback)
        return False

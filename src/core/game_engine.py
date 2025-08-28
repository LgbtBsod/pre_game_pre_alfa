#!/usr/bin/env python3
"""
Game Engine - Основной игровой движок на Panda3D
Отвечает только за координацию всех систем и управление жизненным циклом игры
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

from .interfaces import SystemState, ISystemManager, IEventSystem
from .system_manager import SystemManager
from .event_system import EventSystem
from .config_manager import ConfigManager
from .scene_manager import SceneManager
from .resource_manager import ResourceManager
from .performance_manager import PerformanceManager
from .system_factory import SystemFactory

logger = logging.getLogger(__name__)

class GameEngine(ShowBase):
    """
    Основной игровой движок на Panda3D
    Координирует все системы и управляет жизненным циклом игры
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Инициализация Panda3D ShowBase
        super().__init__()
        
        self.settings = config
        self.running = False
        self.paused = False
        
        # Состояние игры
        self.current_state = SystemState.INITIALIZING
        self.delta_time = 0.0
        self.last_frame_time = time.time()
        
        # Статистика
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Новая архитектура - менеджеры систем
        self.system_manager: Optional[SystemManager] = None
        self.event_system: Optional[EventSystem] = None
        self.system_factory: Optional[SystemFactory] = None
        
        # Существующие менеджеры (для обратной совместимости)
        self.scene_manager: Optional[SceneManager] = None
        self.resource_manager: Optional[ResourceManager] = None
        self.performance_manager: Optional[PerformanceManager] = None
        
        logger.info("Игровой движок Panda3D инициализирован")
    
    def initialize(self) -> bool:
        """Инициализация игрового движка"""
        try:
            logger.info("Начало инициализации игрового движка Panda3D...")
            
            # Инициализация Panda3D
            if not self._initialize_panda3d():
                return False
            
            # Инициализация менеджеров
            if not self._initialize_managers():
                return False
            
            # Инициализация сцен
            if not self._initialize_scenes():
                return False
            
            # Привязываем глобальные клавиши управления сценами
            self._bind_global_inputs()
            
            # Настройка задач
            self._setup_tasks()
            
            self.current_state = SystemState.READY
            logger.info("Игровой движок Panda3D успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации игрового движка: {e}")
            return False
    
    def _initialize_panda3d(self) -> bool:
        """Инициализация Panda3D"""
        try:
            # Настройка окна (окно уже создано ShowBase)
            display_config = self.settings.get('display', {})
            width = display_config.get('window_width', 1600)
            height = display_config.get('window_height', 900)
            fullscreen = display_config.get('fullscreen', False)
            
            # Создание новых свойств окна
            window_props = WindowProperties()
            window_props.setSize(width, height)
            window_props.setTitle("AI-EVOLVE Enhanced Edition - Panda3D")
            
            if fullscreen:
                window_props.setFullscreen(True)
            
            # Применение новых свойств
            self.win.requestProperties(window_props)
            
            logger.info("Panda3D успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Panda3D: {e}")
            return False
    
    def _initialize_managers(self) -> bool:
        """Инициализация менеджеров систем в правильном порядке"""
        try:
            # 1. Менеджер конфигурации (первый)
            self.config_manager = ConfigManager()
            if not self.config_manager.initialize():
                logger.error("Не удалось инициализировать менеджер конфигурации")
                return False
            
            # 2. Система событий (второй)
            self.event_system = EventSystem()
            if not self.event_system.initialize():
                logger.error("Не удалось инициализировать систему событий")
                return False
            
            # 3. Менеджер ресурсов (третий)
            self.resource_manager = ResourceManager()
            if not self.resource_manager.initialize():
                logger.error("Не удалось инициализировать менеджер ресурсов")
                return False
            
            # 4. Менеджер производительности (четвертый)
            self.performance_manager = PerformanceManager()
            if not self.performance_manager.initialize():
                logger.error("Не удалось инициализировать менеджер производительности")
                return False
            
            # 5. Менеджер сцен (пятый)
            self.scene_manager = SceneManager(self.render, self.resource_manager)
            if not self.scene_manager.initialize():
                logger.error("Не удалось инициализировать менеджер сцен")
                return False
            
            # 6. Фабрика систем (шестой)
            self.system_factory = SystemFactory(self.config_manager, self.event_system, None)
            
            # 7. Менеджер систем (седьмой)
            self.system_manager = SystemManager(self.event_system)
            
            # 8. Создание и инициализация всех систем через фабрику
            if not self._create_all_systems():
                logger.error("Не удалось создать системы через фабрику")
                return False
            
            # 9. Добавляем существующие системы в менеджер
            self._add_existing_systems_to_manager()
            
            # 10. Инициализация менеджера систем (последний)
            if not self.system_manager.initialize():
                logger.error("Не удалось инициализировать менеджер систем")
                return False
            
            logger.info("Все менеджеры успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджеров: {e}")
            return False
    
    def _create_all_systems(self) -> bool:
        """Создание всех систем через фабрику"""
        try:
            # Список систем для создания
            systems_to_create = [
                'unified_ai_system',
                'combat_system', 
                'effect_system',
                'skill_system',
                'damage_system',
                'inventory_system',
                'item_system',
                'emotion_system',
                'evolution_system',
                'ui_system',
                'render_system',
                'content_generator'
            ]
            
            # Создаем системы
            for system_name in systems_to_create:
                system = self.system_factory.create_system(system_name)
                if not system:
                    logger.warning(f"Не удалось создать систему: {system_name}")
                    continue
                
                logger.info(f"Система {system_name} создана")
            
            # Инициализируем все созданные системы
            if not self.system_factory.initialize_all_systems():
                logger.error("Не удалось инициализировать системы")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания систем: {e}")
            return False
    
    def _add_existing_systems_to_manager(self):
        """Добавление существующих систем в новый менеджер систем"""
        try:
            # Добавляем существующие системы как адаптеры
            if hasattr(self, 'resource_manager') and self.resource_manager:
                self.system_manager.add_system("resource", self.resource_manager)
            
            if hasattr(self, 'performance_manager') and self.performance_manager:
                self.system_manager.add_system("performance", self.performance_manager)
            
            if hasattr(self, 'scene_manager') and self.scene_manager:
                self.system_manager.add_system("scene", self.scene_manager)
            
            logger.info("Существующие системы добавлены в менеджер систем")
            
        except Exception as e:
            logger.warning(f"Не удалось добавить существующие системы в менеджер: {e}")
    
    def _initialize_scenes(self) -> bool:
        """Инициализация игровых сцен"""
        try:
            # Создание основных сцен
            scenes_to_register = []
            
            # Попытка импорта сцен с обработкой ошибок
            try:
                from ..scenes.menu_scene import MenuScene
                scenes_to_register.append(("menu", MenuScene))
            except ImportError as e:
                logger.warning(f"Не удалось импортировать MenuScene: {e}")
            
            try:
                from ..scenes.game_scene import GameScene
                scenes_to_register.append(("game", GameScene))
            except ImportError as e:
                logger.warning(f"Не удалось импортировать GameScene: {e}")
            
            try:
                from ..scenes.pause_scene import PauseScene
                scenes_to_register.append(("pause", PauseScene))
            except ImportError as e:
                logger.warning(f"Не удалось импортировать PauseScene: {e}")
            
            try:
                from ..scenes.settings_scene import SettingsScene
                scenes_to_register.append(("settings", SettingsScene))
            except ImportError as e:
                logger.warning(f"Не удалось импортировать SettingsScene: {e}")
            
            try:
                from ..scenes.load_scene import LoadScene
                scenes_to_register.append(("load_game", LoadScene))
            except ImportError as e:
                logger.warning(f"Не удалось импортировать LoadScene: {e}")
            
            try:
                from ..scenes.creator_scene import CreatorScene
                scenes_to_register.append(("creator", CreatorScene))
            except ImportError as e:
                logger.warning(f"Не удалось импортировать CreatorScene: {e}")
            
            # Регистрация доступных сцен
            for scene_name, scene_class in scenes_to_register:
                try:
                    self.scene_manager.register_scene(scene_name, scene_class())
                    logger.info(f"Сцена {scene_name} зарегистрирована")
                except Exception as e:
                    logger.error(f"Ошибка регистрации сцены {scene_name}: {e}")
            
            # Установка начальной сцены (первая доступная)
            if scenes_to_register:
                first_scene = scenes_to_register[0][0]
                self.scene_manager.set_active_scene(first_scene)
                logger.info(f"Установлена начальная сцена: {first_scene}")
            else:
                logger.error("Нет доступных сцен для инициализации")
                return False
            
            logger.info("Сцены успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцен: {e}")
            return False
    
    def _setup_tasks(self):
        """Настройка задач Panda3D"""
        # Основная задача обновления
        self.taskMgr.add(self._update_task, "update_task")
        # Отдельная задача для UI с более низким приоритетом
        try:
            self.taskMgr.add(self._ui_update_task, "ui_update_task")
        except Exception as e:
            logger.warning(f"Не удалось добавить отдельную задачу UI: {e}")

    def _bind_global_inputs(self) -> None:
        """Глобальные горячие клавиши для переключения сцен (удобно для отладки)"""
        try:
            def _to(scene_name: str):
                if self.scene_manager:
                    self.scene_manager.switch_to_scene(scene_name, "fade")
            # Пауза/меню/игра
            self.accept('escape', _to, ["pause"])  # ESC -> пауза
            self.accept('p', _to, ["pause"])      # P -> пауза
            self.accept('m', _to, ["menu"])       # M -> меню
            self.accept('g', _to, ["game"])       # G -> игра
            # Восстановление фокуса на окно для считывания клавиш
            try:
                if self.win:
                    props = self.win.getProperties()
                    self.win.requestProperties(props)
            except Exception:
                pass
        except Exception as e:
            logger.debug(f"Не удалось привязать горячие клавиши: {e}")
        
        logger.debug("Задачи Panda3D настроены")
    
    def run(self):
        """Основной игровой цикл Panda3D"""
        if not self.initialize():
            logger.error("Не удалось инициализировать игровой движок")
            return
        
        self.running = True
        logger.info("Запуск игрового цикла Panda3D")
        
        try:
            # Запуск основного цикла Panda3D (наследуется от ShowBase)
            super().run()
            
        except Exception as e:
            logger.error(f"Критическая ошибка в игровом цикле: {e}")
            self._handle_critical_error(e)
        
        finally:
            self._cleanup()
    
    def _update_task(self, task):
        """Задача обновления состояния игры"""
        try:
            if not self.running:
                return task.done
            
            current_time = time.time()
            self.delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            frame_start = current_time
            
            # Обновление всех систем через новый менеджер
            if self.system_manager:
                sys_update_start = time.time()
                self.system_manager.update_all_systems(self.delta_time)
                if self.performance_manager:
                    from .performance_manager import PerformanceMetric
                    self.performance_manager.record_metric(
                        PerformanceMetric.EVENT_PROCESSING_TIME,
                        (time.time() - sys_update_start) * 1000.0,
                        "system_manager"
                    )
            
            # Обновление активной сцены (для обратной совместимости)
            if self.scene_manager and self.scene_manager.active_scene:
                self.scene_manager.active_scene.update(self.delta_time)
            
            # Обновление менеджера производительности (для обратной совместимости)
            if self.performance_manager:
                self.performance_manager.update(self.delta_time)
            
            # Обновление статистики
            self._update_stats()
            # Запись метрик кадра и соблюдение бюджетов
            if self.performance_manager:
                frame_time_ms = (time.time() - frame_start) * 1000.0
                try:
                    from .performance_manager import PerformanceMetric
                    self.performance_manager.record_metric(PerformanceMetric.FRAME_TIME, frame_time_ms, "engine")
                    current_fps = 1000.0 / max(0.001, frame_time_ms)
                    self.performance_manager.record_metric(PerformanceMetric.FPS, current_fps, "engine")
                except Exception:
                    pass
                # Простая защита бюджета кадра на основе max_fps
                try:
                    target_fps = self.settings.get('display', {}).get('fps', 60)
                    min_frame_time = 1.0 / max(1, target_fps)
                    elapsed = time.time() - current_time
                    if elapsed < min_frame_time:
                        time.sleep(max(0.0, min_frame_time - elapsed))
                except Exception:
                    pass
            
            return task.cont
        except Exception as e:
            logger.error(f"Исключение в update_task: {e}")
            self._handle_critical_error(e)
            self.running = False
            return task.done

    def _ui_update_task(self, task):
        """Задача обновления UI, отделенная от общего обновления"""
        try:
            if not self.running:
                return task.done
            if self.system_manager:
                ui_system = self.system_manager.get_system("ui") if hasattr(self.system_manager, "get_system") else None
                if ui_system:
                    # Передаем фиксированный delta для стабильности UI частоты; сам UI троттлит внутри
                    ui_system.update(1.0 / 60.0)
        except Exception as e:
            logger.debug(f"UI task update error: {e}")
        return task.cont
    
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
    
    def _handle_critical_error(self, error: Exception):
        """Обработка критических ошибок"""
        logger.critical(f"Критическая ошибка: {error}")
        try:
            if self.performance_manager:
                from .performance_manager import PerformanceMetric
                self.performance_manager.record_metric(PerformanceMetric.EVENT_PROCESSING_TIME, 0.0, "critical_error")
        except Exception:
            pass
        # Здесь можно добавить логику сохранения состояния, уведомления UI и т.п.
    
    def _cleanup(self):
        """Очистка ресурсов в правильном порядке"""
        logger.info("Очистка ресурсов игрового движка...")
        
        try:
            # Очистка в обратном порядке инициализации
            
            # 1. Очистка менеджера систем
            if self.system_manager:
                self.system_manager.cleanup()
            
            # 2. Очистка фабрики систем
            if self.system_factory:
                self.system_factory.cleanup()
            
            # 3. Очистка системы событий
            if self.event_system:
                self.event_system.cleanup()
            
            # 4. Очистка менеджера сцен
            if self.scene_manager:
                self.scene_manager.cleanup()
            
            # 5. Очистка менеджера ресурсов
            if self.resource_manager:
                self.resource_manager.cleanup()
            
            # 6. Очистка менеджера производительности
            if self.performance_manager:
                self.performance_manager.cleanup()
            
            # 7. Завершение Panda3D
            try:
                self.destroy()
                    
            except Exception as e:
                logger.error(f"Ошибка при завершении Panda3D: {e}")
                # Принудительно завершаем
                try:
                    super().destroy()
                except:
                    pass
            
            logger.info("Ресурсы успешно очищены")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке ресурсов: {e}")
    
    def change_state(self, new_state: SystemState):
        """Изменение состояния игры"""
        old_state = self.current_state
        self.current_state = new_state
        logger.info(f"Изменение состояния игры: {old_state} -> {new_state}")
        
        # Обработка изменения состояния
        if new_state == SystemState.QUITTING:
            self.running = False
        elif new_state == SystemState.PLAYING:
            self.paused = False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        return {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'delta_time': self.delta_time,
            'running_time': time.time() - self.start_time
        }
    
    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        if self.win:
            props = self.win.getProperties()
            fullscreen = not props.getFullscreen()
            
            new_props = WindowProperties()
            new_props.setFullscreen(fullscreen)
            self.win.requestProperties(new_props)
            
            logger.info(f"Переключен полноэкранный режим: {fullscreen}")
    
    def set_window_size(self, width: int, height: int):
        """Изменение размера окна"""
        if self.win:
            new_props = WindowProperties()
            new_props.setSize(width, height)
            self.win.requestProperties(new_props)
            
            logger.info(f"Размер окна изменен: {width}x{height}")
    
    # Методы для доступа к новой архитектуре
    def get_system_manager(self) -> Optional[SystemManager]:
        """Получение менеджера систем"""
        return self.system_manager
    
    def get_event_system(self) -> Optional[EventSystem]:
        """Получение системы событий"""
        return self.event_system
    
    def get_system_factory(self) -> Optional[SystemFactory]:
        """Получение фабрики систем"""
        return self.system_factory
    
    def emit_event(self, event_type: str, data: Any, source: str = "game_engine"):
        """Эмиссия события через новую систему событий"""
        if self.event_system:
            # Поддерживаем оба варианта API (emit_event/emit)
            if hasattr(self.event_system, 'emit_event'):
                self.event_system.emit_event(event_type, data, source)
            else:
                self.event_system.emit(event_type, data, source)
        else:
            logger.warning("Система событий не инициализирована")
    
    def get_system(self, system_name: str):
        """Получение системы по имени"""
        if self.system_manager:
            return self.system_manager.get_system(system_name)
        return None
    
    def create_system(self, system_name: str, **kwargs):
        """Создание новой системы через фабрику"""
        if self.system_factory:
            return self.system_factory.create_system(system_name, **kwargs)
        return None

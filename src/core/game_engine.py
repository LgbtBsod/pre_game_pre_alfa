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
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import WindowProperties, AntialiasAttrib, TransparencyAttrib
from panda3d.core import Vec3, Vec4, Point3, LVector3
from panda3d.core import DirectionalLight, AmbientLight, Spotlight
from panda3d.core import PerspectiveLens, OrthographicLens
from panda3d.core import TextNode, PandaNode, NodePath
from panda3d.core import TransparencyAttrib, AntialiasAttrib
from panda3d.core import WindowProperties, GraphicsPipe, FrameBufferProperties

from .interfaces import GameState, ISystemManager, IEventEmitter
from .system_manager import SystemManager
from .event_system import EventSystem
from .config_manager import ConfigManager
from .scene_manager import SceneManager
from .resource_manager import ResourceManager
from .performance_manager import PerformanceManager

logger = logging.getLogger(__name__)

class GameEngine(ShowBase):
    """
    Основной игровой движок на Panda3D
    Координирует все системы и управляет жизненным циклом игры
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Инициализация Panda3D ShowBase
        super().__init__()
        
        self.config = config
        self.running = False
        self.paused = False
        
        # Panda3D компоненты
        self.window_props = None
        self.main_camera = None
        self.ui_camera = None
        
        # Новая архитектура - менеджеры систем
        self.system_manager: Optional[SystemManager] = None
        self.event_system: Optional[EventSystem] = None
        
        # Существующие менеджеры (для обратной совместимости)
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
        
        # UI элементы
        self.debug_text = None
        self.fps_text = None
        
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
            
            # Настройка освещения
            self._setup_lighting()
            
            # Настройка UI
            self._setup_ui()
            
            # Настройка задач
            self._setup_tasks()
            
            self.current_state = GameState.MAIN_MENU
            logger.info("Игровой движок Panda3D успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации игрового движка: {e}")
            return False
    
    def _initialize_panda3d(self) -> bool:
        """Инициализация Panda3D"""
        try:
            # Настройка окна (окно уже создано ShowBase)
            display_config = self.config.get('display', {})
            width = display_config.get('window_width', 1600)
            height = display_config.get('window_height', 900)
            fullscreen = display_config.get('fullscreen', False)
            
            # Создание новых свойств окна
            self.window_props = WindowProperties()
            self.window_props.setSize(width, height)
            self.window_props.setTitle("AI-EVOLVE Enhanced Edition - Panda3D")
            
            if fullscreen:
                self.window_props.setFullscreen(True)
            
            # Применение новых свойств
            self.win.requestProperties(self.window_props)
            
            # Настройка камер
            self._setup_cameras()
            
            # Настройка рендеринга
            self._setup_rendering()
            
            logger.info("Panda3D успешно инициализирован")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Panda3D: {e}")
            return False
    
    def _setup_cameras(self):
        """Настройка камер"""
        # Основная камера для 3D сцены
        self.main_camera = self.cam
        self.main_camera.setPos(0, -20, 10)
        self.main_camera.lookAt(0, 0, 0)
        
        # UI камера для 2D элементов
        self.ui_camera = self.makeCamera2d(self.win)
        self.ui_camera.setPos(0, 0, 0)
        
        # Настройка изометрической проекции
        lens = OrthographicLens()
        lens.setFilmSize(40, 30)
        lens.setNearFar(-100, 100)
        self.main_camera.node().setLens(lens)
    
    def _setup_rendering(self):
        """Настройка рендеринга"""
        # Включение сглаживания
        self.render.setAntialias(AntialiasAttrib.MAuto)
        
        # Настройка прозрачности
        self.render.setTransparency(TransparencyAttrib.MAlpha)
        
        # Настройка глубины
        self.render.setDepthWrite(True)
        self.render.setDepthTest(True)
    
    def _setup_lighting(self):
        """Настройка освещения"""
        # Основное направленное освещение
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)
        
        # Фоновое освещение
        alight = AmbientLight('alight')
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
        
        logger.debug("Освещение настроено")
    
    def _setup_ui(self):
        """Настройка UI элементов"""
        # Отладочный текст
        self.debug_text = OnscreenText(
            text="AI-EVOLVE Panda3D",
            pos=(-1.3, 0.9),
            scale=0.05,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # FPS текст
        self.fps_text = OnscreenText(
            text="FPS: 0",
            pos=(-1.3, 0.8),
            scale=0.04,
            fg=(1, 1, 0, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        logger.debug("UI элементы настроены")
    
    def _setup_tasks(self):
        """Настройка задач Panda3D"""
        # Основная задача обновления
        self.taskMgr.add(self._update_task, "update_task")
        
        # Задача рендеринга
        self.taskMgr.add(self._render_task, "render_task")
        
        logger.debug("Задачи Panda3D настроены")
    
    def _initialize_managers(self) -> bool:
        """Инициализация менеджеров систем"""
        try:
            # Инициализация системы событий (новая архитектура)
            self.event_system = EventSystem()
            if not self.event_system.initialize():
                logger.error("Не удалось инициализировать систему событий")
                return False
            
            # Инициализация менеджера систем (новая архитектура)
            self.system_manager = SystemManager(self.event_system)
            
            # Добавляем существующие системы в новый менеджер
            self._add_existing_systems_to_manager()
            
            if not self.system_manager.initialize():
                logger.error("Не удалось инициализировать менеджер систем")
                return False
            
            # Инициализация существующих менеджеров (для обратной совместимости)
            self.resource_manager = ResourceManager()
            if not self.resource_manager.initialize():
                logger.error("Не удалось инициализировать менеджер ресурсов")
                return False
            
            self.performance_manager = PerformanceManager()
            if not self.performance_manager.initialize():
                logger.error("Не удалось инициализировать менеджер производительности")
                return False
            
            self.scene_manager = SceneManager(self.render, self.resource_manager)
            if not self.scene_manager.initialize():
                logger.error("Не удалось инициализировать менеджер сцен")
                return False
            
            logger.info("Все менеджеры успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджеров: {e}")
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
            try:
                from scenes.menu_scene import MenuScene
                from scenes.game_scene import GameScene
                from scenes.pause_scene import PauseScene
                from scenes.settings_scene import SettingsScene
                from scenes.load_scene import LoadScene
            except ImportError:
                from src.scenes.menu_scene import MenuScene
                from src.scenes.game_scene import GameScene
                from src.scenes.pause_scene import PauseScene
                from src.scenes.settings_scene import SettingsScene
                from src.scenes.load_scene import LoadScene
            
            # Регистрация сцен
            self.scene_manager.register_scene("menu", MenuScene())
            self.scene_manager.register_scene("game", GameScene())
            self.scene_manager.register_scene("pause", PauseScene())
            self.scene_manager.register_scene("settings", SettingsScene())
            self.scene_manager.register_scene("load_game", LoadScene())
            
            # Установка начальной сцены
            self.scene_manager.set_active_scene("menu")
            
            logger.info("Сцены успешно инициализированы")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации сцен: {e}")
            return False
    
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
        if not self.running:
            return task.done
        
        current_time = time.time()
        self.delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Обновление всех систем через новый менеджер
        if self.system_manager:
            self.system_manager.update_all_systems(self.delta_time)
        
        # Обновление активной сцены (для обратной совместимости)
        if self.scene_manager and self.scene_manager.active_scene:
            self.scene_manager.active_scene.update(self.delta_time)
        
        # Обновление менеджера производительности (для обратной совместимости)
        if self.performance_manager:
            self.performance_manager.update(self.delta_time)
        
        # Обновление статистики
        self._update_stats()
        
        return task.cont
    
    def _render_task(self, task):
        """Задача рендеринга"""
        if not self.running:
            return task.done
        
        # Отрисовка активной сцены
        if self.scene_manager and self.scene_manager.active_scene:
            self.scene_manager.active_scene.render(self.render)
        
        # Обновление UI
        self._update_ui()
        
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
    
    def _update_ui(self):
        """Обновление UI элементов"""
        if self.fps_text:
            self.fps_text.setText(f"FPS: {self.fps}")
        
        if self.debug_text:
            # Обновление отладочной информации
            debug_info = f"AI-EVOLVE Panda3D | State: {self.current_state.value}"
            self.debug_text.setText(debug_info)
    
    def _handle_critical_error(self, error: Exception):
        """Обработка критических ошибок"""
        logger.critical(f"Критическая ошибка: {error}")
        # Здесь можно добавить логику сохранения состояния игры
        # и показа пользователю сообщения об ошибке
    
    def _cleanup(self):
        """Очистка ресурсов"""
        logger.info("Очистка ресурсов игрового движка...")
        
        try:
            # Очистка нового менеджера систем
            if self.system_manager:
                self.system_manager.cleanup()
            
            # Очистка системы событий
            if self.event_system:
                self.event_system.cleanup()
            
            # Очистка существующих менеджеров (для обратной совместимости)
            if self.scene_manager:
                self.scene_manager.cleanup()
            
            if self.resource_manager:
                self.resource_manager.cleanup()
            
            if self.performance_manager:
                self.performance_manager.cleanup()
            
            # Завершение Panda3D
            self.destroy()
            
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
    
    def emit_event(self, event_type: str, data: Any, source: str = "game_engine"):
        """Эмиссия события через новую систему событий"""
        if self.event_system:
            self.event_system.emit_event(event_type, data, source)
        else:
            logger.warning("Система событий не инициализирована")
    
    def get_system(self, system_name: str):
        """Получение системы по имени"""
        if self.system_manager:
            return self.system_manager.get_system(system_name)
        return None

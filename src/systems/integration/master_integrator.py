#!/usr/bin/env python3
"""Главный интегратор всех систем проекта
Координирует работу всех систем и обеспечивает их взаимодействие"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from src.core.architecture import BaseComponent, ComponentType, Priority

# Импорты всех основных систем
from src.systems.ai.ai_system import AISystem
from src.systems.evolution.evolution_system import EvolutionSystem
from src.systems.world.world_integrator import WorldIntegrator
from src.entities.mutants import Mutant

# = ТИПЫ ИНТЕГРАЦИИ
class IntegrationLevel(Enum):
    """Уровни интеграции"""
    BASIC = "basic"           # Базовая интеграция
    ADVANCED = "advanced"     # Продвинутая интеграция
    FULL = "full"            # Полная интеграция

class SystemStatus(Enum):
    """Статусы систем"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    DESTROYED = "destroyed"

# = НАСТРОЙКИ ИНТЕГРАТОРА
@dataclass
class MasterIntegratorSettings:
    """Настройки главного интегратора"""
    integration_level: IntegrationLevel = IntegrationLevel.FULL
    update_interval: float = 0.016  # 60 FPS
    enable_multithreading: bool = True
    max_threads: int = 8
    enable_monitoring: bool = True
    enable_auto_recovery: bool = True
    enable_performance_logging: bool = True

# = СТРУКТУРЫ ДАННЫХ
@dataclass
class SystemInfo:
    """Информация о системе"""
    system_name: str
    system_instance: BaseComponent
    status: SystemStatus
    priority: Priority
    last_update: float = 0.0
    update_count: int = 0
    error_count: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class IntegrationData:
    """Данные интеграции"""
    world_data: Optional[Dict[str, Any]] = None
    ai_data: Optional[Dict[str, Any]] = None
    evolution_data: Optional[Dict[str, Any]] = None
    mutant_data: Optional[Dict[str, Any]] = None
    player_data: Optional[Dict[str, Any]] = None
    created_at: float = field(default_factory=time.time)

# = ГЛАВНЫЙ ИНТЕГРАТОР
class MasterIntegrator(BaseComponent):
    """Главный интегратор всех систем проекта"""
    
    def __init__(self):
        super().__init__(
            component_id="MasterIntegrator",
            component_type=ComponentType.MANAGER,
            priority=Priority.CRITICAL
        )
        
        # Настройки интегратора
        self.settings = MasterIntegratorSettings()
        
        # Системы проекта
        self.systems: Dict[str, SystemInfo] = {}
        self.system_order: List[str] = []
        
        # Данные интеграции
        self.integration_data: Optional[IntegrationData] = None
        
        # Многопоточность
        self.executor: Optional[ThreadPoolExecutor] = None
        self.update_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Мониторинг и статистика
        self.performance_stats = {
            "total_updates": 0,
            "total_update_time": 0.0,
            "system_updates": {},
            "integration_errors": 0,
            "last_frame_time": 0.0
        }
        
        # Callbacks
        self.system_status_changed_callbacks: List[callable] = []
        self.integration_data_changed_callbacks: List[callable] = []
        self.error_callbacks: List[callable] = []
        
        self.logger = logging.getLogger(__name__)
    
    def _on_initialize(self) -> bool:
        """Инициализация главного интегратора"""
        try:
            # Создание систем
            self._create_systems()
            
            # Инициализация систем
            if not self._initialize_systems():
                return False
            
            # Создание пула потоков
            if self.settings.enable_multithreading:
                self.executor = ThreadPoolExecutor(max_workers=self.settings.max_threads)
            
            # Инициализация данных интеграции
            self.integration_data = IntegrationData()
            
            self.logger.info("MasterIntegrator инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации MasterIntegrator: {e}")
            return False
    
    def _create_systems(self):
        """Создание всех систем проекта"""
        # AI система
        self._add_system("AISystem", AISystem(), Priority.HIGH)
        
        # Система эволюции
        self._add_system("EvolutionSystem", EvolutionSystem(), Priority.HIGH)
        
        # Интегратор мира
        self._add_system("WorldIntegrator", WorldIntegrator(), Priority.CRITICAL)
        
        # Определение порядка обновления систем
        self.system_order = [
            "WorldIntegrator",  # Сначала мир
            "AISystem",         # Затем AI
            "EvolutionSystem"   # И эволюция
        ]
    
    def _add_system(self, name: str, system: BaseComponent, priority: Priority):
        """Добавление системы"""
        self.systems[name] = SystemInfo(
            system_name=name,
            system_instance=system,
            status=SystemStatus.UNINITIALIZED,
            priority=priority
        )
    
    def _initialize_systems(self) -> bool:
        """Инициализация всех систем"""
        for name, system_info in self.systems.items():
            try:
                system_info.status = SystemStatus.INITIALIZING
                
                if system_info.system_instance.initialize():
                    system_info.status = SystemStatus.READY
                    self.logger.info(f"Система {name} инициализирована")
                else:
                    system_info.status = SystemStatus.ERROR
                    self.logger.error(f"Ошибка инициализации системы {name}")
                    return False
                    
            except Exception as e:
                system_info.status = SystemStatus.ERROR
                system_info.error_count += 1
                self.logger.error(f"Исключение при инициализации {name}: {e}")
                return False
        
        return True
    
    def start_integration(self):
        """Запуск интеграции"""
        if self.running:
            return
        
        self.running = True
        
        # Запуск систем
        for name, system_info in self.systems.items():
            if system_info.status == SystemStatus.READY:
                try:
                    system_info.system_instance.start()
                    system_info.status = SystemStatus.RUNNING
                except Exception as e:
                    self.logger.error(f"Ошибка запуска системы {name}: {e}")
                    system_info.status = SystemStatus.ERROR
        
        # Запуск потока обновления
        if self.settings.enable_multithreading:
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
        
        self.logger.info("Интеграция запущена")
    
    def stop_integration(self):
        """Остановка интеграции"""
        if not self.running:
            return
        
        self.running = False
        
        # Остановка потока обновления
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5.0)
        
        # Остановка систем
        for name, system_info in self.systems.items():
            if system_info.status == SystemStatus.RUNNING:
                try:
                    system_info.system_instance.stop()
                    system_info.status = SystemStatus.READY
                except Exception as e:
                    self.logger.error(f"Ошибка остановки системы {name}: {e}")
        
        # Закрытие пула потоков
        if self.executor:
            self.executor.shutdown(wait=True)
        
        self.logger.info("Интеграция остановлена")
    
    def _update_loop(self):
        """Цикл обновления интеграции"""
        while self.running:
            try:
                start_time = time.time()
                
                # Обновление интеграции
                self._update_integration()
                
                # Обновление систем
                self._update_systems()
                
                # Обновление статистики
                frame_time = time.time() - start_time
                self.performance_stats["total_updates"] += 1
                self.performance_stats["total_update_time"] += frame_time
                self.performance_stats["last_frame_time"] = frame_time
                
                # Ожидание следующего кадра
                sleep_time = max(0, self.settings.update_interval - frame_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле обновления: {e}")
                self.performance_stats["integration_errors"] += 1
                time.sleep(1.0)
    
    def _update_integration(self):
        """Обновление интеграции"""
        if not self.integration_data:
            return
        
        # Сбор данных от систем
        self._collect_system_data()
        
        # Синхронизация данных между системами
        self._synchronize_systems()
        
        # Уведомление об изменениях
        self._notify_integration_data_changed()
    
    def _collect_system_data(self):
        """Сбор данных от систем"""
        try:
            # Данные мира
            world_integrator = self.systems.get("WorldIntegrator")
            if world_integrator and world_integrator.status == SystemStatus.RUNNING:
                self.integration_data.world_data = world_integrator.system_instance.get_world_statistics()
            
            # Данные AI
            ai_system = self.systems.get("AISystem")
            if ai_system and ai_system.status == SystemStatus.RUNNING:
                self.integration_data.ai_data = ai_system.system_instance.get_statistics()
            
            # Данные эволюции
            evolution_system = self.systems.get("EvolutionSystem")
            if evolution_system and evolution_system.status == SystemStatus.RUNNING:
                self.integration_data.evolution_data = evolution_system.system_instance.get_statistics()
        
        except Exception as e:
            self.logger.error(f"Ошибка сбора данных систем: {e}")
    
    def _synchronize_systems(self):
        """Синхронизация систем"""
        try:
            # Синхронизация AI с миром
            ai_system = self.systems.get("AISystem")
            world_integrator = self.systems.get("WorldIntegrator")
            
            if ai_system and world_integrator and self.integration_data.world_data:
                # Передача данных о мире в AI систему
                pass
            
            # Синхронизация эволюции с AI
            evolution_system = self.systems.get("EvolutionSystem")
            
            if evolution_system and ai_system and self.integration_data.ai_data:
                # Передача данных о AI в систему эволюции
                pass
        
        except Exception as e:
            self.logger.error(f"Ошибка синхронизации систем: {e}")
    
    def _update_systems(self):
        """Обновление систем"""
        for system_name in self.system_order:
            system_info = self.systems.get(system_name)
            if not system_info or system_info.status != SystemStatus.RUNNING:
                continue
            
            try:
                start_time = time.time()
                
                # Обновление системы
                system_info.system_instance.update(self.settings.update_interval)
                
                # Обновление статистики
                update_time = time.time() - start_time
                system_info.last_update = time.time()
                system_info.update_count += 1
                
                if system_name not in self.performance_stats["system_updates"]:
                    self.performance_stats["system_updates"][system_name] = {
                        "total_updates": 0,
                        "total_time": 0.0,
                        "average_time": 0.0
                    }
                
                stats = self.performance_stats["system_updates"][system_name]
                stats["total_updates"] += 1
                stats["total_time"] += update_time
                stats["average_time"] = stats["total_time"] / stats["total_updates"]
                
            except Exception as e:
                self.logger.error(f"Ошибка обновления системы {system_name}: {e}")
                system_info.error_count += 1
                system_info.status = SystemStatus.ERROR
    
    def get_system(self, system_name: str) -> Optional[BaseComponent]:
        """Получение системы"""
        system_info = self.systems.get(system_name)
        return system_info.system_instance if system_info else None
    
    def get_system_status(self, system_name: str) -> Optional[SystemStatus]:
        """Получение статуса системы"""
        system_info = self.systems.get(system_name)
        return system_info.status if system_info else None
    
    def get_all_system_status(self) -> Dict[str, SystemStatus]:
        """Получение статуса всех систем"""
        return {name: info.status for name, info in self.systems.items()}
    
    def get_integration_data(self) -> Optional[IntegrationData]:
        """Получение данных интеграции"""
        return self.integration_data
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        return {
            "integration_running": self.running,
            "systems_count": len(self.systems),
            "running_systems": sum(1 for info in self.systems.values() if info.status == SystemStatus.RUNNING),
            "error_systems": sum(1 for info in self.systems.values() if info.status == SystemStatus.ERROR),
            "system_status": {name: info.status.value for name, info in self.systems.items()},
            "performance_statistics": self.performance_stats.copy(),
            "fps": 1.0 / max(0.001, self.performance_stats["last_frame_time"])
        }
    
    def add_system_status_changed_callback(self, callback: callable):
        """Добавление callback для изменений статуса систем"""
        self.system_status_changed_callbacks.append(callback)
    
    def add_integration_data_changed_callback(self, callback: callable):
        """Добавление callback для изменений данных интеграции"""
        self.integration_data_changed_callbacks.append(callback)
    
    def add_error_callback(self, callback: callable):
        """Добавление callback для ошибок"""
        self.error_callbacks.append(callback)
    
    def _notify_system_status_changed(self, system_name: str, status: SystemStatus):
        """Уведомление об изменениях статуса системы"""
        for callback in self.system_status_changed_callbacks:
            try:
                callback(system_name, status)
            except Exception as e:
                self.logger.error(f"Ошибка в callback статуса системы: {e}")
    
    def _notify_integration_data_changed(self):
        """Уведомление об изменениях данных интеграции"""
        for callback in self.integration_data_changed_callbacks:
            try:
                callback(self.integration_data)
            except Exception as e:
                self.logger.error(f"Ошибка в callback данных интеграции: {e}")
    
    def _on_destroy(self):
        """Уничтожение главного интегратора"""
        # Остановка интеграции
        self.stop_integration()
        
        # Уничтожение систем
        for name, system_info in self.systems.items():
            try:
                system_info.system_instance.destroy()
            except Exception as e:
                self.logger.error(f"Ошибка уничтожения системы {name}: {e}")
        
        # Очистка данных
        self.systems.clear()
        self.system_order.clear()
        self.integration_data = None
        self.system_status_changed_callbacks.clear()
        self.integration_data_changed_callbacks.clear()
        self.error_callbacks.clear()
        
        self.logger.info("MasterIntegrator уничтожен")

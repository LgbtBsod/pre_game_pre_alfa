#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМА УПРАВЛЕНИЯ РЕСУРСАМИ
Централизованное управление всеми ресурсами игры
Соблюдает принцип единой ответственности
"""

import time
import threading
import hashlib
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import json
import pickle
import weakref

from utils.logging_system import get_logger, log_system_event

class ResourceType(Enum):
    """Типы ресурсов"""
    TEXTURE = "texture"
    MODEL = "model"
    AUDIO = "audio"
    FONT = "font"
    SHADER = "shader"
    DATA = "data"
    SCRIPT = "script"
    CONFIG = "config"

class ResourceState(Enum):
    """Состояния ресурсов"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    CACHED = "cached"

@dataclass
class ResourceInfo:
    """Информация о ресурсе"""
    resource_id: str
    file_path: str
    resource_type: ResourceType
    file_size: int
    checksum: str
    last_modified: float
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class Resource:
    """Ресурс"""
    info: ResourceInfo
    data: Any
    state: ResourceState
    load_time: float = 0.0
    access_count: int = 0
    last_access: float = 0.0
    memory_usage: int = 0
    ref_count: int = 0

class ResourceManager:
    """Менеджер ресурсов"""
    
    def __init__(self, resources_directory: str = "assets", cache_directory: str = "cache"):
        self.resources_directory = Path(resources_directory)
        self.cache_directory = Path(cache_directory)
        
        # Создаем директории
        self.resources_directory.mkdir(parents=True, exist_ok=True)
        self.cache_directory.mkdir(parents=True, exist_ok=True)
        
        # Словари для хранения ресурсов
        self.resources: Dict[str, Resource] = {}
        self.resource_info: Dict[str, ResourceInfo] = {}
        
        # Кэш и настройки
        self.memory_limit = 1024 * 1024 * 1024  # 1GB
        self.current_memory_usage = 0
        self.cache_enabled = True
        self.auto_cleanup_enabled = True
        
        # Поток для асинхронной загрузки
        self.loading_thread: Optional[threading.Thread] = None
        self.loading_queue: List[str] = []
        self.running = False
        
        # Callbacks
        self.load_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Статистика
        self.loads_completed = 0
        self.loads_failed = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        self.logger = get_logger("resource_manager")
        
        # Инициализация
        self._initialize_system()
        
        log_system_event("resource_manager", "initialized")
    
    def _initialize_system(self):
        """Инициализация системы"""
        try:
            # Сканируем ресурсы
            self._scan_resources()
            
            # Запускаем поток загрузки
            self.running = True
            self.loading_thread = threading.Thread(target=self._loading_loop, daemon=True)
            self.loading_thread.start()
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации менеджера ресурсов: {e}")
    
    def _scan_resources(self):
        """Сканирование ресурсов"""
        try:
            # Сканируем все файлы в директории ресурсов
            for file_path in self.resources_directory.rglob("*"):
                if file_path.is_file():
                    self._register_resource(file_path)
            
            log_system_event("resource_manager", "resources_scanned", {
                "total_resources": len(self.resource_info)
            })
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования ресурсов: {e}")
    
    def _register_resource(self, file_path: Path):
        """Регистрация ресурса"""
        try:
            # Определяем тип ресурса по расширению
            resource_type = self._get_resource_type(file_path)
            if not resource_type:
                return
            
            # Создаем ID ресурса
            resource_id = self._generate_resource_id(file_path)
            
            # Получаем информацию о файле
            file_size = file_path.stat().st_size
            last_modified = file_path.stat().st_mtime
            checksum = self._calculate_checksum(file_path)
            
            # Создаем информацию о ресурсе
            resource_info = ResourceInfo(
                resource_id=resource_id,
                file_path=str(file_path),
                resource_type=resource_type,
                file_size=file_size,
                checksum=checksum,
                last_modified=last_modified,
                dependencies=[],
                metadata={}
            )
            
            self.resource_info[resource_id] = resource_info
            
        except Exception as e:
            self.logger.error(f"Ошибка регистрации ресурса {file_path}: {e}")
    
    def _get_resource_type(self, file_path: Path) -> Optional[ResourceType]:
        """Определение типа ресурса по расширению"""
        extension = file_path.suffix.lower()
        
        type_mapping = {
            '.png': ResourceType.TEXTURE,
            '.jpg': ResourceType.TEXTURE,
            '.jpeg': ResourceType.TEXTURE,
            '.bmp': ResourceType.TEXTURE,
            '.tga': ResourceType.TEXTURE,
            '.dds': ResourceType.TEXTURE,
            '.obj': ResourceType.MODEL,
            '.fbx': ResourceType.MODEL,
            '.dae': ResourceType.MODEL,
            '.3ds': ResourceType.MODEL,
            '.wav': ResourceType.AUDIO,
            '.mp3': ResourceType.AUDIO,
            '.ogg': ResourceType.AUDIO,
            '.flac': ResourceType.AUDIO,
            '.ttf': ResourceType.FONT,
            '.otf': ResourceType.FONT,
            '.vert': ResourceType.SHADER,
            '.frag': ResourceType.SHADER,
            '.glsl': ResourceType.SHADER,
            '.json': ResourceType.DATA,
            '.xml': ResourceType.DATA,
            '.csv': ResourceType.DATA,
            '.py': ResourceType.SCRIPT,
            '.cfg': ResourceType.CONFIG,
            '.ini': ResourceType.CONFIG
        }
        
        return type_mapping.get(extension)
    
    def _generate_resource_id(self, file_path: Path) -> str:
        """Генерация ID ресурса"""
        # Создаем относительный путь от директории ресурсов
        relative_path = file_path.relative_to(self.resources_directory)
        return str(relative_path).replace('\\', '/').replace('.', '_')
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Вычисление контрольной суммы файла"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Ошибка вычисления контрольной суммы {file_path}: {e}")
            return ""
    
    def load_resource(self, resource_id: str, async_load: bool = True) -> Optional[Any]:
        """Загрузка ресурса"""
        try:
            # Проверяем существование ресурса
            if resource_id not in self.resource_info:
                self.logger.error(f"Ресурс не найден: {resource_id}")
                return None
            
            # Проверяем кэш
            if resource_id in self.resources:
                resource = self.resources[resource_id]
                if resource.state == ResourceState.LOADED:
                    resource.access_count += 1
                    resource.last_access = time.time()
                    self.cache_hits += 1
                    return resource.data
                elif resource.state == ResourceState.LOADING:
                    # Ждем завершения загрузки
                    return self._wait_for_load(resource_id)
            
            self.cache_misses += 1
            
            # Загружаем ресурс
            if async_load:
                self._queue_for_loading(resource_id)
                return self._wait_for_load(resource_id)
            else:
                return self._load_resource_sync(resource_id)
                
        except Exception as e:
            self.logger.error(f"Ошибка загрузки ресурса {resource_id}: {e}")
            return None
    
    def _queue_for_loading(self, resource_id: str):
        """Добавление в очередь загрузки"""
        if resource_id not in self.loading_queue:
            self.loading_queue.append(resource_id)
            
            # Создаем запись ресурса
            if resource_id not in self.resources:
                resource_info = self.resource_info[resource_id]
                self.resources[resource_id] = Resource(
                    info=resource_info,
                    data=None,
                    state=ResourceState.LOADING,
                    load_time=time.time()
                )
    
    def _wait_for_load(self, resource_id: str, timeout: float = 10.0) -> Optional[Any]:
        """Ожидание завершения загрузки"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if resource_id in self.resources:
                resource = self.resources[resource_id]
                if resource.state == ResourceState.LOADED:
                    resource.access_count += 1
                    resource.last_access = time.time()
                    return resource.data
                elif resource.state == ResourceState.ERROR:
                    return None
            
            time.sleep(0.01)
        
        self.logger.warning(f"Таймаут загрузки ресурса: {resource_id}")
        return None
    
    def _load_resource_sync(self, resource_id: str) -> Optional[Any]:
        """Синхронная загрузка ресурса"""
        try:
            resource_info = self.resource_info[resource_id]
            file_path = Path(resource_info.file_path)
            
            # Создаем запись ресурса
            resource = Resource(
                info=resource_info,
                data=None,
                state=ResourceState.LOADING,
                load_time=time.time()
            )
            
            # Загружаем данные в зависимости от типа
            data = self._load_data_by_type(file_path, resource_info.resource_type)
            
            if data is not None:
                resource.data = data
                resource.state = ResourceState.LOADED
                resource.memory_usage = self._calculate_memory_usage(data)
                resource.access_count = 1
                resource.last_access = time.time()
                
                self.resources[resource_id] = resource
                self.current_memory_usage += resource.memory_usage
                self.loads_completed += 1
                
                # Уведомляем о загрузке
                self._notify_load_callbacks(resource_id, data)
                
                return data
            else:
                resource.state = ResourceState.ERROR
                self.resources[resource_id] = resource
                self.loads_failed += 1
                
                # Уведомляем об ошибке
                self._notify_error_callbacks(resource_id, "Failed to load data")
                
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка синхронной загрузки {resource_id}: {e}")
            self.loads_failed += 1
            return None
    
    def _load_data_by_type(self, file_path: Path, resource_type: ResourceType) -> Optional[Any]:
        """Загрузка данных по типу ресурса"""
        try:
            if resource_type == ResourceType.TEXTURE:
                return self._load_texture(file_path)
            elif resource_type == ResourceType.MODEL:
                return self._load_model(file_path)
            elif resource_type == ResourceType.AUDIO:
                return self._load_audio(file_path)
            elif resource_type == ResourceType.FONT:
                return self._load_font(file_path)
            elif resource_type == ResourceType.SHADER:
                return self._load_shader(file_path)
            elif resource_type == ResourceType.DATA:
                return self._load_data(file_path)
            elif resource_type == ResourceType.SCRIPT:
                return self._load_script(file_path)
            elif resource_type == ResourceType.CONFIG:
                return self._load_config(file_path)
            else:
                return self._load_generic(file_path)
                
        except Exception as e:
            self.logger.error(f"Ошибка загрузки данных {file_path}: {e}")
            return None
    
    def _load_texture(self, file_path: Path) -> Optional[Any]:
        """Загрузка текстуры"""
        # Здесь должна быть реальная загрузка текстуры
        # Для демонстрации возвращаем путь к файлу
        return str(file_path)
    
    def _load_model(self, file_path: Path) -> Optional[Any]:
        """Загрузка модели"""
        # Здесь должна быть реальная загрузка модели
        return str(file_path)
    
    def _load_audio(self, file_path: Path) -> Optional[Any]:
        """Загрузка аудио"""
        # Здесь должна быть реальная загрузка аудио
        return str(file_path)
    
    def _load_font(self, file_path: Path) -> Optional[Any]:
        """Загрузка шрифта"""
        # Здесь должна быть реальная загрузка шрифта
        return str(file_path)
    
    def _load_shader(self, file_path: Path) -> Optional[Any]:
        """Загрузка шейдера"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки шейдера {file_path}: {e}")
            return None
    
    def _load_data(self, file_path: Path) -> Optional[Any]:
        """Загрузка данных"""
        try:
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки данных {file_path}: {e}")
            return None
    
    def _load_script(self, file_path: Path) -> Optional[Any]:
        """Загрузка скрипта"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки скрипта {file_path}: {e}")
            return None
    
    def _load_config(self, file_path: Path) -> Optional[Any]:
        """Загрузка конфигурации"""
        try:
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации {file_path}: {e}")
            return None
    
    def _load_generic(self, file_path: Path) -> Optional[Any]:
        """Загрузка общего файла"""
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Ошибка загрузки файла {file_path}: {e}")
            return None
    
    def _calculate_memory_usage(self, data: Any) -> int:
        """Вычисление использования памяти"""
        try:
            if isinstance(data, str):
                return len(data.encode('utf-8'))
            elif isinstance(data, bytes):
                return len(data)
            elif isinstance(data, (dict, list)):
                return len(pickle.dumps(data))
            else:
                return 1024  # Примерная оценка
        except Exception:
            return 1024
    
    def _loading_loop(self):
        """Цикл асинхронной загрузки"""
        while self.running:
            try:
                if self.loading_queue:
                    resource_id = self.loading_queue.pop(0)
                    self._load_resource_sync(resource_id)
                else:
                    time.sleep(0.01)
            except Exception as e:
                self.logger.error(f"Ошибка в цикле загрузки: {e}")
                time.sleep(0.1)
    
    def unload_resource(self, resource_id: str) -> bool:
        """Выгрузка ресурса"""
        try:
            if resource_id not in self.resources:
                return False
            
            resource = self.resources[resource_id]
            
            # Уменьшаем счетчик ссылок
            resource.ref_count -= 1
            
            if resource.ref_count <= 0:
                # Освобождаем память
                self.current_memory_usage -= resource.memory_usage
                
                # Удаляем из памяти
                del self.resources[resource_id]
                
                log_system_event("resource_manager", "resource_unloaded", {
                    "resource_id": resource_id
                })
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка выгрузки ресурса {resource_id}: {e}")
            return False
    
    def preload_resources(self, resource_ids: List[str]) -> bool:
        """Предзагрузка ресурсов"""
        try:
            for resource_id in resource_ids:
                if resource_id in self.resource_info:
                    self._queue_for_loading(resource_id)
            
            log_system_event("resource_manager", "resources_preloaded", {
                "count": len(resource_ids)
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка предзагрузки ресурсов: {e}")
            return False
    
    def cleanup_unused_resources(self):
        """Очистка неиспользуемых ресурсов"""
        try:
            if not self.auto_cleanup_enabled:
                return
            
            current_time = time.time()
            to_unload = []
            
            for resource_id, resource in self.resources.items():
                # Проверяем время последнего доступа
                if (current_time - resource.last_access > 300 and  # 5 минут
                    resource.ref_count <= 0):
                    to_unload.append(resource_id)
            
            # Выгружаем ресурсы
            for resource_id in to_unload:
                self.unload_resource(resource_id)
            
            if to_unload:
                log_system_event("resource_manager", "cleanup_completed", {
                    "unloaded_count": len(to_unload)
                })
                
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
    
    def register_load_callback(self, callback: Callable):
        """Регистрация callback для загрузки"""
        self.load_callbacks.append(callback)
    
    def register_error_callback(self, callback: Callable):
        """Регистрация callback для ошибок"""
        self.error_callbacks.append(callback)
    
    def _notify_load_callbacks(self, resource_id: str, data: Any):
        """Уведомление о загрузке"""
        for callback in self.load_callbacks:
            try:
                callback(resource_id, data)
            except Exception as e:
                self.logger.error(f"Ошибка в callback загрузки: {e}")
    
    def _notify_error_callbacks(self, resource_id: str, error: str):
        """Уведомление об ошибке"""
        for callback in self.error_callbacks:
            try:
                callback(resource_id, error)
            except Exception as e:
                self.logger.error(f"Ошибка в callback ошибки: {e}")
    
    def get_resource_info(self, resource_id: str) -> Optional[ResourceInfo]:
        """Получение информации о ресурсе"""
        return self.resource_info.get(resource_id)
    
    def get_loaded_resources(self) -> List[str]:
        """Получение списка загруженных ресурсов"""
        return [
            resource_id for resource_id, resource in self.resources.items()
            if resource.state == ResourceState.LOADED
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики менеджера"""
        return {
            "total_resources": len(self.resource_info),
            "loaded_resources": len(self.get_loaded_resources()),
            "memory_usage": self.current_memory_usage,
            "memory_limit": self.memory_limit,
            "memory_usage_percent": (self.current_memory_usage / self.memory_limit) * 100,
            "loads_completed": self.loads_completed,
            "loads_failed": self.loads_failed,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
            "resources_by_type": {
                resource_type.value: len([
                    info for info in self.resource_info.values()
                    if info.resource_type == resource_type
                ])
                for resource_type in ResourceType
            }
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.running = False
        
        # Ждем завершения потока загрузки
        if self.loading_thread and self.loading_thread.is_alive():
            self.loading_thread.join(timeout=1.0)
        
        # Выгружаем все ресурсы
        for resource_id in list(self.resources.keys()):
            self.unload_resource(resource_id)
        
        # Очищаем callbacks
        self.load_callbacks.clear()
        self.error_callbacks.clear()
        
        log_system_event("resource_manager", "cleanup_completed")

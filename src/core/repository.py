#!/usr/bin/env python3
"""
Система репозиториев - централизованное управление данными и их хранением
"""

import logging
import time
import json
import pickle
from typing import Dict, List, Optional, Any, Type, TypeVar, Generic, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import copy
from pathlib import Path
from abc import abstractmethod

from .architecture import BaseComponent, ComponentType, Priority, Event, create_event

logger = logging.getLogger(__name__)

# ============================================================================
# ТИПЫ ДАННЫХ
# ============================================================================

class DataType(Enum):
    """Типы данных"""
    ENTITY = "entity"
    ITEM = "item"
    SKILL = "skill"
    EFFECT = "effect"
    CONFIG = "config"
    SAVE = "save"
    TEMPLATE = "template"
    STATISTICS = "statistics"

class StorageType(Enum):
    """Типы хранения"""
    MEMORY = "memory"
    FILE = "file"
    DATABASE = "database"
    CACHE = "cache"

# ============================================================================
# БАЗОВЫЕ КЛАССЫ РЕПОЗИТОРИЕВ
# ============================================================================

@dataclass
class DataRecord:
    """Запись данных"""
    id: str
    data_type: DataType
    data: Any
    created_at: float
    updated_at: float
    version: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QueryFilter:
    """Фильтр для запросов"""
    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, in, not_in, contains, regex
    value: Any

@dataclass
class QuerySort:
    """Сортировка для запросов"""
    field: str
    direction: str  # asc, desc

@dataclass
class QueryOptions:
    """Опции запроса"""
    limit: Optional[int] = None
    offset: int = 0
    filters: List[QueryFilter] = field(default_factory=list)
    sort: List[QuerySort] = field(default_factory=list)

T = TypeVar('T')

class IRepository(Generic[T]):
    """Интерфейс репозитория"""
    
    @property
    @abstractmethod
    def repository_id(self) -> str:
        """Идентификатор репозитория"""
        pass
    
    @property
    @abstractmethod
    def data_type(self) -> DataType:
        """Тип данных"""
        pass
    
    @abstractmethod
    def create(self, id: str, data: T, metadata: Dict[str, Any] = None) -> bool:
        """Создание записи"""
        pass
    
    @abstractmethod
    def read(self, id: str) -> Optional[T]:
        """Чтение записи"""
        pass
    
    @abstractmethod
    def update(self, id: str, data: T, metadata: Dict[str, Any] = None) -> bool:
        """Обновление записи"""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Удаление записи"""
        pass
    
    @abstractmethod
    def exists(self, id: str) -> bool:
        """Проверка существования записи"""
        pass
    
    @abstractmethod
    def query(self, options: QueryOptions) -> List[T]:
        """Запрос данных"""
        pass
    
    @abstractmethod
    def count(self, options: QueryOptions = None) -> int:
        """Подсчет записей"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Очистка репозитория"""
        pass
    
    @abstractmethod
    def backup(self) -> Dict[str, Any]:
        """Создание резервной копии"""
        pass
    
    @abstractmethod
    def restore(self, backup: Dict[str, Any]) -> bool:
        """Восстановление из резервной копии"""
        pass

class BaseRepository(BaseComponent, IRepository[T]):
    """Базовая реализация репозитория"""
    
    def __init__(self, repository_id: str, data_type: DataType, storage_type: StorageType = StorageType.MEMORY):
        super().__init__(repository_id, ComponentType.REPOSITORY, Priority.NORMAL)
        self._data_type = data_type
        self._storage_type = storage_type
        self._records: Dict[str, DataRecord] = {}
        self._indexes: Dict[str, Dict[Any, List[str]]] = {}
        self._lock = threading.RLock()
        self._auto_save = False
        self._auto_save_interval = 300.0  # 5 минут
        self._last_save = 0.0
    
    @property
    def repository_id(self) -> str:
        return self.component_id
    
    @property
    def data_type(self) -> DataType:
        return self._data_type
    
    def create(self, id: str, data: T, metadata: Dict[str, Any] = None) -> bool:
        """Создание записи"""
        with self._lock:
            if id in self._records:
                logger.warning(f"Запись {id} уже существует в репозитории {self.repository_id}")
                return False
            
            current_time = time.time()
            record = DataRecord(
                id=id,
                data_type=self._data_type,
                data=copy.deepcopy(data),
                created_at=current_time,
                updated_at=current_time,
                version=1,
                metadata=metadata or {}
            )
            
            self._records[id] = record
            self._update_indexes(id, record)
            
            logger.debug(f"Создана запись {id} в репозитории {self.repository_id}")
            return True
    
    def read(self, id: str) -> Optional[T]:
        """Чтение записи"""
        with self._lock:
            record = self._records.get(id)
            if record:
                return copy.deepcopy(record.data)
            return None
    
    def update(self, id: str, data: T, metadata: Dict[str, Any] = None) -> bool:
        """Обновление записи"""
        with self._lock:
            if id not in self._records:
                logger.warning(f"Запись {id} не найдена в репозитории {self.repository_id}")
                return False
            
            record = self._records[id]
            record.data = copy.deepcopy(data)
            record.updated_at = time.time()
            record.version += 1
            
            if metadata:
                record.metadata.update(metadata)
            
            self._update_indexes(id, record)
            
            logger.debug(f"Обновлена запись {id} в репозитории {self.repository_id}")
            return True
    
    def delete(self, id: str) -> bool:
        """Удаление записи"""
        with self._lock:
            if id not in self._records:
                return False
            
            record = self._records[id]
            self._remove_from_indexes(id, record)
            del self._records[id]
            
            logger.debug(f"Удалена запись {id} из репозитория {self.repository_id}")
            return True
    
    def exists(self, id: str) -> bool:
        """Проверка существования записи"""
        with self._lock:
            return id in self._records
    
    def query(self, options: QueryOptions) -> List[T]:
        """Запрос данных"""
        with self._lock:
            # Применяем фильтры
            filtered_ids = self._apply_filters(options.filters)
            
            # Применяем сортировку
            sorted_ids = self._apply_sorting(filtered_ids, options.sort)
            
            # Применяем пагинацию
            paginated_ids = self._apply_pagination(sorted_ids, options.limit, options.offset)
            
            # Возвращаем данные
            return [copy.deepcopy(self._records[id].data) for id in paginated_ids]
    
    def count(self, options: QueryOptions = None) -> int:
        """Подсчет записей"""
        with self._lock:
            if not options or not options.filters:
                return len(self._records)
            
            filtered_ids = self._apply_filters(options.filters)
            return len(filtered_ids)
    
    def clear(self) -> bool:
        """Очистка репозитория"""
        with self._lock:
            self._records.clear()
            self._indexes.clear()
            logger.info(f"Репозиторий {self.repository_id} очищен")
            return True
    
    def backup(self) -> Dict[str, Any]:
        """Создание резервной копии"""
        with self._lock:
            backup = {
                "repository_id": self.repository_id,
                "data_type": self._data_type.value,
                "storage_type": self._storage_type.value,
                "records": {},
                "indexes": self._indexes.copy(),
                "timestamp": time.time()
            }
            
            for id, record in self._records.items():
                backup["records"][id] = {
                    "id": record.id,
                    "data_type": record.data_type.value,
                    "data": record.data,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at,
                    "version": record.version,
                    "metadata": record.metadata
                }
            
            return backup
    
    def restore(self, backup: Dict[str, Any]) -> bool:
        """Восстановление из резервной копии"""
        with self._lock:
            try:
                if backup["repository_id"] != self.repository_id:
                    logger.error("Несоответствие ID репозитория при восстановлении")
                    return False
                
                self._records.clear()
                self._indexes.clear()
                
                for id, record_data in backup["records"].items():
                    record = DataRecord(
                        id=record_data["id"],
                        data_type=DataType(record_data["data_type"]),
                        data=record_data["data"],
                        created_at=record_data["created_at"],
                        updated_at=record_data["updated_at"],
                        version=record_data["version"],
                        metadata=record_data["metadata"]
                    )
                    self._records[id] = record
                
                self._indexes = backup["indexes"]
                
                logger.info(f"Репозиторий {self.repository_id} восстановлен из резервной копии")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка восстановления репозитория {self.repository_id}: {e}")
                return False
    
    def add_index(self, field: str) -> bool:
        """Добавление индекса"""
        with self._lock:
            if field in self._indexes:
                return True
            
            self._indexes[field] = {}
            
            # Строим индекс для существующих записей
            for id, record in self._records.items():
                self._add_to_index(field, id, record)
            
            logger.info(f"Добавлен индекс {field} в репозиторий {self.repository_id}")
            return True
    
    def remove_index(self, field: str) -> bool:
        """Удаление индекса"""
        with self._lock:
            if field in self._indexes:
                del self._indexes[field]
                logger.info(f"Удален индекс {field} из репозитория {self.repository_id}")
                return True
            return False
    
    def _update_indexes(self, id: str, record: DataRecord) -> None:
        """Обновление индексов для записи"""
        for field in self._indexes:
            self._add_to_index(field, id, record)
    
    def _remove_from_indexes(self, id: str, record: DataRecord) -> None:
        """Удаление записи из индексов"""
        for field in self._indexes:
            self._remove_from_index(field, id, record)
    
    def _add_to_index(self, field: str, id: str, record: DataRecord) -> None:
        """Добавление записи в индекс"""
        try:
            value = self._get_field_value(record.data, field)
            if value is not None:
                if value not in self._indexes[field]:
                    self._indexes[field][value] = []
                if id not in self._indexes[field][value]:
                    self._indexes[field][value].append(id)
        except Exception as e:
            logger.warning(f"Ошибка добавления в индекс {field}: {e}")
    
    def _remove_from_index(self, field: str, id: str, record: DataRecord) -> None:
        """Удаление записи из индекса"""
        try:
            value = self._get_field_value(record.data, field)
            if value is not None and value in self._indexes[field]:
                if id in self._indexes[field][value]:
                    self._indexes[field][value].remove(id)
                if not self._indexes[field][value]:
                    del self._indexes[field][value]
        except Exception as e:
            logger.warning(f"Ошибка удаления из индекса {field}: {e}")
    
    def _get_field_value(self, data: Any, field: str) -> Any:
        """Получение значения поля из данных"""
        if isinstance(data, dict):
            return data.get(field)
        elif hasattr(data, field):
            return getattr(data, field)
        else:
            return None
    
    def _apply_filters(self, filters: List[QueryFilter]) -> List[str]:
        """Применение фильтров"""
        if not filters:
            return list(self._records.keys())
        
        filtered_ids = set(self._records.keys())
        
        for filter_obj in filters:
            if filter_obj.field in self._indexes:
                # Используем индекс
                if filter_obj.operator == "eq":
                    if filter_obj.value in self._indexes[filter_obj.field]:
                        filtered_ids &= set(self._indexes[filter_obj.field][filter_obj.value])
                    else:
                        filtered_ids.clear()
                elif filter_obj.operator == "in":
                    matching_ids = set()
                    for value in filter_obj.value:
                        if value in self._indexes[filter_obj.field]:
                            matching_ids.update(self._indexes[filter_obj.field][value])
                    filtered_ids &= matching_ids
            else:
                # Фильтруем вручную
                matching_ids = set()
                for id, record in self._records.items():
                    if self._matches_filter(record.data, filter_obj):
                        matching_ids.add(id)
                filtered_ids &= matching_ids
        
        return list(filtered_ids)
    
    def _matches_filter(self, data: Any, filter_obj: QueryFilter) -> bool:
        """Проверка соответствия фильтру"""
        value = self._get_field_value(data, filter_obj.field)
        
        if filter_obj.operator == "eq":
            return value == filter_obj.value
        elif filter_obj.operator == "ne":
            return value != filter_obj.value
        elif filter_obj.operator == "gt":
            return value > filter_obj.value
        elif filter_obj.operator == "lt":
            return value < filter_obj.value
        elif filter_obj.operator == "gte":
            return value >= filter_obj.value
        elif filter_obj.operator == "lte":
            return value <= filter_obj.value
        elif filter_obj.operator == "in":
            return value in filter_obj.value
        elif filter_obj.operator == "not_in":
            return value not in filter_obj.value
        elif filter_obj.operator == "contains":
            return filter_obj.value in str(value)
        elif filter_obj.operator == "regex":
            import re
            return bool(re.search(filter_obj.value, str(value)))
        
        return False
    
    def _apply_sorting(self, ids: List[str], sort: List[QuerySort]) -> List[str]:
        """Применение сортировки"""
        if not sort:
            return ids
        
        def sort_key(id: str) -> tuple:
            record = self._records[id]
            key_values = []
            for sort_obj in sort:
                value = self._get_field_value(record.data, sort_obj.field)
                if sort_obj.direction == "desc":
                    value = (value is None, value)  # None в конец при сортировке по убыванию
                else:
                    value = (value is not None, value)  # None в начало при сортировке по возрастанию
                key_values.append(value)
            return tuple(key_values)
        
        return sorted(ids, key=sort_key)
    
    def _apply_pagination(self, ids: List[str], limit: Optional[int], offset: int) -> List[str]:
        """Применение пагинации"""
        if offset >= len(ids):
            return []
        
        end = offset + limit if limit else len(ids)
        return ids[offset:end]
    
    def _update_impl(self, delta_time: float) -> bool:
        """Обновление - автосохранение"""
        if self._auto_save and time.time() - self._last_save > self._auto_save_interval:
            self._save_data()
            self._last_save = time.time()
        return True
    
    def _save_data(self) -> bool:
        """Сохранение данных"""
        if self._storage_type == StorageType.FILE:
            return self._save_to_file()
        return True
    
    def _save_to_file(self) -> bool:
        """Сохранение в файл"""
        try:
            backup = self.backup()
            file_path = Path(f"data/{self.repository_id}.json")
            file_path.parent.mkdir(exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(backup, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Данные репозитория {self.repository_id} сохранены в файл")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения репозитория {self.repository_id}: {e}")
            return False

# ============================================================================
# МЕНЕДЖЕР РЕПОЗИТОРИЕВ
# ============================================================================

class RepositoryManager(BaseComponent):
    """Менеджер репозиториев"""
    
    def __init__(self):
        super().__init__("repository_manager", ComponentType.MANAGER, Priority.HIGH)
        self._repositories: Dict[str, IRepository] = {}
        self._repository_factories: Dict[DataType, Callable] = {}
        self._lock = threading.RLock()
    
    def register_repository(self, repository: IRepository) -> bool:
        """Регистрация репозитория"""
        with self._lock:
            if repository.repository_id in self._repositories:
                logger.warning(f"Репозиторий {repository.repository_id} уже зарегистрирован")
                return False
            
            self._repositories[repository.repository_id] = repository
            logger.info(f"Репозиторий {repository.repository_id} зарегистрирован")
            return True
    
    def unregister_repository(self, repository_id: str) -> bool:
        """Отмена регистрации репозитория"""
        with self._lock:
            if repository_id not in self._repositories:
                return False
            
            del self._repositories[repository_id]
            logger.info(f"Репозиторий {repository_id} отменен")
            return True
    
    def get_repository(self, repository_id: str) -> Optional[IRepository]:
        """Получение репозитория по ID"""
        with self._lock:
            return self._repositories.get(repository_id)
    
    def get_repositories_by_type(self, data_type: DataType) -> List[IRepository]:
        """Получение репозиториев по типу данных"""
        with self._lock:
            return [repo for repo in self._repositories.values() 
                   if repo.data_type == data_type]
    
    def create_repository(self, repository_id: str, data_type: DataType, storage_type: StorageType = StorageType.MEMORY) -> Optional[IRepository]:
        """Создание нового репозитория"""
        with self._lock:
            if repository_id in self._repositories:
                logger.warning(f"Репозиторий {repository_id} уже существует")
                return self._repositories[repository_id]
            
            repository = BaseRepository(repository_id, data_type, storage_type)
            self._repositories[repository_id] = repository
            
            logger.info(f"Создан репозиторий {repository_id} для типа {data_type.value}")
            return repository
    
    def backup_all(self) -> Dict[str, Any]:
        """Создание резервной копии всех репозиториев"""
        with self._lock:
            backup = {
                "timestamp": time.time(),
                "repositories": {}
            }
            
            for repository_id, repository in self._repositories.items():
                try:
                    backup["repositories"][repository_id] = repository.backup()
                except Exception as e:
                    logger.error(f"Ошибка резервного копирования репозитория {repository_id}: {e}")
            
            return backup
    
    def restore_all(self, backup: Dict[str, Any]) -> bool:
        """Восстановление всех репозиториев"""
        with self._lock:
            try:
                for repository_id, repo_backup in backup["repositories"].items():
                    repository = self._repositories.get(repository_id)
                    if repository:
                        repository.restore(repo_backup)
                
                logger.info("Все репозитории восстановлены из резервной копии")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка восстановления репозиториев: {e}")
                return False
    
    def _initialize_impl(self) -> bool:
        """Инициализация менеджера репозиториев"""
        try:
            # Создаем базовые репозитории
            self._create_base_repositories()
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации менеджера репозиториев: {e}")
            return False
    
    def _create_base_repositories(self) -> None:
        """Создание базовых репозиториев"""
        # Репозитории для игровых данных
        self.create_repository("entities", DataType.ENTITY)
        self.create_repository("items", DataType.ITEM)
        self.create_repository("skills", DataType.SKILL)
        self.create_repository("effects", DataType.EFFECT)
        self.create_repository("templates", DataType.TEMPLATE)
        self.create_repository("statistics", DataType.STATISTICS)
        
        # Репозитории для конфигурации и сохранений
        self.create_repository("configs", DataType.CONFIG, StorageType.FILE)
        self.create_repository("saves", DataType.SAVE, StorageType.FILE)
        
        logger.info("Базовые репозитории созданы")

# ============================================================================
# УТИЛИТЫ ДЛЯ РАБОТЫ С РЕПОЗИТОРИЯМИ
# ============================================================================

def create_query_filter(field: str, operator: str, value: Any) -> QueryFilter:
    """Создание фильтра запроса"""
    return QueryFilter(field=field, operator=operator, value=value)

def create_query_sort(field: str, direction: str = "asc") -> QuerySort:
    """Создание сортировки запроса"""
    return QuerySort(field=field, direction=direction)

def create_query_options(limit: Optional[int] = None, offset: int = 0, 
                        filters: List[QueryFilter] = None, sort: List[QuerySort] = None) -> QueryOptions:
    """Создание опций запроса"""
    return QueryOptions(
        limit=limit,
        offset=offset,
        filters=filters or [],
        sort=sort or []
    )

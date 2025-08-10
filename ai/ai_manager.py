"""
Менеджер AI для координации всех AI систем в игре.
Обеспечивает оптимизацию производительности и управление AI сущностей.
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import weakref

from .ai_core import AICore, AIState, AIPriority
from utils.entity_id_generator import generate_short_entity_id, EntityType

logger = logging.getLogger(__name__)


@dataclass
class AIEntityInfo:
    """Информация о AI сущности"""
    entity_ref: weakref.ref
    ai_core: AICore
    last_update: float
    update_interval: float
    priority: AIPriority
    is_active: bool
    performance_mode: str


class AIManager:
    """Менеджер AI для координации всех AI систем"""
    
    def __init__(self):
        self.entities: Dict[int, AIEntityInfo] = {}
        self.entity_groups: Dict[str, Set[int]] = defaultdict(set)
        self.performance_stats = {
            'total_updates': 0,
            'active_entities': 0,
            'update_time': 0.0,
            'last_stats_time': time.time()
        }
        
        # Настройки производительности
        self.max_active_entities = 100
        self.max_update_time_per_frame = 0.016  # 16ms на кадр
        self.update_budget = 0.01  # 10ms на обновление AI
        
        # Потокобезопасность
        self._lock = threading.RLock()
        self._update_lock = threading.Lock()
        
        # Групповое поведение
        self.group_coordinators: Dict[str, 'GroupCoordinator'] = {}
        
        # Оптимизация
        self.spatial_hash = SpatialHash()
        self.update_queue = UpdateQueue()
        
        logger.info("AI Manager инициализирован")
    
    def register_entity(self, entity, ai_core: AICore) -> bool:
        """Регистрирует сущность в AI системе"""
        try:
            with self._lock:
                # Генерируем 16-ричный ID для сущности
                if hasattr(entity, 'hex_id'):
                    entity_id = entity.hex_id
                else:
                    # Определяем тип сущности
                    entity_type = self._determine_entity_type(entity)
                    entity_id = generate_short_entity_id(entity_type)
                    entity.hex_id = entity_id
                
                if entity_id in self.entities:
                    logger.warning(f"Сущность {entity_id} уже зарегистрирована")
                    return False
                
                # Создаем информацию о сущности
                entity_info = AIEntityInfo(
                    entity_ref=weakref.ref(entity),
                    ai_core=ai_core,
                    last_update=time.time(),
                    update_interval=ai_core.update_interval,
                    priority=ai_core.priority,
                    is_active=True,
                    performance_mode=ai_core.performance_mode
                )
                
                self.entities[entity_id] = entity_info
                
                # Добавляем в пространственный хеш
                if hasattr(entity, 'position'):
                    self.spatial_hash.add_entity(entity_id, entity.position)
                
                # Добавляем в группу, если есть
                if ai_core.group_id:
                    self.entity_groups[ai_core.group_id].add(entity_id)
                    self._ensure_group_coordinator(ai_core.group_id)
                
                logger.info(f"Сущность {entity_id} зарегистрирована в AI системе")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка регистрации сущности: {e}")
            return False
    
    def unregister_entity(self, entity) -> bool:
        """Удаляет сущность из AI системы"""
        try:
            with self._lock:
                # Используем 16-ричный ID
                entity_id = getattr(entity, 'hex_id', None)
                if not entity_id:
                    # Fallback к старому методу
                    entity_id = id(entity)
                
                if entity_id not in self.entities:
                    return False
                
                entity_info = self.entities[entity_id]
                
                # Удаляем из группы
                if entity_info.ai_core.group_id:
                    group_id = entity_info.ai_core.group_id
                    self.entity_groups[group_id].discard(entity_id)
                    
                    # Удаляем группу, если она пуста
                    if not self.entity_groups[group_id]:
                        del self.entity_groups[group_id]
                        if group_id in self.group_coordinators:
                            del self.group_coordinators[group_id]
                
                # Удаляем из пространственного хеша
                self.spatial_hash.remove_entity(entity_id)
                
                # Удаляем из очереди обновлений
                self.update_queue.remove_entity(entity_id)
                
                # Удаляем сущность
                del self.entities[entity_id]
                
                logger.info(f"Сущность {entity_id} удалена из AI системы")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка удаления сущности: {e}")
            return False
    
    def update(self, delta_time: float):
        """Обновляет все AI системы"""
        start_time = time.time()
        
        try:
            with self._update_lock:
                # Очищаем мертвые ссылки
                self._cleanup_dead_entities()
                
                # Обновляем статистику
                self._update_performance_stats()
                
                # Определяем, какие сущности обновлять
                entities_to_update = self._select_entities_for_update()
                
                # Обновляем выбранные сущности
                for entity_id in entities_to_update:
                    self._update_entity(entity_id, delta_time)
                
                # Обновляем групповое поведение
                self._update_group_behavior(delta_time)
                
                # Обновляем пространственный хеш
                self._update_spatial_hash()
                
        except Exception as e:
            logger.error(f"Ошибка обновления AI Manager: {e}")
        
        finally:
            # Обновляем статистику времени
            update_time = time.time() - start_time
            self.performance_stats['update_time'] = update_time
            self.performance_stats['total_updates'] += 1
    
    def _cleanup_dead_entities(self):
        """Очищает мертвые ссылки на сущности"""
        dead_entities = []
        
        for entity_id, entity_info in self.entities.items():
            entity = entity_info.entity_ref()
            if entity is None:
                dead_entities.append(entity_id)
        
        for entity_id in dead_entities:
            self.entities[entity_id].ai_core = None
            del self.entities[entity_id]
            self.spatial_hash.remove_entity(entity_id)
            self.update_queue.remove_entity(entity_id)
        
        if dead_entities:
            logger.info(f"Очищено {len(dead_entities)} мертвых сущностей")
    
    def _select_entities_for_update(self) -> List[int]:
        """Выбирает сущности для обновления на основе приоритета и производительности"""
        current_time = time.time()
        entities_to_update = []
        
        # Сортируем сущности по приоритету и времени последнего обновления
        sorted_entities = sorted(
            self.entities.items(),
            key=lambda x: (
                x[1].priority.value,
                current_time - x[1].last_update
            )
        )
        
        # Выбираем сущности для обновления
        for entity_id, entity_info in sorted_entities:
            if not entity_info.is_active:
                continue
            
            # Проверяем, нужно ли обновление
            if current_time - entity_info.last_update < entity_info.update_interval:
                continue
            
            # Проверяем бюджет времени
            if len(entities_to_update) >= self.max_active_entities:
                break
            
            entities_to_update.append(entity_id)
        
        return entities_to_update
    
    def _update_entity(self, entity_id: int, delta_time: float):
        """Обновляет конкретную сущность"""
        try:
            entity_info = self.entities[entity_id]
            entity = entity_info.entity_ref()
            
            if entity is None:
                return
            
            # Обновляем AI
            entity_info.ai_core.update(delta_time)
            
            # Обновляем время последнего обновления
            entity_info.last_update = time.time()
            
            # Обновляем приоритет
            entity_info.priority = entity_info.ai_core.priority
            
        except Exception as e:
            logger.error(f"Ошибка обновления сущности {entity_id}: {e}")
    
    def _update_group_behavior(self, delta_time: float):
        """Обновляет групповое поведение"""
        for group_id, coordinator in self.group_coordinators.items():
            try:
                coordinator.update(delta_time)
            except Exception as e:
                logger.error(f"Ошибка обновления группы {group_id}: {e}")
    
    def _update_spatial_hash(self):
        """Обновляет пространственный хеш"""
        try:
            self.spatial_hash.clear()
            
            for entity_id, entity_info in self.entities.items():
                entity = entity_info.entity_ref()
                if entity and hasattr(entity, 'position'):
                    self.spatial_hash.add_entity(entity_id, entity.position)
                    
        except Exception as e:
            logger.error(f"Ошибка обновления пространственного хеша: {e}")
    
    def _ensure_group_coordinator(self, group_id: str):
        """Создает координатор группы, если его нет"""
        if group_id not in self.group_coordinators:
            self.group_coordinators[group_id] = GroupCoordinator(group_id, self)
    
    def get_nearby_entities(self, position, radius: float, entity_type: str = None) -> List:
        """Получает ближайшие сущности"""
        try:
            entity_ids = self.spatial_hash.get_entities_in_radius(position, radius)
            nearby_entities = []
            
            for entity_id in entity_ids:
                if entity_id in self.entities:
                    entity_info = self.entities[entity_id]
                    entity = entity_info.entity_ref()
                    
                    if entity is None:
                        continue
                    
                    # Фильтруем по типу, если указан
                    if entity_type:
                        if hasattr(entity, 'entity_type') and entity.entity_type != entity_type:
                            continue
                        if hasattr(entity, 'enemy_type') and entity.enemy_type != entity_type:
                            continue
                    
                    nearby_entities.append(entity)
            
            return nearby_entities
            
        except Exception as e:
            logger.error(f"Ошибка получения ближайших сущностей: {e}")
            return []
    
    def set_entity_active(self, entity, active: bool):
        """Устанавливает активность сущности"""
        try:
            with self._lock:
                entity_id = getattr(entity, 'hex_id', id(entity))
                if entity_id in self.entities:
                    self.entities[entity_id].is_active = active
        except Exception as e:
            logger.error(f"Ошибка установки активности сущности: {e}")
    
    def set_entity_priority(self, entity, priority: AIPriority):
        """Устанавливает приоритет сущности"""
        try:
            with self._lock:
                entity_id = getattr(entity, 'hex_id', id(entity))
                if entity_id in self.entities:
                    self.entities[entity_id].priority = priority
                    self.entities[entity_id].ai_core.priority = priority
        except Exception as e:
            logger.error(f"Ошибка установки приоритета сущности: {e}")
    
    def _determine_entity_type(self, entity) -> EntityType:
        """Определяет тип сущности для генерации ID"""
        try:
            # Проверяем атрибуты сущности
            if hasattr(entity, 'is_boss') and entity.is_boss:
                return EntityType.BOSS
            elif hasattr(entity, 'enemy_type'):
                return EntityType.ENEMY
            elif hasattr(entity, 'is_player') and entity.is_player:
                return EntityType.PLAYER
            elif hasattr(entity, 'is_npc') and entity.is_npc:
                return EntityType.NPC
            elif hasattr(entity, 'type') and entity.type == 'projectile':
                return EntityType.PROJECTILE
            elif hasattr(entity, 'type') and entity.type == 'trap':
                return EntityType.TRAP
            elif hasattr(entity, 'type') and entity.type == 'container':
                return EntityType.CONTAINER
            else:
                # По умолчанию считаем AI сущностью
                return EntityType.AI_ENTITY
        except Exception as e:
            logger.warning(f"Не удалось определить тип сущности: {e}")
            return EntityType.AI_ENTITY
    
    def get_performance_stats(self) -> Dict:
        """Возвращает статистику производительности"""
        with self._lock:
            stats = self.performance_stats.copy()
            stats['active_entities'] = len([e for e in self.entities.values() if e.is_active])
            stats['total_entities'] = len(self.entities)
            stats['groups'] = len(self.group_coordinators)
            return stats
    
    def _update_performance_stats(self):
        """Обновляет статистику производительности"""
        current_time = time.time()
        
        # Обновляем статистику каждые 5 секунд
        if current_time - self.performance_stats['last_stats_time'] > 5.0:
            self.performance_stats['last_stats_time'] = current_time
            
            # Логируем статистику
            stats = self.get_performance_stats()
            logger.info(f"AI Stats: {stats['active_entities']}/{stats['total_entities']} "
                       f"entities, {stats['update_time']:.3f}s update time")


class GroupCoordinator:
    """Координатор группового поведения"""
    
    def __init__(self, group_id: str, ai_manager: 'AIManager'):
        self.group_id = group_id
        self.ai_manager = ai_manager
        self.group_leader = None
        self.formation_type = "circle"  # circle, line, wedge
        self.group_goals = []
        self.communication_queue = []
        
        logger.info(f"Group Coordinator создан для группы {group_id}")
    
    def update(self, delta_time: float):
        """Обновляет групповое поведение"""
        try:
            # Выбираем лидера группы
            self._select_group_leader()
            
            # Обновляем цели группы
            self._update_group_goals()
            
            # Координируем действия
            self._coordinate_actions()
            
            # Обрабатываем коммуникацию
            self._process_communication()
            
        except Exception as e:
            logger.error(f"Ошибка обновления группы {self.group_id}: {e}")
    
    def _select_group_leader(self):
        """Выбирает лидера группы"""
        group_entities = self.ai_manager.entity_groups.get(self.group_id, set())
        
        if not group_entities:
            return
        
        # Ищем сущность с наивысшими лидерскими качествами
        best_leader = None
        best_leadership = 0.0
        
        for entity_id in group_entities:
            if entity_id in self.ai_manager.entities:
                entity_info = self.ai_manager.entities[entity_id]
                entity = entity_info.entity_ref()
                
                if entity and hasattr(entity_info.ai_core, 'personality'):
                    leadership = entity_info.ai_core.personality.leadership
                    if leadership > best_leadership:
                        best_leadership = leadership
                        best_leader = entity_id
        
        self.group_leader = best_leader
    
    def _update_group_goals(self):
        """Обновляет цели группы"""
        # Простая логика - если есть лидер, следуем его целям
        if self.group_leader and self.group_leader in self.ai_manager.entities:
            leader_info = self.ai_manager.entities[self.group_leader]
            leader_entity = leader_info.entity_ref()
            
            if leader_entity:
                # Копируем цели лидера
                self.group_goals = leader_info.ai_core.action_plan.copy()
    
    def _coordinate_actions(self):
        """Координирует действия группы"""
        group_entities = self.ai_manager.entity_groups.get(self.group_id, set())
        
        for entity_id in group_entities:
            if entity_id in self.ai_manager.entities:
                entity_info = self.ai_manager.entities[entity_id]
                entity = entity_info.entity_ref()
                
                if entity and entity_id != self.group_leader:
                    # Следуем групповым целям
                    entity_info.ai_core.action_plan = self.group_goals.copy()
    
    def _process_communication(self):
        """Обрабатывает коммуникацию в группе"""
        # Очищаем старые сообщения
        self.communication_queue = [msg for msg in self.communication_queue 
                                  if time.time() - msg['timestamp'] < 5.0]
    
    def send_message(self, message: str, sender_id: int, target_id: int = None):
        """Отправляет сообщение в группе"""
        msg = {
            'message': message,
            'sender': sender_id,
            'target': target_id,
            'timestamp': time.time()
        }
        self.communication_queue.append(msg)


class SpatialHash:
    """Пространственный хеш для быстрого поиска ближайших сущностей"""
    
    def __init__(self, cell_size: float = 100.0):
        self.cell_size = cell_size
        self.grid = defaultdict(set)
    
    def _get_cell_key(self, position) -> tuple:
        """Получает ключ ячейки для позиции"""
        x, y = position
        cell_x = int(x // self.cell_size)
        cell_y = int(y // self.cell_size)
        return (cell_x, cell_y)
    
    def add_entity(self, entity_id: int, position):
        """Добавляет сущность в пространственный хеш"""
        cell_key = self._get_cell_key(position)
        self.grid[cell_key].add(entity_id)
    
    def remove_entity(self, entity_id: int):
        """Удаляет сущность из пространственного хеша"""
        for cell_entities in self.grid.values():
            cell_entities.discard(entity_id)
    
    def get_entities_in_radius(self, position, radius: float) -> set:
        """Получает сущности в радиусе"""
        entities = set()
        center_cell = self._get_cell_key(position)
        
        # Вычисляем диапазон ячеек для проверки
        cells_to_check = int(radius // self.cell_size) + 1
        
        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                cell_key = (center_cell[0] + dx, center_cell[1] + dy)
                if cell_key in self.grid:
                    entities.update(self.grid[cell_key])
        
        return entities
    
    def clear(self):
        """Очищает пространственный хеш"""
        self.grid.clear()


class UpdateQueue:
    """Очередь обновлений для оптимизации"""
    
    def __init__(self):
        self.queue = []
        self.entity_indices = {}
    
    def add_entity(self, entity_id: int, priority: float):
        """Добавляет сущность в очередь"""
        if entity_id in self.entity_indices:
            self.remove_entity(entity_id)
        
        self.queue.append((entity_id, priority))
        self.entity_indices[entity_id] = len(self.queue) - 1
        
        # Сортируем по приоритету
        self._sort_queue()
    
    def remove_entity(self, entity_id: int):
        """Удаляет сущность из очереди"""
        if entity_id in self.entity_indices:
            index = self.entity_indices[entity_id]
            del self.queue[index]
            del self.entity_indices[entity_id]
            
            # Обновляем индексы
            for i in range(index, len(self.queue)):
                self.entity_indices[self.queue[i][0]] = i
    
    def get_next_entities(self, count: int) -> List[int]:
        """Получает следующие сущности для обновления"""
        entities = []
        for i in range(min(count, len(self.queue))):
            if i < len(self.queue):
                entities.append(self.queue[i][0])
        return entities
    
    def _sort_queue(self):
        """Сортирует очередь по приоритету"""
        self.queue.sort(key=lambda x: x[1], reverse=True)
        
        # Обновляем индексы
        for i, (entity_id, _) in enumerate(self.queue):
            self.entity_indices[entity_id] = i


# Глобальный экземпляр менеджера AI
ai_manager = AIManager()

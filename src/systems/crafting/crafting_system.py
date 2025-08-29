#!/usr/bin/env python3
"""
Система крафтинга - создание предметов из материалов
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from core.interfaces import ISystem, SystemPriority, SystemState
from core.state_manager import StateManager
from core.repository import RepositoryManager, DataType, StorageType
from core.constants import constants_manager, (
    ItemType, ItemRarity, ItemCategory, StatType, BASE_STATS,
    PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class Recipe:
    """Рецепт крафтинга"""
    recipe_id: str
    name: str
    description: str
    category: str
    difficulty: int = 1  # 1-10
    required_level: int = 1
    crafting_time: float = 1.0  # секунды
    experience_gain: int = 10
    success_chance: float = 1.0
    materials: Dict[str, int] = field(default_factory=dict)  # item_id: count
    tools: List[str] = field(default_factory=list)  # required tools
    result_item: str = ""
    result_count: int = 1
    result_quality: float = 1.0
    unlock_conditions: Dict[str, Any] = field(default_factory=dict)
    is_discovered: bool = False
    discovery_chance: float = 0.1

@dataclass
class CraftingSession:
    """Сессия крафтинга"""
    session_id: str
    entity_id: str
    recipe_id: str
    start_time: float = field(default_factory=time.time)
    progress: float = 0.0  # 0.0 - 1.0
    is_completed: bool = False
    is_failed: bool = False
    result_items: List[str] = field(default_factory=list)
    experience_gained: int = 0
    materials_used: Dict[str, int] = field(default_factory=dict)

@dataclass
class CraftingResult:
    """Результат крафтинга"""
    success: bool
    item_id: str = ""
    item_count: int = 0
    quality: float = 1.0
    experience_gained: int = 0
    materials_consumed: Dict[str, int] = field(default_factory=dict)
    error_message: str = ""
    crafting_time: float = 0.0

class CraftingSystem(ISystem):
    """Система крафтинга"""
    
    def __init__(self):
        self._system_name = "crafting"
        self._system_priority = SystemPriority.NORMAL
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        # Интеграция с архитектурой (опционально)
        self.state_manager: Optional[StateManager] = None
        self.repository_manager: Optional[RepositoryManager] = None
        self.event_bus = None
        
        # Рецепты
        self.recipes: Dict[str, Recipe] = {}
        
        # Активные сессии крафтинга
        self.crafting_sessions: Dict[str, CraftingSession] = {}
        
        # История крафтинга
        self.crafting_history: List[Dict[str, Any]] = []
        
        # Настройки системы
        self.system_settings = {
            'max_crafting_sessions': SYSTEM_LIMITS["max_crafting_sessions"],
            'base_success_chance': PROBABILITY_CONSTANTS["base_crafting_success"],
            'quality_variance': 0.2,
            'experience_multiplier': 1.0,
            'auto_discovery_enabled': True
        }
        
        # Статистика системы
        self.system_stats = {
            'total_recipes': 0,
            'active_sessions': 0,
            'completed_crafts': 0,
            'failed_crafts': 0,
            'total_experience_gained': 0,
            'update_time': 0.0
        }
        
        logger.info("Система крафтинга инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы крафтинга"""
        try:
            logger.info("Инициализация системы крафтинга...")
            
            # Настраиваем систему
            self._setup_crafting_system()
            
            # Создаем базовые рецепты
            self._create_base_recipes()

            # Регистрация состояний/репозиториев при наличии менеджеров
            self._register_system_states()
            self._register_system_repositories()
            
            self._system_state = SystemState.READY
            logger.info("Система крафтинга успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы крафтинга: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы крафтинга"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем активные сессии крафтинга
            self._update_crafting_sessions(delta_time)
            
            # Проверяем завершенные сессии
            self._check_completed_sessions()
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы крафтинга: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы крафтинга"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система крафтинга приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы крафтинга: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы крафтинга"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система крафтинга возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы крафтинга: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы крафтинга"""
        try:
            logger.info("Очистка системы крафтинга...")
            
            # Очищаем все данные
            self.recipes.clear()
            self.crafting_sessions.clear()
            self.crafting_history.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'total_recipes': 0,
                'active_sessions': 0,
                'completed_crafts': 0,
                'failed_crafts': 0,
                'total_experience_gained': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система крафтинга очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы крафтинга: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        info = {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'total_recipes': len(self.recipes),
            'active_sessions': len(self.crafting_sessions),
            'stats': self.system_stats
        }
        # Вывод некоторых агрегатов наверх для удобства UI/тестов
        info['completed_crafts'] = self.system_stats.get('completed_crafts', 0)
        info['failed_crafts'] = self.system_stats.get('failed_crafts', 0)
        return info

    def _register_system_states(self) -> None:
        """Регистрация состояний системы (mock-friendly)."""
        if not self.state_manager:
            return
        try:
            # Предпочитаем update_state (для mock в тестах)
            self.state_manager.update_state("crafting_system_settings", self.system_settings)
            self.state_manager.update_state("crafting_system_stats", self.system_stats)
            self.state_manager.update_state("crafting_active_sessions", list(self.crafting_sessions.keys()))
        except Exception:
            # Fallback на реальную реализацию
            try:
                from core.state_manager import StateType, StateScope
                self.state_manager.register_state("crafting_system_settings", self.system_settings, StateType.CONFIGURATION, StateScope.SYSTEM)
                self.state_manager.register_state("crafting_system_stats", self.system_stats, StateType.STATISTICS, StateScope.SYSTEM)
                self.state_manager.register_state("crafting_active_sessions", list(self.crafting_sessions.keys()), StateType.DYNAMIC_DATA, StateScope.SYSTEM)
            except Exception:
                pass

    def _register_system_repositories(self) -> None:
        """Регистрация репозиториев системы (mock-friendly)."""
        if not self.repository_manager:
            return
        try:
            # Совместимо с моками: (repo_id, data_type, storage, payload)
            self.repository_manager.register_repository("crafting_recipes", DataType.CONFIGURATION, StorageType.MEMORY, self.recipes)
            self.repository_manager.register_repository("crafting_sessions", DataType.DYNAMIC_DATA, StorageType.MEMORY, self.crafting_sessions)
            self.repository_manager.register_repository("crafting_history", DataType.HISTORY, StorageType.MEMORY, self.crafting_history)
            # Доп. метрики для паритета с другими системами
            self.repository_manager.register_repository("crafting_metrics", DataType.STATISTICS, StorageType.MEMORY, {})
        except Exception:
            pass
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "entity_destroyed":
                return self._handle_entity_destroyed(event_data)
            elif event_type == "item_acquired":
                return self._handle_item_acquired(event_data)
            elif event_type == "skill_learned":
                return self._handle_skill_learned(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _setup_crafting_system(self) -> None:
        """Настройка системы крафтинга"""
        try:
            # Инициализируем базовые настройки
            logger.debug("Система крафтинга настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему крафтинга: {e}")
    
    def _create_base_recipes(self) -> None:
        """Создание базовых рецептов"""
        try:
            # Простые рецепты
            simple_recipes = [
                Recipe(
                    recipe_id="wooden_stick",
                    name="Деревянная палка",
                    description="Простая деревянная палка",
                    category="woodworking",
                    difficulty=1,
                    required_level=1,
                    crafting_time=2.0,
                    experience_gain=5,
                    materials={"wood": 1},
                    result_item="wooden_stick",
                    result_count=1,
                    is_discovered=True
                ),
                Recipe(
                    recipe_id="stone_tool",
                    name="Каменный инструмент",
                    description="Примитивный каменный инструмент",
                    category="stoneworking",
                    difficulty=2,
                    required_level=2,
                    crafting_time=5.0,
                    experience_gain=15,
                    materials={"stone": 2, "wooden_stick": 1},
                    tools=["hammer"],
                    result_item="stone_tool",
                    result_count=1,
                    is_discovered=True
                ),
                Recipe(
                    recipe_id="leather_armor",
                    name="Кожаная броня",
                    description="Легкая кожаная броня",
                    category="leatherworking",
                    difficulty=3,
                    required_level=3,
                    crafting_time=10.0,
                    experience_gain=25,
                    materials={"leather": 3, "thread": 2},
                    tools=["needle"],
                    result_item="leather_armor",
                    result_count=1,
                    is_discovered=True
                )
            ]
            
            # Средние рецепты
            medium_recipes = [
                Recipe(
                    recipe_id="iron_sword",
                    name="Железный меч",
                    description="Надежный железный меч",
                    category="blacksmithing",
                    difficulty=5,
                    required_level=5,
                    crafting_time=20.0,
                    experience_gain=50,
                    materials={"iron_ingot": 2, "wooden_stick": 1},
                    tools=["anvil", "hammer"],
                    result_item="iron_sword",
                    result_count=1,
                    is_discovered=False,
                    discovery_chance=0.3
                ),
                Recipe(
                    recipe_id="healing_potion",
                    name="Зелье лечения",
                    description="Восстанавливает здоровье",
                    category="alchemy",
                    difficulty=4,
                    required_level=4,
                    crafting_time=15.0,
                    experience_gain=40,
                    materials={"herb": 2, "water": 1, "bottle": 1},
                    tools=["cauldron"],
                    result_item="healing_potion",
                    result_count=1,
                    is_discovered=False,
                    discovery_chance=0.4
                )
            ]
            
            # Сложные рецепты
            complex_recipes = [
                Recipe(
                    recipe_id="magic_staff",
                    name="Магический посох",
                    description="Мощный магический посох",
                    category="enchanting",
                    difficulty=8,
                    required_level=8,
                    crafting_time=60.0,
                    experience_gain=100,
                    materials={"rare_wood": 1, "magic_crystal": 2, "gold_ingot": 1},
                    tools=["enchanting_table"],
                    result_item="magic_staff",
                    result_count=1,
                    is_discovered=False,
                    discovery_chance=0.1
                ),
                Recipe(
                    recipe_id="dragon_armor",
                    name="Драконья броня",
                    description="Легендарная броня из чешуи дракона",
                    category="armorsmithing",
                    difficulty=10,
                    required_level=10,
                    crafting_time=120.0,
                    experience_gain=200,
                    materials={"dragon_scale": 5, "mythril_ingot": 3, "enchanted_thread": 2},
                    tools=["master_anvil", "magic_hammer"],
                    result_item="dragon_armor",
                    result_count=1,
                    is_discovered=False,
                    discovery_chance=0.05
                )
            ]
            
            # Добавляем все рецепты
            all_recipes = simple_recipes + medium_recipes + complex_recipes
            for recipe in all_recipes:
                self.recipes[recipe.recipe_id] = recipe
            
            logger.info(f"Создано {len(all_recipes)} базовых рецептов")
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых рецептов: {e}")
    
    def _update_crafting_sessions(self, delta_time: float) -> None:
        """Обновление активных сессий крафтинга"""
        try:
            current_time = time.time()
            
            for session_id, session in list(self.crafting_sessions.items()):
                if session.is_completed or session.is_failed:
                    continue
                
                # Обновляем прогресс
                recipe = self.recipes.get(session.recipe_id)
                if recipe:
                    progress_increment = delta_time / recipe.crafting_time
                    session.progress = min(1.0, session.progress + progress_increment)
                    
                    # Проверяем завершение
                    if session.progress >= 1.0:
                        session.is_completed = True
                        session.crafting_time = current_time - session.start_time
                        
                        # Определяем успех
                        if self._check_crafting_success(recipe, session):
                            self._complete_crafting_session(session, True)
                        else:
                            self._complete_crafting_session(session, False)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления сессий крафтинга: {e}")
    
    def _check_completed_sessions(self) -> None:
        """Проверка завершенных сессий"""
        try:
            # Удаляем завершенные сессии
            completed_sessions = [
                session_id for session_id, session in self.crafting_sessions.items()
                if session.is_completed or session.is_failed
            ]
            
            for session_id in completed_sessions:
                del self.crafting_sessions[session_id]
                
        except Exception as e:
            logger.warning(f"Ошибка проверки завершенных сессий: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['total_recipes'] = len(self.recipes)
            self.system_stats['active_sessions'] = len(self.crafting_sessions)
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            crafting_skills = event_data.get('crafting_skills', [])
            
            if entity_id:
                # Здесь можно добавить логику для новых сущностей
                logger.debug(f"Обработано событие создания сущности {entity_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                # Отменяем все активные сессии крафтинга
                self._cancel_entity_crafting_sessions(entity_id)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения сущности: {e}")
            return False
    
    def _handle_item_acquired(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события получения предмета"""
        try:
            entity_id = event_data.get('entity_id')
            item_id = event_data.get('item_id')
            item_type = event_data.get('item_type')
            
            if entity_id and item_id and item_type:
                # Проверяем, не разблокирует ли предмет новые рецепты
                self._check_recipe_unlocks(entity_id, item_id, item_type)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события получения предмета: {e}")
            return False
    
    def _handle_skill_learned(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изучения навыка"""
        try:
            entity_id = event_data.get('entity_id')
            skill_name = event_data.get('skill_name')
            
            if entity_id and skill_name:
                # Проверяем, не разблокирует ли навык новые рецепты
                self._check_skill_recipe_unlocks(entity_id, skill_name)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события изучения навыка: {e}")
            return False
    
    def start_crafting(self, entity_id: str, recipe_id: str, materials: Dict[str, int] = None) -> Optional[str]:
        """Начало крафтинга"""
        try:
            if entity_id not in self.recipes:
                logger.warning(f"Рецепт {recipe_id} не найден")
                return None
            
            recipe = self.recipes[recipe_id]
            
            # Проверяем требования
            if not self._check_recipe_requirements(entity_id, recipe):
                logger.warning(f"Не выполнены требования рецепта {recipe_id}")
                return None
            
            # Проверяем лимит сессий
            if len(self.crafting_sessions) >= self.system_settings['max_crafting_sessions']:
                logger.warning("Достигнут лимит активных сессий крафтинга")
                return None
            
            # Создаем сессию крафтинга
            session_id = f"craft_{entity_id}_{int(time.time() * 1000)}"
            session = CraftingSession(
                session_id=session_id,
                entity_id=entity_id,
                recipe_id=recipe_id
            )
            
            # Добавляем в систему
            self.crafting_sessions[session_id] = session
            
            # Записываем в историю
            current_time = time.time()
            self.crafting_history.append({
                'timestamp': current_time,
                'action': 'crafting_started',
                'session_id': session_id,
                'entity_id': entity_id,
                'recipe_id': recipe_id
            })
            
            logger.info(f"Начата сессия крафтинга {session_id} для {entity_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Ошибка начала крафтинга {recipe_id} для {entity_id}: {e}")
            return None
    
    def _check_recipe_requirements(self, entity_id: str, recipe: Recipe) -> bool:
        """Проверка требований рецепта"""
        try:
            # Здесь должна быть проверка уровня, навыков, материалов и инструментов
            # Пока просто возвращаем True для демонстрации
            return True
            
        except Exception as e:
            logger.warning(f"Ошибка проверки требований рецепта: {e}")
            return False
    
    def _check_crafting_success(self, recipe: Recipe, session: CraftingSession) -> bool:
        """Проверка успеха крафтинга"""
        try:
            # Базовая вероятность успеха
            base_chance = recipe.success_chance
            
            # Применяем случайность
            if random.random() <= base_chance:
                return True
            else:
                return False
                
        except Exception as e:
            logger.warning(f"Ошибка проверки успеха крафтинга: {e}")
            return False
    
    def _complete_crafting_session(self, session: CraftingSession, success: bool) -> None:
        """Завершение сессии крафтинга"""
        try:
            recipe = self.recipes.get(session.recipe_id)
            if not recipe:
                return
            
            if success:
                # Успешный крафтинг
                session.result_items = [recipe.result_item] * recipe.result_count
                session.experience_gained = recipe.experience_gain
                
                # Записываем в историю
                current_time = time.time()
                self.crafting_history.append({
                    'timestamp': current_time,
                    'action': 'crafting_completed',
                    'session_id': session.session_id,
                    'entity_id': session.entity_id,
                    'recipe_id': session.recipe_id,
                    'result_items': session.result_items,
                    'experience_gained': session.experience_gained
                })
                
                self.system_stats['completed_crafts'] += 1
                self.system_stats['total_experience_gained'] += session.experience_gained
                
                logger.info(f"Крафтинг {session.recipe_id} успешно завершен")
            else:
                # Неудачный крафтинг
                session.is_failed = True
                
                # Записываем в историю
                current_time = time.time()
                self.crafting_history.append({
                    'timestamp': current_time,
                    'action': 'crafting_failed',
                    'session_id': session.session_id,
                    'entity_id': session.entity_id,
                    'recipe_id': session.recipe_id
                })
                
                self.system_stats['failed_crafts'] += 1
                
                logger.info(f"Крафтинг {session.recipe_id} провален")
                
        except Exception as e:
            logger.error(f"Ошибка завершения сессии крафтинга: {e}")
    
    def _cancel_entity_crafting_sessions(self, entity_id: str) -> None:
        """Отмена всех сессий крафтинга сущности"""
        try:
            sessions_to_cancel = [
                session_id for session_id, session in self.crafting_sessions.items()
                if session.entity_id == entity_id
            ]
            
            for session_id in sessions_to_cancel:
                session = self.crafting_sessions[session_id]
                session.is_failed = True
                
                # Записываем в историю
                current_time = time.time()
                self.crafting_history.append({
                    'timestamp': current_time,
                    'action': 'crafting_cancelled',
                    'session_id': session_id,
                    'entity_id': entity_id,
                    'recipe_id': session.recipe_id
                })
                
                logger.debug(f"Отменена сессия крафтинга {session_id}")
                
        except Exception as e:
            logger.error(f"Ошибка отмены сессий крафтинга для {entity_id}: {e}")
    
    def _check_recipe_unlocks(self, entity_id: str, item_id: str, item_type: str) -> None:
        """Проверка разблокировки рецептов при получении предмета"""
        try:
            if not self.system_settings['auto_discovery_enabled']:
                return
            
            for recipe in self.recipes.values():
                if not recipe.is_discovered and recipe.recipe_id not in self.crafting_history:
                    # Проверяем, не разблокирует ли предмет рецепт
                    if self._check_item_recipe_unlock(recipe, item_id, item_type):
                        if random.random() <= recipe.discovery_chance:
                            recipe.is_discovered = True
                            logger.info(f"Открыт рецепт {recipe.name} для {entity_id}")
                            
        except Exception as e:
            logger.warning(f"Ошибка проверки разблокировки рецептов: {e}")
    
    def _check_item_recipe_unlock(self, recipe: Recipe, item_id: str, item_type: str) -> bool:
        """Проверка разблокировки рецепта предметом"""
        try:
            # Здесь должна быть логика проверки разблокировки
            # Пока просто возвращаем False для демонстрации
            return False
            
        except Exception as e:
            logger.warning(f"Ошибка проверки разблокировки рецепта предметом: {e}")
            return False
    
    def _check_skill_recipe_unlocks(self, entity_id: str, skill_name: str) -> None:
        """Проверка разблокировки рецептов при изучении навыка"""
        try:
            if not self.system_settings['auto_discovery_enabled']:
                return
            
            for recipe in self.recipes.values():
                if not recipe.is_discovered and recipe.recipe_id not in self.crafting_history:
                    # Проверяем, не разблокирует ли навык рецепт
                    if self._check_skill_recipe_unlock(recipe, skill_name):
                        if random.random() <= recipe.discovery_chance:
                            recipe.is_discovered = True
                            logger.info(f"Открыт рецепт {recipe.name} для {entity_id}")
                            
        except Exception as e:
            logger.warning(f"Ошибка проверки разблокировки рецептов навыком: {e}")
    
    def _check_skill_recipe_unlock(self, recipe: Recipe, skill_name: str) -> bool:
        """Проверка разблокировки рецепта навыком"""
        try:
            # Здесь должна быть логика проверки разблокировки
            # Пока просто возвращаем False для демонстрации
            return False
            
        except Exception as e:
            logger.warning(f"Ошибка проверки разблокировки рецепта навыком: {e}")
            return False
    
    def get_recipe_info(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о рецепте"""
        try:
            if recipe_id not in self.recipes:
                return None
            
            recipe = self.recipes[recipe_id]
            
            return {
                'recipe_id': recipe.recipe_id,
                'name': recipe.name,
                'description': recipe.description,
                'category': recipe.category,
                'difficulty': recipe.difficulty,
                'required_level': recipe.required_level,
                'crafting_time': recipe.crafting_time,
                'experience_gain': recipe.experience_gain,
                'success_chance': recipe.success_chance,
                'materials': recipe.materials,
                'tools': recipe.tools,
                'result_item': recipe.result_item,
                'result_count': recipe.result_count,
                'result_quality': recipe.result_quality,
                'unlock_conditions': recipe.unlock_conditions,
                'is_discovered': recipe.is_discovered,
                'discovery_chance': recipe.discovery_chance
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о рецепте {recipe_id}: {e}")
            return None
    
    def get_available_recipes(self, entity_id: str, category: str = None) -> List[Dict[str, Any]]:
        """Получение доступных рецептов"""
        try:
            available_recipes = []
            
            for recipe in self.recipes.values():
                if not recipe.is_discovered:
                    continue
                
                if category and recipe.category != category:
                    continue
                
                # Проверяем доступность
                if self._check_recipe_requirements(entity_id, recipe):
                    recipe_info = self.get_recipe_info(recipe.recipe_id)
                    if recipe_info:
                        available_recipes.append(recipe_info)
            
            return available_recipes
            
        except Exception as e:
            logger.error(f"Ошибка получения доступных рецептов для {entity_id}: {e}")
            return []
    
    def get_crafting_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о сессии крафтинга"""
        try:
            if session_id not in self.crafting_sessions:
                return None
            
            session = self.crafting_sessions[session_id]
            recipe = self.recipes.get(session.recipe_id)
            
            return {
                'session_id': session.session_id,
                'entity_id': session.entity_id,
                'recipe_id': session.recipe_id,
                'recipe_name': recipe.name if recipe else "Неизвестный рецепт",
                'start_time': session.start_time,
                'progress': session.progress,
                'is_completed': session.is_completed,
                'is_failed': session.is_failed,
                'result_items': session.result_items,
                'experience_gained': session.experience_gained,
                'materials_used': session.materials_used
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о сессии крафтинга {session_id}: {e}")
            return None
    
    def cancel_crafting(self, session_id: str) -> bool:
        """Отмена крафтинга"""
        try:
            if session_id not in self.crafting_sessions:
                return False
            
            session = self.crafting_sessions[session_id]
            session.is_failed = True
            
            # Записываем в историю
            current_time = time.time()
            self.crafting_history.append({
                'timestamp': current_time,
                'action': 'crafting_cancelled',
                'session_id': session_id,
                'entity_id': session.entity_id,
                'recipe_id': session.recipe_id
            })
            
            logger.info(f"Отменен крафтинг {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отмены крафтинга {session_id}: {e}")
            return False
    
    def get_crafting_history(self, entity_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение истории крафтинга"""
        try:
            if entity_id:
                # Фильтруем по сущности
                filtered_history = [
                    entry for entry in self.crafting_history
                    if entry.get('entity_id') == entity_id
                ]
                return filtered_history[-limit:]
            else:
                # Возвращаем всю историю
                return self.crafting_history[-limit:]
                
        except Exception as e:
            logger.error(f"Ошибка получения истории крафтинга: {e}")
            return []
    
    def add_custom_recipe(self, recipe_data: Dict[str, Any]) -> bool:
        """Добавление пользовательского рецепта"""
        try:
            recipe_id = recipe_data.get('recipe_id')
            if not recipe_id or recipe_id in self.recipes:
                return False
            
            # Создаем новый рецепт
            recipe = Recipe(
                recipe_id=recipe_id,
                name=recipe_data.get('name', ''),
                description=recipe_data.get('description', ''),
                category=recipe_data.get('category', 'custom'),
                difficulty=recipe_data.get('difficulty', 1),
                required_level=recipe_data.get('required_level', 1),
                crafting_time=recipe_data.get('crafting_time', 1.0),
                experience_gain=recipe_data.get('experience_gain', 10),
                success_chance=recipe_data.get('success_chance', 1.0),
                materials=recipe_data.get('materials', {}),
                tools=recipe_data.get('tools', []),
                result_item=recipe_data.get('result_item', ''),
                result_count=recipe_data.get('result_count', 1),
                result_quality=recipe_data.get('result_quality', 1.0),
                unlock_conditions=recipe_data.get('unlock_conditions', {}),
                is_discovered=recipe_data.get('is_discovered', True),
                discovery_chance=recipe_data.get('discovery_chance', 0.0)
            )
            
            # Добавляем в систему
            self.recipes[recipe_id] = recipe
            
            logger.info(f"Добавлен пользовательский рецепт {recipe_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления пользовательского рецепта: {e}")
            return False
    
    def remove_recipe(self, recipe_id: str) -> bool:
        """Удаление рецепта"""
        try:
            if recipe_id not in self.recipes:
                return False
            
            # Проверяем, нет ли активных сессий с этим рецептом
            active_sessions = [
                session_id for session_id, session in self.crafting_sessions.items()
                if session.recipe_id == recipe_id
            ]
            
            if active_sessions:
                logger.warning(f"Нельзя удалить рецепт {recipe_id} - есть активные сессии")
                return False
            
            # Удаляем рецепт
            del self.recipes[recipe_id]
            
            logger.info(f"Удален рецепт {recipe_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления рецепта {recipe_id}: {e}")
            return False

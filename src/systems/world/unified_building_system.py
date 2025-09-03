#!/usr/bin/env python3
"""Объединенная система зданий и структур
Централизует все функции связанные со зданиями, структурами и поселениями"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import time
import random

from ...core.architecture import BaseComponent, ComponentType, Priority, LifecycleState
from ...core.constants import BuildingType, StructureType
from ...core.state_manager import StateManager, StateType

logger = logging.getLogger(__name__)

# = ДОПОЛНИТЕЛЬНЫЕ ТИПЫ

class BuildingStatus(Enum):
    """Статусы зданий"""
    UNDER_CONSTRUCTION = "under_construction"
    COMPLETED = "completed"
    DAMAGED = "damaged"
    DESTROYED = "destroyed"
    ABANDONED = "abandoned"
    RENOVATING = "renovating"

class StructureStatus(Enum):
    """Статусы структур"""
    INTACT = "intact"
    DAMAGED = "damaged"
    RUINED = "ruined"
    COLLAPSED = "collapsed"
    UNDER_REPAIR = "under_repair"

class BuildingFunction(Enum):
    """Функции зданий"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MILITARY = "military"
    RELIGIOUS = "religious"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    STORAGE = "storage"

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class BuildingTemplate:
    """Шаблон здания"""
    building_id: str
    name: str
    description: str
    building_type: BuildingType
    function: BuildingFunction
    size: Tuple[float, float, float]  # width, height, depth
    construction_time: float
    construction_cost: Dict[str, int]
    maintenance_cost: Dict[str, int]
    capacity: int
    durability: float
    required_level: int = 1
    required_technology: List[str] = field(default_factory=list)
    provides_services: List[str] = field(default_factory=list)
    model_path: Optional[str] = None

@dataclass
class Building:
    """Здание"""
    building_id: str
    template_id: str
    name: str
    building_type: BuildingType
    status: BuildingStatus
    position: Tuple[float, float, float]
    rotation: float
    owner_id: Optional[str]
    construction_progress: float = 0.0
    health: float = 100.0
    max_health: float = 100.0
    last_maintenance: float = field(default_factory=time.time)
    occupants: List[str] = field(default_factory=list)
    inventory: Dict[str, int] = field(default_factory=dict)
    services_active: bool = True
    created_at: float = field(default_factory=time.time)

@dataclass
class Structure:
    """Структура"""
    structure_id: str
    name: str
    structure_type: StructureType
    status: StructureStatus
    position: Tuple[float, float, float]
    size: Tuple[float, float, float]
    rotation: float
    health: float = 100.0
    max_health: float = 100.0
    stability: float = 100.0
    age: float = 0.0
    material: str = "stone"
    created_at: float = field(default_factory=time.time)
    last_inspected: float = field(default_factory=time.time)

@dataclass
class Settlement:
    """Поселение"""
    settlement_id: str
    name: str
    position: Tuple[float, float]
    size: float
    population: int
    buildings: List[str] = field(default_factory=list)
    structures: List[str] = field(default_factory=list)
    resources: Dict[str, int] = field(default_factory=dict)
    prosperity: float = 50.0
    defense_rating: float = 10.0
    trade_routes: List[str] = field(default_factory=list)
    ruler_id: Optional[str] = None
    founded_at: float = field(default_factory=time.time)

class UnifiedBuildingSystem(BaseComponent):
    """Объединенная система зданий и структур
    Управляет всеми зданиями, структурами и поселениями в игре"""
    
    def __init__(self):
        super().__init__(
            component_id="unified_building_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.NORMAL
        )
        
        # Архитектурные компоненты
        self.state_manager: Optional[StateManager] = None
        self.world_manager: Optional[Any] = None
        
        # Данные
        self.building_templates: Dict[str, BuildingTemplate] = {}
        self.buildings: Dict[str, Building] = {}
        self.structures: Dict[str, Structure] = {}
        self.settlements: Dict[str, Settlement] = {}
        
        # Генерация
        self.generation_settings = {
            'auto_generate_settlements': True,
            'settlement_density': 0.1,
            'building_variety': 0.8,
            'structure_decay_rate': 0.01,
            'maintenance_interval': 86400.0  # 1 день
        }
        
        # Статистика
        self.stats = {
            'total_buildings': 0,
            'active_buildings': 0,
            'total_structures': 0,
            'total_settlements': 0,
            'construction_projects': 0,
            'maintenance_operations': 0
        }
        
        logger.info("Объединенная система зданий создана")
    
    def set_architecture_components(self, state_manager: StateManager, world_manager=None):
        """Установка архитектурных компонентов"""
        self.state_manager = state_manager
        self.world_manager = world_manager
        logger.info("Архитектурные компоненты установлены в UnifiedBuildingSystem")
    
    def initialize(self) -> bool:
        """Инициализация системы зданий"""
        try:
            logger.info("Инициализация объединенной системы зданий...")
            
            # Регистрация состояний
            self._register_system_states()
            
            # Загрузка шаблонов зданий
            self._load_building_templates()
            
            # Инициализация генератора
            self._initialize_generator()
            
            self.system_state = LifecycleState.READY
            logger.info("Объединенная система зданий инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы зданий: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def start(self) -> bool:
        """Запуск системы зданий"""
        try:
            logger.info("Запуск объединенной системы зданий...")
            
            if self.system_state != LifecycleState.READY:
                logger.error("Система не готова к запуску")
                return False
            
            # Запуск процессов обслуживания
            self._start_maintenance_processes()
            
            self.system_state = LifecycleState.RUNNING
            logger.info("Объединенная система зданий запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска системы зданий: {e}")
            self.system_state = LifecycleState.ERROR
            return False
    
    def _load_building_templates(self):
        """Загрузка шаблонов зданий"""
        try:
            # Базовые шаблоны зданий
            templates = {
                "house": BuildingTemplate(
                    building_id="house",
                    name="Дом",
                    description="Простое жилое здание",
                    building_type=BuildingType.HOUSE,
                    function=BuildingFunction.RESIDENTIAL,
                    size=(10, 10, 8),
                    construction_time=3600,  # 1 час
                    construction_cost={"wood": 50, "stone": 30},
                    maintenance_cost={"gold": 10},
                    capacity=4,
                    durability=100.0
                ),
                "shop": BuildingTemplate(
                    building_id="shop",
                    name="Магазин",
                    description="Торговое здание",
                    building_type=BuildingType.SHOP,
                    function=BuildingFunction.COMMERCIAL,
                    size=(8, 12, 6),
                    construction_time=7200,  # 2 часа
                    construction_cost={"wood": 30, "stone": 40, "gold": 100},
                    maintenance_cost={"gold": 20},
                    capacity=2,
                    durability=120.0,
                    provides_services=["trading", "item_repair"]
                ),
                "workshop": BuildingTemplate(
                    building_id="workshop",
                    name="Мастерская",
                    description="Производственное здание",
                    building_type=BuildingType.WORKSHOP,
                    function=BuildingFunction.INDUSTRIAL,
                    size=(15, 15, 10),
                    construction_time=10800,  # 3 часа
                    construction_cost={"wood": 40, "stone": 60, "iron": 20},
                    maintenance_cost={"gold": 15},
                    capacity=6,
                    durability=150.0,
                    provides_services=["crafting", "item_enhancement"]
                )
            }
            
            self.building_templates.update(templates)
            logger.info(f"Загружено {len(templates)} шаблонов зданий")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов зданий: {e}")
    
    def _initialize_generator(self):
        """Инициализация генератора"""
        try:
            # Настройка генератора поселений
            logger.info("Генератор зданий инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации генератора: {e}")
    
    def _start_maintenance_processes(self):
        """Запуск процессов обслуживания"""
        try:
            # Запуск системы обслуживания зданий
            logger.info("Процессы обслуживания запущены")
            
        except Exception as e:
            logger.error(f"Ошибка запуска процессов обслуживания: {e}")
    
    def create_building(self, template_id: str, position: Tuple[float, float, float], owner_id: Optional[str] = None) -> Optional[str]:
        """Создание здания"""
        try:
            if template_id not in self.building_templates:
                logger.error(f"Шаблон здания {template_id} не найден")
                return None
            
            template = self.building_templates[template_id]
            building_id = f"building_{len(self.buildings)}_{int(time.time())}"
            
            building = Building(
                building_id=building_id,
                template_id=template_id,
                name=template.name,
                building_type=template.building_type,
                status=BuildingStatus.UNDER_CONSTRUCTION,
                position=position,
                rotation=0.0,
                owner_id=owner_id,
                max_health=template.durability
            )
            
            self.buildings[building_id] = building
            self.stats['total_buildings'] += 1
            self.stats['construction_projects'] += 1
            
            logger.info(f"Здание {building_id} создано")
            return building_id
            
        except Exception as e:
            logger.error(f"Ошибка создания здания: {e}")
            return None
    
    def create_structure(self, structure_type: StructureType, position: Tuple[float, float, float], size: Tuple[float, float, float]) -> Optional[str]:
        """Создание структуры"""
        try:
            structure_id = f"structure_{len(self.structures)}_{int(time.time())}"
            
            structure = Structure(
                structure_id=structure_id,
                name=f"{structure_type.value.title()}",
                structure_type=structure_type,
                status=StructureStatus.INTACT,
                position=position,
                size=size,
                rotation=0.0
            )
            
            self.structures[structure_id] = structure
            self.stats['total_structures'] += 1
            
            logger.info(f"Структура {structure_id} создана")
            return structure_id
            
        except Exception as e:
            logger.error(f"Ошибка создания структуры: {e}")
            return None
    
    def create_settlement(self, name: str, position: Tuple[float, float], size: float) -> Optional[str]:
        """Создание поселения"""
        try:
            settlement_id = f"settlement_{len(self.settlements)}_{int(time.time())}"
            
            settlement = Settlement(
                settlement_id=settlement_id,
                name=name,
                position=position,
                size=size,
                population=random.randint(50, 500)
            )
            
            self.settlements[settlement_id] = settlement
            self.stats['total_settlements'] += 1
            
            # Генерация базовых зданий для поселения
            self._generate_settlement_buildings(settlement_id)
            
            logger.info(f"Поселение {settlement_id} создано")
            return settlement_id
            
        except Exception as e:
            logger.error(f"Ошибка создания поселения: {e}")
            return None
    
    def _generate_settlement_buildings(self, settlement_id: str):
        """Генерация зданий для поселения"""
        try:
            settlement = self.settlements[settlement_id]
            
            # Базовые здания для любого поселения
            basic_buildings = ["house", "shop", "workshop"]
            
            for template_id in basic_buildings:
                if template_id in self.building_templates:
                    # Случайная позиция в пределах поселения
                    x = settlement.position[0] + random.uniform(-settlement.size/2, settlement.size/2)
                    y = settlement.position[1] + random.uniform(-settlement.size/2, settlement.size/2)
                    z = 0.0
                    
                    building_id = self.create_building(template_id, (x, y, z))
                    if building_id:
                        settlement.buildings.append(building_id)
                        # Сразу завершаем строительство для NPC поселений
                        self.buildings[building_id].status = BuildingStatus.COMPLETED
                        self.buildings[building_id].construction_progress = 1.0
            
            logger.info(f"Сгенерированы здания для поселения {settlement_id}")
            
        except Exception as e:
            logger.error(f"Ошибка генерации зданий для поселения: {e}")
    
    def _register_system_states(self):
        """Регистрация состояний системы"""
        if self.state_manager:
            self.state_manager.set_state(
                f"{self.component_id}_settings",
                self.generation_settings,
                StateType.SETTINGS
            )
            
            self.state_manager.set_state(
                f"{self.component_id}_stats",
                self.stats,
                StateType.STATISTICS
            )
    
    def update(self, delta_time: float):
        """Обновление системы зданий"""
        if self.system_state != LifecycleState.RUNNING:
            return
        
        try:
            start_time = time.time()
            
            # Обновление строительства
            self._update_construction(delta_time)
            
            # Обновление обслуживания
            self._update_maintenance(delta_time)
            
            # Обновление статистики
            self._update_stats()
            
            # Обновление состояния в менеджере
            if self.state_manager:
                self.state_manager.set_state(
                    f"{self.component_id}_stats",
                    self.stats,
                    StateType.STATISTICS
                )
                
        except Exception as e:
            logger.error(f"Ошибка обновления системы зданий: {e}")
    
    def _update_construction(self, delta_time: float):
        """Обновление процесса строительства"""
        try:
            for building in self.buildings.values():
                if building.status == BuildingStatus.UNDER_CONSTRUCTION:
                    template = self.building_templates.get(building.template_id)
                    if template:
                        progress_rate = delta_time / template.construction_time
                        building.construction_progress += progress_rate
                        
                        if building.construction_progress >= 1.0:
                            building.construction_progress = 1.0
                            building.status = BuildingStatus.COMPLETED
                            building.health = building.max_health
                            self.stats['construction_projects'] -= 1
                            logger.info(f"Строительство здания {building.building_id} завершено")
                            
        except Exception as e:
            logger.error(f"Ошибка обновления строительства: {e}")
    
    def _update_maintenance(self, delta_time: float):
        """Обновление обслуживания"""
        try:
            current_time = time.time()
            
            for building in self.buildings.values():
                if building.status == BuildingStatus.COMPLETED:
                    # Проверка необходимости обслуживания
                    time_since_maintenance = current_time - building.last_maintenance
                    if time_since_maintenance > self.generation_settings['maintenance_interval']:
                        self._perform_maintenance(building)
                        
        except Exception as e:
            logger.error(f"Ошибка обновления обслуживания: {e}")
    
    def _perform_maintenance(self, building: Building):
        """Выполнение обслуживания здания"""
        try:
            # Восстановление здоровья
            building.health = min(building.max_health, building.health + 10.0)
            building.last_maintenance = time.time()
            self.stats['maintenance_operations'] += 1
            
            logger.debug(f"Выполнено обслуживание здания {building.building_id}")
            
        except Exception as e:
            logger.error(f"Ошибка обслуживания здания: {e}")
    
    def _update_stats(self):
        """Обновление статистики"""
        try:
            self.stats['total_buildings'] = len(self.buildings)
            self.stats['active_buildings'] = sum(
                1 for b in self.buildings.values() 
                if b.status == BuildingStatus.COMPLETED
            )
            self.stats['total_structures'] = len(self.structures)
            self.stats['total_settlements'] = len(self.settlements)
            self.stats['construction_projects'] = sum(
                1 for b in self.buildings.values() 
                if b.status == BuildingStatus.UNDER_CONSTRUCTION
            )
            
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")
    
    def stop(self) -> bool:
        """Остановка системы зданий"""
        try:
            logger.info("Остановка объединенной системы зданий...")
            
            self.system_state = LifecycleState.STOPPED
            logger.info("Объединенная система зданий остановлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка остановки системы зданий: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение системы зданий"""
        try:
            logger.info("Уничтожение объединенной системы зданий...")
            
            # Остановка если запущена
            if self.system_state == LifecycleState.RUNNING:
                self.stop()
            
            # Очистка данных
            self.building_templates.clear()
            self.buildings.clear()
            self.structures.clear()
            self.settlements.clear()
            
            self.system_state = LifecycleState.DESTROYED
            logger.info("Объединенная система зданий уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения системы зданий: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'component_id': self.component_id,
            'state': self.system_state.value,
            'stats': self.stats.copy(),
            'templates_count': len(self.building_templates),
            'settings': self.generation_settings.copy()
        }

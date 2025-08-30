#!/usr/bin/env python3
"""Генератор структур для процедурного мира
Создает древние руины, заброшенные города и подземные комплексы"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
import logging
import random
import time
import math

from src.core.architecture import BaseComponent, ComponentType, Priority

# = ТИПЫ СТРУКТУР
class StructureType(Enum):
    """Типы структур"""
    RUINS = "ruins"           # Древние руины
    CITY = "city"             # Заброшенный город
    DUNGEON = "dungeon"       # Подземелье
    TOWER = "tower"           # Башня
    TEMPLE = "temple"         # Храм
    FORTRESS = "fortress"      # Крепость
    MINE = "mine"             # Шахта
    CAVE = "cave"             # Пещера

class StructureSize(Enum):
    """Размеры структур"""
    SMALL = "small"           # Маленькая
    MEDIUM = "medium"         # Средняя
    LARGE = "large"           # Большая
    MASSIVE = "massive"       # Огромная

class LootRarity(Enum):
    """Редкость добычи"""
    COMMON = "common"         # Обычная
    UNCOMMON = "uncommon"     # Необычная
    RARE = "rare"             # Редкая
    EPIC = "epic"             # Эпическая
    LEGENDARY = "legendary"   # Легендарная

# = ДАТАКЛАССЫ
@dataclass
class StructureTemplate:
    """Шаблон структуры"""
    template_id: str
    name: str
    description: str
    structure_type: StructureType
    size: StructureSize
    min_level: int = 1
    max_level: int = 100
    spawn_chance: float = 0.1
    loot_tables: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    traps: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeneratedStructure:
    """Сгенерированная структура"""
    structure_id: str
    template: StructureTemplate
    position: Tuple[float, float, float]
    rotation: float = 0.0
    scale: float = 1.0
    level: int = 1
    loot_containers: List[str] = field(default_factory=list)
    active_enemies: List[str] = field(default_factory=list)
    discovered: bool = False
    explored: bool = False
    generation_time: float = field(default_factory=time.time)

@dataclass
class LootContainer:
    """Контейнер с добычей"""
    container_id: str
    name: str
    loot_type: str
    rarity: LootRarity
    items: List[str] = field(default_factory=list)
    gold: int = 0
    experience: int = 0
    locked: bool = False
    trapped: bool = False
    required_key: Optional[str] = None

# = ОСНОВНАЯ СИСТЕМА ГЕНЕРАЦИИ СТРУКТУР
class StructureGenerator(BaseComponent):
    """Генератор структур для процедурного мира"""
    
    def __init__(self):
        super().__init__(
            component_id="StructureGenerator",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Шаблоны структур
        self.structure_templates: Dict[str, StructureTemplate] = {}
        self.generated_structures: Dict[str, GeneratedStructure] = {}
        
        # Настройки генерации
        self.spawn_density = 0.01  # Структур на единицу площади
        self.min_distance = 100.0  # Минимальное расстояние между структурами
        
        # Кэш и статистика
        self.generation_cache: Dict[str, Any] = {}
        self.generation_stats = {
            "total_structures": 0,
            "structures_by_type": {},
            "total_loot_containers": 0,
            "generation_time": 0.0
        }
        
        # Инициализация шаблонов
        self._initialize_templates()
    
    def _on_initialize(self) -> bool:
        """Инициализация генератора структур"""
        try:
            self._logger.info("Генератор структур инициализирован")
            return True
        except Exception as e:
            self._logger.error(f"Ошибка инициализации генератора структур: {e}")
            return False
    
    def _initialize_templates(self):
        """Инициализация шаблонов структур"""
        try:
            # Древние руины
            self.structure_templates["ancient_ruins"] = StructureTemplate(
                template_id="ancient_ruins",
                name="Древние руины",
                description="Остатки древней цивилизации",
                structure_type=StructureType.RUINS,
                size=StructureSize.MEDIUM,
                min_level=5,
                max_level=30,
                spawn_chance=0.15,
                loot_tables=["ancient_relics", "magical_items"],
                enemies=["ancient_guardian", "corrupted_spirit"],
                traps=["poison_dart", "falling_ceiling"]
            )
            
            # Заброшенный город
            self.structure_templates["abandoned_city"] = StructureTemplate(
                template_id="abandoned_city",
                name="Заброшенный город",
                description="Покинутый город с богатой историей",
                structure_type=StructureType.CITY,
                size=StructureSize.MASSIVE,
                min_level=20,
                max_level=80,
                spawn_chance=0.05,
                loot_tables=["city_treasures", "historical_artifacts"],
                enemies=["city_scavenger", "fallen_noble"],
                traps=["explosive_barrel", "electrified_floor"]
            )
            
            # Подземелье
            self.structure_templates["underground_dungeon"] = StructureTemplate(
                template_id="underground_dungeon",
                name="Подземелье",
                description="Мрачные подземные катакомбы",
                structure_type=StructureType.DUNGEON,
                size=StructureSize.LARGE,
                min_level=10,
                max_level=50,
                spawn_chance=0.12,
                loot_tables=["dungeon_loot", "dark_artifacts"],
                enemies=["undead_warrior", "shadow_creature"],
                traps=["spike_pit", "poison_gas"]
            )
            
            # Башня мага
            self.structure_templates["mage_tower"] = StructureTemplate(
                template_id="mage_tower",
                name="Башня мага",
                description="Высокая башня, полная магических тайн",
                structure_type=StructureType.TOWER,
                size=StructureSize.MEDIUM,
                min_level=25,
                max_level=60,
                spawn_chance=0.08,
                loot_tables=["magical_tomes", "enchanted_items"],
                enemies=["rogue_mage", "magical_construct"],
                traps=["magical_barrier", "teleport_trap"]
            )
            
            # Храм
            self.structure_templates["ancient_temple"] = StructureTemplate(
                template_id="ancient_temple",
                name="Древний храм",
                description="Священное место древних богов",
                structure_type=StructureType.TEMPLE,
                size=StructureSize.LARGE,
                min_level=15,
                max_level=70,
                spawn_chance=0.06,
                loot_tables=["divine_relics", "sacred_items"],
                enemies=["temple_guardian", "corrupted_priest"],
                traps=["holy_fire", "curse_trap"]
            )
            
            self._logger.info(f"Инициализировано {len(self.structure_templates)} шаблонов структур")
            
        except Exception as e:
            self._logger.error(f"Ошибка инициализации шаблонов: {e}")
    
    def generate_structures_for_chunk(self, chunk_x: int, chunk_y: int, 
                                    chunk_size: int, world_seed: int) -> List[GeneratedStructure]:
        """Генерация структур для чанка мира"""
        try:
            start_time = time.time()
            chunk_key = f"{chunk_x}_{chunk_y}"
            
            # Проверяем кэш
            if chunk_key in self.generation_cache:
                return self.generation_cache[chunk_key]
            
            structures = []
            random.seed(world_seed + hash(chunk_key))
            
            # Определяем количество структур для чанка
            chunk_area = chunk_size * chunk_size
            target_structures = int(chunk_area * self.spawn_density)
            
            # Генерируем структуры
            for i in range(target_structures):
                if random.random() < 0.3:  # 30% шанс генерации структуры
                    structure = self._generate_random_structure(chunk_x, chunk_y, chunk_size)
                    if structure:
                        structures.append(structure)
                        self.generated_structures[structure.structure_id] = structure
            
            # Кэшируем результат
            self.generation_cache[chunk_key] = structures
            
            # Обновляем статистику
            generation_time = time.time() - start_time
            self.generation_stats["generation_time"] += generation_time
            self.generation_stats["total_structures"] += len(structures)
            
            self._logger.debug(f"Сгенерировано {len(structures)} структур для чанка {chunk_x}, {chunk_y}")
            
            return structures
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации структур для чанка {chunk_x}, {chunk_y}: {e}")
            return []
    
    def _generate_random_structure(self, chunk_x: int, chunk_y: int, chunk_size: int) -> Optional[GeneratedStructure]:
        """Генерация случайной структуры"""
        try:
            # Выбираем случайный шаблон
            available_templates = [t for t in self.structure_templates.values() 
                                 if random.random() < t.spawn_chance]
            
            if not available_templates:
                return None
            
            template = random.choice(available_templates)
            
            # Определяем позицию в чанке
            pos_x = chunk_x * chunk_size + random.uniform(0, chunk_size)
            pos_y = chunk_y * chunk_size + random.uniform(0, chunk_size)
            pos_z = 0.0  # Будет скорректировано по высоте местности
            
            # Проверяем минимальное расстояние до других структур
            if not self._check_minimum_distance((pos_x, pos_y, pos_z)):
                return None
            
            # Создаем структуру
            structure = GeneratedStructure(
                structure_id=f"{template.template_id}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
                template=template,
                position=(pos_x, pos_y, pos_z),
                rotation=random.uniform(0, 2 * math.pi),
                scale=random.uniform(0.8, 1.2),
                level=random.randint(template.min_level, template.max_level)
            )
            
            # Генерируем контейнеры с добычей
            structure.loot_containers = self._generate_loot_containers(template, structure.level)
            
            # Генерируем врагов
            structure.active_enemies = self._generate_enemies(template, structure.level)
            
            return structure
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации случайной структуры: {e}")
            return None
    
    def _check_minimum_distance(self, position: Tuple[float, float, float]) -> bool:
        """Проверка минимального расстояния до других структур"""
        try:
            for structure in self.generated_structures.values():
                distance = math.sqrt(
                    (position[0] - structure.position[0]) ** 2 +
                    (position[1] - structure.position[1]) ** 2
                )
                if distance < self.min_distance:
                    return False
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка проверки минимального расстояния: {e}")
            return True
    
    def _generate_loot_containers(self, template: StructureTemplate, level: int) -> List[str]:
        """Генерация контейнеров с добычей"""
        try:
            containers = []
            num_containers = random.randint(2, 8)  # 2-8 контейнеров на структуру
            
            for i in range(num_containers):
                container = LootContainer(
                    container_id=f"loot_{template.template_id}_{i}_{int(time.time() * 1000)}",
                    name=f"Сундук {i + 1}",
                    loot_type="treasure_chest",
                    rarity=self._determine_loot_rarity(level),
                    gold=random.randint(10, 100) * level,
                    experience=random.randint(5, 25) * level,
                    locked=random.random() < 0.3,
                    trapped=random.random() < 0.2
                )
                
                # Добавляем предметы
                container.items = self._generate_loot_items(template.loot_tables, container.rarity, level)
                
                containers.append(container.container_id)
                self.generation_stats["total_loot_containers"] += 1
            
            return containers
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации контейнеров с добычей: {e}")
            return []
    
    def _determine_loot_rarity(self, level: int) -> LootRarity:
        """Определение редкости добычи на основе уровня"""
        try:
            # Базовые шансы
            chances = {
                LootRarity.COMMON: 0.5,
                LootRarity.UNCOMMON: 0.3,
                LootRarity.RARE: 0.15,
                LootRarity.EPIC: 0.04,
                LootRarity.LEGENDARY: 0.01
            }
            
            # Модификаторы на основе уровня
            if level > 50:
                chances[LootRarity.EPIC] *= 2.0
                chances[LootRarity.LEGENDARY] *= 1.5
            elif level > 30:
                chances[LootRarity.RARE] *= 1.5
                chances[LootRarity.EPIC] *= 1.3
            
            # Нормализуем шансы
            total = sum(chances.values())
            normalized = {k: v / total for k, v in chances.items()}
            
            # Выбираем редкость
            rand = random.random()
            cumulative = 0.0
            
            for rarity, chance in normalized.items():
                cumulative += chance
                if rand <= cumulative:
                    return rarity
            
            return LootRarity.COMMON
            
        except Exception as e:
            self._logger.error(f"Ошибка определения редкости добычи: {e}")
            return LootRarity.COMMON
    
    def _generate_loot_items(self, loot_tables: List[str], rarity: LootRarity, level: int) -> List[str]:
        """Генерация предметов добычи"""
        try:
            items = []
            num_items = random.randint(1, 5)  # 1-5 предметов на контейнер
            
            # Базовые предметы для всех структур
            base_items = ["gold_coin", "silver_coin", "precious_gem"]
            
            # Предметы на основе редкости
            rarity_items = {
                LootRarity.COMMON: ["basic_weapon", "basic_armor", "health_potion"],
                LootRarity.UNCOMMON: ["enhanced_weapon", "enhanced_armor", "mana_potion"],
                LootRarity.RARE: ["magical_weapon", "magical_armor", "elixir"],
                LootRarity.EPIC: ["legendary_weapon", "legendary_armor", "phoenix_feather"],
                LootRarity.LEGENDARY: ["artifact_weapon", "artifact_armor", "dragon_scale"]
            }
            
            # Добавляем базовые предметы
            items.extend(random.sample(base_items, min(2, len(base_items))))
            
            # Добавляем предметы на основе редкости
            if rarity in rarity_items:
                rarity_item = random.choice(rarity_items[rarity])
                items.append(rarity_item)
            
            # Добавляем случайные предметы из таблиц добычи
            for loot_table in loot_tables:
                if random.random() < 0.4:  # 40% шанс
                    table_items = self._get_loot_table_items(loot_table, rarity, level)
                    if table_items:
                        items.append(random.choice(table_items))
            
            return items[:num_items]  # Ограничиваем количество
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации предметов добычи: {e}")
            return ["gold_coin"]
    
    def _get_loot_table_items(self, loot_table: str, rarity: LootRarity, level: int) -> List[str]:
        """Получение предметов из таблицы добычи"""
        try:
            # Заглушка для таблиц добычи
            # В реальной реализации здесь будет загрузка из конфигурации
            loot_tables = {
                "ancient_relics": ["ancient_scroll", "mysterious_artifact", "forgotten_tome"],
                "magical_items": ["magic_wand", "enchanted_ring", "spell_book"],
                "city_treasures": ["noble_crown", "royal_jewel", "city_seal"],
                "historical_artifacts": ["historical_document", "ancient_map", "royal_scepter"],
                "dungeon_loot": ["dark_blade", "shadow_cloak", "soul_gem"],
                "dark_artifacts": ["cursed_weapon", "demonic_armor", "void_crystal"],
                "magical_tomes": ["spell_tome", "ritual_book", "arcane_scroll"],
                "enchanted_items": ["enchanted_sword", "magical_staff", "crystal_orb"],
                "divine_relics": ["holy_symbol", "sacred_weapon", "blessed_armor"],
                "sacred_items": ["divine_scroll", "holy_relic", "sacred_gem"]
            }
            
            return loot_tables.get(loot_table, ["mysterious_item"])
            
        except Exception as e:
            self._logger.error(f"Ошибка получения предметов из таблицы добычи: {e}")
            return ["mysterious_item"]
    
    def _generate_enemies(self, template: StructureTemplate, level: int) -> List[str]:
        """Генерация врагов для структуры"""
        try:
            enemies = []
            num_enemies = random.randint(1, 6)  # 1-6 врагов на структуру
            
            for i in range(num_enemies):
                if template.enemies:
                    enemy_type = random.choice(template.enemies)
                    enemy_id = f"{enemy_type}_{i}_{int(time.time() * 1000)}"
                    enemies.append(enemy_id)
            
            return enemies
            
        except Exception as e:
            self._logger.error(f"Ошибка генерации врагов: {e}")
            return []
    
    def get_structures_in_area(self, center: Tuple[float, float, float], 
                              radius: float) -> List[GeneratedStructure]:
        """Получение структур в заданной области"""
        try:
            structures = []
            
            for structure in self.generated_structures.values():
                distance = math.sqrt(
                    (center[0] - structure.position[0]) ** 2 +
                    (center[1] - structure.position[1]) ** 2
                )
                if distance <= radius:
                    structures.append(structure)
            
            return structures
            
        except Exception as e:
            self._logger.error(f"Ошибка получения структур в области: {e}")
            return []
    
    def discover_structure(self, structure_id: str) -> bool:
        """Открытие структуры игроком"""
        try:
            if structure_id in self.generated_structures:
                structure = self.generated_structures[structure_id]
                structure.discovered = True
                
                self._logger.info(f"Структура {structure.template.name} открыта игроком")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Ошибка открытия структуры {structure_id}: {e}")
            return False
    
    def explore_structure(self, structure_id: str) -> bool:
        """Исследование структуры игроком"""
        try:
            if structure_id in self.generated_structures:
                structure = self.generated_structures[structure_id]
                structure.explored = True
                
                self._logger.info(f"Структура {structure.template.name} полностью исследована")
                return True
            
            return False
            
        except Exception as e:
            self._logger.error(f"Ошибка исследования структуры {structure_id}: {e}")
            return False
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        try:
            # Подсчитываем структуры по типам
            structures_by_type = {}
            for structure in self.generated_structures.values():
                structure_type = structure.template.structure_type.value
                structures_by_type[structure_type] = structures_by_type.get(structure_type, 0) + 1
            
            return {
                "total_structures": self.generation_stats["total_structures"],
                "structures_by_type": structures_by_type,
                "total_loot_containers": self.generation_stats["total_loot_containers"],
                "generation_time": self.generation_stats["generation_time"],
                "cache_size": len(self.generation_cache),
                "templates_count": len(self.structure_templates)
            }
            
        except Exception as e:
            self._logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def clear_cache(self) -> None:
        """Очистка кэша"""
        try:
            self.generation_cache.clear()
            self._logger.info("Кэш генератора структур очищен")
            
        except Exception as e:
            self._logger.error(f"Ошибка очистки кэша: {e}")
    
    def _on_destroy(self) -> bool:
        """Уничтожение генератора структур"""
        try:
            # Очищаем кэш
            self.clear_cache()
            
            # Очищаем структуры
            self.generated_structures.clear()
            
            # Сбрасываем статистику
            self.generation_stats = {
                "total_structures": 0,
                "structures_by_type": {},
                "total_loot_containers": 0,
                "generation_time": 0.0
            }
            
            self._logger.info("Генератор структур уничтожен")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка уничтожения генератора структур: {e}")
            return False

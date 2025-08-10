"""
Фабрика для создания сущностей.
Использует централизованный менеджер данных для создания различных типов сущностей.
"""

import random
import logging
from typing import Tuple, Optional, List
from dataclasses import dataclass

from core.data_manager import data_manager, EnemyData
from .player import Player
from .enemy import Enemy

logger = logging.getLogger(__name__)


@dataclass
class EntityTemplate:
    """Шаблон для создания сущностей."""

    id: str
    name: str
    entity_type: str
    level: int
    position: Tuple[float, float]
    attributes: dict
    combat_stats: dict
    skills: List[str]
    equipment: dict
    ai_behavior: Optional[str]
    loot_table: List[str]
    tags: List[str]


class EntityFactory:
    """Фабрика для создания различных типов сущностей."""

    def __init__(self):
        self._cache = {}

    def create_player(
        self, player_id: str = "player", position: Tuple[float, float] = (0, 0)
    ) -> Player:
        """Создание игрока."""
        try:
            player = Player(position)
            player.entity_id = player_id

            # Инициализируем AI core для игрока
            from ai.ai_core import AICore

            player.ai_core = AICore(player)

            logger.debug(f"Создан игрок: {player_id}")
            return player
        except Exception as e:
            logger.error(f"Ошибка создания игрока: {e}")
            return Player(position)

    def create_enemy(
        self,
        enemy_type: str = None,
        level: int = 1,
        position: Tuple[float, float] = None,
    ) -> Enemy:
        """Создание врага."""
        try:
            if position is None:
                position = (random.randint(-100, 100), random.randint(-100, 100))

            # Выбираем тип врага
            if enemy_type is None:
                enemy_type = self._select_random_enemy_type()

            # Получаем данные врага
            enemy_data = self._get_enemy_data(enemy_type, level)

            # Создаем врага
            enemy = Enemy(enemy_type, level, position)

            # Применяем данные
            self._apply_enemy_data(enemy, enemy_data)

            # Инициализируем AI core для врага
            from ai.ai_core import AICore

            enemy.ai_core = AICore(enemy)

            logger.debug(f"Создан враг: {enemy_type} уровня {level}")
            return enemy

        except Exception as e:
            logger.error(f"Ошибка создания врага: {e}")
            enemy = Enemy("warrior", level, position or (0, 0))
            # Инициализируем AI core даже для fallback врага
            from ai.ai_core import AICore

            enemy.ai_core = AICore(enemy)
            return enemy

    def create_boss(
        self,
        boss_type: str = None,
        level: int = 10,
        position: Tuple[float, float] = None,
    ) -> Enemy:
        """Создание босса."""
        try:
            if position is None:
                position = (random.randint(-200, 200), random.randint(-200, 200))

            # Выбираем тип босса
            if boss_type is None:
                boss_type = self._select_random_boss_type()

            # Получаем данные босса
            boss_data = self._get_boss_data(boss_type, level)

            # Создаем босса как врага с особыми параметрами
            boss = Enemy(boss_type, level, position)
            boss.is_boss = True

            # Применяем данные
            self._apply_boss_data(boss, boss_data)

            # Инициализируем AI core для босса
            from ai.ai_core import AICore

            boss.ai_core = AICore(boss)

            logger.debug(f"Создан босс: {boss_type} уровня {level}")
            return boss

        except Exception as e:
            logger.error(f"Ошибка создания босса: {e}")
            boss = Enemy("warrior", level, position or (0, 0))
            boss.is_boss = True
            # Инициализируем AI core даже для fallback босса
            from ai.ai_core import AICore

            boss.ai_core = AICore(boss)
            return boss

    def create_npc(
        self, npc_type: str, position: Tuple[float, float] = (0, 0)
    ) -> Enemy:
        """Создание NPC."""
        try:
            npc = Enemy(npc_type, 1, position)
            npc.ai_behavior = "friendly"
            logger.debug(f"Создан NPC: {npc_type}")
            return npc
        except Exception as e:
            logger.error(f"Ошибка создания NPC: {e}")
            return Enemy(npc_type, 1, position)

    def create_enemy_pack(
        self,
        pack_size: int = 3,
        level: int = 1,
        center_position: Tuple[float, float] = (0, 0),
        spread: float = 50.0,
    ) -> List[Enemy]:
        """Создание группы врагов."""
        enemies = []
        for i in range(pack_size):
            # Случайное смещение от центра группы
            offset_x = random.uniform(-spread, spread)
            offset_y = random.uniform(-spread, spread)
            position = (center_position[0] + offset_x, center_position[1] + offset_y)

            enemy = self.create_enemy(level=level, position=position)
            enemies.append(enemy)

        return enemies

    def create_boss_with_minions(
        self,
        boss_level: int = 15,
        minion_count: int = 3,
        center_position: Tuple[float, float] = (0, 0),
    ) -> Tuple[Enemy, List[Enemy]]:
        """Создание босса с миньонами."""
        # Создаем босса в центре
        boss = self.create_boss(level=boss_level, position=center_position)

        # Создаем миньонов вокруг босса
        minions = self.create_enemy_pack(
            pack_size=minion_count,
            level=max(1, boss_level - 5),
            center_position=center_position,
            spread=100.0,
        )

        return boss, minions

    def create_arena_encounter(
        self, arena_level: int, arena_type: str = "balanced"
    ) -> dict:
        """Создание аренного боя."""
        if arena_type == "boss_fight":
            # Бой с боссом
            boss = self.create_boss(level=arena_level)
            return {"type": "boss_fight", "entities": [boss]}

        elif arena_type == "horde":
            # Бой с ордой
            enemy_count = min(10, arena_level + 5)
            enemies = self.create_enemy_pack(
                pack_size=enemy_count,
                level=arena_level,
                center_position=(0, 0),
                spread=200.0,
            )
            return {"type": "horde", "entities": enemies}

        elif arena_type == "mixed":
            # Смешанный бой
            boss = self.create_boss(level=arena_level)
            minions = self.create_enemy_pack(
                pack_size=3,
                level=max(1, arena_level - 3),
                center_position=(0, 0),
                spread=150.0,
            )
            return {"type": "mixed", "entities": [boss] + minions}

        else:
            # Сбалансированный бой
            enemies = self.create_enemy_pack(
                pack_size=arena_level,
                level=arena_level,
                center_position=(0, 0),
                spread=100.0,
            )
            return {"type": "balanced", "entities": enemies}

    def _select_random_enemy_type(self) -> str:
        """Выбирает случайный тип врага."""
        enemy_types = ["warrior", "archer", "mage", "rogue", "berserker"]
        return random.choice(enemy_types)

    def _select_random_boss_type(self) -> str:
        """Выбирает случайный тип босса."""
        boss_types = ["dragon", "demon", "giant", "lich", "behemoth"]
        return random.choice(boss_types)

    def _get_enemy_data(self, enemy_type: str, level: int) -> Optional[EnemyData]:
        """Получает данные врага из менеджера данных."""
        # Ищем врага по типу
        enemies = data_manager.get_enemies_by_type(enemy_type)
        if enemies:
            # Выбираем случайного врага данного типа
            enemy_data = random.choice(enemies)
            # Масштабируем под уровень
            return self._scale_enemy_data(enemy_data, level)

        # Если не найдено, создаем базовые данные
        return self._create_default_enemy_data(enemy_type, level)

    def _get_boss_data(self, boss_type: str, level: int) -> Optional[EnemyData]:
        """Получает данные босса из менеджера данных."""
        # Ищем босса по типу
        bosses = data_manager.get_enemies_by_type(boss_type)
        if bosses:
            # Выбираем случайного босса данного типа
            boss_data = random.choice(bosses)
            # Масштабируем под уровень
            return self._scale_enemy_data(boss_data, level)

        # Если не найдено, создаем базовые данные
        return self._create_default_boss_data(boss_type, level)

    def _scale_enemy_data(self, enemy_data: EnemyData, level: int) -> EnemyData:
        """Масштабирует данные врага под уровень."""
        # Создаем копию данных
        scaled_data = EnemyData(
            id=enemy_data.id,
            name=enemy_data.name,
            description=enemy_data.description,
            enemy_type=enemy_data.enemy_type,
            level=level,
            experience_reward=enemy_data.experience_reward * level,
            attributes={k: v * level for k, v in enemy_data.attributes.items()},
            combat_stats={k: v * level for k, v in enemy_data.combat_stats.items()},
            ai_behavior=enemy_data.ai_behavior,
            loot_table=enemy_data.loot_table,
            skills=enemy_data.skills,
            tags=enemy_data.tags,
            phases=enemy_data.phases,
        )
        return scaled_data

    def _create_default_enemy_data(self, enemy_type: str, level: int) -> EnemyData:
        """Создает базовые данные врага."""
        return EnemyData(
            id=f"{enemy_type}_{level}",
            name=f"{enemy_type.title()} Level {level}",
            description=f"A level {level} {enemy_type}",
            enemy_type=enemy_type,
            level=level,
            experience_reward=10 * level,
            attributes={
                "strength": 10 * level,
                "dexterity": 8 * level,
                "intelligence": 6 * level,
                "vitality": 12 * level,
                "endurance": 10 * level,
            },
            combat_stats={
                "health": 50 * level,
                "max_health": 50 * level,
                "mana": 20 * level,
                "max_mana": 20 * level,
                "stamina": 30 * level,
                "max_stamina": 30 * level,
                "damage_output": 8 * level,
                "defense": 3 * level,
                "movement_speed": 80.0,
                "attack_speed": 1.0,
            },
            ai_behavior="aggressive",
            loot_table=[],
            skills=[],
            tags=[enemy_type],
            phases=[],
        )

    def _create_default_boss_data(self, boss_type: str, level: int) -> EnemyData:
        """Создает базовые данные босса."""
        return EnemyData(
            id=f"{boss_type}_{level}",
            name=f"{boss_type.title()} Boss Level {level}",
            description=f"A powerful level {level} {boss_type} boss",
            enemy_type=boss_type,
            level=level,
            experience_reward=50 * level,
            attributes={
                "strength": 20 * level,
                "dexterity": 15 * level,
                "intelligence": 18 * level,
                "vitality": 25 * level,
                "endurance": 20 * level,
            },
            combat_stats={
                "health": 200 * level,
                "max_health": 200 * level,
                "mana": 100 * level,
                "max_mana": 100 * level,
                "stamina": 150 * level,
                "max_stamina": 150 * level,
                "damage_output": 25 * level,
                "defense": 10 * level,
                "movement_speed": 60.0,
                "attack_speed": 0.8,
            },
            ai_behavior="boss",
            loot_table=[],
            skills=[],
            tags=[boss_type, "boss"],
            phases=[],
        )

    def _apply_enemy_data(self, enemy: Enemy, enemy_data: EnemyData):
        """Применяет данные к врагу."""
        enemy.name = enemy_data.name
        enemy.level = enemy_data.level
        enemy.experience_reward = enemy_data.experience_reward

        # Применяем атрибуты
        for attr_name, attr_value in enemy_data.attributes.items():
            enemy.attribute_manager.set_attribute_base(attr_name, attr_value)

        # Применяем боевые характеристики
        for stat_name, stat_value in enemy_data.combat_stats.items():
            if hasattr(enemy, stat_name):
                setattr(enemy, stat_name, stat_value)

        # Применяем навыки
        for skill_id in enemy_data.skills:
            # Здесь можно добавить логику применения навыков
            pass

    def _apply_boss_data(self, boss: Enemy, boss_data: EnemyData):
        """Применяет данные к боссу."""
        self._apply_enemy_data(boss, boss_data)
        boss.is_boss = True

        # Дополнительные настройки для босса
        boss.combat_stats["health"] *= 2
        boss.combat_stats["max_health"] *= 2
        boss.combat_stats["damage_output"] *= 1.5

    def clear_cache(self):
        """Очищает кэш фабрики."""
        self._cache.clear()


# Глобальный экземпляр фабрики сущностей
entity_factory = EntityFactory()

"""Оптимизированная фабрика сущностей с использованием новой системы управления ресурсами."""

import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from core.resource_manager import resource_manager
from entities.player import Player
from entities.enemy import Enemy
from entities.boss import Boss
from entities.npc import NPCEnemy

logger = logging.getLogger(__name__)


@dataclass
class EntityTemplate:
    """Шаблон для создания сущностей."""
    id: str
    name: str
    entity_type: str
    base_stats: Dict[str, Any]
    attributes: Dict[str, float]
    skills: List[str]
    equipment: Dict[str, str]
    ai_behavior: str
    loot_table: List[str]
    tags: List[str]


class OptimizedEntityFactory:
    """Оптимизированная фабрика сущностей."""
    
    def __init__(self):
        self._entity_cache = {}
        self._template_cache = {}
        self._difficulty_settings = resource_manager.get_setting("difficulty", "normal", {})
        
    def create_player(self, player_id: str = "player", position: Tuple[float, float] = (0, 0)) -> Player:
        """Создает игрока с оптимизированной загрузкой данных."""
        try:
            # Получаем шаблон игрока
            player_template = self._get_player_template()
            
            # Создаем игрока
            player = Player(player_id, position)
            
            # Применяем шаблон
            self._apply_template_to_player(player, player_template)
            
            # Применяем настройки сложности
            self._apply_difficulty_modifiers(player)
            
            logger.debug(f"Создан игрок: {player_id}")
            return player
            
        except Exception as e:
            logger.error(f"Ошибка создания игрока: {e}")
            # Возвращаем базового игрока
            return Player(player_id, position)
    
    def create_enemy(self, enemy_type: str = None, level: int = 1, 
                    position: Tuple[float, float] = None) -> Enemy:
        """Создает врага с оптимизированной загрузкой данных."""
        try:
            if position is None:
                position = (random.randint(-100, 100), random.randint(-100, 100))
            
            # Выбираем тип врага
            if enemy_type is None:
                enemy_type = self._select_random_enemy_type()
            
            # Получаем шаблон врага
            enemy_template = self._get_enemy_template(enemy_type)
            
            # Создаем врага
            enemy = Enemy(enemy_type, level, position)
            
            # Применяем шаблон
            self._apply_template_to_enemy(enemy, enemy_template, level)
            
            # Применяем настройки сложности
            self._apply_difficulty_modifiers(enemy)
            
            logger.debug(f"Создан враг: {enemy_type} уровня {level}")
            return enemy
            
        except Exception as e:
            logger.error(f"Ошибка создания врага: {e}")
            # Возвращаем базового врага
            return Enemy("warrior", level, position or (0, 0))
    
    def create_boss(self, boss_type: str = None, level: int = 10, 
                   position: Tuple[float, float] = None) -> Boss:
        """Создает босса с оптимизированной загрузкой данных."""
        try:
            if position is None:
                position = (random.randint(-200, 200), random.randint(-200, 200))
            
            # Выбираем тип босса
            if boss_type is None:
                boss_type = self._select_random_boss_type()
            
            # Получаем шаблон босса
            boss_template = self._get_boss_template(boss_type)
            
            # Создаем босса
            boss = Boss(boss_type, level, position)
            
            # Применяем шаблон
            self._apply_template_to_boss(boss, boss_template, level)
            
            # Применяем настройки сложности
            self._apply_difficulty_modifiers(boss)
            
            logger.debug(f"Создан босс: {boss_type} уровня {level}")
            return boss
            
        except Exception as e:
            logger.error(f"Ошибка создания босса: {e}")
            # Возвращаем базового босса
            return Boss("goblin_chief", level, position or (0, 0))
    
    def create_enemy_pack(self, pack_size: int = 3, level: int = 1, 
                         center_position: Tuple[float, float] = (0, 0),
                         spread: float = 50.0) -> List[Enemy]:
        """Создает группу врагов."""
        enemies = []
        
        for i in range(pack_size):
            # Случайное смещение от центра группы
            offset_x = random.uniform(-spread, spread)
            offset_y = random.uniform(-spread, spread)
            position = (center_position[0] + offset_x, center_position[1] + offset_y)
            
            # Создаем врага
            enemy = self.create_enemy(level=level, position=position)
            enemies.append(enemy)
        
        return enemies
    
    def create_boss_with_minions(self, boss_level: int = 15, minion_count: int = 3,
                                center_position: Tuple[float, float] = (0, 0)) -> Tuple[Boss, List[Enemy]]:
        """Создает босса с миньонами."""
        # Создаем босса в центре
        boss = self.create_boss(level=boss_level, position=center_position)
        
        # Создаем миньонов вокруг босса
        minions = self.create_enemy_pack(
            pack_size=minion_count,
            level=max(1, boss_level - 5),
            center_position=center_position,
            spread=100.0
        )
        
        return boss, minions
    
    def _get_player_template(self) -> EntityTemplate:
        """Получает шаблон игрока."""
        cache_key = "player_template"
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        # Загружаем данные игрока из ресурсов
        player_data = resource_manager.get_enemy("player_001")  # Используем существующую структуру
        
        if player_data:
            template = EntityTemplate(
                id=player_data['id'],
                name=player_data['name'],
                entity_type=player_data['type'],
                base_stats=player_data.get('combat_stats', {}),
                attributes=player_data.get('attributes', {}),
                skills=player_data.get('skills', []),
                equipment={},
                ai_behavior="player",
                loot_table=[],
                tags=player_data.get('tags', [])
            )
        else:
            # Шаблон по умолчанию
            template = EntityTemplate(
                id="player_default",
                name="Игрок",
                entity_type="player",
                base_stats={
                    "health": 100,
                    "max_health": 100,
                    "mana": 50,
                    "max_mana": 50,
                    "stamina": 100,
                    "max_stamina": 100,
                    "damage_output": 10,
                    "defense": 5,
                    "movement_speed": 100,
                    "attack_speed": 1.0
                },
                attributes={
                    "str_001": 10.0,
                    "dex_001": 10.0,
                    "int_001": 10.0,
                    "vit_001": 10.0,
                    "end_001": 10.0
                },
                skills=["whirlwind_attack", "healing_light"],
                equipment={},
                ai_behavior="player",
                loot_table=[],
                tags=["playable", "humanoid"]
            )
        
        self._template_cache[cache_key] = template
        return template
    
    def _get_enemy_template(self, enemy_type: str) -> EntityTemplate:
        """Получает шаблон врага."""
        cache_key = f"enemy_template_{enemy_type}"
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        # Загружаем данные врага из ресурсов
        enemies = resource_manager.get_enemies_by_type(enemy_type)
        
        if enemies:
            enemy_data = random.choice(enemies)
            template = EntityTemplate(
                id=enemy_data['id'],
                name=enemy_data['name'],
                entity_type=enemy_data['type'],
                base_stats=enemy_data.get('combat_stats', {}),
                attributes=enemy_data.get('attributes', {}),
                skills=enemy_data.get('skills', []),
                equipment={},
                ai_behavior=enemy_data.get('ai_behavior', 'aggressive'),
                loot_table=enemy_data.get('loot_table', []),
                tags=enemy_data.get('tags', [])
            )
        else:
            # Шаблон по умолчанию
            template = EntityTemplate(
                id=f"enemy_default_{enemy_type}",
                name=f"Враг {enemy_type}",
                entity_type="enemy",
                base_stats={
                    "health": 80,
                    "max_health": 80,
                    "mana": 30,
                    "max_mana": 30,
                    "stamina": 80,
                    "max_stamina": 80,
                    "damage_output": 8,
                    "defense": 3,
                    "movement_speed": 100,
                    "attack_speed": 0.8
                },
                attributes={
                    "str_001": 8.0,
                    "dex_001": 10.0,
                    "vit_001": 8.0,
                    "end_001": 6.0
                },
                skills=["basic_attack"],
                equipment={},
                ai_behavior="aggressive",
                loot_table=[],
                tags=["enemy", enemy_type]
            )
        
        self._template_cache[cache_key] = template
        return template
    
    def _get_boss_template(self, boss_type: str) -> EntityTemplate:
        """Получает шаблон босса."""
        cache_key = f"boss_template_{boss_type}"
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        # Загружаем данные босса из ресурсов
        boss_data = resource_manager.get_enemy(f"boss_{boss_type}")
        
        if boss_data:
            template = EntityTemplate(
                id=boss_data['id'],
                name=boss_data['name'],
                entity_type=boss_data['type'],
                base_stats=boss_data.get('combat_stats', {}),
                attributes=boss_data.get('attributes', {}),
                skills=boss_data.get('skills', []),
                equipment={},
                ai_behavior=boss_data.get('ai_behavior', 'boss'),
                loot_table=boss_data.get('loot_table', []),
                tags=boss_data.get('tags', [])
            )
        else:
            # Шаблон по умолчанию
            template = EntityTemplate(
                id=f"boss_default_{boss_type}",
                name=f"Босс {boss_type}",
                entity_type="boss",
                base_stats={
                    "health": 300,
                    "max_health": 300,
                    "mana": 100,
                    "max_mana": 100,
                    "stamina": 150,
                    "max_stamina": 150,
                    "damage_output": 25,
                    "defense": 15,
                    "movement_speed": 85,
                    "attack_speed": 0.9
                },
                attributes={
                    "str_001": 15.0,
                    "dex_001": 12.0,
                    "vit_001": 20.0,
                    "end_001": 15.0,
                    "int_001": 10.0
                },
                skills=["basic_attack", "special_ability"],
                equipment={},
                ai_behavior="boss",
                loot_table=[],
                tags=["boss", boss_type]
            )
        
        self._template_cache[cache_key] = template
        return template
    
    def _apply_template_to_player(self, player: Player, template: EntityTemplate):
        """Применяет шаблон к игроку."""
        # Применяем базовые характеристики
        for stat_name, stat_value in template.base_stats.items():
            if hasattr(player, stat_name):
                setattr(player, stat_name, stat_value)
        
        # Применяем атрибуты
        if hasattr(player, 'attributes'):
            player.attributes.update(template.attributes)
        
        # Применяем навыки
        if hasattr(player, 'skills'):
            player.skills.extend(template.skills)
        
        # Применяем теги
        if hasattr(player, 'tags'):
            player.tags.extend(template.tags)
    
    def _apply_template_to_enemy(self, enemy: Enemy, template: EntityTemplate, level: int):
        """Применяет шаблон к врагу."""
        # Масштабируем характеристики по уровню
        level_multiplier = 1.0 + (level - 1) * 0.2
        
        # Применяем базовые характеристики
        for stat_name, stat_value in template.base_stats.items():
            if hasattr(enemy, stat_name):
                scaled_value = stat_value * level_multiplier
                setattr(enemy, stat_name, scaled_value)
        
        # Применяем атрибуты
        if hasattr(enemy, 'attributes'):
            enemy.attributes.update(template.attributes)
        
        # Применяем навыки
        if hasattr(enemy, 'skills'):
            enemy.skills.extend(template.skills)
        
        # Применяем теги
        if hasattr(enemy, 'tags'):
            enemy.tags.extend(template.tags)
        
        # Устанавливаем тип врага
        enemy.enemy_type = template.entity_type
    
    def _apply_template_to_boss(self, boss: Boss, template: EntityTemplate, level: int):
        """Применяет шаблон к боссу."""
        # Масштабируем характеристики по уровню (боссы сильнее)
        level_multiplier = 1.0 + (level - 1) * 0.3
        
        # Применяем базовые характеристики
        for stat_name, stat_value in template.base_stats.items():
            if hasattr(boss, stat_name):
                scaled_value = stat_value * level_multiplier
                setattr(boss, stat_name, scaled_value)
        
        # Применяем атрибуты
        if hasattr(boss, 'attributes'):
            boss.attributes.update(template.attributes)
        
        # Применяем навыки
        if hasattr(boss, 'skills'):
            boss.skills.extend(template.skills)
        
        # Применяем теги
        if hasattr(boss, 'tags'):
            boss.tags.extend(template.tags)
        
        # Устанавливаем тип босса
        boss.boss_type = template.entity_type
    
    def _apply_difficulty_modifiers(self, entity):
        """Применяет модификаторы сложности к сущности."""
        difficulty = resource_manager.get_setting("game_settings", "difficulty", "normal")
        difficulty_settings = resource_manager.get_section("difficulty").get(difficulty, {})
        
        if entity.__class__ == Player:
            # Модификаторы для игрока
            health_mult = difficulty_settings.get('player_health_multiplier', 1.0)
            damage_mult = difficulty_settings.get('player_damage_multiplier', 1.0)
            
            if hasattr(entity, 'max_health'):
                entity.max_health *= health_mult
                entity.health = entity.max_health
            
            if hasattr(entity, 'damage_output'):
                entity.damage_output *= damage_mult
        
        else:
            # Модификаторы для врагов
            health_mult = difficulty_settings.get('enemy_health_multiplier', 1.0)
            damage_mult = difficulty_settings.get('enemy_damage_multiplier', 1.0)
            
            if hasattr(entity, 'max_health'):
                entity.max_health *= health_mult
                entity.health = entity.max_health
            
            if hasattr(entity, 'damage_output'):
                entity.damage_output *= damage_mult
    
    def _select_random_enemy_type(self) -> str:
        """Выбирает случайный тип врага."""
        enemy_types = ["warrior", "archer", "mage"]
        return random.choice(enemy_types)
    
    def _select_random_boss_type(self) -> str:
        """Выбирает случайный тип босса."""
        boss_types = ["goblin_chief", "orc_warlord", "dark_mage"]
        return random.choice(boss_types)
    
    def clear_cache(self):
        """Очищает кэш шаблонов."""
        self._template_cache.clear()
        logger.info("Кэш шаблонов сущностей очищен")
    
    def get_template_info(self) -> Dict[str, Any]:
        """Возвращает информацию о загруженных шаблонах."""
        return {
            'cached_templates': list(self._template_cache.keys()),
            'template_count': len(self._template_cache)
        }


# Глобальный экземпляр оптимизированной фабрики
optimized_entity_factory = OptimizedEntityFactory()

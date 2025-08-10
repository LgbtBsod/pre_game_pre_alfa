"""Фабрика для создания сущностей."""

import random
from typing import Tuple, Optional
from .player import Player
from .enemy import Enemy, EnemyGenerator
from .boss import Boss, BossGenerator
from .npc import NPCEnemy


class EntityFactory:
    """Фабрика для создания различных типов сущностей."""
    
    @staticmethod
    def create_player(entity_id: str = "player", position: Tuple[float, float] = (0, 0)) -> Player:
        """Создание игрока"""
        return Player(entity_id, position)
    
    @staticmethod
    def create_enemy(enemy_type: str = None, level: int = 1, 
                    position: Tuple[float, float] = None) -> Enemy:
        """Создание врага"""
        if position is None:
            position = (random.randint(0, 100), random.randint(0, 100))
        
        return EnemyGenerator.generate_enemy(level=level, position=position)
    
    @staticmethod
    def create_boss(boss_type: str = None, level: int = 10, 
                   position: Tuple[float, float] = None) -> Boss:
        """Создание босса"""
        if position is None:
            position = (random.randint(0, 100), random.randint(0, 100))
        
        return BossGenerator.generate_boss(level=level, position=position)
    
    @staticmethod
    def create_npc(npc_type: str, position: Tuple[float, float] = (0, 0)) -> 'NPCEnemy':
        """Создание NPC"""
        return NPCEnemy(npc_type, position)
    
    @staticmethod
    def create_random_enemy(level_range: Tuple[int, int] = (1, 5), 
                           position: Tuple[float, float] = None) -> Enemy:
        """Создание случайного врага"""
        level = random.randint(*level_range)
        return EntityFactory.create_enemy(level=level, position=position)
    
    @staticmethod
    def create_random_boss(level_range: Tuple[int, int] = (10, 20), 
                          position: Tuple[float, float] = None) -> Boss:
        """Создание случайного босса"""
        level = random.randint(*level_range)
        return EntityFactory.create_boss(level=level, position=position)
    
    @staticmethod
    def create_enemy_pack(pack_size: int = 3, level: int = 1, 
                         center_position: Tuple[float, float] = (0, 0),
                         spread: float = 50.0) -> list:
        """Создание группы врагов"""
        enemies = []
        for i in range(pack_size):
            # Случайное смещение от центра группы
            offset_x = random.uniform(-spread, spread)
            offset_y = random.uniform(-spread, spread)
            position = (center_position[0] + offset_x, center_position[1] + offset_y)
            
            enemy = EntityFactory.create_enemy(level=level, position=position)
            enemies.append(enemy)
        
        return enemies
    
    @staticmethod
    def create_boss_with_minions(boss_level: int = 15, minion_count: int = 3,
                                center_position: Tuple[float, float] = (0, 0)) -> Tuple[Boss, list]:
        """Создание босса с миньонами"""
        # Создаем босса в центре
        boss = EntityFactory.create_boss(level=boss_level, position=center_position)
        
        # Создаем миньонов вокруг босса
        minions = EntityFactory.create_enemy_pack(
            pack_size=minion_count,
            level=max(1, boss_level - 5),
            center_position=center_position,
            spread=100.0
        )
        
        return boss, minions
    
    @staticmethod
    def create_arena_encounter(arena_level: int, arena_type: str = "balanced") -> dict:
        """Создание аренного боя"""
        if arena_type == "boss_fight":
            # Бой с боссом
            boss = EntityFactory.create_boss(level=arena_level)
            return {"type": "boss_fight", "entities": [boss]}
        
        elif arena_type == "horde":
            # Бой с ордой
            enemy_count = min(10, arena_level + 5)
            enemies = EntityFactory.create_enemy_pack(
                pack_size=enemy_count,
                level=max(1, arena_level - 2)
            )
            return {"type": "horde", "entities": enemies}
        
        elif arena_type == "mixed":
            # Смешанный бой
            boss = EntityFactory.create_boss(level=arena_level)
            minions = EntityFactory.create_enemy_pack(
                pack_size=5,
                level=max(1, arena_level - 3)
            )
            return {"type": "mixed", "entities": [boss] + minions}
        
        else:
            # Сбалансированный бой
            enemy_count = arena_level + 2
            enemies = EntityFactory.create_enemy_pack(
                pack_size=enemy_count,
                level=arena_level
            )
            return {"type": "balanced", "entities": enemies}

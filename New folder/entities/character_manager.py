#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
МЕНЕДЖЕР ПЕРСОНАЖЕЙ
Централизованное управление всеми персонажами в игре
Соблюдает принцип единой ответственности
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from character import Character
from enemy import Enemy
from utils.logging_system import get_logger, log_system_event

class CharacterType(Enum):
    """Типы персонажей"""
    PLAYER = "player"
    ENEMY = "enemy"
    NPC = "npc"
    BOSS = "boss"

@dataclass
class CharacterData:
    """Данные персонажа"""
    character: Character
    character_type: CharacterType
    spawn_time: float
    last_update: float
    is_active: bool = True

class CharacterManager:
    """Менеджер персонажей"""
    
    def __init__(self, game):
        self.game = game
        self.characters: Dict[str, CharacterData] = {}
        self.player: Optional[Character] = None
        self.logger = get_logger("character_manager")
        
        # Настройки
        self.max_characters = 100
        self.update_interval = 0.016  # 60 FPS
        self.cleanup_interval = 5.0   # Очистка каждые 5 секунд
        self.last_cleanup = time.time()
        
        log_system_event("character_manager", "initialized")
    
    def create_player(self, x: float = 0, y: float = 0, z: float = 0, 
                     color: tuple = (0.2, 0.8, 0.2, 1)) -> Character:
        """Создание игрока"""
        if self.player:
            self.remove_character("player")
        
        player = Character(self.game, x, y, z, color)
        player.entity_id = "player"
        
        self.player = player
        self.add_character("player", player, CharacterType.PLAYER)
        
        log_system_event("character_manager", "player_created", {
            "position": (x, y, z),
            "color": color
        })
        
        return player
    
    def create_enemy(self, enemy_type: str = "basic", x: float = 0, y: float = 0, z: float = 0) -> Enemy:
        """Создание врага"""
        enemy_id = f"enemy_{int(time.time() * 1000)}"
        enemy = Enemy(self.game, x, y, z, enemy_type)
        enemy.entity_id = enemy_id
        
        self.add_character(enemy_id, enemy, CharacterType.ENEMY)
        
        log_system_event("character_manager", "enemy_created", {
            "enemy_id": enemy_id,
            "enemy_type": enemy_type,
            "position": (x, y, z)
        })
        
        return enemy
    
    def add_character(self, character_id: str, character: Character, character_type: CharacterType):
        """Добавление персонажа в менеджер"""
        if len(self.characters) >= self.max_characters:
            self.logger.warning(f"Достигнуто максимальное количество персонажей: {self.max_characters}")
            return False
        
        character_data = CharacterData(
            character=character,
            character_type=character_type,
            spawn_time=time.time(),
            last_update=time.time()
        )
        
        self.characters[character_id] = character_data
        
        log_system_event("character_manager", "character_added", {
            "character_id": character_id,
            "character_type": character_type.value
        })
        
        return True
    
    def remove_character(self, character_id: str) -> bool:
        """Удаление персонажа из менеджера"""
        if character_id not in self.characters:
            return False
        
        character_data = self.characters[character_id]
        character_data.character.destroy()
        
        del self.characters[character_id]
        
        if character_id == "player":
            self.player = None
        
        log_system_event("character_manager", "character_removed", {
            "character_id": character_id
        })
        
        return True
    
    def get_character(self, character_id: str) -> Optional[Character]:
        """Получение персонажа по ID"""
        if character_id in self.characters:
            return self.characters[character_id].character
        return None
    
    def get_characters_by_type(self, character_type: CharacterType) -> List[Character]:
        """Получение персонажей по типу"""
        characters = []
        for character_data in self.characters.values():
            if character_data.character_type == character_type and character_data.is_active:
                characters.append(character_data.character)
        return characters
    
    def get_all_enemies(self) -> List[Enemy]:
        """Получение всех врагов"""
        enemies = []
        for character_data in self.characters.values():
            if (character_data.character_type in [CharacterType.ENEMY, CharacterType.BOSS] 
                and character_data.is_active):
                enemies.append(character_data.character)
        return enemies
    
    def get_nearby_characters(self, position: tuple, radius: float, 
                            character_type: Optional[CharacterType] = None) -> List[Character]:
        """Получение персонажей в радиусе"""
        nearby = []
        x, y, z = position
        
        for character_data in self.characters.values():
            if not character_data.is_active:
                continue
            
            if character_type and character_data.character_type != character_type:
                continue
            
            char = character_data.character
            distance = math.sqrt((char.x - x)**2 + (char.y - y)**2)
            
            if distance <= radius:
                nearby.append(char)
        
        return nearby
    
    def update(self, dt: float):
        """Обновление всех персонажей"""
        current_time = time.time()
        
        # Обновляем персонажей
        for character_id, character_data in self.characters.items():
            if not character_data.is_active:
                continue
            
            try:
                character_data.character.update_cooldown(dt)
                character_data.last_update = current_time
                
                # Обновляем ИИ для врагов
                if (character_data.character_type in [CharacterType.ENEMY, CharacterType.BOSS] 
                    and self.player and self.player.is_alive()):
                    character_data.character.update_ai(self.player, dt)
                
            except Exception as e:
                self.logger.error(f"Ошибка обновления персонажа {character_id}: {e}")
                character_data.is_active = False
        
        # Периодическая очистка
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_inactive_characters()
            self.last_cleanup = current_time
    
    def _cleanup_inactive_characters(self):
        """Очистка неактивных персонажей"""
        to_remove = []
        
        for character_id, character_data in self.characters.items():
            if not character_data.is_active:
                to_remove.append(character_id)
            elif not character_data.character.is_alive():
                to_remove.append(character_id)
        
        for character_id in to_remove:
            self.remove_character(character_id)
        
        if to_remove:
            self.logger.info(f"Очищено {len(to_remove)} неактивных персонажей")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики менеджера"""
        stats = {
            'total_characters': len(self.characters),
            'active_characters': sum(1 for cd in self.characters.values() if cd.is_active),
            'player_exists': self.player is not None,
            'enemies_count': len(self.get_all_enemies()),
            'character_types': {}
        }
        
        # Подсчет по типам
        for character_data in self.characters.values():
            char_type = character_data.character_type.value
            if char_type not in stats['character_types']:
                stats['character_types'][char_type] = 0
            stats['character_types'][char_type] += 1
        
        return stats
    
    def cleanup(self):
        """Очистка всех ресурсов"""
        for character_id in list(self.characters.keys()):
            self.remove_character(character_id)
        
        self.characters.clear()
        self.player = None
        
        log_system_event("character_manager", "cleanup_completed")

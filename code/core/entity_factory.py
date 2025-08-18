"""
Entity factory for creating game objects
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
from .logger import GameLogger
from .constants import ENEMY_DATA, WEAPON_DATA, MAGIC_DATA

class EntityFactory:
    """Factory for creating game entities"""
    
    def __init__(self, resource_manager, game_data_manager, audio_manager, config_manager):
        self.resource_manager = resource_manager
        self.game_data_manager = game_data_manager
        self.audio_manager = audio_manager
        self.config_manager = config_manager
        self.logger = GameLogger("EntityFactory")
        
        # Cache for loaded sprites
        self._sprite_cache: Dict[str, List[pygame.Surface]] = {}
        
    def create_player(self, pos: Tuple[int, int], groups: List[pygame.sprite.Group], 
                     obstacle_sprites: pygame.sprite.Group, create_attack: callable,
                     destroy_attack: callable, create_magic: callable) -> 'Player':
        """Create a player entity"""
        try:
            from player import Player
            
            player = Player(
                pos=pos,
                groups=groups,
                obstacle_sprites=obstacle_sprites,
                create_attack=create_attack,
                destroy_attack=destroy_attack,
                create_magic=create_magic,
                input_manager=None,  # Will be set by the level
                audio_manager=self.audio_manager,
                resource_manager=self.resource_manager,
                game_data_manager=self.game_data_manager,
                config_manager=self.config_manager
            )
            
            self.logger.info(f"Created player at position {pos}")
            return player
            
        except Exception as e:
            self.logger.error(f"Failed to create player: {e}")
            return None
    
    def create_enemy(self, enemy_type: str, pos: Tuple[int, int], 
                    groups: List[pygame.sprite.Group], obstacle_sprites: pygame.sprite.Group,
                    damage_player: callable, trigger_death_particles: callable, 
                    add_exp: callable) -> 'Enemy':
        """Create an enemy entity"""
        try:
            from enemy import Enemy
            
            enemy = Enemy(
                monster_name=enemy_type,
                pos=pos,
                groups=groups,
                obstacle_sprites=obstacle_sprites,
                damage_player=damage_player,
                trigger_death_particles=trigger_death_particles,
                add_exp=add_exp
            )
            
            self.logger.info(f"Created {enemy_type} enemy at position {pos}")
            return enemy
            
        except Exception as e:
            self.logger.error(f"Failed to create {enemy_type} enemy: {e}")
            return None
    
    def create_tile(self, pos: Tuple[int, int], groups: List[pygame.sprite.Group], 
                   tile_type: str, surface: Optional[pygame.Surface] = None) -> 'Tile':
        """Create a tile entity"""
        try:
            from tile import Tile
            
            tile = Tile(pos, groups, tile_type, surface)
            
            self.logger.debug(f"Created {tile_type} tile at position {pos}")
            return tile
            
        except Exception as e:
            self.logger.error(f"Failed to create tile: {e}")
            return None
    
    def create_weapon(self, weapon_type: str, pos: Tuple[int, int], 
                     groups: List[pygame.sprite.Group]) -> 'Weapon':
        """Create a weapon entity"""
        try:
            from weapon import Weapon
            
            weapon = Weapon(
                pos=pos,
                groups=groups,
                create_spell=self._create_spell_for_weapon(weapon_type)
            )
            
            self.logger.info(f"Created {weapon_type} weapon at position {pos}")
            return weapon
            
        except Exception as e:
            self.logger.error(f"Failed to create weapon: {e}")
            return None
    
    def create_magic(self, magic_type: str, pos: Tuple[int, int], 
                    groups: List[pygame.sprite.Group]) -> 'Magic':
        """Create a magic entity"""
        try:
            from magic import MagicPlayer
            
            magic = MagicPlayer(animation_player=None)  # TODO: Add animation player
            
            self.logger.info(f"Created {magic_type} magic at position {pos}")
            return magic
            
        except Exception as e:
            self.logger.error(f"Failed to create magic: {e}")
            return None
    
    def _create_spell_for_weapon(self, weapon_type: str) -> callable:
        """Create a spell function for a weapon"""
        def create_spell(pos, groups):
            # TODO: Implement spell creation based on weapon type
            pass
        return create_spell
    
    def load_enemy_sprites(self, enemy_type: str) -> List[pygame.Surface]:
        """Load sprites for an enemy type"""
        cache_key = f"enemy_{enemy_type}"
        
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        
        try:
            sprite_path = f"graphics/monsters/{enemy_type}"
            sprites = self.resource_manager.load_folder(sprite_path, "image")
            
            if sprites:
                self._sprite_cache[cache_key] = sprites
                self.logger.info(f"Loaded {len(sprites)} sprites for {enemy_type}")
                return sprites
            else:
                self.logger.warning(f"No sprites found for {enemy_type}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to load sprites for {enemy_type}: {e}")
            return []
    
    def load_weapon_sprites(self, weapon_type: str) -> List[pygame.Surface]:
        """Load sprites for a weapon type"""
        cache_key = f"weapon_{weapon_type}"
        
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        
        try:
            sprite_path = f"graphics/weapons/{weapon_type}"
            sprites = self.resource_manager.load_folder(sprite_path, "image")
            
            if sprites:
                self._sprite_cache[cache_key] = sprites
                self.logger.info(f"Loaded {len(sprites)} sprites for {weapon_type}")
                return sprites
            else:
                self.logger.warning(f"No sprites found for {weapon_type}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to load sprites for {weapon_type}: {e}")
            return []
    
    def get_enemy_data(self, enemy_type: str) -> Optional[Dict[str, Any]]:
        """Get enemy data from configuration"""
        return ENEMY_DATA.get(enemy_type)
    
    def get_weapon_data(self, weapon_type: str) -> Optional[Dict[str, Any]]:
        """Get weapon data from configuration"""
        return WEAPON_DATA.get(weapon_type)
    
    def get_magic_data(self, magic_type: str) -> Optional[Dict[str, Any]]:
        """Get magic data from configuration"""
        return MAGIC_DATA.get(magic_type)
    
    def clear_cache(self) -> None:
        """Clear the sprite cache"""
        self._sprite_cache.clear()
        self.logger.info("Entity factory cache cleared")
    
    def get_cache_info(self) -> Dict[str, int]:
        """Get information about the cache"""
        return {
            'cached_entities': len(self._sprite_cache),
            'total_sprites': sum(len(sprites) for sprites in self._sprite_cache.values())
        }

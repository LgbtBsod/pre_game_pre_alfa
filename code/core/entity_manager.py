"""
Entity Manager for handling entity creation and management
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any, Callable
from .logger import GameLogger
from .entity_factory import EntityFactory

class EntityManager:
    """Manages entity creation and lifecycle according to Single Responsibility Principle"""
    
    def __init__(self, entity_factory: EntityFactory):
        self.entity_factory = entity_factory
        self.logger = GameLogger("EntityManager")
        
        # Entity storage
        self.entities: Dict[str, List[Any]] = {
            'player': [],
            'enemies': [],
            'tiles': [],
            'weapons': [],
            'magic': []
        }
        
        # Entity groups
        self.sprite_groups: Dict[str, pygame.sprite.Group] = {
            'visible': pygame.sprite.Group(),
            'obstacle': pygame.sprite.Group(),
            'attack': pygame.sprite.Group(),
            'attackable': pygame.sprite.Group()
        }
        
        # Entity callbacks
        self.callbacks: Dict[str, Callable] = {}
        
        # Entity statistics
        self.stats = {
            'total_entities': 0,
            'entities_created': 0,
            'entities_destroyed': 0
        }
    
    def set_callbacks(self, callbacks: Dict[str, Callable]) -> None:
        """Set entity callbacks"""
        self.callbacks.update(callbacks)
        self.logger.debug(f"Set {len(callbacks)} callbacks")
    
    def create_player(self, position: Tuple[int, int]) -> Optional[Any]:
        """Create a player entity"""
        try:
            player = self.entity_factory.create_player(
                pos=position,
                groups=[self.sprite_groups['visible']],
                obstacle_sprites=self.sprite_groups['obstacle'],
                create_attack=self.callbacks.get('create_attack'),
                destroy_attack=self.callbacks.get('destroy_attack'),
                create_magic=self.callbacks.get('create_magic')
            )
            
            if player:
                self.entities['player'].append(player)
                self.stats['entities_created'] += 1
                self.stats['total_entities'] += 1
                self.logger.info(f"Created player at position {position}")
                return player
            else:
                self.logger.error("Failed to create player")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating player: {e}")
            return None
    
    def create_enemy(self, enemy_type: str, position: Tuple[int, int]) -> Optional[Any]:
        """Create an enemy entity"""
        try:
            enemy = self.entity_factory.create_enemy(
                enemy_type=enemy_type,
                pos=position,
                groups=[self.sprite_groups['visible'], self.sprite_groups['attackable']],
                obstacle_sprites=self.sprite_groups['obstacle'],
                damage_player=self.callbacks.get('damage_player'),
                trigger_death_particles=self.callbacks.get('trigger_death_particles'),
                add_exp=self.callbacks.get('add_exp')
            )
            
            if enemy:
                self.entities['enemies'].append(enemy)
                self.stats['entities_created'] += 1
                self.stats['total_entities'] += 1
                self.logger.info(f"Created {enemy_type} enemy at position {position}")
                return enemy
            else:
                self.logger.error(f"Failed to create {enemy_type} enemy")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating {enemy_type} enemy: {e}")
            return None
    
    def create_tile(self, position: Tuple[int, int], tile_type: str, 
                   surface: Optional[pygame.Surface] = None) -> Optional[Any]:
        """Create a tile entity"""
        try:
            groups = [self.sprite_groups['visible']]
            if tile_type in ['boundary', 'object']:
                groups.append(self.sprite_groups['obstacle'])
            if tile_type == 'grass':
                groups.append(self.sprite_groups['attackable'])
            
            tile = self.entity_factory.create_tile(
                pos=position,
                groups=groups,
                tile_type=tile_type,
                surface=surface
            )
            
            if tile:
                self.entities['tiles'].append(tile)
                self.stats['entities_created'] += 1
                self.stats['total_entities'] += 1
                self.logger.debug(f"Created {tile_type} tile at position {position}")
                return tile
            else:
                self.logger.error(f"Failed to create {tile_type} tile")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating {tile_type} tile: {e}")
            return None
    
    def create_weapon(self, weapon_type: str, position: Tuple[int, int]) -> Optional[Any]:
        """Create a weapon entity"""
        try:
            weapon = self.entity_factory.create_weapon(
                weapon_type=weapon_type,
                pos=position,
                groups=[self.sprite_groups['visible'], self.sprite_groups['attack']]
            )
            
            if weapon:
                self.entities['weapons'].append(weapon)
                self.stats['entities_created'] += 1
                self.stats['total_entities'] += 1
                self.logger.info(f"Created {weapon_type} weapon at position {position}")
                return weapon
            else:
                self.logger.error(f"Failed to create {weapon_type} weapon")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating {weapon_type} weapon: {e}")
            return None
    
    def create_magic(self, magic_type: str, position: Tuple[int, int]) -> Optional[Any]:
        """Create a magic entity"""
        try:
            magic = self.entity_factory.create_magic(
                magic_type=magic_type,
                pos=position,
                groups=[self.sprite_groups['visible']]
            )
            
            if magic:
                self.entities['magic'].append(magic)
                self.stats['entities_created'] += 1
                self.stats['total_entities'] += 1
                self.logger.info(f"Created {magic_type} magic at position {position}")
                return magic
            else:
                self.logger.error(f"Failed to create {magic_type} magic")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating {magic_type} magic: {e}")
            return None
    
    def get_player(self) -> Optional[Any]:
        """Get the current player"""
        if self.entities['player']:
            return self.entities['player'][0]
        return None
    
    def get_enemies(self, enemy_type: Optional[str] = None) -> List[Any]:
        """Get all enemies or enemies of specific type"""
        if enemy_type:
            return [enemy for enemy in self.entities['enemies'] 
                   if hasattr(enemy, 'monster_name') and enemy.monster_name == enemy_type]
        return self.entities['enemies']
    
    def get_entities_by_type(self, entity_type: str) -> List[Any]:
        """Get all entities of a specific type"""
        return self.entities.get(entity_type, [])
    
    def get_sprite_group(self, group_name: str) -> Optional[pygame.sprite.Group]:
        """Get a sprite group by name"""
        return self.sprite_groups.get(group_name)
    
    def remove_entity(self, entity: Any, entity_type: str) -> bool:
        """Remove an entity from the manager"""
        try:
            if entity in self.entities.get(entity_type, []):
                self.entities[entity_type].remove(entity)
                self.stats['entities_destroyed'] += 1
                self.stats['total_entities'] -= 1
                self.logger.debug(f"Removed {entity_type} entity")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing {entity_type} entity: {e}")
            return False
    
    def clear_entities(self, entity_type: Optional[str] = None) -> None:
        """Clear all entities or entities of specific type"""
        if entity_type:
            if entity_type in self.entities:
                count = len(self.entities[entity_type])
                self.entities[entity_type].clear()
                self.stats['total_entities'] -= count
                self.logger.info(f"Cleared {count} {entity_type} entities")
        else:
            total_count = sum(len(entities) for entities in self.entities.values())
            for entity_list in self.entities.values():
                entity_list.clear()
            self.stats['total_entities'] = 0
            self.logger.info(f"Cleared all {total_count} entities")
    
    def update_entities(self, dt: float) -> None:
        """Update all entities"""
        try:
            # Update visible sprites
            self.sprite_groups['visible'].update(dt)
            
            # Update enemies specifically
            for enemy in self.entities['enemies']:
                if hasattr(enemy, 'enemy_update') and self.get_player():
                    enemy.enemy_update(self.get_player())
                    
        except Exception as e:
            self.logger.error(f"Error updating entities: {e}")
    
    def render_entities(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """Render all entities"""
        try:
            # Sort sprites by Y position for proper depth rendering
            sprites = sorted(self.sprite_groups['visible'].sprites(), 
                           key=lambda sprite: sprite.rect.centery)
            
            for sprite in sprites:
                offset_pos = sprite.rect.topleft - pygame.math.Vector2(camera_offset)
                surface.blit(sprite.image, offset_pos)
                
        except Exception as e:
            self.logger.error(f"Error rendering entities: {e}")
    
    def get_entity_statistics(self) -> Dict[str, Any]:
        """Get entity statistics"""
        stats = self.stats.copy()
        stats.update({
            'entity_counts': {k: len(v) for k, v in self.entities.items()},
            'sprite_group_counts': {k: len(v) for k, v in self.sprite_groups.items()}
        })
        return stats
    
    def validate_entities(self) -> bool:
        """Validate that all entities are in correct state"""
        try:
            # Check if player exists
            if not self.get_player():
                self.logger.error("No player entity found")
                return False
            
            # Check if entities are in correct groups
            for entity_type, entities in self.entities.items():
                for entity in entities:
                    if not hasattr(entity, 'groups'):
                        self.logger.error(f"{entity_type} entity missing groups attribute")
                        return False
            
            self.logger.debug("Entity validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Entity validation failed: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup entity manager resources"""
        try:
            self.clear_entities()
            for group in self.sprite_groups.values():
                group.empty()
            self.callbacks.clear()
            self.logger.info("Entity manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during entity manager cleanup: {e}")

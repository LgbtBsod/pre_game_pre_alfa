"""
Map Manager for handling map loading and creation
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from .logger import GameLogger
from .utils import load_image
from support import import_csv_layout, import_folder

class MapManager:
    """Manages map loading and creation according to Single Responsibility Principle"""
    
    def __init__(self, resource_manager=None):
        self.resource_manager = resource_manager
        self.logger = GameLogger("MapManager")
        
        # Map data storage
        self.layouts: Dict[str, List[List[str]]] = {}
        self.graphics: Dict[str, List[pygame.Surface]] = {}
        
        # Map configuration
        self.tile_size = 64
        self.map_paths = {
            'boundary': 'map/map_FloorBlocks.csv',
            'grass': 'map/map_Grass.csv',
            'object': 'map/map_Objects.csv',
            'entities': 'map/map_Entities.csv'
        }
        
        self.graphics_paths = {
            'grass': 'graphics/grass',
            'objects': 'graphics/objects'
        }
        
        # Entity mapping
        self.entity_mapping = {
            '394': 'player',
            '390': 'bamboo',
            '391': 'spirit',
            '392': 'raccoon',
            '393': 'squid'
        }
    
    def load_map_data(self) -> Tuple[Dict[str, List[List[str]]], Dict[str, List[pygame.Surface]]]:
        """Load all map data including layouts and graphics"""
        try:
            self._load_layouts()
            self._load_graphics()
            self.logger.info("Map data loaded successfully")
            return self.layouts, self.graphics
        except Exception as e:
            self.logger.error(f"Failed to load map data: {e}")
            return {}, {}
    
    def _load_layouts(self) -> None:
        """Load map layouts from CSV files"""
        for layout_type, path in self.map_paths.items():
            try:
                layout_data = import_csv_layout(path)
                if layout_data:
                    self.layouts[layout_type] = layout_data
                    self.logger.debug(f"Loaded {layout_type} layout: {len(layout_data)} rows")
                else:
                    self.logger.warning(f"Empty layout data for {layout_type}")
                    self.layouts[layout_type] = []
            except Exception as e:
                self.logger.error(f"Failed to load {layout_type} layout: {e}")
                self.layouts[layout_type] = []
    
    def _load_graphics(self) -> None:
        """Load map graphics from folders"""
        for graphics_type, path in self.graphics_paths.items():
            try:
                graphics_data = import_folder(path)
                if graphics_data:
                    self.graphics[graphics_type] = graphics_data
                    self.logger.debug(f"Loaded {graphics_type} graphics: {len(graphics_data)} images")
                else:
                    self.logger.warning(f"No graphics found for {graphics_type}")
                    self.graphics[graphics_type] = []
            except Exception as e:
                self.logger.error(f"Failed to load {graphics_type} graphics: {e}")
                self.graphics[graphics_type] = []
    
    def get_entity_positions(self, entity_type: str) -> List[Tuple[int, int]]:
        """Get all positions for a specific entity type"""
        positions = []
        
        if 'entities' not in self.layouts:
            return positions
        
        entity_id = None
        for entity_id_str, entity_name in self.entity_mapping.items():
            if entity_name == entity_type:
                entity_id = entity_id_str
                break
        
        if not entity_id:
            return positions
        
        for row_index, row in enumerate(self.layouts['entities']):
            for col_index, cell in enumerate(row):
                if cell == entity_id:
                    x = col_index * self.tile_size
                    y = row_index * self.tile_size
                    positions.append((x, y))
        
        self.logger.debug(f"Found {len(positions)} positions for {entity_type}")
        return positions
    
    def get_player_position(self) -> Optional[Tuple[int, int]]:
        """Get the player's starting position"""
        player_positions = self.get_entity_positions('player')
        if player_positions:
            return player_positions[0]
        return None
    
    def get_enemy_positions(self) -> Dict[str, List[Tuple[int, int]]]:
        """Get all enemy positions by type"""
        enemy_positions = {}
        
        for entity_name in ['bamboo', 'spirit', 'raccoon', 'squid']:
            positions = self.get_entity_positions(entity_name)
            if positions:
                enemy_positions[entity_name] = positions
        
        return enemy_positions
    
    def get_tile_data(self, tile_type: str, position: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """Get tile data for a specific position and type"""
        x, y = position
        col = x // self.tile_size
        row = y // self.tile_size
        
        if tile_type not in self.layouts:
            return None
        
        if row >= len(self.layouts[tile_type]) or col >= len(self.layouts[tile_type][row]):
            return None
        
        cell_value = self.layouts[tile_type][row][col]
        
        return {
            'value': cell_value,
            'position': position,
            'grid_position': (col, row),
            'graphics': self._get_tile_graphics(tile_type, cell_value)
        }
    
    def _get_tile_graphics(self, tile_type: str, cell_value: str) -> Optional[pygame.Surface]:
        """Get graphics for a tile"""
        if tile_type == 'grass' and 'grass' in self.graphics:
            return self._get_random_grass()
        elif tile_type == 'object' and 'objects' in self.graphics:
            return self._get_object_graphics(cell_value)
        return None
    
    def _get_random_grass(self) -> Optional[pygame.Surface]:
        """Get a random grass tile"""
        import random
        if self.graphics.get('grass'):
            return random.choice(self.graphics['grass'])
        return None
    
    def _get_object_graphics(self, cell_value: str) -> Optional[pygame.Surface]:
        """Get object graphics by index"""
        try:
            obj_index = int(cell_value)
            if 'objects' in self.graphics and 0 <= obj_index < len(self.graphics['objects']):
                return self.graphics['objects'][obj_index]
        except (ValueError, IndexError):
            pass
        return None
    
    def validate_map_data(self) -> bool:
        """Validate that all required map data is present"""
        required_layouts = ['boundary', 'grass', 'object', 'entities']
        required_graphics = ['grass', 'objects']
        
        # Check layouts
        for layout in required_layouts:
            if layout not in self.layouts or not self.layouts[layout]:
                self.logger.error(f"Missing or empty layout: {layout}")
                return False
        
        # Check graphics
        for graphics in required_graphics:
            if graphics not in self.graphics or not self.graphics[graphics]:
                self.logger.error(f"Missing or empty graphics: {graphics}")
                return False
        
        # Check for player
        player_positions = self.get_player_position()
        if not player_positions:
            self.logger.error("No player position found in map")
            return False
        
        self.logger.info("Map data validation passed")
        return True
    
    def get_map_info(self) -> Dict[str, Any]:
        """Get comprehensive map information"""
        info = {
            'layouts': {k: len(v) for k, v in self.layouts.items()},
            'graphics': {k: len(v) for k, v in self.graphics.items()},
            'player_position': self.get_player_position(),
            'enemy_positions': self.get_enemy_positions(),
            'map_size': self._get_map_size(),
            'validation_passed': self.validate_map_data()
        }
        return info
    
    def _get_map_size(self) -> Tuple[int, int]:
        """Get the map size in tiles"""
        if 'entities' in self.layouts and self.layouts['entities']:
            rows = len(self.layouts['entities'])
            cols = len(self.layouts['entities'][0]) if rows > 0 else 0
            return (cols * self.tile_size, rows * self.tile_size)
        return (0, 0)
    
    def create_fallback_map(self) -> Tuple[Dict[str, List[List[str]]], Dict[str, List[pygame.Surface]]]:
        """Create a fallback map when loading fails"""
        self.logger.warning("Creating fallback map")
        
        # Create minimal layouts
        fallback_layouts = {
            'boundary': [['1'] * 20 for _ in range(15)],
            'grass': [['1'] * 20 for _ in range(15)],
            'object': [['-1'] * 20 for _ in range(15)],
            'entities': [['-1'] * 20 for _ in range(15)]
        }
        
        # Add player in center
        fallback_layouts['entities'][7][10] = '394'
        
        # Create fallback graphics
        fallback_graphics = {
            'grass': [self._create_fallback_surface()],
            'objects': [self._create_fallback_surface()]
        }
        
        return fallback_layouts, fallback_graphics
    
    def _create_fallback_surface(self) -> pygame.Surface:
        """Create a fallback surface"""
        surf = pygame.Surface((self.tile_size, self.tile_size))
        surf.fill((100, 100, 100))
        return surf
    
    def cleanup(self) -> None:
        """Cleanup map resources"""
        self.layouts.clear()
        self.graphics.clear()
        self.logger.info("Map manager cleanup completed")

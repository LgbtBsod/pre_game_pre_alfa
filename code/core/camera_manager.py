"""
Camera Manager for handling camera movement and rendering
"""

import pygame
from typing import Tuple, Optional, Any
from .logger import GameLogger

class CameraManager:
    """Manages camera movement and rendering according to Single Responsibility Principle"""
    
    def __init__(self, screen_size: Tuple[int, int], tile_size: int = 64):
        self.logger = GameLogger("CameraManager")
        
        # Camera properties
        self.screen_size = screen_size
        self.tile_size = tile_size
        self.half_width = screen_size[0] // 2
        self.half_height = screen_size[1] // 2
        
        # Camera position and offset
        self.offset = pygame.math.Vector2()
        self.target_offset = pygame.math.Vector2()
        
        # Camera settings
        self.smooth_following = True
        self.follow_speed = 0.1
        self.bounds = None  # Optional camera bounds
        
        # Floor texture
        self.floor_surf: Optional[pygame.Surface] = None
        self.floor_rect: Optional[pygame.Rect] = None
        self._load_floor_texture()
        
        self.logger.info("Camera manager initialized")
    
    def _load_floor_texture(self) -> None:
        """Load the floor texture"""
        try:
            self.floor_surf = pygame.image.load('graphics/tilemap/ground.png').convert()
            if self.floor_surf:
                self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))
                self.logger.debug("Floor texture loaded successfully")
            else:
                raise pygame.error("Failed to load floor texture")
        except pygame.error as e:
            self.logger.warning(f"Could not load floor texture: {e}")
            self.floor_surf = self._create_fallback_floor()
            self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))
    
    def _create_fallback_floor(self) -> pygame.Surface:
        """Create a fallback floor surface"""
        surf = pygame.Surface((self.tile_size, self.tile_size))
        surf.fill((100, 100, 100))
        return surf
    
    def set_target(self, target: Any) -> None:
        """Set the camera target (usually the player)"""
        if hasattr(target, 'rect') and hasattr(target.rect, 'center'):
            self.target_offset.x = target.rect.centerx - self.half_width
            self.target_offset.y = target.rect.centery - self.half_height
            
            # Apply bounds if set
            if self.bounds:
                self.target_offset.x = max(self.bounds[0], min(self.bounds[2], self.target_offset.x))
                self.target_offset.y = max(self.bounds[1], min(self.bounds[3], self.target_offset.y))
    
    def update(self, dt: float) -> None:
        """Update camera position"""
        if self.smooth_following:
            # Smooth camera following
            self.offset.x += (self.target_offset.x - self.offset.x) * self.follow_speed
            self.offset.y += (self.target_offset.y - self.offset.y) * self.follow_speed
        else:
            # Instant camera following
            self.offset = self.target_offset.copy()
    
    def get_offset(self) -> pygame.math.Vector2:
        """Get the current camera offset"""
        return self.offset
    
    def get_offset_tuple(self) -> Tuple[int, int]:
        """Get the current camera offset as a tuple"""
        return (int(self.offset.x), int(self.offset.y))
    
    def world_to_screen(self, world_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates"""
        return (world_pos[0] - int(self.offset.x), world_pos[1] - int(self.offset.y))
    
    def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert screen coordinates to world coordinates"""
        return (screen_pos[0] + int(self.offset.x), screen_pos[1] + int(self.offset.y))
    
    def render_floor(self, surface: pygame.Surface) -> None:
        """Render the floor texture"""
        if self.floor_surf and self.floor_rect:
            floor_offset_pos = self.floor_rect.topleft - self.offset
            surface.blit(self.floor_surf, floor_offset_pos)
    
    def render_sprite(self, surface: pygame.Surface, sprite: Any) -> None:
        """Render a sprite with camera offset"""
        if hasattr(sprite, 'image') and hasattr(sprite, 'rect'):
            offset_pos = sprite.rect.topleft - self.offset
            surface.blit(sprite.image, offset_pos)
    
    def render_sprites(self, surface: pygame.Surface, sprites: list) -> None:
        """Render multiple sprites with camera offset and Y-sorting"""
        # Sort sprites by Y position for proper depth rendering
        sorted_sprites = sorted(sprites, key=lambda sprite: sprite.rect.centery)
        
        for sprite in sorted_sprites:
            self.render_sprite(surface, sprite)
    
    def is_in_view(self, rect: pygame.Rect, margin: int = 100) -> bool:
        """Check if a rectangle is in camera view"""
        screen_rect = pygame.Rect(0, 0, self.screen_size[0], self.screen_size[1])
        screen_rect.inflate_ip(margin * 2, margin * 2)
        
        world_rect = rect.copy()
        world_rect.x -= int(self.offset.x)
        world_rect.y -= int(self.offset.y)
        
        return screen_rect.colliderect(world_rect)
    
    def set_bounds(self, bounds: Optional[Tuple[int, int, int, int]]) -> None:
        """Set camera bounds (left, top, right, bottom)"""
        self.bounds = bounds
        if bounds:
            self.logger.debug(f"Camera bounds set: {bounds}")
        else:
            self.logger.debug("Camera bounds cleared")
    
    def set_smooth_following(self, enabled: bool, speed: float = 0.1) -> None:
        """Set smooth camera following"""
        self.smooth_following = enabled
        self.follow_speed = speed
        self.logger.debug(f"Smooth following {'enabled' if enabled else 'disabled'} with speed {speed}")
    
    def shake(self, intensity: float, duration: float) -> None:
        """Add camera shake effect"""
        # TODO: Implement camera shake
        self.logger.debug(f"Camera shake: intensity={intensity}, duration={duration}")
    
    def zoom(self, factor: float) -> None:
        """Set camera zoom factor"""
        # TODO: Implement camera zoom
        self.logger.debug(f"Camera zoom: factor={factor}")
    
    def reset(self) -> None:
        """Reset camera to initial state"""
        self.offset = pygame.math.Vector2()
        self.target_offset = pygame.math.Vector2()
        self.logger.debug("Camera reset")
    
    def get_camera_info(self) -> dict:
        """Get camera information"""
        return {
            'offset': self.get_offset_tuple(),
            'target_offset': (int(self.target_offset.x), int(self.target_offset.y)),
            'screen_size': self.screen_size,
            'tile_size': self.tile_size,
            'smooth_following': self.smooth_following,
            'follow_speed': self.follow_speed,
            'bounds': self.bounds
        }
    
    def cleanup(self) -> None:
        """Cleanup camera resources"""
        self.floor_surf = None
        self.floor_rect = None
        self.logger.info("Camera manager cleanup completed")

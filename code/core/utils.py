"""
Utility functions and helper classes
"""

import pygame
import math
from typing import Tuple, List, Optional, Any
from pathlib import Path
import json

def load_image(path: str, convert_alpha: bool = True) -> Optional[pygame.Surface]:
    """Load an image with error handling"""
    try:
        image = pygame.image.load(path)
        if convert_alpha:
            image = image.convert_alpha()
        return image
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return None

def load_sound(path: str) -> Optional[pygame.mixer.Sound]:
    """Load a sound with error handling"""
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"Error loading sound {path}: {e}")
        return None

def load_font(path: str, size: int) -> Optional[pygame.font.Font]:
    """Load a font with error handling"""
    try:
        return pygame.font.Font(path, size)
    except Exception as e:
        print(f"Error loading font {path}: {e}")
        return None

def distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calculate distance between two points"""
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

def normalize_vector(vector: Tuple[float, float]) -> Tuple[float, float]:
    """Normalize a 2D vector"""
    length = math.sqrt(vector[0]**2 + vector[1]**2)
    if length == 0:
        return (0, 0)
    return (vector[0] / length, vector[1] / length)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(value, max_val))

def lerp(start: float, end: float, factor: float) -> float:
    """Linear interpolation between two values"""
    return start + (end - start) * factor

def point_in_rect(point: Tuple[int, int], rect: pygame.Rect) -> bool:
    """Check if a point is inside a rectangle"""
    return rect.collidepoint(point)

def rects_overlap(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    """Check if two rectangles overlap"""
    return rect1.colliderect(rect2)

def create_surface_with_alpha(size: Tuple[int, int], color: Tuple[int, int, int, int] = (0, 0, 0, 0)) -> pygame.Surface:
    """Create a surface with alpha channel"""
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    return surface

def draw_text_with_shadow(surface: pygame.Surface, text: str, font: pygame.font.Font, 
                         color: Tuple[int, int, int], pos: Tuple[int, int], 
                         shadow_color: Tuple[int, int, int] = (0, 0, 0), 
                         shadow_offset: int = 2) -> None:
    """Draw text with a shadow effect"""
    # Draw shadow
    shadow_surface = font.render(text, True, shadow_color)
    shadow_rect = shadow_surface.get_rect(center=(pos[0] + shadow_offset, pos[1] + shadow_offset))
    surface.blit(shadow_surface, shadow_rect)
    
    # Draw main text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=pos)
    surface.blit(text_surface, text_rect)

def create_gradient_surface(size: Tuple[int, int], start_color: Tuple[int, int, int], 
                           end_color: Tuple[int, int, int], vertical: bool = True) -> pygame.Surface:
    """Create a gradient surface"""
    surface = pygame.Surface(size)
    
    if vertical:
        for y in range(size[1]):
            factor = y / size[1]
            color = tuple(int(start_color[i] + (end_color[i] - start_color[i]) * factor) for i in range(3))
            pygame.draw.line(surface, color, (0, y), (size[0], y))
    else:
        for x in range(size[0]):
            factor = x / size[0]
            color = tuple(int(start_color[i] + (end_color[i] - start_color[i]) * factor) for i in range(3))
            pygame.draw.line(surface, color, (x, 0), (x, size[1]))
    
    return surface

def save_json(data: Any, filepath: str) -> bool:
    """Save data to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON to {filepath}: {e}")
        return False

def load_json(filepath: str) -> Optional[Any]:
    """Load data from JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON from {filepath}: {e}")
        return None

def ensure_directory(path: str) -> bool:
    """Ensure a directory exists, create if it doesn't"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {path}: {e}")
        return False

def get_file_extension(filepath: str) -> str:
    """Get file extension from path"""
    return Path(filepath).suffix.lower()

def is_valid_file(filepath: str, allowed_extensions: List[str] = None) -> bool:
    """Check if file exists and has valid extension"""
    path = Path(filepath)
    if not path.exists() or not path.is_file():
        return False
    
    if allowed_extensions:
        return path.suffix.lower() in allowed_extensions
    
    return True

def create_animation_frames(image: pygame.Surface, frame_width: int, frame_height: int) -> List[pygame.Surface]:
    """Create animation frames from a sprite sheet"""
    frames = []
    sheet_width, sheet_height = image.get_size()
    
    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(image, (0, 0), (x, y, frame_width, frame_height))
            frames.append(frame)
    
    return frames

def scale_surface(surface: pygame.Surface, scale: float) -> pygame.Surface:
    """Scale a surface by a factor"""
    new_size = (int(surface.get_width() * scale), int(surface.get_height() * scale))
    return pygame.transform.scale(surface, new_size)

def rotate_surface(surface: pygame.Surface, angle: float) -> pygame.Surface:
    """Rotate a surface by an angle in degrees"""
    return pygame.transform.rotate(surface, angle)

def flip_surface(surface: pygame.Surface, flip_x: bool = False, flip_y: bool = False) -> pygame.Surface:
    """Flip a surface horizontally and/or vertically"""
    return pygame.transform.flip(surface, flip_x, flip_y)

def get_center_position(surface: pygame.Surface) -> Tuple[int, int]:
    """Get the center position of a surface"""
    return (surface.get_width() // 2, surface.get_height() // 2)

def get_center_rect(surface: pygame.Surface, parent_rect: pygame.Rect) -> pygame.Rect:
    """Get a rect centered in a parent rect"""
    center_pos = parent_rect.center
    surface_rect = surface.get_rect(center=center_pos)
    return surface_rect

def create_button_surface(size: Tuple[int, int], text: str, font: pygame.font.Font,
                         normal_color: Tuple[int, int, int] = (100, 100, 100),
                         hover_color: Tuple[int, int, int] = (150, 150, 150),
                         text_color: Tuple[int, int, int] = (255, 255, 255)) -> Tuple[pygame.Surface, pygame.Surface]:
    """Create normal and hover button surfaces"""
    normal_surface = pygame.Surface(size)
    normal_surface.fill(normal_color)
    
    hover_surface = pygame.Surface(size)
    hover_surface.fill(hover_color)
    
    # Draw text on both surfaces
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=get_center_position(normal_surface))
    
    normal_surface.blit(text_surface, text_rect)
    hover_surface.blit(text_surface, text_rect)
    
    return normal_surface, hover_surface

def format_time(seconds: float) -> str:
    """Format time in seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_number(number: float, decimal_places: int = 1) -> str:
    """Format a number with specified decimal places"""
    return f"{number:.{decimal_places}f}"

def create_particle_effect(center: Tuple[int, int], color: Tuple[int, int, int], 
                          particle_count: int = 10, speed_range: Tuple[float, float] = (1.0, 3.0),
                          size_range: Tuple[int, int] = (2, 6), lifetime_range: Tuple[int, int] = (30, 60)) -> List[dict]:
    """Create a particle effect"""
    import random
    
    particles = []
    for _ in range(particle_count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(speed_range[0], speed_range[1])
        size = random.randint(size_range[0], size_range[1])
        lifetime = random.randint(lifetime_range[0], lifetime_range[1])
        
        velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
        
        particles.append({
            'pos': list(center),
            'velocity': velocity,
            'size': size,
            'color': color,
            'lifetime': lifetime,
            'max_lifetime': lifetime
        })
    
    return particles

def update_particles(particles: List[dict]) -> List[dict]:
    """Update particle positions and lifetimes"""
    updated_particles = []
    
    for particle in particles:
        # Update position
        particle['pos'][0] += particle['velocity'][0]
        particle['pos'][1] += particle['velocity'][1]
        
        # Update lifetime
        particle['lifetime'] -= 1
        
        # Keep particle if still alive
        if particle['lifetime'] > 0:
            updated_particles.append(particle)
    
    return updated_particles

def draw_particles(surface: pygame.Surface, particles: List[dict]) -> None:
    """Draw particles on a surface"""
    for particle in particles:
        alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
        color = (*particle['color'], alpha)
        
        particle_surface = create_surface_with_alpha((particle['size'], particle['size']), color)
        surface.blit(particle_surface, (particle['pos'][0] - particle['size']//2, 
                                      particle['pos'][1] - particle['size']//2))

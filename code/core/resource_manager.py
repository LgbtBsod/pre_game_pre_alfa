import pygame
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import json

class ResourceType:
    """Resource type constants"""
    IMAGE = "image"
    SOUND = "sound"
    MUSIC = "music"
    FONT = "font"
    DATA = "data"

class ResourceManager:
    """Centralized resource management system"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self._resources: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._resource_cache: Dict[str, Any] = {}
        self._cache_size_limit = 100  # Maximum cached resources
        
        # Supported file extensions
        self._supported_formats = {
            ResourceType.IMAGE: ['.png', '.jpg', '.jpeg', '.bmp', '.tga'],
            ResourceType.SOUND: ['.wav', '.ogg', '.mp3'],
            ResourceType.MUSIC: ['.ogg', '.mp3', '.wav'],
            ResourceType.FONT: ['.ttf', '.otf'],
            ResourceType.DATA: ['.json', '.csv', '.txt']
        }
    
    def _get_resource_type(self, file_path: str) -> str:
        """Determine resource type from file extension"""
        ext = Path(file_path).suffix.lower()
        
        for resource_type, extensions in self._supported_formats.items():
            if ext in extensions:
                return resource_type
        
        return ResourceType.DATA
    
    def _normalize_path(self, path: str) -> Path:
        """Normalize and validate file path"""
        normalized = Path(path)
        if not normalized.is_absolute():
            normalized = self.base_path / normalized
        return normalized
    
    def load_image(self, path: str, convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """Load an image resource"""
        try:
            full_path = self._normalize_path(path)
            if not full_path.exists():
                print(f"Warning: Image file not found: {full_path}")
                return None
            
            image = pygame.image.load(str(full_path))
            if convert_alpha:
                image = image.convert_alpha()
            
            # Cache the loaded image
            cache_key = f"image_{path}"
            self._cache_resource(cache_key, image)
            
            return image
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None
    
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound resource"""
        try:
            full_path = self._normalize_path(path)
            if not full_path.exists():
                print(f"Warning: Sound file not found: {full_path}")
                return None
            
            sound = pygame.mixer.Sound(str(full_path))
            
            # Cache the loaded sound
            cache_key = f"sound_{path}"
            self._cache_resource(cache_key, sound)
            
            return sound
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
            return None
    
    def load_font(self, path: str, size: int) -> Optional[pygame.font.Font]:
        """Load a font resource"""
        try:
            full_path = self._normalize_path(path)
            if not full_path.exists():
                print(f"Warning: Font file not found: {full_path}")
                return None
            
            font = pygame.font.Font(str(full_path), size)
            
            # Cache the loaded font
            cache_key = f"font_{path}_{size}"
            self._cache_resource(cache_key, font)
            
            return font
        except Exception as e:
            print(f"Error loading font {path}: {e}")
            return None
    
    def load_data_file(self, path: str) -> Optional[Any]:
        """Load a data file (JSON, CSV, etc.)"""
        try:
            full_path = self._normalize_path(path)
            if not full_path.exists():
                print(f"Warning: Data file not found: {full_path}")
                return None
            
            ext = full_path.suffix.lower()
            
            if ext == '.json':
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif ext == '.csv':
                import csv
                data = []
                with open(full_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        data.append(row)
                return data  # Return immediately for CSV files
            else:
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = f.read()
            
            # Cache the loaded data
            cache_key = f"data_{path}"
            self._cache_resource(cache_key, data)
            
            return data
        except Exception as e:
            print(f"Error loading data file {path}: {e}")
            return None
    
    def load_folder(self, folder_path: str, resource_type: str = None) -> List[Any]:
        """Load all resources from a folder"""
        try:
            full_path = self._normalize_path(folder_path)
            if not full_path.exists() or not full_path.is_dir():
                print(f"Warning: Folder not found: {full_path}")
                return []
            
            resources = []
            
            for file_path in full_path.iterdir():
                if file_path.is_file():
                    if resource_type is None:
                        resource_type = self._get_resource_type(str(file_path))
                    
                    relative_path = str(file_path.relative_to(self.base_path))
                    
                    if resource_type == ResourceType.IMAGE:
                        resource = self.load_image(relative_path)
                    elif resource_type == ResourceType.SOUND:
                        resource = self.load_sound(relative_path)
                    elif resource_type == ResourceType.MUSIC:
                        resource = self.load_sound(relative_path)
                    else:
                        continue
                    
                    if resource:
                        resources.append(resource)
            
            return resources
        except Exception as e:
            print(f"Error loading folder {folder_path}: {e}")
            return []
    
    def _cache_resource(self, key: str, resource: Any) -> None:
        """Cache a resource with size limit management"""
        if len(self._resource_cache) >= self._cache_size_limit:
            # Remove oldest cached resource
            oldest_key = next(iter(self._resource_cache))
            del self._resource_cache[oldest_key]
        
        self._resource_cache[key] = resource
    
    def get_cached_resource(self, key: str) -> Optional[Any]:
        """Get a cached resource"""
        return self._resource_cache.get(key)
    
    def clear_cache(self) -> None:
        """Clear the resource cache"""
        self._resource_cache.clear()
    
    def preload_resources(self, resource_list: List[Tuple[str, str]]) -> int:
        """Preload a list of resources"""
        loaded_count = 0
        
        for resource_type, path in resource_list:
            try:
                if resource_type == ResourceType.IMAGE:
                    if self.load_image(path):
                        loaded_count += 1
                elif resource_type == ResourceType.SOUND:
                    if self.load_sound(path):
                        loaded_count += 1
                elif resource_type == ResourceType.MUSIC:
                    if self.load_sound(path):
                        loaded_count += 1
                elif resource_type == ResourceType.FONT:
                    if self.load_font(path, 16):  # Default size
                        loaded_count += 1
                elif resource_type == ResourceType.DATA:
                    if self.load_data_file(path):
                        loaded_count += 1
            except Exception as e:
                print(f"Error preloading {resource_type} resource {path}: {e}")
        
        return loaded_count
    
    def get_resource_info(self) -> Dict[str, int]:
        """Get information about loaded resources"""
        info = {
            'cached_resources': len(self._resource_cache),
            'cache_size_limit': self._cache_size_limit
        }
        
        for resource_type in self._supported_formats:
            count = len([k for k in self._resource_cache.keys() if k.startswith(resource_type)])
            info[f'{resource_type}_count'] = count
        
        return info
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        self.clear_cache()
        pygame.mixer.stop()

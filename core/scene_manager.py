import pygame
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod
from .game_state import GameState
from .logger import GameLogger

class Scene(ABC):
    """Abstract base class for all game scenes"""
    
    def __init__(self, scene_manager: 'SceneManager'):
        self.scene_manager = scene_manager
        self.logger = GameLogger(self.__class__.__name__)
        self.is_active = False
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the scene"""
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update scene logic"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """Render the scene"""
        pass
    
    @abstractmethod
    def handle_events(self, events: list) -> None:
        """Handle scene-specific events"""
        pass
    
    def activate(self) -> None:
        """Activate the scene"""
        self.logger.info(f"Activating scene {self.__class__.__name__}")
        print(f"Activating scene {self.__class__.__name__}")  # Debug print
        
        if not self.is_initialized:
            self.logger.info(f"Initializing scene {self.__class__.__name__} for the first time")
            print(f"Initializing scene {self.__class__.__name__} for the first time")  # Debug print
            self.initialize()
            self.is_initialized = True
            self.logger.info(f"Scene {self.__class__.__name__} initialized")
            print(f"Scene {self.__class__.__name__} initialized")  # Debug print
        
        self.is_active = True
        self.logger.info(f"Scene {self.__class__.__name__} activated successfully")
        print(f"Scene {self.__class__.__name__} activated successfully")  # Debug print
    
    def deactivate(self) -> None:
        """Deactivate the scene"""
        self.is_active = False
        self.logger.info(f"Scene {self.__class__.__name__} deactivated")
        print(f"Scene {self.__class__.__name__} deactivated")  # Debug print
    
    def cleanup(self) -> None:
        """Cleanup scene resources"""
        pass

class SceneManager:
    """Manages different game scenes and transitions"""
    
    def __init__(self):
        self.logger = GameLogger("SceneManager")
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.next_scene: Optional[str] = None
        self.transitioning = False
    
    def register_scene(self, scene_name: str, scene: Scene) -> None:
        """Register a scene with the manager"""
        self.scenes[scene_name] = scene
        self.logger.info(f"Registered scene: {scene_name}")
    
    def switch_scene(self, scene_name: str) -> None:
        """Switch to a different scene"""
        self.logger.info(f"Attempting to switch to scene: {scene_name}")
        print(f"Attempting to switch to scene: {scene_name}")  # Debug print
        
        if scene_name not in self.scenes:
            self.logger.error(f"Scene not found: {scene_name}")
            self.logger.error(f"Available scenes: {list(self.scenes.keys())}")
            print(f"Scene not found: {scene_name}")  # Debug print
            print(f"Available scenes: {list(self.scenes.keys())}")  # Debug print
            return
        
        if self.current_scene:
            self.logger.info(f"Deactivating current scene: {self.current_scene.__class__.__name__}")
            print(f"Deactivating current scene: {self.current_scene.__class__.__name__}")  # Debug print
            self.current_scene.deactivate()
        
        self.current_scene = self.scenes[scene_name]
        self.logger.info(f"Setting current scene to: {scene_name}")
        print(f"Setting current scene to: {scene_name}")  # Debug print
        
        self.current_scene.activate()
        self.logger.info(f"Successfully switched to scene: {scene_name}")
        print(f"Successfully switched to scene: {scene_name}")  # Debug print
    
    def update(self, dt: float) -> None:
        """Update the current scene"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.update(dt)
        else:
            print("No active scene to update")  # Debug print
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the current scene"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.render(screen)
    
    def handle_events(self, events: list) -> None:
        """Handle events for the current scene"""
        if self.current_scene and self.current_scene.is_active:
            self.current_scene.handle_events(events)
    
    def get_current_scene(self) -> Optional[Scene]:
        """Get the current active scene"""
        return self.current_scene
    
    def cleanup(self) -> None:
        """Cleanup all scenes"""
        for scene in self.scenes.values():
            scene.cleanup()
        self.logger.info("Scene manager cleanup completed")

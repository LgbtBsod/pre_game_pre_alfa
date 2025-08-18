from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

@dataclass
class GameConfig:
    """Game configuration with validation"""
    
    # Display settings
    width: int = 1280
    height: int = 720
    fps: int = 60
    fullscreen: bool = False
    vsync: bool = True
    
    # Game settings
    tilesize: int = 64
    hitbox_offset: Dict[str, int] = field(default_factory=lambda: {
        'player': -26,
        'object': -40,
        'grass': -10,
        'invisible': 0
    })
    
    # UI settings
    bar_height: int = 20
    health_bar_width: int = 200
    energy_bar_width: int = 140
    item_box_size: int = 80
    ui_font: str = 'graphics/font/joystix.ttf'
    ui_font_size: int = 18
    
    # Colors
    water_color: str = '#71ddee'
    ui_bg_color: str = '#222222'
    ui_border_color: str = '#111111'
    text_color: str = '#EEEEEE'
    health_color: str = 'red'
    energy_color: str = 'blue'
    ui_border_color_active: str = 'gold'
    
    # Audio settings
    master_volume: float = 1.0
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    
    # Performance settings
    show_fps: bool = False
    max_particles: int = 100
    enable_vsync: bool = True
    
    def validate(self) -> bool:
        """Validate configuration values"""
        if self.width < 800 or self.height < 600:
            return False
        if self.fps < 30 or self.fps > 144:
            return False
        if not 0.0 <= self.master_volume <= 1.0:
            return False
        if not 0.0 <= self.music_volume <= 1.0:
            return False
        if not 0.0 <= self.sfx_volume <= 1.0:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'fullscreen': self.fullscreen,
            'vsync': self.vsync,
            'tilesize': self.tilesize,
            'hitbox_offset': self.hitbox_offset,
            'bar_height': self.bar_height,
            'health_bar_width': self.health_bar_width,
            'energy_bar_width': self.energy_bar_width,
            'item_box_size': self.item_box_size,
            'ui_font': self.ui_font,
            'ui_font_size': self.ui_font_size,
            'water_color': self.water_color,
            'ui_bg_color': self.ui_bg_color,
            'ui_border_color': self.ui_border_color,
            'text_color': self.text_color,
            'health_color': self.health_color,
            'energy_color': self.energy_color,
            'ui_border_color_active': self.ui_border_color_active,
            'master_volume': self.master_volume,
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            'show_fps': self.show_fps,
            'max_particles': self.max_particles,
            'enable_vsync': self.enable_vsync
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameConfig':
        """Create config from dictionary"""
        return cls(**data)

class ConfigManager:
    """Manages game configuration"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = GameConfig()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config = GameConfig.from_dict(data)
                    
                    if not self.config.validate():
                        print("Warning: Invalid config loaded, using defaults")
                        self.config = GameConfig()
            else:
                self.save_config()  # Create default config file
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = GameConfig()
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_setting(self, key: str) -> Any:
        """Get a configuration setting"""
        return getattr(self.config, key, None)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a configuration setting"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            if self.config.validate():
                self.save_config()
                return True
            else:
                # Revert invalid change
                self.load_config()
                return False
        return False
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = GameConfig()
        self.save_config()
    
    def get_display_mode(self) -> tuple[int, int]:
        """Get current display mode"""
        return self.config.width, self.config.height
    
    def get_fps(self) -> int:
        """Get target FPS"""
        return self.config.fps
    
    def get_audio_volumes(self) -> tuple[float, float, float]:
        """Get audio volume levels"""
        return (
            self.config.master_volume,
            self.config.music_volume,
            self.config.sfx_volume
        )

# Migration Guide - From Old to New Architecture

This guide helps developers understand the changes made during the refactoring and how to work with the new architecture.

## 🔄 What Changed

### Before (Old Architecture)
- **Monolithic design**: All game logic in a few large classes
- **Mixed responsibilities**: Classes handled multiple concerns
- **Hard-coded values**: Settings scattered throughout code
- **Limited error handling**: Basic try-catch blocks
- **No type hints**: Python 2 style code
- **Direct pygame calls**: Pygame used directly in game logic

### After (New Architecture)
- **Modular design**: Each system has a single responsibility
- **Clear separation**: Systems are independent and focused
- **Configuration-driven**: Centralized settings management
- **Comprehensive error handling**: Proper logging and recovery
- **Full type hints**: Modern Python 3.8+ features
- **Abstraction layers**: Pygame wrapped in resource managers

## 🏗️ New System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Game Manager                             │
│              (Main Coordinator)                             │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐
│ State │   │  Event  │   │  Input  │
│Manager│   │ Manager │   │ Manager │
└───────┘   └─────────┘   └─────────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐
│Config │   │ Logger  │   │Resource │
│Manager│   │         │   │Manager  │
└───────┘   └─────────┘   └─────────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐
│Audio  │   │Performance│   │ Game   │
│Manager│   │ Monitor  │   │ Data   │
└───────┘   └─────────┘   └─────────┘
```

## 📝 Code Migration Examples

### 1. Old Way - Direct Pygame Usage

```python
# OLD CODE
class Player:
    def __init__(self):
        self.image = pygame.image.load('player.png')
        self.sound = pygame.mixer.Sound('attack.wav')
    
    def attack(self):
        pygame.mixer.Sound.play(self.sound)
```

### 2. New Way - Resource Manager

```python
# NEW CODE
class Player:
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.image = resource_manager.load_image('player.png')
        self.sound = resource_manager.load_sound('attack.wav')
    
    def attack(self):
        if self.sound:
            self.sound.play()
```

### 3. Old Way - Hard-coded Settings

```python
# OLD CODE
WIDTH = 1280
HEIGHT = 720
FPS = 60

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.clock.tick(FPS)
```

### 4. New Way - Configuration Manager

```python
# NEW CODE
class Game:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        width, height = config_manager.get_display_mode()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.clock.tick(config_manager.get_fps())
```

### 5. Old Way - Basic Error Handling

```python
# OLD CODE
def load_image(path):
    try:
        return pygame.image.load(path)
    except:
        return None
```

### 6. New Way - Comprehensive Error Handling

```python
# NEW CODE
def load_image(self, path: str) -> Optional[pygame.Surface]:
    try:
        full_path = self._normalize_path(path)
        if not full_path.exists():
            self.logger.warning(f"Image file not found: {full_path}")
            return None
        
        image = pygame.image.load(str(full_path))
        if self.convert_alpha:
            image = image.convert_alpha()
        
        return image
    except Exception as e:
        self.logger.error(f"Error loading image {path}: {e}")
        return None
```

## 🚀 How to Use New Systems

### 1. Getting System Instances

```python
# Instead of creating instances directly
from core.game_manager import get_game_manager
from core.resource_manager import ResourceManager

game_manager = get_game_manager()
resource_manager = game_manager.resource_manager
```

### 2. Working with Configuration

```python
from core.config import ConfigManager

config = ConfigManager()
width = config.get_setting('width')
config.set_setting('fullscreen', True)
```

### 3. Using the Event System

```python
from core.event_manager import EventManager, EventType, GameEvent

event_manager = EventManager()

def handle_player_death(event):
    print("Player died!")

event_manager.register_handler(EventType.PLAYER_ACTION, handle_player_death)

# Emit an event
death_event = GameEvent(EventType.PLAYER_ACTION, {'action': 'death'})
event_manager.emit_event(death_event)
```

### 4. Input Management

```python
from core.input_manager import InputManager, InputAction

input_manager = InputManager()

def handle_attack():
    print("Attack!")

input_manager.register_action_handler(InputAction.ATTACK, handle_attack)

# In game loop
input_manager.update()
input_manager.handle_actions()

# Check input state
if input_manager.is_action_pressed(InputAction.MOVE_LEFT):
    player.move_left()
```

### 5. Performance Monitoring

```python
from core.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()

# In game loop
monitor.start_frame()
# ... game logic ...
monitor.end_frame()

# Get performance info
metrics = monitor.get_current_metrics()
print(f"FPS: {metrics.fps:.1f}")
```

## 🔧 Updating Existing Code

### Step 1: Identify Responsibilities
Look at your existing class and ask: "What is the single responsibility of this class?"

**Example**: If you have a `Player` class that handles:
- Player movement
- Player rendering
- Player audio
- Player input

**Split into**:
- `Player` - Core player logic
- `PlayerRenderer` - Rendering only
- `PlayerAudio` - Audio only
- `PlayerInput` - Input only

### Step 2: Update Imports
Replace old imports with new core system imports:

```python
# OLD
from settings import *
import pygame

# NEW
from core.config import ConfigManager
from core.resource_manager import ResourceManager
from core.audio_manager import AudioManager
```

### Step 3: Update Constructor
Inject dependencies instead of creating them:

```python
# OLD
class Player:
    def __init__(self):
        self.image = pygame.image.load('player.png')
        self.sound = pygame.mixer.Sound('attack.wav')

# NEW
class Player:
    def __init__(self, resource_manager: ResourceManager, audio_manager: AudioManager):
        self.resource_manager = resource_manager
        self.audio_manager = audio_manager
        self.image = resource_manager.load_image('player.png')
        self.sound = resource_manager.load_sound('attack.wav')
```

### Step 4: Add Type Hints
Add type annotations to all methods:

```python
# OLD
def move(self, direction):
    self.x += direction[0]
    self.y += direction[1]

# NEW
def move(self, direction: tuple[float, float]) -> None:
    self.x += direction[0]
    self.y += direction[1]
```

### Step 5: Add Error Handling
Wrap operations in try-catch blocks with proper logging:

```python
# OLD
def attack(self):
    self.sound.play()

# NEW
def attack(self) -> bool:
    try:
        if self.sound:
            self.sound.play()
            return True
        return False
    except Exception as e:
        self.logger.error(f"Error playing attack sound: {e}")
        return False
```

## 🧪 Testing New Systems

### 1. Unit Testing
Each system can be tested independently:

```python
import unittest
from unittest.mock import Mock
from core.resource_manager import ResourceManager

class TestResourceManager(unittest.TestCase):
    def setUp(self):
        self.resource_manager = ResourceManager()
    
    def test_load_image_success(self):
        # Test successful image loading
        pass
    
    def test_load_image_not_found(self):
        # Test handling of missing files
        pass
```

### 2. Integration Testing
Test how systems work together:

```python
def test_game_manager_integration():
    game_manager = get_game_manager()
    
    # Test that all systems are properly initialized
    assert game_manager.resource_manager is not None
    assert game_manager.audio_manager is not None
    assert game_manager.config_manager is not None
```

## 🐛 Common Issues and Solutions

### Issue 1: Circular Imports
**Problem**: Systems trying to import each other
**Solution**: Use dependency injection and lazy imports

```python
# In game_manager.py
def initialize_game_components(self):
    # Import here to avoid circular imports
    from ..level import Level
    from ..menu import Menu
```

### Issue 2: Missing Dependencies
**Problem**: Required packages not installed
**Solution**: Install from requirements.txt

```bash
pip install -r requirements.txt
```

### Issue 3: Type Hint Errors
**Problem**: Type checker complaining about missing types
**Solution**: Add proper type hints or use type ignores

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .some_module import SomeClass

def method(self, obj: 'SomeClass') -> None:
    pass
```

### Issue 4: Performance Issues
**Problem**: Game running slowly
**Solution**: Use performance monitor to identify bottlenecks

```python
# Enable FPS display in config
config.set_setting('show_fps', True)

# Check performance metrics
metrics = performance_monitor.get_current_metrics()
if metrics.fps < 30:
    print("Performance issue detected!")
```

## 📚 Best Practices

### 1. Single Responsibility
- Each class should have one reason to change
- If a class does multiple things, split it

### 2. Dependency Injection
- Don't create dependencies inside classes
- Pass them in through constructors

### 3. Error Handling
- Always handle exceptions gracefully
- Log errors with context
- Provide fallback behavior

### 4. Type Hints
- Use type hints for all public methods
- Use Optional for nullable values
- Use Union for multiple types

### 5. Documentation
- Document all public interfaces
- Use clear, descriptive names
- Add examples for complex methods

## 🔮 Future Enhancements

The new architecture makes it easy to add:

- **Save System**: Centralized save/load management
- **Mod System**: Plugin architecture for mods
- **Multiplayer**: Network layer abstraction
- **AI System**: Enemy behavior management
- **Physics Engine**: Collision and movement systems
- **UI Framework**: Advanced user interface components

## 📞 Getting Help

If you encounter issues during migration:

1. **Check the logs**: Look at the log files for error details
2. **Review examples**: Look at how other systems are implemented
3. **Use type hints**: Let your IDE help identify issues
4. **Ask questions**: Create an issue with detailed information

Remember: The new architecture is designed to make development easier, not harder. Take your time to understand the principles, and the benefits will become clear!

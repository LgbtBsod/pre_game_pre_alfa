# Usage Examples - Zelda Game Enhanced Edition

This document provides practical examples of how to use the new architecture systems.

## 🚀 Getting Started

### Basic Game Setup

```python
from core.game_manager import get_game_manager, cleanup_game_manager

def main():
    try:
        # Get the game manager instance
        game_manager = get_game_manager()
        
        # Run the game
        game_manager.run()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup resources
        cleanup_game_manager()

if __name__ == '__main__':
    main()
```

### Custom Game Configuration

```python
from core.config import ConfigManager

# Create custom configuration
config = ConfigManager("custom_config.json")

# Set custom settings
config.set_setting('width', 1920)
config.set_setting('height', 1080)
config.set_setting('fullscreen', True)
config.set_setting('fps', 120)
config.set_setting('show_fps', True)

# Save configuration
config.save_config()
```

## 🎮 Working with Game Systems

### 1. Resource Management

#### Loading Individual Resources

```python
from core.resource_manager import ResourceManager

# Initialize resource manager
resource_manager = ResourceManager()

# Load different types of resources
player_image = resource_manager.load_image('graphics/player/down/down_0.png')
attack_sound = resource_manager.load_sound('audio/attack/slash.wav')
game_font = resource_manager.load_font('graphics/font/joystix.ttf', 24)
level_data = resource_manager.load_data_file('map/level_1.csv')

# Check if resources loaded successfully
if player_image and attack_sound and game_font:
    print("All resources loaded successfully!")
else:
    print("Some resources failed to load")
```

#### Batch Resource Loading

```python
# Preload multiple resources
resources_to_load = [
    ('image', 'graphics/player/down/down_0.png'),
    ('image', 'graphics/player/down/down_1.png'),
    ('image', 'graphics/player/down/down_2.png'),
    ('sound', 'audio/attack/slash.wav'),
    ('sound', 'audio/attack/claw.wav'),
    ('font', 'graphics/font/joystix.ttf')
]

loaded_count = resource_manager.preload_resources(resources_to_load)
print(f"Loaded {loaded_count} resources out of {len(resources_to_load)}")
```

#### Resource Caching

```python
# Get information about cached resources
cache_info = resource_manager.get_resource_info()
print(f"Cached resources: {cache_info['cached_resources']}")
print(f"Image count: {cache_info['image_count']}")
print(f"Sound count: {cache_info['sound_count']}")

# Clear cache if needed
resource_manager.clear_cache()
```

### 2. Audio Management

#### Basic Audio Operations

```python
from core.audio_manager import AudioManager, AudioType

# Initialize audio manager with resource manager
audio_manager = AudioManager(resource_manager)

# Load audio files
audio_manager.load_sound('attack', 'audio/attack/slash.wav')
audio_manager.load_music('main_theme', 'audio/main.ogg')

# Play audio
audio_manager.play_sound('attack')
audio_manager.play_music('main_theme', loops=-1)  # Loop indefinitely

# Control playback
audio_manager.pause_music()
audio_manager.unpause_music()
audio_manager.stop_music()
```

#### Volume Control

```python
# Set individual volume levels
audio_manager.set_master_volume(0.8)      # 80% master volume
audio_manager.set_music_volume(0.6)       # 60% music volume
audio_manager.set_sound_volume(0.9)       # 90% sound effects volume

# Get current volume settings
volumes = audio_manager.get_volume_info()
print(f"Master: {volumes['master']:.1%}")
print(f"Music: {volumes['music']:.1%}")
print(f"Sound: {volumes['sound']:.1%}")

# Mute/unmute
audio_manager.mute()
audio_manager.unmute()
```

#### Audio Folder Loading

```python
# Load all audio files from a folder
sounds_loaded = audio_manager.load_audio_folder('audio/attack', AudioType.SOUND)
music_loaded = audio_manager.load_audio_folder('audio/music', AudioType.MUSIC)

print(f"Loaded {sounds_loaded} sound effects")
print(f"Loaded {music_loaded} music tracks")
```

### 3. Event System

#### Basic Event Handling

```python
from core.event_manager import EventManager, EventType, GameEvent

# Initialize event manager
event_manager = EventManager()

# Define event handlers
def handle_player_death(event):
    print(f"Player died! Reason: {event.data.get('reason', 'unknown')}")

def handle_level_complete(event):
    print(f"Level {event.data.get('level', 'unknown')} completed!")

# Register event handlers
event_manager.register_handler(EventType.PLAYER_ACTION, handle_player_death)
event_manager.register_handler(EventType.GAME_STATE_CHANGE, handle_level_complete)

# Emit events
death_event = GameEvent(EventType.PLAYER_ACTION, {'reason': 'enemy_attack'})
level_event = GameEvent(EventType.GAME_STATE_CHANGE, {'level': 1})

event_manager.emit_event(death_event)
event_manager.emit_event(level_event)
```

#### Pygame Event Integration

```python
# Process pygame events and convert to game events
game_events = event_manager.process_pygame_events()

for event in game_events:
    if event.event_type == EventType.QUIT:
        print("Quit event received")
    elif event.event_type == EventType.KEY_PRESS:
        key = event.data.get('key')
        print(f"Key pressed: {key}")
```

### 4. Input Management

#### Basic Input Handling

```python
from core.input_manager import InputManager, InputAction

# Initialize input manager
input_manager = InputManager()

# Register action handlers
def handle_attack():
    print("Attack action triggered!")

def handle_magic():
    print("Magic action triggered!")

input_manager.register_action_handler(InputAction.ATTACK, handle_attack)
input_manager.register_action_handler(InputAction.USE_MAGIC, handle_magic)

# In game loop
input_manager.update()
input_manager.handle_actions()
```

#### Input State Checking

```python
# Check current input state
if input_manager.is_action_pressed(InputAction.MOVE_LEFT):
    player.move_left()

if input_manager.is_action_just_pressed(InputAction.ATTACK):
    player.start_attack()

if input_manager.is_action_just_released(InputAction.USE_MAGIC):
    player.stop_magic()
```

#### Movement Vector

```python
# Get normalized movement vector
movement = input_manager.get_movement_vector()
player.move(movement)

# Custom key bindings
input_manager.set_key_binding(InputAction.ATTACK, pygame.K_SPACE)
input_manager.set_key_binding(InputAction.USE_MAGIC, pygame.K_LCTRL)
```

### 5. State Management

#### Basic State Operations

```python
from core.game_state import GameStateManager, GameState

# Initialize state manager
state_manager = GameStateManager()

# Check current state
if state_manager.is_state(GameState.PLAYING):
    print("Game is currently playing")

# Change state
if state_manager.can_transition_to(GameState.PAUSED):
    state_manager.change_state(GameState.PAUSED)
    print("Game paused")

# Get state information
current_state = state_manager.current_state
previous_state = state_manager.previous_state
print(f"Current: {current_state.value}, Previous: {previous_state.value if previous_state else 'None'}")
```

#### State Validation

```python
# Check if state transition is valid
if state_manager.can_transition_to(GameState.MENU):
    state_manager.change_state(GameState.MENU)
else:
    print("Cannot transition to menu from current state")

# Reset to initial state
state_manager.reset()
```

### 6. Performance Monitoring

#### Basic Performance Tracking

```python
from core.performance_monitor import PerformanceMonitor

# Initialize performance monitor
monitor = PerformanceMonitor()

# In game loop
monitor.start_frame()

# ... game logic ...

monitor.end_frame()

# Get performance metrics
metrics = monitor.get_current_metrics()
print(f"FPS: {metrics.fps:.1f}")
print(f"Frame Time: {metrics.frame_time:.2f}ms")
print(f"Memory: {metrics.memory_usage:.1f}MB")
```

#### Performance Alerts

```python
# Get performance alerts
alerts = monitor.get_performance_alerts()
for alert in alerts:
    print(f"Performance Alert: {alert}")

# Get recommendations
recommendations = monitor.get_recommendations()
for rec in recommendations:
    print(f"Recommendation: {rec}")

# Check if performance is good
if monitor.is_performance_good():
    print("Performance is acceptable")
else:
    print("Performance issues detected")
```

#### Performance History

```python
# Get average performance over time
avg_metrics = monitor.get_average_metrics(window=60)  # Last 60 frames
print(f"Average FPS: {avg_metrics.fps:.1f}")
print(f"Average Frame Time: {avg_metrics.avg_frame_time:.2f}ms")

# Export performance data
monitor.export_data("performance_report.json")
```

### 7. Game Data Management

#### Working with Game Content

```python
from core.game_data import GameDataManager

# Initialize game data manager
game_data = GameDataManager()

# Get weapon information
sword_data = game_data.get_weapon('sword')
if sword_data:
    print(f"Sword damage: {sword_data.damage}")
    print(f"Sword cooldown: {sword_data.cooldown}ms")

# Get all weapons
all_weapons = game_data.get_all_weapons()
for weapon in all_weapons:
    print(f"{weapon.name}: {weapon.damage} damage")

# Get enemy information
enemy_data = game_data.get_enemy('squid')
if enemy_data:
    print(f"Squid health: {enemy_data.health}")
    print(f"Squid weaknesses: {enemy_data.weaknesses}")
```

#### Custom Game Data

```python
from core.game_data import WeaponData, WeaponType

# Create custom weapon
custom_weapon = WeaponData(
    name="Thunder Sword",
    cooldown=150,
    damage=25,
    graphic='graphics/weapons/thunder_sword.png',
    weapon_type=WeaponType.SWORD,
    description="A sword imbued with lightning",
    special_effects=["lightning", "chain_lightning"]
)

# Add to game data
game_data.add_weapon(custom_weapon)

# Export all data
game_data.export_data("custom_game_data.json")
```

## 🔧 Advanced Usage Patterns

### 1. Custom Game Manager

```python
from core.game_manager import GameManager

class CustomGameManager(GameManager):
    def __init__(self):
        super().__init__()
        self.custom_system = None
    
    def initialize_custom_system(self):
        # Initialize custom game systems
        self.custom_system = CustomSystem()
    
    def run(self):
        # Custom initialization
        self.initialize_custom_system()
        
        # Run parent implementation
        super().run()
    
    def _custom_update(self):
        # Custom update logic
        if self.custom_system:
            self.custom_system.update()

# Usage
custom_manager = CustomGameManager()
custom_manager.run()
```

### 2. System Integration

```python
class GameSystem:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.resource_manager = game_manager.resource_manager
        self.audio_manager = game_manager.audio_manager
        self.event_manager = game_manager.event_manager
        
        # Register for events
        self.event_manager.register_handler(EventType.PLAYER_ACTION, self.handle_player_action)
    
    def handle_player_action(self, event):
        action = event.data.get('action')
        if action == 'attack':
            self.audio_manager.play_sound('attack')
    
    def update(self):
        # System update logic
        pass
    
    def cleanup(self):
        # System cleanup
        pass
```

### 3. Configuration-Driven Systems

```python
class ConfigurableSystem:
    def __init__(self, config_manager):
        self.config = config_manager
        self.enabled = self.config.get_setting('system_enabled', True)
        self.max_objects = self.config.get_setting('max_objects', 100)
    
    def update(self):
        if not self.enabled:
            return
        
        # System logic based on configuration
        pass
    
    def reload_config(self):
        # Reload configuration
        self.enabled = self.config.get_setting('system_enabled', True)
        self.max_objects = self.config.get_setting('max_objects', 100)
```

### 4. Error Recovery

```python
class RobustSystem:
    def __init__(self, logger):
        self.logger = logger
        self.error_count = 0
        self.max_errors = 3
    
    def safe_operation(self, operation_func, *args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Operation failed: {e}")
            
            if self.error_count >= self.max_errors:
                self.logger.critical("Too many errors, disabling system")
                return None
            
            # Try fallback operation
            return self.fallback_operation(*args, **kwargs)
    
    def fallback_operation(self, *args, **kwargs):
        # Fallback implementation
        pass
```

## 🧪 Testing Examples

### 1. Unit Testing

```python
import unittest
from unittest.mock import Mock, patch
from core.resource_manager import ResourceManager

class TestResourceManager(unittest.TestCase):
    def setUp(self):
        self.resource_manager = ResourceManager()
    
    def test_load_image_success(self):
        with patch('pygame.image.load') as mock_load:
            mock_surface = Mock()
            mock_load.return_value = mock_surface
            
            result = self.resource_manager.load_image('test.png')
            
            self.assertIsNotNone(result)
            mock_load.assert_called_once_with('test.png')
    
    def test_load_image_not_found(self):
        with patch('pygame.image.load') as mock_load:
            mock_load.side_effect = FileNotFoundError("File not found")
            
            result = self.resource_manager.load_image('missing.png')
            
            self.assertIsNone(result)
```

### 2. Integration Testing

```python
def test_system_integration():
    # Test that systems work together
    game_manager = get_game_manager()
    
    # Verify all systems are initialized
    assert game_manager.resource_manager is not None
    assert game_manager.audio_manager is not None
    assert game_manager.config_manager is not None
    
    # Test system interaction
    game_manager.change_state(GameState.PLAYING)
    assert game_manager.state_manager.is_state(GameState.PLAYING)
    
    # Test resource loading through audio manager
    sound_loaded = game_manager.audio_manager.load_sound('test', 'test.wav')
    assert sound_loaded is False  # File doesn't exist
    
    # Cleanup
    cleanup_game_manager()
```

## 📊 Performance Optimization

### 1. Resource Preloading

```python
def optimize_resource_loading():
    resource_manager = ResourceManager()
    
    # Preload critical resources
    critical_resources = [
        ('image', 'graphics/player/down/down_0.png'),
        ('image', 'graphics/player/down/down_1.png'),
        ('sound', 'audio/attack/slash.wav'),
        ('font', 'graphics/font/joystix.ttf')
    ]
    
    loaded_count = resource_manager.preload_resources(critical_resources)
    print(f"Preloaded {loaded_count} critical resources")
    
    return resource_manager
```

### 2. Performance Monitoring

```python
def monitor_game_performance():
    monitor = PerformanceMonitor()
    
    # Set custom thresholds
    monitor.fps_warning_threshold = 45  # More strict FPS requirement
    monitor.memory_warning_threshold = 300  # Lower memory threshold
    
    # Monitor performance
    while True:
        monitor.start_frame()
        
        # ... game logic ...
        
        monitor.end_frame()
        
        # Check for issues
        if not monitor.is_performance_good():
            alerts = monitor.get_performance_alerts()
            recommendations = monitor.get_recommendations()
            
            print("Performance issues detected:")
            for alert in alerts:
                print(f"  - {alert}")
            
            print("Recommendations:")
            for rec in recommendations:
                print(f"  - {rec}")
        
        # Export data periodically
        if monitor.frame_count % 3600 == 0:  # Every 60 seconds at 60 FPS
            monitor.export_data(f"performance_{monitor.frame_count}.json")
```

## 🔮 Future-Proofing

### 1. Plugin Architecture

```python
class PluginSystem:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, name, plugin_class):
        self.plugins[name] = plugin_class
    
    def get_plugin(self, name):
        return self.plugins.get(name)
    
    def execute_plugin(self, name, *args, **kwargs):
        plugin = self.get_plugin(name)
        if plugin:
            return plugin.execute(*args, **kwargs)
        return None

# Usage
plugin_system = PluginSystem()
plugin_system.register_plugin('custom_weapon', CustomWeaponPlugin)
result = plugin_system.execute_plugin('custom_weapon', damage=50)
```

### 2. Event-Driven Architecture

```python
class EventDrivenSystem:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.subscribers = {}
    
    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def publish(self, event_type, data):
        event = GameEvent(event_type, data)
        self.event_manager.emit_event(event)
        
        # Also notify local subscribers
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in callback: {e}")

# Usage
event_system = EventDrivenSystem(event_manager)

def handle_player_level_up(data):
    print(f"Player reached level {data.get('level')}")

event_system.subscribe(EventType.PLAYER_ACTION, handle_player_level_up)
event_system.publish(EventType.PLAYER_ACTION, {'action': 'level_up', 'level': 5})
```

---

These examples demonstrate the flexibility and power of the new architecture. The modular design makes it easy to create custom systems while maintaining consistency and reliability.

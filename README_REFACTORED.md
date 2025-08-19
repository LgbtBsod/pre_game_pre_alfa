# 🎮 Эволюционная Адаптация: Генетический Резонанс
## 🏗️ Обновленная архитектура с принципом единой ответственности

### 📋 Обзор

Этот проект представляет собой игру "Эволюционная Адаптация: Генетический Резонанс" с полностью рефакторенной архитектурой, основанной на принципах SOLID и компонентной архитектуре (ECS).

### 🎯 Основные принципы архитектуры

- **Принцип единой ответственности (SRP)** - каждый класс имеет одну четкую ответственность
- **Компонентная архитектура (ECS)** - гибкая система компонентов для сущностей
- **Слабая связанность** - компоненты не зависят друг от друга напрямую
- **Высокая когезия** - логически связанный код сгруппирован вместе

## 🚀 Быстрый старт

### Установка зависимостей

```bash
pip install pygame numpy
```

### Запуск игры

```bash
# Запуск обновленной игры
python run_refactored_game.py

# Тестирование архитектуры
python run_refactored_game.py test

# Информация об архитектуре
python run_refactored_game.py info
```

## 🏗️ Архитектура системы

### Компонентная система (ECS)

```
core/components/
├── base_component.py          # Базовый класс для всех компонентов
├── transform_component.py     # Позиция, поворот, масштаб
├── animation_component.py     # Управление анимацией
└── sprite_component.py        # Отрисовка спрайтов
```

### Игровые системы

```
core/
├── entity_system.py           # Управление сущностями
├── resource_loader.py         # Загрузка ресурсов
├── error_handler.py           # Обработка ошибок
├── game_systems.py            # Игровые системы
└── refactored_game_loop.py    # Обновленный игровой цикл
```

### Конфигурация

```
config/
├── config_manager.py          # Менеджер конфигурации
└── config_factory.py          # Фабрика конфигурации
```

## 🔧 Компоненты системы

### 1. AnimationComponent
Управляет состоянием анимации сущности.

```python
from core.components.animation_component import AnimationComponent, Direction, AnimationState

# Создание компонента
animation = AnimationComponent(entity_id, "graphics/player")

# Установка направления и состояния
animation.set_direction(Direction.DOWN)
animation.set_state(AnimationState.WALKING)

# Обновление
animation.update(delta_time)
```

### 2. SpriteComponent
Отвечает за отрисовку спрайтов.

```python
from core.components.sprite_component import SpriteComponent

# Создание компонента
sprite = SpriteComponent(entity_id)

# Связывание с другими компонентами
sprite.set_transform_component(transform_component)
sprite.set_animation_component(animation_component)

# Отрисовка
sprite.render(screen, camera_offset)
```

### 3. TransformComponent
Управляет позицией и трансформацией.

```python
from core.components.transform_component import TransformComponent, Vector3

# Создание компонента
transform = TransformComponent(entity_id, Vector3(100, 100, 0))

# Управление позицией
transform.set_position(200, 150, 0)
transform.move(10, 5, 0)

# Получение информации
position = transform.get_position_2d()
distance = transform.distance_to(other_transform)
```

### 4. EntityManager
Управляет жизненным циклом сущностей.

```python
from core.entity_system import EntityManager, EntityFactory

# Создание менеджера
entity_manager = EntityManager()
entity_factory = EntityFactory(entity_manager, resource_loader)

# Создание сущности
player = entity_factory.create_player_entity("Игрок", Vector3(0, 0, 0))

# Обновление всех сущностей
entity_manager.update_entities(delta_time)

# Получение статистики
stats = entity_manager.get_statistics()
```

### 5. ResourceLoader
Загружает и кэширует ресурсы.

```python
from core.resource_loader import ResourceLoader

# Создание загрузчика
loader = ResourceLoader()

# Загрузка анимаций
animations = loader.load_sprite_animations("graphics/player")

# Загрузка звуков
sound = loader.load_sound("audio/attack.wav")

# Получение статистики
stats = loader.get_statistics()
```

### 6. ErrorHandler
Централизованная обработка ошибок.

```python
from core.error_handler import error_handler, ErrorType, ErrorSeverity

# Обработка ошибки
error_handler.handle_error(
    ErrorType.RESOURCE_LOADING,
    "Не удалось загрузить спрайт",
    severity=ErrorSeverity.WARNING
)

# Получение статистики
stats = error_handler.get_error_statistics()
```

## ⚙️ Конфигурация

### Типы конфигураций

- `GAME_SETTINGS` - настройки игры (разрешение, FPS, звук)
- `ENTITIES` - конфигурация сущностей
- `ITEMS` - конфигурация предметов
- `AI` - настройки искусственного интеллекта
- `UI` - настройки интерфейса
- `AUDIO` - настройки звука
- `GRAPHICS` - настройки графики
- `NETWORK` - сетевые настройки

### Использование

```python
from config.config_factory import config_factory, ConfigType

# Загрузка конфигурации
game_config = config_factory.create_config(ConfigType.GAME_SETTINGS)

# Получение значений
window_width = game_config.get('display', {}).get('window_width', 1280)
fps = game_config.get('display', {}).get('render_fps', 60)

# Сохранение изменений
game_config['display']['window_width'] = 1920
config_factory.save_config(ConfigType.GAME_SETTINGS, game_config)
```

## 🎮 Управление

- **ESC** - выход из игры
- **P** - пауза/возобновление
- **F1** - отладочная информация
- **F2** - сохранение скриншота

## 📊 Мониторинг и отладка

### Статистика системы

```python
# Получение статистики всех систем
stats = game_systems.get_statistics()

print(f"Время игры: {stats['game_time']:.2f} сек")
print(f"FPS: {stats['fps']}")
print(f"Сущности: {stats['entities']['total_entities']}")
print(f"Ошибки: {stats['errors']['total_errors']}")
```

### Логирование

Все системы используют централизованное логирование:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Тест компонентной архитектуры
python run_refactored_game.py test

# Тест системы конфигурации
python run_refactored_game.py config

# Тест обработки ошибок
python run_refactored_game.py errors
```

### Создание собственных тестов

```python
def test_custom_component():
    # Создание компонента
    component = CustomComponent(entity_id)
    
    # Инициализация
    assert component.initialize()
    
    # Тестирование функциональности
    component.update(0.016)  # 60 FPS
    
    # Очистка
    component.cleanup()
```

## 🔄 Расширение системы

### Создание нового компонента

```python
from core.components.base_component import BaseComponent

class HealthComponent(BaseComponent):
    def __init__(self, entity_id: str, max_health: float = 100.0):
        super().__init__(entity_id)
        self.max_health = max_health
        self.current_health = max_health
    
    def _initialize(self) -> bool:
        return True
    
    def take_damage(self, damage: float) -> bool:
        self.current_health = max(0, self.current_health - damage)
        return self.current_health > 0
    
    def heal(self, amount: float) -> None:
        self.current_health = min(self.max_health, self.current_health + amount)
```

### Создание новой системы

```python
class CombatSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
    
    def process_combat(self, attacker_id: str, target_id: str, damage: float) -> bool:
        attacker = self.entity_manager.get_entity(attacker_id)
        target = self.entity_manager.get_entity(target_id)
        
        if attacker and target:
            target_health = self.entity_manager.get_component(target_id, HealthComponent)
            if target_health:
                return target_health.take_damage(damage)
        
        return False
```

## 📁 Структура проекта

```
AI-EVOLVE/
├── core/
│   ├── components/           # Компоненты ECS
│   ├── entity_system.py     # Система сущностей
│   ├── resource_loader.py   # Загрузчик ресурсов
│   ├── error_handler.py     # Обработка ошибок
│   ├── game_systems.py      # Игровые системы
│   └── refactored_game_loop.py # Обновленный игровой цикл
├── config/
│   ├── config_manager.py    # Менеджер конфигурации
│   └── config_factory.py    # Фабрика конфигурации
├── graphics/                # Графические ресурсы
├── audio/                   # Звуковые ресурсы
├── data/                    # Игровые данные
├── logs/                    # Логи
├── screenshots/             # Скриншоты
├── run_refactored_game.py   # Запуск обновленной игры
└── README_REFACTORED.md     # Этот файл
```

## 🛠️ Требования

- Python 3.8+
- Pygame 2.0+
- NumPy (опционально, для улучшения производительности)

## 📝 Лицензия

Этот проект является частью образовательного процесса и демонстрирует применение принципов SOLID и компонентной архитектуры в игровой разработке.

## 🤝 Вклад в проект

При внесении изменений в проект:

1. Следуйте принципу единой ответственности
2. Добавляйте компоненты в папку `core/components/`
3. Обновляйте документацию
4. Добавляйте тесты для новых функций
5. Используйте централизованную обработку ошибок

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи в папке `logs/`
2. Запустите тесты: `python run_refactored_game.py test`
3. Проверьте конфигурацию: `python run_refactored_game.py config`
4. Обратитесь к отладочной информации (F1 в игре)

---

**🎮 Наслаждайтесь игрой с новой архитектурой!**

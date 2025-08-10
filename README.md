# AI-EVOLVE

Игровой проект с архитектурой, основанной на принципе единой ответственности.

## Архитектура проекта

### Принципы проектирования

1. **Единая ответственность (Single Responsibility Principle)** - каждый модуль отвечает за одну конкретную задачу
2. **Разделение данных и логики** - данные хранятся в JSON и БД, логика в коде
3. **Централизованное управление** - все системы управляются через единые менеджеры
4. **Модульность** - каждый компонент может быть легко заменен или расширен

### Структура проекта

```
AI-EVOLVE/
├── config/                 # Настройки игры
│   ├── settings_manager.py # Централизованный менеджер настроек
│   └── game_constants.py   # Константы игры
├── core/                   # Основные системы
│   ├── data_manager.py     # Менеджер данных (предметы, враги, эффекты)
│   ├── game_state_manager.py # Менеджер состояния игры
│   ├── game_logic_manager.py # Менеджер игровой логики
│   └── resource_manager.py # Менеджер ресурсов
├── entities/               # Сущности игры
│   ├── entity_factory.py   # Фабрика сущностей
│   ├── entity.py          # Базовая сущность
│   ├── player.py          # Игрок
│   ├── enemy.py           # Враг
│   ├── boss.py            # Босс
│   └── npc.py             # NPC
├── items/                  # Система предметов
│   └── item_manager.py    # Менеджер предметов
├── ai/                     # Искусственный интеллект
│   ├── behavior_tree.py   # Дерево поведения
│   ├── decision_maker.py  # Принятие решений
│   ├── memory.py          # Память ИИ
│   └── learning.py        # Обучение ИИ
├── combat/                 # Боевая система
│   ├── damage_system.py   # Система урона
│   └── elemental_combat.py # Элементальный бой
├── ui/                     # Пользовательский интерфейс
│   ├── game_menu.py       # Игровое меню
│   ├── render_manager.py  # Менеджер рендеринга
│   └── buttons.py         # Кнопки UI
├── data/                   # Данные игры
│   ├── items.json         # Предметы
│   ├── entities.json      # Сущности
│   ├── effects.json       # Эффекты
│   ├── abilities.json     # Способности
│   └── game_data.db       # База данных
└── main.py                # Главный файл игры
```

## Основные системы

### 1. Менеджер настроек (`config/settings_manager.py`)

Централизованное управление всеми настройками игры:
- Графика (разрешение, качество, FPS)
- Звук (громкость, эффекты)
- Геймплей (сложность, интерфейс)
- Бой (параметры атак, защиты)
- Движение (скорость, физика)
- ИИ (обучение, поведение)

```python
from config.settings_manager import settings_manager

# Получение настройки
window_width = settings_manager.get_setting("window_width", 1200)

# Установка настройки
settings_manager.set_setting("master_volume", 0.8)

# Сохранение настроек
settings_manager.save_settings()
```

### 2. Менеджер данных (`core/data_manager.py`)

Управление всеми игровыми данными:
- Предметы (оружие, броня, расходники)
- Враги (типы, характеристики, поведение)
- Эффекты (баффы, дебаффы)
- Способности (умения, заклинания)

Данные хранятся в JSON файлах и синхронизируются с SQLite базой данных.

```python
from core.data_manager import data_manager

# Получение предмета
item = data_manager.get_item("wpn_001")

# Получение врагов по типу
enemies = data_manager.get_enemies_by_type("warrior")

# Получение эффектов
effects = data_manager.get_effects_by_type("buff")
```

### 3. Менеджер состояния игры (`core/game_state_manager.py`)

Управление сохранением и загрузкой игры:
- Сохранение состояния игрока
- Сохранение состояния мира
- Автосохранение
- Экспорт/импорт сохранений

```python
from core.game_state_manager import game_state_manager

# Создание новой игры
game_id = game_state_manager.create_new_game("Моя игра", "Игрок", "normal")

# Загрузка игры
success = game_state_manager.load_game(game_id)

# Сохранение игры
game_state_manager.save_game()
```

### 4. Фабрика сущностей (`entities/entity_factory.py`)

Создание различных типов сущностей:
- Игроки
- Враги
- Боссы
- NPC

```python
from entities.entity_factory import entity_factory

# Создание игрока
player = entity_factory.create_player("player", (0, 0))

# Создание врага
enemy = entity_factory.create_enemy("warrior", level=5, position=(100, 100))

# Создание группы врагов
enemies = entity_factory.create_enemy_pack(pack_size=3, level=3)
```

### 5. Менеджер предметов (`items/item_manager.py`)

Управление предметами в игре:
- Создание предметов
- Модификация характеристик
- Зачарование и камни
- Таблицы добычи

```python
from items.item_manager import item_manager

# Создание предмета
item = item_manager.create_item("wpn_001", quality=0.9)

# Создание случайного предмета
random_item = item_manager.create_random_item(item_type="weapon", rarity="rare")

# Создание таблицы добычи
loot = item_manager.create_loot_table(enemy_level=10)
```

## Хранение данных

### JSON файлы

Настройки и статические данные хранятся в JSON файлах:

- `data/items.json` - предметы
- `data/entities.json` - сущности
- `data/effects.json` - эффекты
- `data/abilities.json` - способности
- `data/game_settings.json` - настройки игры

### База данных SQLite

Динамические данные хранятся в SQLite:

- `data/game_data.db` - игровые данные
- `saves/saves.db` - сохранения игр

## Система 16-ричных ID

### Преимущества
- **Эффективность памяти**: 16-ричные ID занимают меньше места в памяти
- **Уникальность**: Гарантированно уникальные ID для всех сущностей
- **Простота хранения**: Оптимизированы для хранения в базе данных
- **Масштабируемость**: Поддерживает миллионы сущностей
- **Обратная совместимость**: Конвертер для старых ID

### Формат ID
- **Короткий формат**: `plr_00000000` (префикс + 8 символов hex)
- **Полный формат**: `plr_0001000500011107` (16 символов hex с метаданными)
- **Префиксы типов**: plr (игрок), enm (враг), bos (босс), itm (предмет), eff (эффект)

### Типы сущностей
- `AI_ENTITY` - AI сущности
- `ITEM` - Предметы
- `EFFECT` - Эффекты и способности
- `PLAYER` - Игроки
- `ENEMY` - Враги
- `BOSS` - Боссы
- `NPC` - NPC
- `PROJECTILE` - Снаряды
- `TRAP` - Ловушки
- `CONTAINER` - Контейнеры

### Использование

```python
from utils.entity_id_generator import generate_short_entity_id, EntityType

# Генерация ID для разных типов сущностей
player_id = generate_short_entity_id(EntityType.PLAYER)  # plr_00000000
enemy_id = generate_short_entity_id(EntityType.ENEMY)    # enm_00010000
item_id = generate_short_entity_id(EntityType.ITEM)      # itm_00020000
effect_id = generate_short_entity_id(EntityType.EFFECT)  # eff_00030000
```

### Конвертация старых ID

```python
from utils.entity_id_generator import convert_legacy_id

# Конвертация старых ID в новые
new_id = convert_legacy_id("player_001", EntityType.PLAYER)  # plr_00000000
new_id = convert_legacy_id("wpn_001", EntityType.ITEM)       # itm_00010000
```

## Запуск игры

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск игры
python main.py
```

## Расширение проекта

### Добавление нового типа предметов

1. Добавить данные в `data/items.json`
2. Обновить `ItemType` в `items/item_manager.py`
3. Добавить логику в `ItemManager`

### Добавление нового типа врагов

1. Добавить данные в `data/entities.json`
2. Обновить `EntityFactory` для создания нового типа
3. Добавить логику поведения в AI систему

### Добавление новых эффектов

1. Добавить данные в `data/effects.json`
2. Создать класс эффекта в `entities/effect.py`
3. Интегрировать с системой эффектов

## Преимущества новой архитектуры

1. **Модульность** - каждый компонент независим
2. **Масштабируемость** - легко добавлять новые функции
3. **Поддерживаемость** - код структурирован и понятен
4. **Производительность** - оптимизированная работа с данными
5. **Гибкость** - легко изменять настройки и данные

## Требования

- Python 3.8+
- SQLite3
- Panda3D (для рендеринга)
- Дополнительные библиотеки в `requirements.txt`

# Улучшенные системы игры

## Обзор

В этом документе описаны новые улучшенные системы, которые были добавлены в проект для реализации требований по AI-управлению, спецэффектам предметов и улучшенной архитектуре.

## 1. Система эффектов (Effect System)

### 1.1. Описание
Система эффектов заменяет строковые описания на полноценные объекты с полной семантикой. Каждый эффект содержит всю необходимую информацию для применения, включая тип, значение, длительность, масштабирование от статов и специальные параметры.

### 1.2. Основные компоненты

#### Effect
Базовый класс для всех эффектов в игре:
- **name**: Название эффекта
- **category**: Категория (INSTANT, BUFF, DEBUFF, DOT, HOT, SHIELD, TRANSFORM, SUMMON)
- **value**: Значение эффекта (число или словарь статов)
- **duration**: Длительность (0 для мгновенных)
- **period**: Период применения для DOT/HOT эффектов
- **damage_types**: Типы урона
- **scaling**: Масштабирование от статов персонажа
- **target_type**: Тип цели (SELF, ENEMY, ALLY, AREA, PROJECTILE)

#### SpecialEffect
Структура для специальных эффектов предметов:
- **chance**: Вероятность срабатывания (0.0 - 1.0)
- **effect**: Экземпляр класса Effect
- **trigger_condition**: Условие срабатывания
- **cooldown**: Кулдаун между срабатываниями
- **max_procs**: Максимальное количество срабатываний

#### TriggerSystem
Система для обработки триггеров спецэффектов:
- Поддерживает различные типы триггеров (on_hit, on_crit, on_spell_cast и др.)
- Позволяет регистрировать callback-функции для каждого типа
- Автоматически активирует все зарегистрированные триггеры

### 1.3. Примеры использования

```python
# Создание эффекта поджига
burn_effect = Effect(
    name="Ожог",
    category=EffectCategory.DOT,
    value=8,
    damage_types=[DamageType.FIRE],
    duration=5,
    period=1,
    scaling={"intelligence": 0.2},
    target_type=TargetType.ENEMY
)

# Создание спецэффекта оружия
burn_special = SpecialEffect(
    chance=0.25,
    effect=burn_effect,
    trigger_condition="on_hit",
    cooldown=0,
    max_procs=0
)
```

## 2. Система предметов (Enhanced Item System)

### 2.1. Описание
Улучшенная система предметов с поддержкой спецэффектов, различных типов экипировки и интеллектуального управления предметами.

### 2.2. Основные компоненты

#### BaseItem
Базовый класс для всех предметов:
- **name**: Название предмета
- **description**: Описание
- **item_type**: Тип предмета
- **rarity**: Редкость (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, MYTHIC)
- **required_level**: Требуемый уровень
- **durability**: Долговечность
- **stackable**: Можно ли складывать

#### Weapon
Класс оружия с поддержкой спецэффектов:
- **damage**: Базовый урон
- **attack_speed**: Скорость атаки
- **damage_type**: Тип урона
- **special_effects**: Список спецэффектов
- **range**: Дальность атаки
- **accuracy**: Точность

#### Accessory
Класс аксессуаров:
- **slot**: Слот для экипировки
- **stats**: Бонусы к статам
- **special_effects**: Спецэффекты

#### Consumable
Класс расходуемых предметов:
- **effects**: Список эффектов при использовании
- **cooldown**: Кулдаун использования
- **stackable**: Можно складывать

### 2.3. Система слотов
- **MAIN_HAND**: Основная рука
- **OFF_HAND**: Вторая рука
- **HEAD**: Голова
- **CHEST**: Грудь
- **LEGS**: Ноги
- **FEET**: Обувь
- **RING_1/RING_2**: Кольца
- **NECKLACE**: Ожерелье
- **CLOAK**: Плащ

### 2.4. Примеры использования

```python
# Создание огненного меча
fire_sword = Weapon(
    name="Пылающий клинок",
    description="Меч, наполненный мощью огненного элементаля",
    damage=35,
    attack_speed=1.1,
    damage_type=DamageType.FIRE,
    slot=ItemSlot.MAIN_HAND,
    rarity=ItemRarity.EPIC,
    special_effects=[burn_special, explosion_special],
    required_level=15
)

# Создание кольца молний
lightning_ring = Accessory(
    name="Кольцо грозы",
    description="Увеличивает мощь заклинаний молнии",
    slot=ItemSlot.RING_1,
    stats=ItemStats(intelligence=15),
    rarity=ItemRarity.RARE,
    special_effects=[chain_effect, conductivity_effect],
    required_level=10
)
```

## 3. Система навыков (Enhanced Skill System)

### 3.1. Описание
Система навыков с поддержкой AI-приоритетов, комбо-цепочек, глобальных кулдаунов и различных типов навыков.

### 3.2. Основные компоненты

#### Skill
Базовый класс навыка:
- **name**: Название навыка
- **skill_type**: Тип (ATTACK, HEAL, BUFF, DEBUFF, UTILITY, MOVEMENT, SUMMON)
- **effects**: Список эффектов
- **cooldown_info**: Информация о кулдаунах
- **range_params**: Параметры дальности
- **requirements**: Требования для использования
- **scaling**: Масштабирование от статов
- **ai_priority**: Приоритеты для AI

#### SkillCooldown
Система кулдаунов:
- **base_cooldown**: Базовый кулдаун
- **gcd_group**: Группа глобального кулдауна
- **gcd**: Глобальный кулдаун
- **charges**: Количество зарядов
- **max_charges**: Максимальное количество зарядов

#### AIPriority
Приоритеты для AI:
- **base_priority**: Базовый приоритет
- **health_threshold**: Порог здоровья для использования
- **mana_threshold**: Порог маны для использования
- **tags**: Теги для AI

### 3.3. Типы навыков

#### WeaponAttackSkill
Навык атаки оружия с поддержкой спецэффектов:
- Автоматически применяет спецэффекты оружия при использовании
- Интегрируется с системой предметов

#### ComboSkill
Навык, являющийся частью комбо:
- Увеличивает урон с каждым ударом в комбо
- Поддерживает цепочки комбо

### 3.4. Примеры использования

```python
# Создание базовой атаки
basic_attack = Skill(
    name="Базовая атака",
    description="Простая атака оружием",
    skill_type=SkillType.ATTACK,
    effects=[attack_effect],
    cooldown=1.0,
    gcd_group="melee",
    gcd=1.0,
    range_params=SkillRange(max_range=1.0),
    requirements=SkillRequirements(),
    scaling=SkillScaling(strength=0.5, agility=0.3),
    ai_priority=AIPriority(base_priority=0.7, tags=["attack", "melee"])
)

# Создание огненного шара
fireball = Skill(
    name="Огненный шар",
    description="Магический снаряд из огня",
    skill_type=SkillType.ATTACK,
    effects=[fireball_effect],
    cooldown=3.0,
    gcd_group="spell",
    gcd=1.5,
    range_params=SkillRange(max_range=8.0, area_shape="circle", area_size=1.5),
    requirements=SkillRequirements(level=5, intelligence=15, mana_cost=20),
    scaling=SkillScaling(intelligence=0.8),
    ai_priority=AIPriority(base_priority=0.6, tags=["attack", "magic", "fire"])
)
```

## 4. Система AI с обучением (Enhanced AI System)

### 4.1. Описание
Улучшенная система AI с поддержкой обучения, памяти поколений и принятия решений на основе опыта.

### 4.2. Основные компоненты

#### EnhancedAISystem
Основная система AI с обучением:
- **individual_memory**: Индивидуальная память каждой сущности
- **shared_memories**: Общая память для групп AI
- **learning_data**: Данные об обучении
- **q_table**: Q-learning таблица
- **generation_memory**: Память поколений

#### SharedMemory
Общая память для групп AI:
- **enemies**: Память врагов
- **bosses**: Память боссов
- **npcs**: Память NPC
- Поддерживает передачу знаний между поколениями

#### LearningData
Данные об обучении AI:
- **total_actions**: Общее количество действий
- **successful_actions**: Успешные действия
- **failed_actions**: Неудачные действия
- **total_reward**: Общее вознаграждение
- **average_reward**: Среднее вознаграждение
- **learning_rate**: Скорость обучения
- **exploration_rate**: Скорость исследования

### 4.3. Типы обучения

#### Reinforcement Learning
Обучение с подкреплением:
- AI получает вознаграждение за успешные действия
- Обновляет Q-таблицу на основе результатов
- Адаптирует стратегии поведения

#### Observation Learning
Обучение через наблюдение:
- AI наблюдает за действиями других сущностей
- Копирует успешные стратегии
- Адаптирует их под свои нужды

#### Social Learning
Социальное обучение:
- AI обменивается знаниями с другими
- Создает общую базу знаний
- Улучшает коллективный интеллект

### 4.4. Память поколений

Система сохраняет память AI между игровыми сессиями:
- **save_generation_memory()**: Сохранение памяти поколения
- **load_generation_memory()**: Загрузка памяти поколения
- **current_generation**: Текущее поколение AI

### 4.5. Примеры использования

```python
# Создание AI системы
ai_system = EnhancedAISystem()
ai_system.initialize()

# Регистрация сущности с групповой памятью
ai_system.register_entity("enemy_1", enemy_data, memory_group="enemies")

# Обновление AI с обучением
ai_system.update_entity("enemy_1", enemy_data, delta_time)

# Запись результата действия для обучения
ai_system.record_action_result(
    entity_id="enemy_1",
    action="attack",
    success=True,
    reward=1.0,
    context={"target": "player", "health": 80}
)

# Сохранение памяти поколения
ai_system.save_generation_memory("save_1")

# Загрузка памяти поколения
ai_system.load_generation_memory("save_1")
```

## 5. Интеграция систем

### 5.1. Связь между системами

Все системы интегрированы между собой:

1. **Effect System** → **Item System**: Предметы используют эффекты
2. **Item System** → **Skill System**: Навыки используют предметы
3. **Skill System** → **AI System**: AI использует навыки
4. **AI System** → **Effect System**: AI применяет эффекты

### 5.2. Пример полного цикла

```python
# 1. AI принимает решение атаковать
decision = ai_system.make_decision(ai_data, entity_data)

# 2. AI использует навык
skill_result = skill_system.use_skill("basic_attack", entity, [target])

# 3. Навык применяет эффекты
for effect in skill.effects:
    effect.apply_instant(entity, target)

# 4. Оружие применяет спецэффекты
if entity.equipped_weapon:
    entity.equipped_weapon.apply_special_effects(entity, target, "on_hit")

# 5. Система триггеров активируется
trigger_system.trigger("on_hit", entity, target)

# 6. AI записывает результат для обучения
ai_system.record_action_result(entity.id, "attack", True, 1.0, context)
```

## 6. Преимущества новой архитектуры

### 6.1. Геймплейные преимущества
- **Глубина механик**: Сложные взаимодействия между эффектами
- **Балансировка**: Точный контроль над вероятностью и частотой
- **Тактическое разнообразие**: Уникальные игровые стили
- **Комбинаторика**: Синергия между предметами

### 6.2. Технические преимущества
- **Производительность**: Оптимизированная обработка
- **Масштабируемость**: Легкое добавление новых механик
- **Поддерживаемость**: Четкая структура кода
- **Тестируемость**: Изолированные компоненты

### 6.3. AI-интеграция
- **Анализ эффектов**: ИИ оценивает полезность предметов
- **Принятие решений**: Учет вероятностных эффектов
- **Адаптация**: Динамическая оценка эффективности
- **Обучение**: На основе статистики срабатывания

## 7. Заключение

Новая архитектура систем предоставляет:

1. **Структурированные спецэффекты** вместо строковых описаний
2. **Систему триггеров** для условного срабатывания
3. **Улучшенные классы предметов** с поддержкой спецэффектов
4. **Систему навыков** с AI-приоритетами и комбо
5. **AI-систему с обучением** и памятью поколений
6. **Полную интеграцию** всех систем

Это создает основу для создания сложных, сбалансированных и интересных игровых механик, где AI может обучаться и адаптироваться, а предметы предоставляют уникальные возможности для различных игровых стилей.

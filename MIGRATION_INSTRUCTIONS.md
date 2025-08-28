# Инструкции по миграции на BaseSystem

Найдено 15 систем, требующих миграции:

## AISystem (src\systems\ai\ai_system.py)
# Миграция AISystem на BaseSystem
# Файл: src\systems\ai\ai_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class AISystem(ISystem):
# НА:
class AISystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="aisystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="aisystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## CombatSystem (src\systems\combat\combat_system.py)
# Миграция CombatSystem на BaseSystem
# Файл: src\systems\combat\combat_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class CombatSystem(ISystem):
# НА:
class CombatSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="combatsystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="combatsystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## ContentDatabase (src\systems\content\content_database.py)
# Миграция ContentDatabase на BaseSystem
# Файл: src\systems\content\content_database.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class ContentDatabase(ISystem):
# НА:
class ContentDatabase(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="contentdatabase", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="contentdatabase", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## ContentGenerator (src\systems\content\content_generator.py)
# Миграция ContentGenerator на BaseSystem
# Файл: src\systems\content\content_generator.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class ContentGenerator(ISystem):
# НА:
class ContentGenerator(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="contentgenerator", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="contentgenerator", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## CraftingSystem (src\systems\crafting\crafting_system.py)
# Миграция CraftingSystem на BaseSystem
# Файл: src\systems\crafting\crafting_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class CraftingSystem(ISystem):
# НА:
class CraftingSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="craftingsystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="craftingsystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## EffectSystem (src\systems\effects\effect_system.py)
# Миграция EffectSystem на BaseSystem
# Файл: src\systems\effects\effect_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class EffectSystem(ISystem):
# НА:
class EffectSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="effectsystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="effectsystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## EmotionSystem (src\systems\emotion\emotion_system.py)
# Миграция EmotionSystem на BaseSystem
# Файл: src\systems\emotion\emotion_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class EmotionSystem(ISystem):
# НА:
class EmotionSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="emotionsystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="emotionsystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## EntityStatsSystem (src\systems\entity\entity_stats_system.py)
# Миграция EntityStatsSystem на BaseSystem
# Файл: src\systems\entity\entity_stats_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class EntityStatsSystem(ISystem):
# НА:
class EntityStatsSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="entitystatssystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="entitystatssystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## EvolutionSystem (src\systems\evolution\evolution_system.py)
# Миграция EvolutionSystem на BaseSystem
# Файл: src\systems\evolution\evolution_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class EvolutionSystem(ISystem):
# НА:
class EvolutionSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="evolutionsystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="evolutionsystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## GenomeSystem (src\systems\genome\genome_system.py)
# Миграция GenomeSystem на BaseSystem
# Файл: src\systems\genome\genome_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class GenomeSystem(ISystem):
# НА:
class GenomeSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="genomesystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="genomesystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## InventorySystem (src\systems\inventory\inventory_system.py)
# Миграция InventorySystem на BaseSystem
# Файл: src\systems\inventory\inventory_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class InventorySystem(ISystem):
# НА:
class InventorySystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="inventorysystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="inventorysystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## ItemSystem (src\systems\items\item_system.py)
# Миграция ItemSystem на BaseSystem
# Файл: src\systems\items\item_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class ItemSystem(ISystem):
# НА:
class ItemSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="itemsystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="itemsystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## RenderSystem (src\systems\rendering\render_system.py)
# Миграция RenderSystem на BaseSystem
# Файл: src\systems\rendering\render_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class RenderSystem(ISystem):
# НА:
class RenderSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="rendersystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="rendersystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## SkillSystem (src\systems\skills\skill_system.py)
# Миграция SkillSystem на BaseSystem
# Файл: src\systems\skills\skill_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class SkillSystem(ISystem):
# НА:
class SkillSystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="skillsystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="skillsystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()

## UISystem (src\systems\ui\ui_system.py)
# Миграция UISystem на BaseSystem
# Файл: src\systems\ui\ui_system.py

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class UISystem(ISystem):
# НА:
class UISystem(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="uisystem", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="uisystem", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()


#!/usr/bin/env python3
"""
Основные интерфейсы для системы AI-EVOLVE
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from .constants import SystemPriority, SystemState

# ============================================================================
# БАЗОВЫЙ ИНТЕРФЕЙС СИСТЕМЫ
# ============================================================================

class ISystem(ABC):
    """Базовый интерфейс для всех игровых систем"""
    
    @property
    @abstractmethod
    def system_name(self) -> str:
        """Имя системы"""
        pass
    
    @property
    @abstractmethod
    def system_priority(self) -> SystemPriority:
        """Приоритет системы"""
        pass
    
    @property
    @abstractmethod
    def system_state(self) -> SystemState:
        """Текущее состояние системы"""
        pass
    
    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """Список зависимостей от других систем"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация системы"""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> bool:
        """Обновление системы"""
        pass
    
    @abstractmethod
    def pause(self) -> bool:
        """Приостановка системы"""
        pass
    
    @abstractmethod
    def resume(self) -> bool:
        """Возобновление системы"""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Очистка системы"""
        pass
    
    @abstractmethod
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        pass
    
    @abstractmethod
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ УПРАВЛЕНИЯ РЕСУРСАМИ
# ============================================================================

class IResourceManager(ABC):
    """Интерфейс для управления ресурсами"""
    
    @abstractmethod
    def load_resource(self, resource_id: str) -> Any:
        """Загрузка ресурса"""
        pass
    
    @abstractmethod
    def unload_resource(self, resource_id: str) -> bool:
        """Выгрузка ресурса"""
        pass
    
    @abstractmethod
    def get_resource_info(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о ресурсе"""
        pass

class IConfigManager(ABC):
    """Интерфейс для управления конфигурацией"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        pass
    
    @abstractmethod
    def load_config(self, config_path: str) -> bool:
        """Загрузка конфигурации из файла"""
        pass
    
    @abstractmethod
    def save_config(self, config_path: str) -> bool:
        """Сохранение конфигурации в файл"""
        pass

class IPerformanceMonitor(ABC):
    """Интерфейс для мониторинга производительности"""
    
    @abstractmethod
    def start_timer(self, timer_name: str) -> None:
        """Запуск таймера"""
        pass
    
    @abstractmethod
    def stop_timer(self, timer_name: str) -> float:
        """Остановка таймера и получение времени"""
        pass
    
    @abstractmethod
    def get_performance_stats(self) -> Dict[str, Any]:
        """Получение статистики производительности"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ УПРАВЛЕНИЯ СЦЕНОЙ
# ============================================================================

class ISceneManager(ABC):
    """Интерфейс для управления сценами"""
    
    @abstractmethod
    def create_scene(self, scene_id: str) -> bool:
        """Создание сцены"""
        pass
    
    @abstractmethod
    def destroy_scene(self, scene_id: str) -> bool:
        """Уничтожение сцены"""
        pass
    
    @abstractmethod
    def set_active_scene(self, scene_id: str) -> bool:
        """Установка активной сцены"""
        pass
    
    @abstractmethod
    def get_active_scene(self) -> Optional[str]:
        """Получение активной сцены"""
        pass

class IGameEngine(ABC):
    """Интерфейс для игрового движка"""
    
    @abstractmethod
    def start(self) -> bool:
        """Запуск движка"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Остановка движка"""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Проверка, запущен ли движок"""
        pass

class ISystemManager(ABC):
    """Интерфейс для управления системами"""
    
    @abstractmethod
    def register_system(self, system: ISystem) -> bool:
        """Регистрация системы"""
        pass
    
    @abstractmethod
    def unregister_system(self, system_name: str) -> bool:
        """Отмена регистрации системы"""
        pass
    
    @abstractmethod
    def get_system(self, system_name: str) -> Optional[ISystem]:
        """Получение системы по имени"""
        pass
    
    @abstractmethod
    def get_all_systems(self) -> List[ISystem]:
        """Получение всех систем"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ ГЕНЕРАЦИИ КОНТЕНТА
# ============================================================================

class IContentGenerator(ABC):
    """Интерфейс для генерации контента"""
    
    @abstractmethod
    def generate_content(self, content_type: str, **kwargs) -> Any:
        """Генерация контента"""
        pass
    
    @abstractmethod
    def get_generation_stats(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        pass

class IAIEntity(ABC):
    """Интерфейс для AI сущности"""
    
    @abstractmethod
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Принятие решения"""
        pass
    
    @abstractmethod
    def update_behavior(self, delta_time: float) -> None:
        """Обновление поведения"""
        pass
    
    @abstractmethod
    def get_ai_state(self) -> str:
        """Получение состояния AI"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ БОЕВОЙ СИСТЕМЫ
# ============================================================================

class ICombatSystem(ABC):
    """Интерфейс для боевой системы"""
    
    @abstractmethod
    def start_combat(self, participants: List[str]) -> str:
        """Начало боя"""
        pass
    
    @abstractmethod
    def end_combat(self, combat_id: str) -> bool:
        """Завершение боя"""
        pass
    
    @abstractmethod
    def perform_attack(self, attacker_id: str, target_id: str, attack_data: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение атаки"""
        pass
    
    @abstractmethod
    def get_combat_info(self, combat_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о бое"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ ИНВЕНТАРЯ
# ============================================================================

class IInventorySystem(ABC):
    """Интерфейс для системы инвентаря"""
    
    @abstractmethod
    def create_inventory(self, owner_id: str, max_slots: int) -> bool:
        """Создание инвентаря"""
        pass
    
    @abstractmethod
    def add_item(self, owner_id: str, item_id: str, quantity: int) -> bool:
        """Добавление предмета"""
        pass
    
    @abstractmethod
    def remove_item(self, owner_id: str, item_id: str, quantity: int) -> bool:
        """Удаление предмета"""
        pass
    
    @abstractmethod
    def get_inventory_contents(self, owner_id: str) -> List[Dict[str, Any]]:
        """Получение содержимого инвентаря"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ КРАФТИНГА
# ============================================================================

class ICraftingSystem(ABC):
    """Интерфейс для системы крафтинга"""
    
    @abstractmethod
    def can_craft(self, crafter_id: str, recipe_id: str) -> bool:
        """Проверка возможности крафтинга"""
        pass
    
    @abstractmethod
    def start_crafting(self, crafter_id: str, recipe_id: str) -> str:
        """Начало крафтинга"""
        pass
    
    @abstractmethod
    def get_crafting_progress(self, craft_id: str) -> Optional[Dict[str, Any]]:
        """Получение прогресса крафтинга"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ ЭВОЛЮЦИИ
# ============================================================================

class IEvolutionSystem(ABC):
    """Интерфейс для системы эволюции"""
    
    @abstractmethod
    def can_evolve(self, entity_id: str) -> bool:
        """Проверка возможности эволюции"""
        pass
    
    @abstractmethod
    def trigger_evolution(self, entity_id: str) -> bool:
        """Запуск эволюции"""
        pass
    
    @abstractmethod
    def get_evolution_progress(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение прогресса эволюции"""
        pass

class IGenomeSystem(ABC):
    """Интерфейс для системы генов"""
    
    @abstractmethod
    def get_genome(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение генома"""
        pass
    
    @abstractmethod
    def mutate_genome(self, entity_id: str, mutation_type: str) -> bool:
        """Мутация генома"""
        pass
    
    @abstractmethod
    def get_genetic_traits(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение генетических черт"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ ЭМОЦИЙ
# ============================================================================

class IEmotionSystem(ABC):
    """Интерфейс для системы эмоций"""
    
    @abstractmethod
    def add_emotion(self, entity_id: str, emotion_type: str, intensity: float) -> bool:
        """Добавление эмоции"""
        pass
    
    @abstractmethod
    def get_emotional_state(self, entity_id: str) -> Dict[str, Any]:
        """Получение эмоционального состояния"""
        pass
    
    @abstractmethod
    def update_emotions(self, delta_time: float) -> None:
        """Обновление эмоций"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ НАВЫКОВ
# ============================================================================

class ISkillSystem(ABC):
    """Интерфейс для системы навыков"""
    
    @abstractmethod
    def learn_skill(self, entity_id: str, skill_id: str) -> bool:
        """Изучение навыка"""
        pass
    
    @abstractmethod
    def use_skill(self, entity_id: str, skill_id: str, target: Any = None) -> bool:
        """Использование навыка"""
        pass
    
    @abstractmethod
    def get_skill_tree(self, entity_id: str) -> Dict[str, Any]:
        """Получение дерева навыков"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ ЭФФЕКТОВ
# ============================================================================

class IEffectSystem(ABC):
    """Интерфейс для системы эффектов"""
    
    @abstractmethod
    def apply_effect(self, target_id: str, effect_id: str, duration: float) -> bool:
        """Применение эффекта"""
        pass
    
    @abstractmethod
    def remove_effect(self, target_id: str, effect_id: str) -> bool:
        """Удаление эффекта"""
        pass
    
    @abstractmethod
    def get_active_effects(self, target_id: str) -> List[Dict[str, Any]]:
        """Получение активных эффектов"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ ПРЕДМЕТОВ
# ============================================================================

class IItemSystem(ABC):
    """Интерфейс для системы предметов"""
    
    @abstractmethod
    def create_item(self, item_template: str, **kwargs) -> Optional[Any]:
        """Создание предмета"""
        pass
    
    @abstractmethod
    def destroy_item(self, item_id: str) -> bool:
        """Уничтожение предмета"""
        pass
    
    @abstractmethod
    def get_item_info(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о предмете"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ РЕНДЕРИНГА
# ============================================================================

class IRenderSystem(ABC):
    """Интерфейс для системы рендеринга"""
    
    @abstractmethod
    def render_scene(self, scene_id: str) -> bool:
        """Рендеринг сцены"""
        pass
    
    @abstractmethod
    def create_render_object(self, object_data: Dict[str, Any]) -> str:
        """Создание объекта рендеринга"""
        pass
    
    @abstractmethod
    def update_render_object(self, object_id: str, transform: Dict[str, Any]) -> bool:
        """Обновление объекта рендеринга"""
        pass
    
    @abstractmethod
    def destroy_render_object(self, object_id: str) -> bool:
        """Уничтожение объекта рендеринга"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ UI
# ============================================================================

class IUISystem(ABC):
    """Интерфейс для системы UI"""
    
    @abstractmethod
    def create_ui_element(self, element_type: str, **kwargs) -> str:
        """Создание UI элемента"""
        pass
    
    @abstractmethod
    def update_ui_element(self, element_id: str, **kwargs) -> bool:
        """Обновление UI элемента"""
        pass
    
    @abstractmethod
    def destroy_ui_element(self, element_id: str) -> bool:
        """Уничтожение UI элемента"""
        pass
    
    @abstractmethod
    def handle_ui_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка UI событий"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ AI
# ============================================================================

class IAISystem(ABC):
    """Интерфейс для системы AI"""
    
    @abstractmethod
    def register_ai_entity(self, entity_id: str, ai_config: Dict[str, Any]) -> bool:
        """Регистрация AI сущности"""
        pass
    
    @abstractmethod
    def unregister_ai_entity(self, entity_id: str) -> bool:
        """Отмена регистрации AI сущности"""
        pass
    
    @abstractmethod
    def get_ai_entity_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об AI сущности"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ БАЗЫ ДАННЫХ
# ============================================================================

class IContentDatabase(ABC):
    """Интерфейс для базы данных контента"""
    
    @abstractmethod
    def create_session(self, session_id: str = None) -> str:
        """Создание сессии"""
        pass
    
    @abstractmethod
    def add_content_item(self, content_item: Any) -> bool:
        """Добавление элемента контента"""
        pass
    
    @abstractmethod
    def get_content_by_session(self, session_id: str, content_type: str = None) -> List[Any]:
        """Получение контента по сессии"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ ХАРАКТЕРИСТИК
# ============================================================================

class IEntityStatsSystem(ABC):
    """Интерфейс для системы характеристик сущностей"""
    
    @abstractmethod
    def create_entity_stats(self, entity_id: str, base_stats: Dict[str, float]) -> bool:
        """Создание характеристик сущности"""
        pass
    
    @abstractmethod
    def modify_entity_stats(self, entity_id: str, stat_type: str, value: float, duration: float = 0.0) -> bool:
        """Модификация характеристик сущности"""
        pass
    
    @abstractmethod
    def get_entity_stats(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение характеристик сущности"""
        pass

# ============================================================================
# ИНТЕРФЕЙСЫ СОБЫТИЙ
# ============================================================================

class IEventSubscriber(ABC):
    """Интерфейс для подписчика событий"""
    
    @abstractmethod
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка события"""
        pass

class IEventSystem(ABC):
    """Интерфейс для системы событий"""
    
    @abstractmethod
    def emit(self, event_type: str, event_data: Any) -> bool:
        """Отправка события"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, callback: callable, 
                  subscriber_id: str = "unknown") -> bool:
        """Подписка на событие"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, subscriber_id: str) -> bool:
        """Отписка от события"""
        pass
    
    @abstractmethod
    def process_events(self) -> bool:
        """Обработка событий"""
        pass
#!/usr/bin/env python3
"""
Интерфейсы для игровых систем
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from enum import Enum

class SystemPriority(Enum):
    """Приоритеты систем"""
    CRITICAL = 0      # Критические системы (рендеринг, ввод)
    HIGH = 1          # Высокий приоритет (физика, AI)
    NORMAL = 2        # Обычный приоритет (игровая логика)
    LOW = 3           # Низкий приоритет (UI, звук)
    BACKGROUND = 4    # Фоновые задачи (сохранение, логирование)

class SystemState(Enum):
    """Состояния систем"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    DESTROYED = "destroyed"

class ISystem(ABC):
    """Базовый интерфейс для всех игровых систем"""
    
    @property
    @abstractmethod
    def system_name(self) -> str:
        """Уникальное имя системы"""
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

class IEventEmitter(ABC):
    """Интерфейс для эмиттеров событий"""
    
    @abstractmethod
    def emit(self, event_type: str, event_data: Any = None) -> bool:
        """Эмиссия события"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, callback: callable) -> bool:
        """Подписка на событие"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, callback: callable) -> bool:
        """Отписка от события"""
        pass

class IEventSubscriber(ABC):
    """Интерфейс для подписчиков событий"""
    
    @abstractmethod
    def on_event(self, event_type: str, event_data: Any) -> None:
        """Обработка события"""
        pass

class IResourceManager(ABC):
    """Интерфейс для менеджера ресурсов"""
    
    @abstractmethod
    def load_resource(self, resource_path: str, resource_type: str) -> Any:
        """Загрузка ресурса"""
        pass
    
    @abstractmethod
    def unload_resource(self, resource_path: str) -> bool:
        """Выгрузка ресурса"""
        pass
    
    @abstractmethod
    def get_resource(self, resource_path: str) -> Optional[Any]:
        """Получение ресурса"""
        pass
    
    @abstractmethod
    def preload_resources(self, resource_list: List[str]) -> bool:
        """Предзагрузка ресурсов"""
        pass

class IConfigManager(ABC):
    """Интерфейс для менеджера конфигурации"""
    
    @abstractmethod
    def load_config(self, config_path: str) -> bool:
        """Загрузка конфигурации"""
        pass
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> bool:
        """Установка значения конфигурации"""
        pass
    
    @abstractmethod
    def save_config(self) -> bool:
        """Сохранение конфигурации"""
        pass

class IPerformanceMonitor(ABC):
    """Интерфейс для мониторинга производительности"""
    
    @abstractmethod
    def start_monitoring(self) -> bool:
        """Запуск мониторинга"""
        pass
    
    @abstractmethod
    def stop_monitoring(self) -> bool:
        """Остановка мониторинга"""
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Получение метрик производительности"""
        pass
    
    @abstractmethod
    def optimize_performance(self) -> bool:
        """Оптимизация производительности"""
        pass

class ISceneManager(ABC):
    """Интерфейс для менеджера сцен"""
    
    @abstractmethod
    def create_scene(self, scene_name: str, scene_class: type) -> bool:
        """Создание сцены"""
        pass
    
    @abstractmethod
    def switch_scene(self, scene_name: str) -> bool:
        """Переключение сцены"""
        pass
    
    @abstractmethod
    def get_current_scene(self) -> Optional[str]:
        """Получение текущей сцены"""
        pass
    
    @abstractmethod
    def destroy_scene(self, scene_name: str) -> bool:
        """Уничтожение сцены"""
        pass

class IGameEngine(ABC):
    """Интерфейс для игрового движка"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Инициализация движка"""
        pass
    
    @abstractmethod
    def run(self) -> bool:
        """Запуск игрового цикла"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Остановка движка"""
        pass
    
    @abstractmethod
    def get_system_manager(self) -> 'ISystemManager':
        """Получение менеджера систем"""
        pass
    
    @abstractmethod
    def get_scene_manager(self) -> ISceneManager:
        """Получение менеджера сцен"""
        pass

class ISystemManager(ABC):
    """Интерфейс для менеджера систем"""
    
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
    def update_all_systems(self, delta_time: float) -> bool:
        """Обновление всех систем"""
        pass
    
    @abstractmethod
    def initialize_all_systems(self) -> bool:
        """Инициализация всех систем"""
        pass

class IContentGenerator(ABC):
    """Интерфейс для генератора контента"""
    
    @abstractmethod
    def generate_content(self, content_type: str, parameters: Dict[str, Any]) -> Any:
        """Генерация контента"""
        pass
    
    @abstractmethod
    def validate_content(self, content: Any) -> bool:
        """Валидация контента"""
        pass
    
    @abstractmethod
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Получение статистики генерации"""
        pass

class IAIEntity(ABC):
    """Интерфейс для AI сущности"""
    
    @abstractmethod
    def make_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Принятие решения"""
        pass
    
    @abstractmethod
    def update_emotion(self, stimulus: Dict[str, Any]) -> bool:
        """Обновление эмоций"""
        pass
    
    @abstractmethod
    def learn(self, experience: Dict[str, Any]) -> bool:
        """Обучение на опыте"""
        pass
    
    @abstractmethod
    def get_memory(self) -> Dict[str, Any]:
        """Получение памяти"""
        pass

class ICombatSystem(ABC):
    """Интерфейс для системы боя"""
    
    @abstractmethod
    def initiate_combat(self, attacker: str, target: str) -> bool:
        """Инициация боя"""
        pass
    
    @abstractmethod
    def process_attack(self, attacker: str, target: str, attack_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка атаки"""
        pass
    
    @abstractmethod
    def end_combat(self, combat_id: str) -> bool:
        """Завершение боя"""
        pass
    
    @abstractmethod
    def get_combat_status(self, combat_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса боя"""
        pass

class IInventorySystem(ABC):
    """Интерфейс для системы инвентаря"""
    
    @abstractmethod
    def add_item(self, entity_id: str, item: Dict[str, Any]) -> bool:
        """Добавление предмета"""
        pass
    
    @abstractmethod
    def remove_item(self, entity_id: str, item_id: str) -> bool:
        """Удаление предмета"""
        pass
    
    @abstractmethod
    def get_inventory(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение инвентаря"""
        pass
    
    @abstractmethod
    def has_item(self, entity_id: str, item_id: str) -> bool:
        """Проверка наличия предмета"""
        pass

class ICraftingSystem(ABC):
    """Интерфейс для системы крафтинга"""
    
    @abstractmethod
    def can_craft(self, recipe_id: str, materials: List[str]) -> bool:
        """Проверка возможности крафта"""
        pass
    
    @abstractmethod
    def craft_item(self, recipe_id: str, materials: List[str]) -> Optional[Dict[str, Any]]:
        """Крафт предмета"""
        pass
    
    @abstractmethod
    def get_available_recipes(self, skill_level: int) -> List[Dict[str, Any]]:
        """Получение доступных рецептов"""
        pass
    
    @abstractmethod
    def learn_recipe(self, entity_id: str, recipe_id: str) -> bool:
        """Изучение рецепта"""
        pass

class IEvolutionSystem(ABC):
    """Интерфейс для системы эволюции"""
    
    @abstractmethod
    def evolve_entity(self, entity_id: str, evolution_path: str) -> bool:
        """Эволюция сущности"""
        pass
    
    @abstractmethod
    def get_evolution_options(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение вариантов эволюции"""
        pass
    
    @abstractmethod
    def apply_mutation(self, entity_id: str, mutation_type: str) -> bool:
        """Применение мутации"""
        pass
    
    @abstractmethod
    def get_evolution_progress(self, entity_id: str) -> Dict[str, Any]:
        """Получение прогресса эволюции"""
        pass

class IGenomeSystem(ABC):
    """Интерфейс для системы генома"""
    
    @abstractmethod
    def create_genome(self, entity_id: str, parent_genomes: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Создание генома"""
        pass
    
    @abstractmethod
    def mutate_genome(self, genome: Dict[str, Any], mutation_rate: float) -> Dict[str, Any]:
        """Мутация генома"""
        pass
    
    @abstractmethod
    def crossover_genomes(self, genome1: Dict[str, Any], genome2: Dict[str, Any]) -> Dict[str, Any]:
        """Скрещивание геномов"""
        pass
    
    @abstractmethod
    def get_genome_traits(self, genome: Dict[str, Any]) -> Dict[str, Any]:
        """Получение черт генома"""
        pass

class IEmotionSystem(ABC):
    """Интерфейс для системы эмоций"""
    
    @abstractmethod
    def update_emotion(self, entity_id: str, emotion_type: str, intensity: float) -> bool:
        """Обновление эмоции"""
        pass
    
    @abstractmethod
    def get_emotional_state(self, entity_id: str) -> Dict[str, Any]:
        """Получение эмоционального состояния"""
        pass
    
    @abstractmethod
    def process_emotional_stimulus(self, entity_id: str, stimulus: Dict[str, Any]) -> bool:
        """Обработка эмоционального стимула"""
        pass
    
    @abstractmethod
    def get_emotion_history(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение истории эмоций"""
        pass

class ISkillSystem(ABC):
    """Интерфейс для системы скиллов"""
    
    @abstractmethod
    def learn_skill(self, entity_id: str, skill_id: str) -> bool:
        """Изучение скилла"""
        pass
    
    @abstractmethod
    def use_skill(self, entity_id: str, skill_id: str, target: str = None) -> bool:
        """Использование скилла"""
        pass
    
    @abstractmethod
    def get_skill_level(self, entity_id: str, skill_id: str) -> int:
        """Получение уровня скилла"""
        pass
    
    @abstractmethod
    def upgrade_skill(self, entity_id: str, skill_id: str) -> bool:
        """Улучшение скилла"""
        pass

class IEffectSystem(ABC):
    """Интерфейс для системы эффектов"""
    
    @abstractmethod
    def apply_effect(self, target_id: str, effect_type: str, effect_data: Dict[str, Any]) -> bool:
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
    
    @abstractmethod
    def update_effects(self, delta_time: float) -> bool:
        """Обновление эффектов"""
        pass

class IItemSystem(ABC):
    """Интерфейс для системы предметов"""
    
    @abstractmethod
    def create_item(self, item_type: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание предмета"""
        pass
    
    @abstractmethod
    def modify_item(self, item_id: str, modifications: Dict[str, Any]) -> bool:
        """Модификация предмета"""
        pass
    
    @abstractmethod
    def destroy_item(self, item_id: str) -> bool:
        """Уничтожение предмета"""
        pass
    
    @abstractmethod
    def get_item_properties(self, item_id: str) -> Dict[str, Any]:
        """Получение свойств предмета"""
        pass

class IRenderSystem(ABC):
    """Интерфейс для системы рендеринга"""
    
    @abstractmethod
    def render_scene(self, scene_data: Dict[str, Any]) -> bool:
        """Рендеринг сцены"""
        pass
    
    @abstractmethod
    def create_render_object(self, object_type: str, object_data: Dict[str, Any]) -> Any:
        """Создание объекта рендеринга"""
        pass
    
    @abstractmethod
    def update_render_object(self, object_id: str, object_data: Dict[str, Any]) -> bool:
        """Обновление объекта рендеринга"""
        pass
    
    @abstractmethod
    def destroy_render_object(self, object_id: str) -> bool:
        """Уничтожение объекта рендеринга"""
        pass

class IUISystem(ABC):
    """Интерфейс для системы UI"""
    
    @abstractmethod
    def create_ui_element(self, element_type: str, element_data: Dict[str, Any]) -> Any:
        """Создание UI элемента"""
        pass
    
    @abstractmethod
    def update_ui_element(self, element_id: str, element_data: Dict[str, Any]) -> bool:
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

class IAISystem(ABC):
    """Интерфейс для AI системы"""
    
    @abstractmethod
    def create_ai_entity(self, entity_id: str, ai_type: str) -> IAIEntity:
        """Создание AI сущности"""
        pass
    
    @abstractmethod
    def update_ai_entities(self, delta_time: float) -> bool:
        """Обновление AI сущностей"""
        pass
    
    @abstractmethod
    def get_ai_entity(self, entity_id: str) -> Optional[IAIEntity]:
        """Получение AI сущности"""
        pass
    
    @abstractmethod
    def destroy_ai_entity(self, entity_id: str) -> bool:
        """Уничтожение AI сущности"""
        pass

class IContentDatabase(ABC):
    """Интерфейс для базы данных контента"""
    
    @abstractmethod
    def store_content(self, content_id: str, content_data: Dict[str, Any]) -> bool:
        """Сохранение контента"""
        pass
    
    @abstractmethod
    def retrieve_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Получение контента"""
        pass
    
    @abstractmethod
    def search_content(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Поиск контента"""
        pass
    
    @abstractmethod
    def delete_content(self, content_id: str) -> bool:
        """Удаление контента"""
        pass

class IEntityStatsSystem(ABC):
    """Интерфейс для системы характеристик сущностей"""
    
    @abstractmethod
    def create_entity_stats(self, entity_id: str, base_stats: Dict[str, Any]) -> bool:
        """Создание характеристик сущности"""
        pass
    
    @abstractmethod
    def modify_entity_stats(self, entity_id: str, stat_modifications: Dict[str, Any]) -> bool:
        """Модификация характеристик сущности"""
        pass
    
    @abstractmethod
    def get_entity_stats(self, entity_id: str) -> Dict[str, Any]:
        """Получение характеристик сущности"""
        pass
    
    @abstractmethod
    def calculate_derived_stats(self, entity_id: str) -> Dict[str, Any]:
        """Расчет производных характеристик"""
        pass
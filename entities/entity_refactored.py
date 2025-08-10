"""Рефакторенный базовый класс Entity с компонентной архитектурой."""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from core.component import ComponentManager, Component
from entities.effect import Effect
from core.attributes import AttributesComponent
from core.combat_stats import CombatStatsComponent
from core.inventory import InventoryComponent
from core.transform import TransformComponent
from core.interfaces import Updatable, Renderable, Saveable


class EntityType(Enum):
    """Типы сущностей."""
    PLAYER = "player"
    ENEMY = "enemy"
    BOSS = "boss"
    NPC = "npc"
    ITEM = "item"


class _CombatStatsDictView:
    """Слоевое представление боевых статов как dict для обратной совместимости.

    Доступ по ключам направляет чтение/запись к полям `CombatStats` внутри
    `CombatStatsComponent`. Неизвестные поля сохраняются во внутреннем словаре
    extras, чтобы внешние системы могли добавлять свои значения.
    """

    def __init__(self, combat_component: CombatStatsComponent):
        self._combat_component = combat_component
        self._extras: Dict[str, Any] = {}

    def __getitem__(self, key: str) -> Any:
        stats = self._combat_component.stats
        if hasattr(stats, key):
            return getattr(stats, key)
        return self._extras.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        stats = self._combat_component.stats
        if hasattr(stats, key):
            setattr(stats, key, value)
        else:
            self._extras[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        value = self.__getitem__(key)
        return default if value is None else value

    def keys(self):
        stats = self._combat_component.stats
        return set(list(stats.__dict__.keys()) + list(self._extras.keys()))


class Entity(Updatable, Renderable, Saveable):
    """Базовый класс для всех игровых сущностей."""
    
    def __init__(self, entity_id: str, entity_type: EntityType, position: Tuple[float, float] = (0, 0)):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        self.alive = True
        # Для совместимости со старой системой эффектов
        self.active_effects: List[Any] = []
        
        # Менеджер компонентов
        self.component_manager = ComponentManager()
        
        # Инициализация базовых компонентов
        self._initialize_components(position)
        # Кэш представления статов для совместимости
        self._combat_stats_view: Optional[_CombatStatsDictView] = None
    
    def _initialize_components(self, position: Tuple[float, float]) -> None:
        """Инициализация базовых компонентов."""
        # Компонент трансформации (позиция, движение)
        transform = TransformComponent(self)
        transform.set_position(*position)
        self.component_manager.add_component(transform)
        
        # Компонент атрибутов
        attributes = AttributesComponent(self)
        self.component_manager.add_component(attributes)
        
        # Компонент боевых характеристик
        combat_stats = CombatStatsComponent(self)
        self.component_manager.add_component(combat_stats)
        
        # Компонент инвентаря
        inventory = InventoryComponent(self)
        self.component_manager.add_component(inventory)
    
    def get_component(self, component_type: str) -> Optional[Component]:
        """Получить компонент по типу."""
        # Создаем словарь для быстрого поиска по имени класса
        component_map = {
            'TransformComponent': self.component_manager.get_component(TransformComponent),
            'AttributesComponent': self.component_manager.get_component(AttributesComponent),
            'CombatStatsComponent': self.component_manager.get_component(CombatStatsComponent),
            'InventoryComponent': self.component_manager.get_component(InventoryComponent)
        }
        return component_map.get(component_type)

    # Совместимость: свойства-адаптеры
    @property
    def position(self) -> List[float]:
        """Доступ к позиции как к списку [x, y] для обратной совместимости."""
        transform = self.component_manager.get_component(TransformComponent)
        return transform.position if transform else [0.0, 0.0]

    @position.setter
    def position(self, value: Tuple[float, float]):
        transform = self.component_manager.get_component(TransformComponent)
        if transform and value and len(value) >= 2:
            transform.position[0] = float(value[0])
            transform.position[1] = float(value[1])
    
    def has_component(self, component_type: str) -> bool:
        """Проверить наличие компонента."""
        return self.get_component(component_type) is not None
    
    # Методы для работы с позицией (через TransformComponent)
    def get_position(self) -> Tuple[float, float]:
        """Получить позицию."""
        transform = self.get_component('TransformComponent')
        return transform.get_position() if transform else (0, 0)
    
    def set_position(self, x: float, y: float) -> None:
        """Установить позицию."""
        transform = self.get_component('TransformComponent')
        if transform:
            transform.set_position(x, y)
    
    def move_towards(self, target_pos: Tuple[float, float], delta_time: float) -> bool:
        """Двигаться к цели."""
        transform = self.get_component('TransformComponent')
        if transform:
            return transform.move_towards(target_pos, delta_time)
        return False
    
    def distance_to(self, target_pos: Tuple[float, float]) -> float:
        """Вычислить расстояние до цели."""
        transform = self.get_component('TransformComponent')
        return transform.distance_to(target_pos) if transform else float('inf')
    
    def distance_to_entity(self, other_entity) -> float:
        """Вычислить расстояние до другой сущности."""
        transform = self.get_component('TransformComponent')
        return transform.distance_to_entity(other_entity) if transform else float('inf')
    
    # Методы для работы с атрибутами (через AttributesComponent)
    @property
    def attributes(self) -> Dict[str, Any]:
        """Словарь адаптеров атрибутов вида {name: adapter} совместимый со старым API.

        adapter.value -> читает/пишет current_value соответствующего атрибута.
        """
        attributes_component: AttributesComponent = self.component_manager.get_component(AttributesComponent)
        if not attributes_component:
            return {}

        class AttributeAdapter:
            def __init__(self, attr_obj):
                self._attr = attr_obj

            @property
            def value(self) -> float:
                return float(self._attr.current_value)

            @value.setter
            def value(self, v: float) -> None:
                v = float(v)
                self._attr.current_value = max(0.0, min(v, self._attr.max_value))

            def __float__(self) -> float:
                return float(self._attr.current_value)

            def __int__(self) -> int:
                try:
                    return int(round(float(self._attr.current_value)))
                except Exception:
                    return 0

            def __repr__(self) -> str:
                return f"AttributeAdapter(value={self._attr.current_value})"

        return {name: AttributeAdapter(attr) for name, attr in attributes_component.attributes.items()}

    @property
    def attribute_points(self) -> int:
        attributes_component: AttributesComponent = self.component_manager.get_component(AttributesComponent)
        return attributes_component.attribute_points if attributes_component else 0

    @attribute_points.setter
    def attribute_points(self, value: int) -> None:
        attributes_component: AttributesComponent = self.component_manager.get_component(AttributesComponent)
        if attributes_component:
            attributes_component.attribute_points = max(0, int(value))
    def get_attribute(self, name: str) -> float:
        """Получить значение атрибута."""
        attributes = self.get_component('AttributesComponent')
        return attributes.get_attribute_value(name) if attributes else 0.0
    
    def set_attribute_base(self, name: str, value: float) -> None:
        """Установить базовое значение атрибута."""
        attributes = self.get_component('AttributesComponent')
        if attributes:
            attributes.set_attribute_base(name, value)
    
    def has_attribute(self, name: str) -> bool:
        """Проверить, есть ли атрибут."""
        attributes = self.get_component('AttributesComponent')
        return attributes.has_attribute(name) if attributes else False
    
    def add_attribute_bonus(self, name: str, source: str, value: float) -> None:
        """Добавить бонус к атрибуту."""
        attributes = self.get_component('AttributesComponent')
        if attributes:
            attributes.add_attribute_bonus(name, source, value)
    
    def remove_attribute_bonus(self, name: str, source: str) -> None:
        """Убрать бонус от атрибута."""
        attributes = self.get_component('AttributesComponent')
        if attributes:
            attributes.remove_attribute_bonus(name, source)

    # Инвентарь и экипировка (через InventoryComponent)
    @property
    def inventory(self) -> List[Dict[str, Any]]:
        inv: InventoryComponent = self.component_manager.get_component(InventoryComponent)
        return inv.inventory if inv else []

    @inventory.setter
    def inventory(self, items: List[Dict[str, Any]]) -> None:
        inv: InventoryComponent = self.component_manager.get_component(InventoryComponent)
        if inv and isinstance(items, list):
            inv.inventory = items

    @property
    def equipment(self) -> Dict[str, Optional[Dict[str, Any]]]:
        inv: InventoryComponent = self.component_manager.get_component(InventoryComponent)
        return inv.equipment if inv else {}

    @equipment.setter
    def equipment(self, eq: Dict[str, Optional[Dict[str, Any]]]) -> None:
        inv: InventoryComponent = self.component_manager.get_component(InventoryComponent)
        if inv and isinstance(eq, dict):
            inv.equipment = eq
    
    def invest_attribute_point(self, name: str) -> bool:
        """Инвестировать очко атрибута."""
        attributes = self.get_component('AttributesComponent')
        return attributes.invest_attribute_point(name) if attributes else False
    
    def gain_attribute_points(self, amount: int) -> None:
        """Получить очки атрибутов."""
        attributes = self.get_component('AttributesComponent')
        if attributes:
            attributes.gain_attribute_points(amount)
    
    # Методы для работы с боевыми характеристиками (через CombatStatsComponent)
    def get_health(self) -> float:
        """Получить здоровье."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.stats.health if combat_stats else 0.0

    @property
    def health(self) -> float:
        return self.get_health()

    @health.setter
    def health(self, value: float) -> None:
        combat_stats = self.get_component('CombatStatsComponent')
        if combat_stats:
            combat_stats.stats.health = max(0.0, min(float(value), combat_stats.stats.max_health))
    
    def get_max_health(self) -> float:
        """Получить максимальное здоровье."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.stats.max_health if combat_stats else 0.0

    @property
    def max_health(self) -> float:
        return self.get_max_health()
    
    def get_mana(self) -> float:
        """Получить ману."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.stats.mana if combat_stats else 0.0

    @property
    def mana(self) -> float:
        return self.get_mana()

    @mana.setter
    def mana(self, value: float) -> None:
        combat_stats = self.get_component('CombatStatsComponent')
        if combat_stats:
            combat_stats.stats.mana = max(0.0, min(float(value), combat_stats.stats.max_mana))
    
    def get_max_mana(self) -> float:
        """Получить максимальную ману."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.stats.max_mana if combat_stats else 0.0

    @property
    def max_mana(self) -> float:
        return self.get_max_mana()
    
    def get_stamina(self) -> float:
        """Получить выносливость."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.stats.stamina if combat_stats else 0.0

    @property
    def stamina(self) -> float:
        return self.get_stamina()

    @stamina.setter
    def stamina(self, value: float) -> None:
        combat_stats = self.get_component('CombatStatsComponent')
        if combat_stats:
            combat_stats.stats.stamina = max(0.0, min(float(value), combat_stats.stats.max_stamina))
    
    def get_max_stamina(self) -> float:
        """Получить максимальную выносливость."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.stats.max_stamina if combat_stats else 0.0

    @property
    def max_stamina(self) -> float:
        return self.get_max_stamina()

    @property
    def combat_stats(self) -> Dict[str, Any]:
        """Dict-представление боевых статов для совместимости со старым кодом."""
        comp = self.component_manager.get_component(CombatStatsComponent)
        if not comp:
            return {}
        if self._combat_stats_view is None:
            self._combat_stats_view = _CombatStatsDictView(comp)
        return self._combat_stats_view

    @property
    def attack_cooldown(self) -> float:
        comp = self.component_manager.get_component(CombatStatsComponent)
        return comp.attack_cooldown if comp else 0.0

    @attack_cooldown.setter
    def attack_cooldown(self, value: float) -> None:
        comp = self.component_manager.get_component(CombatStatsComponent)
        if comp:
            comp.attack_cooldown = max(0.0, float(value))

    # Адаптеры для основных боевых полей, чтобы эффекты могли их изменять напрямую
    @property
    def movement_speed(self) -> float:
        comp = self.component_manager.get_component(CombatStatsComponent)
        return comp.stats.movement_speed if comp else 0.0

    @movement_speed.setter
    def movement_speed(self, value: float) -> None:
        comp = self.component_manager.get_component(CombatStatsComponent)
        if comp:
            comp.stats.movement_speed = float(value)

    @property
    def damage_output(self) -> float:
        comp = self.component_manager.get_component(CombatStatsComponent)
        return comp.stats.damage_output if comp else 0.0

    @damage_output.setter
    def damage_output(self, value: float) -> None:
        comp = self.component_manager.get_component(CombatStatsComponent)
        if comp:
            comp.stats.damage_output = float(value)

    @property
    def defense(self) -> float:
        comp = self.component_manager.get_component(CombatStatsComponent)
        return comp.stats.defense if comp else 0.0

    @defense.setter
    def defense(self, value: float) -> None:
        comp = self.component_manager.get_component(CombatStatsComponent)
        if comp:
            comp.stats.defense = float(value)

    @property
    def attack_speed(self) -> float:
        comp = self.component_manager.get_component(CombatStatsComponent)
        return comp.stats.attack_speed if comp else 1.0

    @attack_speed.setter
    def attack_speed(self, value: float) -> None:
        comp = self.component_manager.get_component(CombatStatsComponent)
        if comp:
            comp.stats.attack_speed = float(value)

    @property
    def critical_chance(self) -> float:
        comp = self.component_manager.get_component(CombatStatsComponent)
        return comp.stats.critical_chance if comp else 0.0

    @critical_chance.setter
    def critical_chance(self, value: float) -> None:
        comp = self.component_manager.get_component(CombatStatsComponent)
        if comp:
            comp.stats.critical_chance = float(value)

    @property
    def critical_multiplier(self) -> float:
        comp = self.component_manager.get_component(CombatStatsComponent)
        return comp.stats.critical_multiplier if comp else 1.0

    @critical_multiplier.setter
    def critical_multiplier(self, value: float) -> None:
        comp = self.component_manager.get_component(CombatStatsComponent)
        if comp:
            comp.stats.critical_multiplier = float(value)

    # Сопротивления и универсальные поля
    def _get_resist(self, field: str) -> float:
        comp = self.component_manager.get_component(CombatStatsComponent)
        return getattr(comp.stats, field) if comp and hasattr(comp.stats, field) else 0.0

    def _set_resist(self, field: str, value: float) -> None:
        comp = self.component_manager.get_component(CombatStatsComponent)
        if comp and hasattr(comp.stats, field):
            setattr(comp.stats, field, float(value))

    @property
    def all_resist(self) -> float:
        return self._get_resist("all_resist")

    @all_resist.setter
    def all_resist(self, value: float) -> None:
        self._set_resist("all_resist", value)

    @property
    def physical_resist(self) -> float:
        return self._get_resist("physical_resist")

    @physical_resist.setter
    def physical_resist(self, value: float) -> None:
        self._set_resist("physical_resist", value)

    @property
    def fire_resist(self) -> float:
        return self._get_resist("fire_resist")

    @fire_resist.setter
    def fire_resist(self, value: float) -> None:
        self._set_resist("fire_resist", value)

    @property
    def ice_resist(self) -> float:
        return self._get_resist("ice_resist")

    @ice_resist.setter
    def ice_resist(self, value: float) -> None:
        self._set_resist("ice_resist", value)

    @property
    def lightning_resist(self) -> float:
        return self._get_resist("lightning_resist")

    @lightning_resist.setter
    def lightning_resist(self, value: float) -> None:
        self._set_resist("lightning_resist", value)

    @property
    def poison_resist(self) -> float:
        return self._get_resist("poison_resist")

    @poison_resist.setter
    def poison_resist(self, value: float) -> None:
        self._set_resist("poison_resist", value)

    @property
    def magic_resist(self) -> float:
        return self._get_resist("magic_resist")

    @magic_resist.setter
    def magic_resist(self, value: float) -> None:
        self._set_resist("magic_resist", value)

    @property
    def holy_resist(self) -> float:
        return self._get_resist("holy_resist")

    @holy_resist.setter
    def holy_resist(self, value: float) -> None:
        self._set_resist("holy_resist", value)

    @property
    def dark_resist(self) -> float:
        return self._get_resist("dark_resist")

    @dark_resist.setter
    def dark_resist(self, value: float) -> None:
        self._set_resist("dark_resist", value)
    
    def take_damage(self, damage: float, damage_type: str = "physical") -> float:
        """Получить урон. Поддерживает как число, так и damage_report словарь."""
        combat_stats = self.get_component('CombatStatsComponent')
        if not combat_stats:
            return 0.0

        # Совместимость с отчётом урона
        if isinstance(damage, dict):
            total = float(damage.get('total', 0) or 0)
            old = combat_stats.stats.health
            combat_stats.stats.health = max(0.0, combat_stats.stats.health - total)
            if combat_stats.is_dead():
                self.die()
            return max(0.0, old - combat_stats.stats.health)

        # Базовая обработка урона компонентом
        actual_damage = combat_stats.take_damage(float(damage), damage_type)
        if combat_stats.is_dead():
            self.die()
        return actual_damage
    
    def heal(self, amount: float) -> float:
        """Восстановить здоровье."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.heal(amount) if combat_stats else 0.0
    
    def restore_mana(self, amount: float) -> float:
        """Восстановить ману."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.restore_mana(amount) if combat_stats else 0.0
    
    def restore_stamina(self, amount: float) -> float:
        """Восстановить выносливость."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.restore_stamina(amount) if combat_stats else 0.0
    
    def can_attack(self) -> bool:
        """Может ли сущность атаковать."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.can_attack() if combat_stats else False
    
    def start_attack_cooldown(self) -> None:
        """Начать кулдаун атаки."""
        combat_stats = self.get_component('CombatStatsComponent')
        if combat_stats:
            combat_stats.start_attack_cooldown()
    
    def is_alive(self) -> bool:
        """Жива ли сущность."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.is_alive() if combat_stats else False
    
    def is_dead(self) -> bool:
        """Мертва ли сущность."""
        combat_stats = self.get_component('CombatStatsComponent')
        return combat_stats.is_dead() if combat_stats else True
    
    # Методы для работы с инвентарем (через InventoryComponent)
    def add_to_inventory(self, item: Dict[str, Any]) -> bool:
        """Добавить предмет в инвентарь."""
        inventory = self.get_component('InventoryComponent')
        return inventory.add_item(item) if inventory else False
    
    def remove_from_inventory(self, item: Dict[str, Any]) -> bool:
        """Убрать предмет из инвентаря."""
        inventory = self.get_component('InventoryComponent')
        return inventory.remove_item(item) if inventory else False
    
    def equip_item(self, item: Dict[str, Any], slot: str) -> bool:
        """Экипировать предмет."""
        inventory = self.get_component('InventoryComponent')
        return inventory.equip_item(item, slot) if inventory else False
    
    def unequip_item(self, slot: str) -> Optional[Dict[str, Any]]:
        """Снять предмет из слота."""
        inventory = self.get_component('InventoryComponent')
        return inventory.unequip_item(slot) if inventory else None
    
    def use_consumable(self, item: Dict[str, Any]) -> bool:
        """Использовать расходуемый предмет."""
        inventory = self.get_component('InventoryComponent')
        return inventory.use_consumable(item) if inventory else False
    
    # Методы для работы с опытом и уровнем
    def gain_experience(self, amount: int) -> None:
        """Получить опыт."""
        self.experience += amount
        while self.experience >= self.experience_to_next:
            self._level_up()
    
    def _level_up(self) -> None:
        """Повысить уровень."""
        self.experience -= self.experience_to_next
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * 1.5)
        
        # Даем очки атрибутов
        self.gain_attribute_points(5)
        
        # Увеличиваем характеристики
        self._increase_stats_on_level_up()
    
    def _increase_stats_on_level_up(self) -> None:
        """Увеличить характеристики при повышении уровня."""
        combat_stats = self.get_component('CombatStatsComponent')
        if combat_stats:
            # Увеличиваем здоровье и ману
            combat_stats.stats.max_health += 20
            combat_stats.stats.max_mana += 10
            combat_stats.stats.max_stamina += 15
            
            # Восстанавливаем до максимума
            combat_stats.stats.health = combat_stats.stats.max_health
            combat_stats.stats.mana = combat_stats.stats.max_mana
            combat_stats.stats.stamina = combat_stats.stats.max_stamina

    # Совместимость: перерасчет производных характеристик
    def update_derived_stats(self) -> None:
        """Обновить боевые характеристики на основе атрибутов и экипировки."""
        attributes: AttributesComponent = self.component_manager.get_component(AttributesComponent)
        combat: CombatStatsComponent = self.component_manager.get_component(CombatStatsComponent)
        inventory: InventoryComponent = self.component_manager.get_component(InventoryComponent)
        if not attributes or not combat:
            return

        strength = attributes.get_attribute_value("strength")
        dexterity = attributes.get_attribute_value("dexterity")
        intelligence = attributes.get_attribute_value("intelligence")
        vitality = attributes.get_attribute_value("vitality")
        endurance = attributes.get_attribute_value("endurance")

        # Ресурсы
        combat.stats.max_health = 100 + vitality * 10
        combat.stats.health = min(combat.stats.health, combat.stats.max_health)
        combat.stats.max_mana = 50 + intelligence * 5
        combat.stats.mana = min(combat.stats.mana, combat.stats.max_mana)
        combat.stats.max_stamina = 100 + endurance * 5
        combat.stats.stamina = min(combat.stats.stamina, combat.stats.max_stamina)

        # Урон и скорость атаки
        base_damage = 10 + strength * 2 + dexterity
        weapon_damage = 0.0
        weapon_attack_speed = None
        weapon_item = inventory.get_equipped_item("weapon") if inventory else None
        if weapon_item:
            if isinstance(weapon_item, dict):
                weapon_damage = float(weapon_item.get("base_damage", 0) or 0)
                weapon_attack_speed = weapon_item.get("attack_speed")
            else:
                try:
                    if hasattr(weapon_item, "damage_types"):
                        for dmg in getattr(weapon_item, "damage_types", []):
                            try:
                                if isinstance(dmg, dict):
                                    weapon_damage += float(dmg.get("value", 0) or 0)
                                else:
                                    weapon_damage += float(getattr(dmg, "value", 0) or 0)
                            except Exception:
                                pass
                    if hasattr(weapon_item, "attack_speed"):
                        weapon_attack_speed = float(getattr(weapon_item, "attack_speed", 1.0))
                except Exception:
                    pass

        combat.stats.damage_output = base_damage + weapon_damage
        attack_speed = combat.stats.attack_speed
        if weapon_attack_speed is not None:
            attack_speed = float(weapon_attack_speed)
        combat.stats.attack_speed = attack_speed

        # Защита
        defense = 5.0
        if inventory:
            for slot, item in inventory.equipment.items():
                if not item:
                    continue
                if isinstance(item, dict) and "defense" in item:
                    defense += float(item.get("defense", 0) or 0)
                elif hasattr(item, "defense"):
                    try:
                        defense += float(getattr(item, "defense", 0) or 0)
                    except Exception:
                        pass
        combat.stats.defense = defense
    
    def die(self) -> None:
        """Смерть сущности."""
        self.alive = False
        self._on_death()
    
    def _on_death(self) -> None:
        """Обработка смерти сущности."""
        pass
    
    def respawn(self, position: Tuple[float, float]) -> None:
        """Возрождение сущности."""
        self.alive = True
        self.set_position(*position)
        
        # Восстанавливаем характеристики
        combat_stats = self.get_component('CombatStatsComponent')
        if combat_stats:
            combat_stats.stats.health = combat_stats.stats.max_health
            combat_stats.stats.mana = combat_stats.stats.max_mana
            combat_stats.stats.stamina = combat_stats.stats.max_stamina
    
    # Реализация интерфейсов
    def update(self, delta_time: float) -> None:
        """Обновить сущность."""
        if not self.alive:
            return
        
        # Обновляем все компоненты
        self.component_manager.update_all(delta_time)
        
        # Обновляем специфичную логику сущности
        self._on_update(delta_time)
    
    def render(self, canvas, camera_position: Tuple[float, float]) -> None:
        """Отрисовать сущность."""
        if not self.alive:
            return
        
        self._on_render(canvas, camera_position)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализовать сущность в словарь."""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type.value,
            'level': self.level,
            'experience': self.experience,
            'experience_to_next': self.experience_to_next,
            'alive': self.alive,
            'components': self.component_manager.to_dict()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Загрузить сущность из словаря."""
        self.entity_id = data.get('entity_id', self.entity_id)
        self.entity_type = EntityType(data.get('entity_type', self.entity_type.value))
        self.level = data.get('level', 1)
        self.experience = data.get('experience', 0)
        self.experience_to_next = data.get('experience_to_next', 100)
        self.alive = data.get('alive', True)
        
        # Загружаем компоненты
        if 'components' in data:
            self.component_manager.from_dict(data['components'])
    
    # Абстрактные методы для переопределения
    def _on_update(self, delta_time: float) -> None:
        """Обновление специфичной логики сущности."""
        pass
    
    def _on_render(self, canvas, camera_position: Tuple[float, float]) -> None:
        """Отрисовка специфичной логики сущности."""
        pass

    # --- Эффекты и навыки (совместимость со старым API) ---
    def has_effect_tag(self, tag: str) -> bool:
        for eff in getattr(self, 'active_effects', []) or []:
            if tag in getattr(eff, 'tags', []):
                return True
        return False

    def add_effect(self, effect_id: str, effect_data: dict, stacks: int = 1) -> None:
        if not effect_data:
            return
        # Если уже есть такой эффект — увеличим стаки
        existing = None
        for eff in self.active_effects:
            if getattr(eff, 'id', None) == effect_id:
                existing = eff
                break
        if existing:
            existing.stacks = max(1, int(existing.stacks) + max(1, int(stacks)))
            return
        effect = Effect(effect_id, effect_data.get('tags', []), effect_data.get('modifiers', []))
        effect.stacks = max(1, int(stacks))
        effect.apply(self, True)
        self.active_effects.append(effect)

    def remove_effect(self, effect_id: str) -> None:
        for eff in list(self.active_effects):
            if getattr(eff, 'id', None) == effect_id:
                eff.apply(self, False)
                self.active_effects.remove(eff)
                break

    def update_effects(self, delta_time: float) -> None:
        if not getattr(self, 'active_effects', None):
            return
        expired = []
        for eff in list(self.active_effects):
            eff.process_tick(self, delta_time)
            if eff.is_expired():
                expired.append(eff)
        for eff in expired:
            eff.apply(self, False)
            self.active_effects.remove(eff)

    def use_skill(self, ability_id: str) -> None:
        skills = getattr(self, 'skills', {})
        if ability_id not in skills:
            return
        skill_data = skills[ability_id]
        # Урон по цели, если есть ссылка на игрока
        target = getattr(self, 'player_ref', None)
        damage = float(skill_data.get('damage', 0) or 0)
        if target and getattr(target, 'alive', False) and damage > 0:
            target.take_damage({'total': damage, 'physical': damage, 'source': self})
        # Эффект от способности
        effect_id = skill_data.get('apply_effect')
        if effect_id and hasattr(self, 'effects_db') and effect_id in getattr(self, 'effects_db', {}):
            self.add_effect(effect_id, self.effects_db[effect_id])

    # --- Геометрия/движение совместимость ---
    def distance_to(self, target) -> float:
        """Если target — позиция (x, y) или сущность с позицией."""
        if isinstance(target, (tuple, list)) and len(target) >= 2:
            tx, ty = float(target[0]), float(target[1])
        elif hasattr(target, 'position'):
            pos = getattr(target, 'position')
            tx, ty = float(pos[0]), float(pos[1])
        else:
            return float('inf')
        cx, cy = self.get_position()
        dx = tx - cx
        dy = ty - cy
        return (dx * dx + dy * dy) ** 0.5

    # Свойство-алиас для id
    @property
    def id(self) -> str:
        return self.entity_id

    @id.setter
    def id(self, value: str) -> None:
        self.entity_id = value

"""
Система HUD - специализированный интерфейс для отображения игровых механик
"""

import time
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.core.architecture import BaseComponent, ComponentType, Priority


class HUDType(Enum):
    """Типы HUD"""
    MAIN_HUD = "main_hud"           # Основной HUD
    COMBAT_HUD = "combat_hud"       # Боевой HUD
    INVENTORY_HUD = "inventory_hud" # HUD инвентаря
    SKILLS_HUD = "skills_hud"       # HUD навыков
    EFFECTS_HUD = "effects_hud"     # HUD эффектов


class HUDLayout(Enum):
    """Расположения HUD элементов"""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    FULL_SCREEN = "full_screen"


@dataclass
class HUDElement:
    """Элемент HUD"""
    element_id: str
    element_type: str
    position: Tuple[float, float]
    size: Tuple[float, float]
    layout: HUDLayout
    visible: bool = True
    data: Dict[str, Any] = field(default_factory=dict)
    update_callback: Optional[Callable] = None


@dataclass
class HealthBar:
    """Полоса здоровья"""
    current: float = 100.0
    maximum: float = 100.0
    percentage: float = 100.0
    color: Tuple[float, float, float] = (0, 1, 0)  # RGB
    is_critical: bool = False
    show_shield: bool = False
    shield_value: float = 0.0


@dataclass
class ResourceBar:
    """Полоса ресурса"""
    current: float = 100.0
    maximum: float = 100.0
    percentage: float = 100.0
    color: Tuple[float, float, float] = (0, 0, 1)  # RGB
    resource_type: str = "mana"
    regeneration_rate: float = 0.0


@dataclass
class EffectIcon:
    """Иконка эффекта"""
    effect_id: str
    effect_name: str
    icon_path: str
    duration: float = 0.0
    remaining_time: float = 0.0
    is_positive: bool = True
    tooltip_text: str = ""


class HUDSystem(BaseComponent):
    """
    Система HUD
    Специализированная система для отображения игровых механик
    """
    
    def __init__(self):
        super().__init__(
            name="HUDSystem",
            component_type=ComponentType.SYSTEM,
            priority=Priority.MEDIUM
        )
        
        # HUD элементы
        self.hud_elements: Dict[str, HUDElement] = {}
        self.hud_layouts: Dict[HUDLayout, List[str]] = {}
        
        # Данные для отображения
        self.health_bars: Dict[str, HealthBar] = {}
        self.resource_bars: Dict[str, ResourceBar] = {}
        self.effect_icons: Dict[str, List[EffectIcon]] = {}
        
        # Настройки
        self.auto_update_interval = 0.1  # секунды
        self.last_update_time = 0.0
        self.show_debug_info = False
        
    def _on_initialize(self) -> bool:
        """Инициализация HUD системы"""
        try:
            # Создание базовых HUD элементов
            self._create_basic_hud()
            
            # Настройка обновлений
            self._setup_updates()
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка инициализации HUDSystem: {e}")
            return False
    
    def _create_basic_hud(self):
        """Создание базовых HUD элементов"""
        # Основной HUD
        self.create_main_hud()
        
        # Боевой HUD
        self.create_combat_hud()
        
        # HUD инвентаря
        self.create_inventory_hud()
        
        # HUD навыков
        self.create_skills_hud()
        
        # HUD эффектов
        self.create_effects_hud()
    
    def _setup_updates(self):
        """Настройка обновлений"""
        self.auto_update_interval = 0.1
    
    # Создание HUD элементов
    def create_main_hud(self):
        """Создать основной HUD"""
        # Полоса здоровья
        health_element = HUDElement(
            element_id="main_health_bar",
            element_type="health_bar",
            position=(50, 50),
            size=(200, 20),
            layout=HUDLayout.TOP_LEFT
        )
        self.hud_elements["main_health_bar"] = health_element
        
        # Полоса маны
        mana_element = HUDElement(
            element_id="main_mana_bar",
            element_type="resource_bar",
            position=(50, 80),
            size=(200, 20),
            layout=HUDLayout.TOP_LEFT
        )
        self.hud_elements["main_mana_bar"] = mana_element
        
        # Полоса энергии
        energy_element = HUDElement(
            element_id="main_energy_bar",
            element_type="resource_bar",
            position=(50, 110),
            size=(200, 20),
            layout=HUDLayout.TOP_LEFT
        )
        self.hud_elements["main_energy_bar"] = energy_element
        
        # Полоса выносливости
        stamina_element = HUDElement(
            element_id="main_stamina_bar",
            element_type="resource_bar",
            position=(50, 140),
            size=(200, 20),
            layout=HUDLayout.TOP_LEFT
        )
        self.hud_elements["main_stamina_bar"] = stamina_element
        
        # Добавляем в layout
        self._add_to_layout(HUDLayout.TOP_LEFT, ["main_health_bar", "main_mana_bar", "main_energy_bar", "main_stamina_bar"])
    
    def create_combat_hud(self):
        """Создать боевой HUD"""
        # Индикатор боевого состояния
        combat_state_element = HUDElement(
            element_id="combat_state_indicator",
            element_type="label",
            position=(50, 200),
            size=(150, 30),
            layout=HUDLayout.TOP_LEFT
        )
        self.hud_elements["combat_state_indicator"] = combat_state_element
        
        # Индикатор инициативы
        initiative_element = HUDElement(
            element_id="initiative_indicator",
            element_type="progress_bar",
            position=(50, 240),
            size=(150, 15),
            layout=HUDLayout.TOP_LEFT
        )
        self.hud_elements["initiative_indicator"] = initiative_element
        
        # Добавляем в layout
        self._add_to_layout(HUDLayout.TOP_LEFT, ["combat_state_indicator", "initiative_indicator"])
    
    def create_inventory_hud(self):
        """Создать HUD инвентаря"""
        # Счетчик предметов
        item_count_element = HUDElement(
            element_id="item_count",
            element_type="label",
            position=(50, 300),
            size=(150, 30),
            layout=HUDLayout.TOP_LEFT
        )
        self.hud_elements["item_count"] = item_count_element
        
        # Индикатор веса
        weight_element = HUDElement(
            element_id="weight_indicator",
            element_type="progress_bar",
            position=(50, 340),
            size=(150, 15),
            layout=HUDLayout.TOP_LEFT
        )
        self.hud_elements["weight_indicator"] = weight_element
        
        # Добавляем в layout
        self._add_to_layout(HUDLayout.TOP_LEFT, ["item_count", "weight_indicator"])
    
    def create_skills_hud(self):
        """Создать HUD навыков"""
        # Слоты навыков
        for i in range(4):
            skill_slot_element = HUDElement(
                element_id=f"skill_slot_{i}",
                element_type="skill_slot",
                position=(50 + i * 60, 400),
                size=(50, 50),
                layout=HUDLayout.TOP_LEFT
            )
            self.hud_elements[f"skill_slot_{i}"] = skill_slot_element
        
        # Добавляем в layout
        self._add_to_layout(HUDLayout.TOP_LEFT, ["skill_slot_0", "skill_slot_1", "skill_slot_2", "skill_slot_3"])
    
    def create_effects_hud(self):
        """Создать HUD эффектов"""
        # Панель активных эффектов
        effects_panel_element = HUDElement(
            element_id="effects_panel",
            element_type="panel",
            position=(50, 500),
            size=(200, 100),
            layout=HUDLayout.TOP_LEFT
        )
        self.hud_elements["effects_panel"] = effects_panel_element
        
        # Добавляем в layout
        self._add_to_layout(HUDLayout.TOP_LEFT, ["effects_panel"])
    
    def _add_to_layout(self, layout: HUDLayout, element_ids: List[str]):
        """Добавить элементы в layout"""
        if layout not in self.hud_layouts:
            self.hud_layouts[layout] = []
        
        for element_id in element_ids:
            if element_id not in self.hud_layouts[layout]:
                self.hud_layouts[layout].append(element_id)
    
    # Управление данными HUD
    def update_health_bar(self, entity_id: str, current: float, maximum: float, shield: float = 0.0):
        """Обновить полосу здоровья"""
        if entity_id not in self.health_bars:
            self.health_bars[entity_id] = HealthBar()
        
        health_bar = self.health_bars[entity_id]
        health_bar.current = current
        health_bar.maximum = maximum
        health_bar.percentage = (current / maximum) * 100.0 if maximum > 0 else 0.0
        health_bar.shield_value = shield
        health_bar.show_shield = shield > 0
        
        # Определяем цвет
        if health_bar.percentage > 50:
            health_bar.color = (0, 1, 0)  # Зеленый
            health_bar.is_critical = False
        elif health_bar.percentage > 25:
            health_bar.color = (1, 1, 0)  # Желтый
            health_bar.is_critical = False
        else:
            health_bar.color = (1, 0, 0)  # Красный
            health_bar.is_critical = True
        
        # Обновляем отображение
        self._update_health_display(entity_id, health_bar)
    
    def update_resource_bar(self, entity_id: str, resource_type: str, current: float, maximum: float, regeneration_rate: float = 0.0):
        """Обновить полосу ресурса"""
        bar_id = f"{entity_id}_{resource_type}"
        
        if bar_id not in self.resource_bars:
            self.resource_bars[bar_id] = ResourceBar()
        
        resource_bar = self.resource_bars[bar_id]
        resource_bar.current = current
        resource_bar.maximum = maximum
        resource_bar.percentage = (current / maximum) * 100.0 if maximum > 0 else 0.0
        resource_bar.resource_type = resource_type
        resource_bar.regeneration_rate = regeneration_rate
        
        # Определяем цвет по типу ресурса
        if resource_type == "mana":
            resource_bar.color = (0, 0, 1)  # Синий
        elif resource_type == "energy":
            resource_bar.color = (1, 0.5, 0)  # Оранжевый
        elif resource_type == "stamina":
            resource_bar.color = (0.5, 0.5, 0.5)  # Серый
        else:
            resource_bar.color = (1, 1, 1)  # Белый
        
        # Обновляем отображение
        self._update_resource_display(bar_id, resource_bar)
    
    def update_combat_state(self, entity_id: str, state: str, initiative: float = 0.0):
        """Обновить боевое состояние"""
        # Обновляем индикатор состояния
        state_element_id = f"{entity_id}_combat_state"
        if state_element_id in self.hud_elements:
            element = self.hud_elements[state_element_id]
            element.data["combat_state"] = state
            element.data["text"] = f"Бой: {state}"
        
        # Обновляем индикатор инициативы
        initiative_element_id = f"{entity_id}_initiative"
        if initiative_element_id in self.hud_elements:
            element = self.hud_elements[initiative_element_id]
            element.data["initiative"] = initiative
            element.data["percentage"] = min(100.0, initiative)
    
    def update_inventory_info(self, entity_id: str, item_count: int, max_items: int, weight: float, max_weight: float):
        """Обновить информацию об инвентаре"""
        # Обновляем счетчик предметов
        count_element_id = f"{entity_id}_item_count"
        if count_element_id in self.hud_elements:
            element = self.hud_elements[count_element_id]
            element.data["item_count"] = item_count
            element.data["max_items"] = max_items
            element.data["text"] = f"Предметы: {item_count}/{max_items}"
        
        # Обновляем индикатор веса
        weight_element_id = f"{entity_id}_weight"
        if weight_element_id in self.hud_elements:
            element = self.hud_elements[weight_element_id]
            element.data["current_weight"] = weight
            element.data["max_weight"] = max_weight
            element.data["percentage"] = (weight / max_weight) * 100.0 if max_weight > 0 else 0.0
            
            # Определяем цвет
            if element.data["percentage"] > 80:
                element.data["color"] = (1, 0, 0)  # Красный
            elif element.data["percentage"] > 60:
                element.data["color"] = (1, 1, 0)  # Желтый
            else:
                element.data["color"] = (0, 1, 0)  # Зеленый
    
    def update_skill_slots(self, entity_id: str, skills: List[Dict[str, Any]]):
        """Обновить слоты навыков"""
        for i, skill in enumerate(skills[:4]):  # Максимум 4 слота
            slot_element_id = f"{entity_id}_skill_slot_{i}"
            if slot_element_id in self.hud_elements:
                element = self.hud_elements[slot_element_id]
                element.data["skill_name"] = skill.get("name", "")
                element.data["skill_icon"] = skill.get("icon", "")
                element.data["cooldown"] = skill.get("cooldown", 0.0)
                element.data["can_use"] = skill.get("can_use", False)
                element.data["mana_cost"] = skill.get("mana_cost", 0)
    
    def update_effects(self, entity_id: str, effects: List[Dict[str, Any]]):
        """Обновить активные эффекты"""
        if entity_id not in self.effect_icons:
            self.effect_icons[entity_id] = []
        
        # Очищаем старые эффекты
        self.effect_icons[entity_id].clear()
        
        # Добавляем новые эффекты
        for effect in effects:
            effect_icon = EffectIcon(
                effect_id=effect.get("id", ""),
                effect_name=effect.get("name", ""),
                icon_path=effect.get("icon", ""),
                duration=effect.get("duration", 0.0),
                remaining_time=effect.get("remaining_time", 0.0),
                is_positive=effect.get("is_positive", True),
                tooltip_text=effect.get("tooltip", "")
            )
            self.effect_icons[entity_id].append(effect_icon)
        
        # Обновляем отображение
        self._update_effects_display(entity_id)
    
    # Обновление отображения
    def _update_health_display(self, entity_id: str, health_bar: HealthBar):
        """Обновить отображение полосы здоровья"""
        # Обновляем основной HUD
        main_health_id = "main_health_bar"
        if main_health_id in self.hud_elements:
            element = self.hud_elements[main_health_id]
            element.data["current"] = health_bar.current
            element.data["maximum"] = health_bar.maximum
            element.data["percentage"] = health_bar.percentage
            element.data["color"] = health_bar.color
            element.data["is_critical"] = health_bar.is_critical
            element.data["shield"] = health_bar.shield_value
            element.data["show_shield"] = health_bar.show_shield
    
    def _update_resource_display(self, bar_id: str, resource_bar: ResourceBar):
        """Обновить отображение полосы ресурса"""
        # Находим соответствующий элемент HUD
        for element_id, element in self.hud_elements.items():
            if element.element_type == "resource_bar" and resource_bar.resource_type in element_id:
                element.data["current"] = resource_bar.current
                element.data["maximum"] = resource_bar.maximum
                element.data["percentage"] = resource_bar.percentage
                element.data["color"] = resource_bar.color
                element.data["resource_type"] = resource_bar.resource_type
                element.data["regeneration_rate"] = resource_bar.regeneration_rate
                break
    
    def _update_effects_display(self, entity_id: str):
        """Обновить отображение эффектов"""
        effects_panel_id = "effects_panel"
        if effects_panel_id in self.hud_elements:
            element = self.hud_elements[effects_panel_id]
            element.data["effects"] = self.effect_icons.get(entity_id, [])
            element.data["effect_count"] = len(self.effect_icons.get(entity_id, []))
    
    # Управление видимостью
    def show_hud(self, hud_type: HUDType):
        """Показать HUD"""
        # Находим элементы данного типа HUD
        for element_id, element in self.hud_elements.items():
            if element.data.get("hud_type") == hud_type.value:
                element.visible = True
    
    def hide_hud(self, hud_type: HUDType):
        """Скрыть HUD"""
        # Находим элементы данного типа HUD
        for element_id, element in self.hud_elements.items():
            if element.data.get("hud_type") == hud_type.value:
                element.visible = False
    
    def toggle_hud(self, hud_type: HUDType):
        """Переключить видимость HUD"""
        # Проверяем текущее состояние
        visible = False
        for element_id, element in self.hud_elements.items():
            if element.data.get("hud_type") == hud_type.value:
                if element.visible:
                    visible = True
                    break
        
        if visible:
            self.hide_hud(hud_type)
        else:
            self.show_hud(hud_type)
    
    # Обновление системы
    def update(self, delta_time: float):
        """Обновить HUD систему"""
        current_time = time.time()
        
        # Проверяем, нужно ли обновлять HUD
        if current_time - self.last_update_time < self.auto_update_interval:
            return
        
        # Обновляем все видимые элементы
        for element_id, element in self.hud_elements.items():
            if element.visible:
                self._update_element(element, delta_time)
        
        self.last_update_time = current_time
    
    def _update_element(self, element: HUDElement, delta_time: float):
        """Обновить отдельный элемент"""
        # Обновляем прогресс-бары
        if element.element_type == "progress_bar":
            self._update_progress_bar_animation(element, delta_time)
        
        # Обновляем эффекты
        elif element.element_type == "panel" and "effects" in element.data:
            self._update_effects_animation(element, delta_time)
    
    def _update_progress_bar_animation(self, element: HUDElement, delta_time: float):
        """Обновить анимацию прогресс-бара"""
        # TODO: Плавная анимация изменения значений
        pass
    
    def _update_effects_animation(self, element: HUDElement, delta_time: float):
        """Обновить анимацию эффектов"""
        # TODO: Анимация эффектов (мерцание, пульсация)
        pass
    
    # Публичные методы
    def get_hud_element(self, element_id: str) -> Optional[HUDElement]:
        """Получить элемент HUD"""
        return self.hud_elements.get(element_id)
    
    def get_visible_elements(self) -> List[HUDElement]:
        """Получить все видимые элементы"""
        return [e for e in self.hud_elements.values() if e.visible]
    
    def get_layout_elements(self, layout: HUDLayout) -> List[HUDElement]:
        """Получить элементы по layout"""
        element_ids = self.hud_layouts.get(layout, [])
        return [self.hud_elements[eid] for eid in element_ids if eid in self.hud_elements]
    
    def set_debug_mode(self, enabled: bool):
        """Включить/выключить режим отладки"""
        self.show_debug_info = enabled
        
        # Показываем/скрываем отладочную информацию
        debug_element_id = "debug_info"
        if debug_element_id in self.hud_elements:
            self.hud_elements[debug_element_id].visible = enabled
    
    def refresh_all_hud(self):
        """Обновить весь HUD"""
        self.last_update_time = 0.0  # Принудительное обновление
        self.update(0.0)

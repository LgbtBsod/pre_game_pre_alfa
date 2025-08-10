"""
Система атрибутов сущностей.
Управляет базовыми характеристиками персонажей и их ростом.
Поддерживает шаблоны из JSON и индивидуальные атрибуты сущностей.
"""

import json
import logging
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AttributeTemplate:
    """Шаблон атрибута из JSON файла"""

    id: str
    name: str
    description: str
    base_value: float
    max_value: float
    growth_rate: float
    category: str
    effects: Dict[str, float] = field(default_factory=dict)


@dataclass
class Attribute:
    """Атрибут сущности с текущим значением, максимумом и скоростью роста"""

    current: float
    maximum: float
    growth_rate: float
    template_id: str = ""

    def increase(self, amount: float = 1.0) -> bool:
        """Увеличивает атрибут"""
        if self.current < self.maximum:
            self.current = min(self.current + amount, self.maximum)
            return True
        return False

    def set_base(self, value: float) -> None:
        """Устанавливает базовое значение"""
        self.current = max(0, min(value, self.maximum))

    def set_max(self, value: float) -> None:
        """Устанавливает максимальное значение"""
        self.maximum = max(0, value)
        self.current = min(self.current, self.maximum)

    def get_percentage(self) -> float:
        """Возвращает процент заполнения атрибута"""
        return self.current / self.maximum if self.maximum > 0 else 0.0


class AttributeTemplateManager:
    """Менеджер шаблонов атрибутов из JSON"""

    def __init__(self):
        self.templates: Dict[str, AttributeTemplate] = {}
        self._load_templates()

    def _load_templates(self):
        """Загружает шаблоны атрибутов из базы данных"""
        try:
            import sqlite3

            db_path = Path("data/game_data.db")
            if db_path.exists():
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM attributes")
                    rows = cursor.fetchall()

                    for row in rows:
                        try:
                            # Создаем шаблон из данных БД
                            template = AttributeTemplate(
                                id=row[0],
                                name=row[1],
                                description=row[2] or "",
                                base_value=row[3] or 10.0,
                                max_value=row[4] or 100.0,
                                growth_rate=row[5] or 1.0,
                                category=row[6] or "physical",
                                effects=json.loads(row[7]) if row[7] else {},
                            )
                            self.templates[template.id] = template
                        except Exception as e:
                            logger.warning(
                                f"Ошибка загрузки шаблона атрибута {row[0]}: {e}"
                            )
                            continue

                logger.info(f"Загружено {len(self.templates)} шаблонов атрибутов из БД")
            else:
                logger.warning("База данных не найдена, создаем стандартные шаблоны")
                self._create_default_templates()
        except Exception as e:
            logger.error(f"Ошибка загрузки шаблонов атрибутов: {e}")
            self._create_default_templates()

    def _create_default_templates(self):
        """Создает стандартные шаблоны атрибутов"""
        default_templates = {
            "str_001": AttributeTemplate(
                "str_001",
                "Сила",
                "Увеличивает физический урон",
                10.0,
                100.0,
                1.0,
                "physical",
                {"damage_output": 2.0},
            ),
            "dex_001": AttributeTemplate(
                "dex_001",
                "Ловкость",
                "Увеличивает точность",
                10.0,
                100.0,
                1.0,
                "physical",
                {"critical_chance": 0.01},
            ),
            "int_001": AttributeTemplate(
                "int_001",
                "Интеллект",
                "Увеличивает магический урон",
                10.0,
                100.0,
                1.0,
                "magical",
                {"magic_damage": 2.0},
            ),
            "vit_001": AttributeTemplate(
                "vit_001",
                "Живучесть",
                "Увеличивает здоровье",
                10.0,
                100.0,
                1.0,
                "survival",
                {"max_health": 20.0},
            ),
            "end_001": AttributeTemplate(
                "end_001",
                "Выносливость",
                "Увеличивает выносливость",
                10.0,
                100.0,
                1.0,
                "survival",
                {"max_stamina": 15.0},
            ),
            "fai_001": AttributeTemplate(
                "fai_001",
                "Вера",
                "Увеличивает священную магию",
                10.0,
                100.0,
                1.0,
                "magical",
                {"holy_damage": 2.0},
            ),
            "luc_001": AttributeTemplate(
                "luc_001",
                "Удача",
                "Увеличивает критический шанс",
                10.0,
                100.0,
                1.0,
                "utility",
                {"critical_chance": 0.005},
            ),
        }
        self.templates.update(default_templates)
        logger.info("Созданы стандартные шаблоны атрибутов")

    def get_template(self, template_id: str) -> Optional[AttributeTemplate]:
        """Получает шаблон атрибута по ID"""
        return self.templates.get(template_id)

    def get_all_templates(self) -> Dict[str, AttributeTemplate]:
        """Получает все шаблоны атрибутов"""
        return self.templates.copy()

    def create_attribute_from_template(
        self, template_id: str, level: int = 1
    ) -> Optional[Attribute]:
        """Создает атрибут на основе шаблона"""
        template = self.get_template(template_id)
        if template:
            # Уровень влияет на базовое значение
            base_value = template.base_value + (template.growth_rate * (level - 1))
            return Attribute(
                current=base_value,
                maximum=template.max_value,
                growth_rate=template.growth_rate,
                template_id=template_id,
            )
        return None


class AttributeManager:
    """Менеджер атрибутов сущности"""

    def __init__(self, entity_id: str = ""):
        self.entity_id = entity_id
        self.attributes: Dict[str, Attribute] = {}
        self.attribute_points = 0
        self.template_manager = AttributeTemplateManager()

    def initialize_from_templates(self, template_ids: Dict[str, float] = None):
        """Инициализирует атрибуты из шаблонов"""
        if template_ids is None:
            # Используем стандартные атрибуты
            template_ids = {
                "str_001": 10.0,
                "dex_001": 10.0,
                "int_001": 10.0,
                "vit_001": 10.0,
                "end_001": 10.0,
                "fai_001": 10.0,
                "luc_001": 10.0,
            }

        for template_id, base_value in template_ids.items():
            attr = self.template_manager.create_attribute_from_template(template_id)
            if attr:
                attr.set_base(base_value)
                self.attributes[template_id] = attr

    def initialize_default_attributes(self):
        """Инициализирует стандартные атрибуты (для обратной совместимости)"""
        self.initialize_from_templates()

    def get_attribute(self, name: str) -> Optional[Attribute]:
        """Получает атрибут по имени"""
        return self.attributes.get(name)

    def get_attribute_value(self, name: str) -> float:
        """Получает текущее значение атрибута"""
        attr = self.get_attribute(name)
        return attr.current if attr else 0.0

    def get_attribute_max(self, name: str) -> float:
        """Получает максимальное значение атрибута"""
        attr = self.get_attribute(name)
        return attr.maximum if attr else 0.0

    def get_attribute_growth(self, name: str) -> float:
        """Получает скорость роста атрибута"""
        attr = self.get_attribute(name)
        return attr.growth_rate if attr else 0.0

    def set_attribute_base(self, name: str, value: float) -> None:
        """Устанавливает базовое значение атрибута"""
        if name in self.attributes:
            self.attributes[name].set_base(value)
        else:
            # Создаем новый атрибут с базовыми значениями
            self.attributes[name] = Attribute(value, value, 1.0, name)

    def set_attribute_max(self, name: str, value: float) -> None:
        """Устанавливает максимальное значение атрибута"""
        if name in self.attributes:
            self.attributes[name].set_max(value)
        else:
            self.attributes[name] = Attribute(0, value, 1.0, name)

    def increase_attribute(self, name: str, amount: float = 1.0) -> bool:
        """Увеличивает атрибут"""
        if name in self.attributes:
            return self.attributes[name].increase(amount)
        return False

    def has_attribute(self, name: str) -> bool:
        """Проверяет наличие атрибута"""
        return name in self.attributes

    def spend_attribute_point(self, attribute_name: str) -> bool:
        """Тратит очко атрибута"""
        if self.attribute_points > 0 and self.has_attribute(attribute_name):
            if self.increase_attribute(attribute_name, 1.0):
                self.attribute_points -= 1
                return True
        return False

    def get_all_attributes(self) -> Dict[str, Attribute]:
        """Получает все атрибуты"""
        return self.attributes.copy()

    def get_attribute_summary(self) -> Dict[str, Dict[str, float]]:
        """Получает сводку всех атрибутов"""
        summary = {}
        for name, attr in self.attributes.items():
            summary[name] = {
                "current": attr.current,
                "maximum": attr.maximum,
                "growth_rate": attr.growth_rate,
                "template_id": attr.template_id,
            }
        return summary

    def get_effects_from_attributes(self) -> Dict[str, float]:
        """Получает все эффекты от атрибутов"""
        effects = {}
        for attr_id, attr in self.attributes.items():
            template = self.template_manager.get_template(attr_id)
            if template:
                for effect_name, effect_value in template.effects.items():
                    if effect_name in effects:
                        effects[effect_name] += effect_value * attr.current
                    else:
                        effects[effect_name] = effect_value * attr.current
        return effects

    def save_to_dict(self) -> Dict[str, Any]:
        """Сохраняет атрибуты в словарь для БД/JSON"""
        return {
            "entity_id": self.entity_id,
            "attribute_points": self.attribute_points,
            "attributes": self.get_attribute_summary(),
        }

    def load_from_dict(self, data: Dict[str, Any]):
        """Загружает атрибуты из словаря"""
        self.entity_id = data.get("entity_id", "")
        self.attribute_points = data.get("attribute_points", 0)

        attributes_data = data.get("attributes", {})
        for attr_id, attr_data in attributes_data.items():
            attr = Attribute(
                current=attr_data["current"],
                maximum=attr_data["maximum"],
                growth_rate=attr_data["growth_rate"],
                template_id=attr_data.get("template_id", attr_id),
            )
            self.attributes[attr_id] = attr

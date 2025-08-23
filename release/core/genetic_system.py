"""
Генетическая система с риском мутаций и генетическими аномалиями.
Управляет генами, их комбинациями и эволюционными изменениями.
"""

import random
import uuid
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

from .effect_system import EffectCode, EffectDatabase

logger = logging.getLogger(__name__)


class GeneCode(Enum):
    """Кодовые идентификаторы генов"""
    # Базовые гены
    HYPER_METABOLISM = "GENE_001"
    REGENERATION = "GENE_002"
    ACID_BLOOD = "GENE_003"
    ADAPTIVE_SKIN = "GENE_004"
    PHOTOSYNTHESIS = "GENE_005"
    ELECTRIC_ORGANS = "GENE_006"
    VENOM_GLANDS = "GENE_007"
    CRYSTAL_BONES = "GENE_008"
    PLASMA_HEART = "GENE_009"
    QUANTUM_BRAIN = "GENE_010"
    
    # Эволюционные гены
    EVOLUTION_ACCELERATOR = "GENE_101"
    MUTATION_RESISTANCE = "GENE_102"
    GENE_STABILITY = "GENE_103"
    ADAPTIVE_LEARNING = "GENE_104"
    
    # Специальные гены
    SYMBIOTIC_BOND = "GENE_201"
    ECOLOGICAL_HARMONY = "GENE_202"
    COSMIC_RESONANCE = "GENE_203"


class MutationType(Enum):
    """Типы мутаций"""
    POSITIVE = "positive"      # Полезная мутация
    NEGATIVE = "negative"      # Вредная мутация
    NEUTRAL = "neutral"        # Нейтральная мутация
    CHIMERA = "chimera"        # Химера (непредсказуемая)
    REGRESSION = "regression"  # Регрессия (деградация)


@dataclass
class Gene:
    """Ген с кодовым идентификатором"""
    code: str
    name: str
    description: str
    rarity: float  # Редкость гена (0.0 - 1.0)
    stability: float  # Стабильность гена (0.0 - 1.0)
    effects: List[str] = field(default_factory=list)  # Список эффектов
    requirements: List[str] = field(default_factory=list)  # Требования для активации
    conflicts: List[str] = field(default_factory=list)  # Конфликтующие гены
    
    def __post_init__(self):
        if not self.effects:
            # Автоматическое добавление эффекта по коду гена
            self.effects = [self.code]


@dataclass
class GeneticAnomaly:
    """Генетическая аномалия"""
    anomaly_type: MutationType
    description: str
    effects: List[str]
    duration: float = 0.0  # 0.0 = постоянная
    severity: float = 1.0  # Сила аномалии (0.0 - 2.0)


class AdvancedGeneticSystem:
    """Продвинутая генетическая система"""
    
    def __init__(self, effect_db: EffectDatabase):
        self.effect_db = effect_db
        self.unlocked_genes: List[str] = []
        self.active_genes: List[str] = []
        self.gene_slots: int = 3
        self.mutation_resistance: float = 0.0
        self.generation: int = 1
        self.evolution_path: List[Dict[str, Any]] = []
        
        # Комбинации генов
        self.gene_combos = {
            (GeneCode.HYPER_METABOLISM.value, GeneCode.REGENERATION.value): {
                "result": EffectCode.REGENERATION.value,
                "chance": 0.8,
                "description": "Ускоренный метаболизм + Регенерация = Сверхбыстрое восстановление"
            },
            (GeneCode.ACID_BLOOD.value, GeneCode.ADAPTIVE_SKIN.value): {
                "result": EffectCode.ACID_BLOOD.value,
                "chance": 0.7,
                "description": "Кислотная кровь + Адаптивная кожа = Кислотная броня"
            },
            (GeneCode.PHOTOSYNTHESIS.value, GeneCode.ELECTRIC_ORGANS.value): {
                "result": "GENE_COMBO_001",
                "chance": 0.6,
                "description": "Фотосинтез + Электрические органы = Биоэлектрический синтез"
            },
            (GeneCode.VENOM_GLANDS.value, GeneCode.CRYSTAL_BONES.value): {
                "result": "GENE_COMBO_002",
                "chance": 0.5,
                "description": "Ядовитые железы + Кристальные кости = Кристаллический яд"
            }
        }
        
        # Генетические аномалии
        self.anomalies = {
            "chimera": {
                "chance": 0.15,  # 15% шанс химеры
                "effects": [
                    EffectCode.DAMAGE_BOOST.value,
                    EffectCode.SPEED_BOOST.value,
                    EffectCode.DEFENSE_BOOST.value
                ],
                "description": "Химера: непредсказуемая комбинация генов"
            },
            "regression": {
                "chance": 0.05,  # 5% шанс регрессии
                "effects": [
                    "GENE_REGRESSION_001",  # Снижение характеристик
                    "GENE_REGRESSION_002"   # Нестабильность
                ],
                "description": "Регрессия: деградация генетического материала"
            }
        }
        
        # Инициализация базовых генов
        self._init_base_genes()
    
    def _init_base_genes(self):
        """Инициализация базовых генов"""
        base_genes = [
            Gene(GeneCode.HYPER_METABOLISM.value, "Гиперметаболизм", 
                 "Ускоренный обмен веществ", 0.3, 0.8),
            Gene(GeneCode.REGENERATION.value, "Регенерация", 
                 "Быстрое восстановление", 0.4, 0.9),
            Gene(GeneCode.ACID_BLOOD.value, "Кислотная кровь", 
                 "Кровь с кислотными свойствами", 0.2, 0.6),
            Gene(GeneCode.ADAPTIVE_SKIN.value, "Адаптивная кожа", 
                 "Кожа, адаптирующаяся к среде", 0.5, 0.7),
            Gene(GeneCode.PHOTOSYNTHESIS.value, "Фотосинтез", 
                 "Поглощение энергии света", 0.1, 0.5),
            Gene(GeneCode.ELECTRIC_ORGANS.value, "Электрические органы", 
                 "Генерация электричества", 0.15, 0.4),
        ]
        
        # Добавление генов в систему
        for gene in base_genes:
            self._add_gene(gene)
    
    def _add_gene(self, gene: Gene):
        """Добавление гена в систему"""
        # Здесь можно добавить логику сохранения генов в БД
        pass
    
    def combine_genes(self, gene_code1: str, gene_code2: str) -> Optional[Dict[str, Any]]:
        """Комбинирование двух генов"""
        # Проверка на генетическую аномалию
        anomaly_chance = random.random()
        if anomaly_chance < 0.25:  # 25% шанс аномалии
            anomaly_type = self._determine_anomaly_type()
            
            if anomaly_type == MutationType.CHIMERA:
                return self._create_chimera(gene_code1, gene_code2)
            elif anomaly_type == MutationType.REGRESSION:
                return self._create_regression(gene_code1, gene_code2)
        
        # Стандартная комбинация
        combo_key = (gene_code1, gene_code2)
        reverse_key = (gene_code2, gene_code1)
        
        combo_data = self.gene_combos.get(combo_key) or self.gene_combos.get(reverse_key)
        
        if combo_data and random.random() < combo_data["chance"]:
            return self._create_combo_effect(combo_data, gene_code1, gene_code2)
        
        # Простая комбинация без специального эффекта
        return self._create_simple_combo(gene_code1, gene_code2)
    
    def _determine_anomaly_type(self) -> MutationType:
        """Определение типа аномалии"""
        rand = random.random()
        
        if rand < self.anomalies["chimera"]["chance"]:
            return MutationType.CHIMERA
        elif rand < self.anomalies["chimera"]["chance"] + self.anomalies["regression"]["chance"]:
            return MutationType.REGRESSION
        else:
            return MutationType.NEUTRAL
    
    def _create_chimera(self, gene_code1: str, gene_code2: str) -> Dict[str, Any]:
        """Создание химеры"""
        # Выбор случайного эффекта из доступных
        effect = random.choice(self.anomalies["chimera"]["effects"])
        
        return {
            "type": "chimera",
            "description": self.anomalies["chimera"]["description"],
            "effect": effect,
            "genes_used": [gene_code1, gene_code2],
            "severity": random.uniform(1.0, 2.0),
            "duration": random.uniform(30.0, 120.0)
        }
    
    def _create_regression(self, gene_code1: str, gene_code2: str) -> Dict[str, Any]:
        """Создание регрессии"""
        effect = random.choice(self.anomalies["regression"]["effects"])
        
        return {
            "type": "regression",
            "description": self.anomalies["regression"]["description"],
            "effect": effect,
            "genes_used": [gene_code1, gene_code2],
            "severity": random.uniform(0.5, 1.5),
            "duration": random.uniform(60.0, 300.0)
        }
    
    def _create_combo_effect(self, combo_data: Dict[str, Any], 
                            gene_code1: str, gene_code2: str) -> Dict[str, Any]:
        """Создание комбинированного эффекта"""
        return {
            "type": "combo",
            "description": combo_data["description"],
            "effect": combo_data["result"],
            "genes_used": [gene_code1, gene_code2],
            "chance": combo_data["chance"],
            "duration": 0.0  # Постоянный эффект
        }
    
    def _create_simple_combo(self, gene_code1: str, gene_code2: str) -> Dict[str, Any]:
        """Создание простой комбинации"""
        return {
            "type": "simple",
            "description": f"Комбинация {gene_code1} + {gene_code2}",
            "effects": [gene_code1, gene_code2],
            "genes_used": [gene_code1, gene_code2],
            "duration": 0.0
        }
    
    def unlock_gene(self, gene_code: str) -> bool:
        """Разблокировка гена"""
        if gene_code not in self.unlocked_genes:
            self.unlocked_genes.append(gene_code)
            logger.info(f"Разблокирован ген {gene_code}")
            return True
        return False
    
    def activate_gene(self, gene_code: str) -> bool:
        """Активация гена"""
        if gene_code in self.unlocked_genes and gene_code not in self.active_genes:
            if len(self.active_genes) < self.gene_slots:
                self.active_genes.append(gene_code)
                logger.info(f"Активирован ген {gene_code}")
                return True
            else:
                logger.warning("Нет свободных слотов для генов")
                return False
        return False
    
    def deactivate_gene(self, gene_code: str) -> bool:
        """Деактивация гена"""
        if gene_code in self.active_genes:
            self.active_genes.remove(gene_code)
            logger.info(f"Деактивирован ген {gene_code}")
            return True
        return False
    
    def evolve(self, evolution_data: Dict[str, Any]) -> bool:
        """Эволюция генетической системы"""
        try:
            # Увеличение поколения
            self.generation += 1
            
            # Запись в историю эволюции
            self.evolution_path.append({
                "generation": self.generation,
                "data": evolution_data,
                "timestamp": 0.0  # Здесь будет время игры
            })
            
            # Применение эволюционных бонусов
            if "gene_slots" in evolution_data:
                self.gene_slots = min(10, self.gene_slots + evolution_data["gene_slots"])
            
            if "mutation_resistance" in evolution_data:
                self.mutation_resistance = min(0.8, 
                    self.mutation_resistance + evolution_data["mutation_resistance"])
            
            if "starting_effects" in evolution_data:
                for effect_code in evolution_data["starting_effects"]:
                    self.unlock_gene(effect_code)
            
            logger.info(f"Генетическая система эволюционировала до поколения {self.generation}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка эволюции генетической системы: {e}")
            return False
    
    def get_evolution_bonus(self) -> Dict[str, Any]:
        """Расчёт бонуса за эволюцию"""
        bonus = {
            "gene_slots": min(2, 1 + len(self.unlocked_genes) // 5),
            "mutation_resistance": 0.05 * self.generation,
            "starting_effects": []
        }
        
        # Бонусы за стабильность
        if self.generation > 5:
            bonus["gene_stability"] = 0.1 * (self.generation - 5)
        
        # Бонусы за разнообразие генов
        if len(self.unlocked_genes) > 10:
            bonus["gene_diversity"] = 0.02 * len(self.unlocked_genes)
        
        return bonus
    
    def get_mutation_chance(self) -> float:
        """Расчёт шанса мутации"""
        base_chance = 0.25  # Базовый шанс 25%
        resistance = self.mutation_resistance
        return max(0.05, base_chance - resistance)
    
    def get_gene_stability(self, gene_code: str) -> float:
        """Получение стабильности гена"""
        # Здесь можно добавить логику расчёта стабильности
        return 0.8  # Базовая стабильность
    
    def get_active_effects(self) -> List[str]:
        """Получение активных эффектов от генов"""
        effects = []
        for gene_code in self.active_genes:
            # Получение эффекта гена из БД
            effect = self.effect_db.get_effect_by_code(gene_code)
            if effect:
                effects.append(effect.code)
        return effects
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """Получение истории эволюции"""
        return self.evolution_path.copy()
    
    def reset_generation(self):
        """Сброс к первому поколению"""
        self.generation = 1
        self.evolution_path.clear()
        logger.info("Генетическая система сброшена к первому поколению")
    
    def get_gene_info(self, gene_code: str) -> Optional[Dict[str, Any]]:
        """Получение информации о гене"""
        # Здесь можно добавить логику получения информации о гене
        return {
            "code": gene_code,
            "name": f"Ген {gene_code}",
            "description": f"Описание гена {gene_code}",
            "rarity": 0.5,
            "stability": 0.8
        }
    
    def update(self, delta_time: float):
        """Обновление генетической системы"""
        try:
            # Проверка стабильности активных генов
            for gene_code in self.active_genes[:]:  # Копия списка для безопасного удаления
                stability = self.get_gene_stability(gene_code)
                if stability < 0.3:  # Ген становится нестабильным
                    # Шанс деактивации нестабильного гена
                    if random.random() < 0.01 * delta_time:  # 1% в секунду
                        self.deactivate_gene(gene_code)
                        logger.warning(f"Нестабильный ген {gene_code} деактивирован")
            
            # Проверка возможности мутации
            mutation_chance = self.get_mutation_chance()
            if random.random() < mutation_chance * 0.001 * delta_time:  # Очень низкий шанс
                self._trigger_random_mutation()
                
        except Exception as e:
            logger.error(f"Ошибка обновления генетической системы: {e}")
    
    def _trigger_random_mutation(self):
        """Случайная мутация"""
        try:
            mutation_types = list(MutationType)
            mutation_type = random.choice(mutation_types)
            
            # Создание аномалии
            anomaly = GeneticAnomaly(
                anomaly_type=mutation_type,
                description=f"Случайная мутация типа {mutation_type.value}",
                effects=["random_effect"],
                duration=0.0,  # Постоянная
                severity=random.uniform(0.5, 1.5)
            )
            
            logger.info(f"Сработала случайная мутация: {mutation_type.value}")
            
        except Exception as e:
            logger.error(f"Ошибка случайной мутации: {e}")

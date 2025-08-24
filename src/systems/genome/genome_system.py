#!/usr/bin/env python3
"""
Система генома - управление генетической информацией сущностей
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from ...core.interfaces import ISystem, SystemPriority, SystemState
from ...core.constants import (
    GeneType, GeneRarity, StatType, BASE_STATS,
    PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class GeneSequence:
    """Последовательность генов"""
    sequence_id: str
    genes: List[str] = field(default_factory=list)
    length: int = 0
    complexity: float = 0.0
    stability: float = 1.0
    generation: int = 1

@dataclass
class GeneticTrait:
    """Генетический признак"""
    trait_id: str
    name: str
    description: str
    gene_sequence: str
    expression_level: float = 1.0
    dominant: bool = False
    inherited: bool = False
    mutation_rate: float = 0.01
    active: bool = True

@dataclass
class GenomeProfile:
    """Профиль генома сущности"""
    entity_id: str
    genome_id: str
    gene_sequences: List[GeneSequence] = field(default_factory=list)
    traits: List[GeneticTrait] = field(default_factory=list)
    mutation_count: int = 0
    recombination_count: int = 0
    last_update: float = field(default_factory=time.time)
    generation: int = 1

class GenomeSystem(ISystem):
    """Система управления геномом"""
    
    def __init__(self):
        self._system_name = "genome"
        self._system_priority = SystemPriority.HIGH
        self._system_state = SystemState.UNINITIALIZED
        self._dependencies = []
        
        # Профили геномов сущностей
        self.genome_profiles: Dict[str, GenomeProfile] = {}
        
        # Генетические шаблоны
        self.genetic_templates: Dict[str, Dict[str, Any]] = {}
        
        # История генетических изменений
        self.genetic_history: List[Dict[str, Any]] = []
        
        # Настройки системы
        self.system_settings = {
            'max_genes_per_entity': SYSTEM_LIMITS["max_genes_per_entity"],
            'mutation_rate': PROBABILITY_CONSTANTS["base_mutation_rate"],
            'recombination_rate': PROBABILITY_CONSTANTS["base_recombination_rate"],
            'gene_expression_threshold': 0.5,
            'genome_complexity_limit': 1000,
            'trait_activation_chance': 0.7
        }
        
        # Статистика системы
        self.system_stats = {
            'genomes_count': 0,
            'total_genes': 0,
            'mutations_occurred': 0,
            'recombinations_occurred': 0,
            'traits_activated': 0,
            'update_time': 0.0
        }
        
        logger.info("Система генома инициализирована")
    
    @property
    def system_name(self) -> str:
        return self._system_name
    
    @property
    def system_priority(self) -> SystemPriority:
        return self._system_priority
    
    @property
    def system_state(self) -> SystemState:
        return self._system_state
    
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    
    def initialize(self) -> bool:
        """Инициализация системы генома"""
        try:
            logger.info("Инициализация системы генома...")
            
            # Настраиваем систему
            self._setup_genome_system()
            
            # Загружаем генетические шаблоны
            self._load_genetic_templates()
            
            self._system_state = SystemState.READY
            logger.info("Система генома успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы генома: {e}")
            self._system_state = SystemState.ERROR
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы генома"""
        try:
            if self._system_state != SystemState.READY:
                return False
            
            start_time = time.time()
            
            # Обновляем экспрессию генов
            self._update_gene_expression(delta_time)
            
            # Проверяем мутации
            self._check_mutations(delta_time)
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы генома: {e}")
            return False
    
    def pause(self) -> bool:
        """Приостановка системы генома"""
        try:
            if self._system_state == SystemState.READY:
                self._system_state = SystemState.PAUSED
                logger.info("Система генома приостановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка приостановки системы генома: {e}")
            return False
    
    def resume(self) -> bool:
        """Возобновление системы генома"""
        try:
            if self._system_state == SystemState.PAUSED:
                self._system_state = SystemState.READY
                logger.info("Система генома возобновлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка возобновления системы генома: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Очистка системы генома"""
        try:
            logger.info("Очистка системы генома...")
            
            # Очищаем все данные
            self.genome_profiles.clear()
            self.genetic_templates.clear()
            self.genetic_history.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'genomes_count': 0,
                'total_genes': 0,
                'mutations_occurred': 0,
                'recombinations_occurred': 0,
                'traits_activated': 0,
                'update_time': 0.0
            }
            
            self._system_state = SystemState.DESTROYED
            logger.info("Система генома очищена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы генома: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'dependencies': self.dependencies,
            'genomes_count': len(self.genome_profiles),
            'genetic_templates': len(self.genetic_templates),
            'total_genes': self.system_stats['total_genes'],
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "entity_destroyed":
                return self._handle_entity_destroyed(event_data)
            elif event_type == "reproduction":
                return self._handle_reproduction(event_data)
            elif event_type == "environment_change":
                return self._handle_environment_change(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _setup_genome_system(self) -> None:
        """Настройка системы генома"""
        try:
            # Инициализируем базовые настройки
            logger.debug("Система генома настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему генома: {e}")
    
    def _load_genetic_templates(self) -> None:
        """Загрузка генетических шаблонов"""
        try:
            # Шаблоны для разных типов сущностей
            self.genetic_templates = {
                'basic': {
                    'gene_types': [GeneType.PHYSICAL, GeneType.MENTAL, GeneType.ENERGY],
                    'complexity_range': (10, 50),
                    'mutation_rate': 0.01,
                    'trait_count': 5
                },
                'advanced': {
                    'gene_types': [GeneType.PHYSICAL, GeneType.MENTAL, GeneType.ENERGY, GeneType.SPECIAL],
                    'complexity_range': (30, 100),
                    'mutation_rate': 0.015,
                    'trait_count': 8
                },
                'elite': {
                    'gene_types': [GeneType.PHYSICAL, GeneType.MENTAL, GeneType.ENERGY, GeneType.SPECIAL, GeneType.LEGENDARY],
                    'complexity_range': (80, 200),
                    'mutation_rate': 0.02,
                    'trait_count': 12
                }
            }
            
            logger.info(f"Загружено {len(self.genetic_templates)} генетических шаблонов")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки генетических шаблонов: {e}")
    
    def _update_gene_expression(self, delta_time: float) -> None:
        """Обновление экспрессии генов"""
        try:
            current_time = time.time()
            
            for entity_id, profile in self.genome_profiles.items():
                # Обновляем время последнего обновления
                profile.last_update = current_time
                
                # Обновляем экспрессию признаков
                for trait in profile.traits:
                    if trait.active:
                        # Случайные изменения экспрессии
                        expression_change = random.uniform(-0.05, 0.05)
                        trait.expression_level = max(0.0, min(2.0, trait.expression_level + expression_change))
                
        except Exception as e:
            logger.warning(f"Ошибка обновления экспрессии генов: {e}")
    
    def _check_mutations(self, delta_time: float) -> None:
        """Проверка мутаций"""
        try:
            for entity_id, profile in self.genome_profiles.items():
                # Проверяем мутации для каждого признака
                for trait in profile.traits:
                    if random.random() < trait.mutation_rate * delta_time:
                        self._trigger_trait_mutation(entity_id, trait)
                
                # Проверяем мутации последовательностей
                for sequence in profile.gene_sequences:
                    if random.random() < self.system_settings['mutation_rate'] * delta_time:
                        self._trigger_sequence_mutation(entity_id, sequence)
                
        except Exception as e:
            logger.warning(f"Ошибка проверки мутаций: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['genomes_count'] = len(self.genome_profiles)
            self.system_stats['total_genes'] = sum(len(profile.traits) for profile in self.genome_profiles.values())
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            genome_template = event_data.get('genome_template', 'basic')
            parent_genomes = event_data.get('parent_genomes', [])
            
            if entity_id:
                if parent_genomes:
                    return self.create_inherited_genome(entity_id, parent_genomes)
                else:
                    return self.create_genome_from_template(entity_id, genome_template)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                return self.destroy_genome(entity_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения сущности: {e}")
            return False
    
    def _handle_reproduction(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события размножения"""
        try:
            parent1_id = event_data.get('parent1_id')
            parent2_id = event_data.get('parent2_id')
            offspring_id = event_data.get('offspring_id')
            
            if parent1_id and parent2_id and offspring_id:
                return self.create_offspring_genome(offspring_id, parent1_id, parent2_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события размножения: {e}")
            return False
    
    def _handle_environment_change(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события изменения окружения"""
        try:
            environment_type = event_data.get('environment_type')
            affected_entities = event_data.get('affected_entities', [])
            
            if environment_type and affected_entities:
                # Адаптируем геномы к новому окружению
                for entity_id in affected_entities:
                    if entity_id in self.genome_profiles:
                        self._adapt_to_environment(entity_id, environment_type)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события изменения окружения: {e}")
            return False
    
    def create_genome_from_template(self, entity_id: str, template_name: str = 'basic') -> bool:
        """Создание генома из шаблона"""
        try:
            if entity_id in self.genome_profiles:
                logger.warning(f"Геном для сущности {entity_id} уже существует")
                return False
            
            if template_name not in self.genetic_templates:
                logger.warning(f"Генетический шаблон {template_name} не найден")
                template_name = 'basic'
            
            template = self.genetic_templates[template_name]
            
            # Создаем профиль генома
            profile = GenomeProfile(
                entity_id=entity_id,
                genome_id=f"genome_{entity_id}_{int(time.time() * 1000)}"
            )
            
            # Создаем последовательности генов
            for i in range(template['trait_count']):
                gene_type = random.choice(template['gene_types'])
                sequence = GeneSequence(
                    sequence_id=f"seq_{i}_{entity_id}",
                    genes=[f"gene_{j}_{gene_type.value}" for j in range(random.randint(5, 15))],
                    length=random.randint(5, 15),
                    complexity=random.uniform(*template['complexity_range']),
                    stability=random.uniform(0.8, 1.0),
                    generation=1
                )
                profile.gene_sequences.append(sequence)
            
            # Создаем генетические признаки
            for i in range(template['trait_count']):
                trait = GeneticTrait(
                    trait_id=f"trait_{i}_{entity_id}",
                    name=f"Признак {i+1}",
                    description=f"Автоматически сгенерированный признак {i+1}",
                    gene_sequence=profile.gene_sequences[i].sequence_id,
                    expression_level=random.uniform(0.5, 1.5),
                    dominant=random.random() < 0.3,
                    inherited=False,
                    mutation_rate=template['mutation_rate'],
                    active=random.random() < self.system_settings['trait_activation_chance']
                )
                profile.traits.append(trait)
            
            # Добавляем в систему
            self.genome_profiles[entity_id] = profile
            
            logger.info(f"Создан геном для сущности {entity_id} из шаблона {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания генома для {entity_id}: {e}")
            return False
    
    def create_inherited_genome(self, entity_id: str, parent_genomes: List[str]) -> bool:
        """Создание наследуемого генома"""
        try:
            if entity_id in self.genome_profiles:
                logger.warning(f"Геном для сущности {entity_id} уже существует")
                return False
            
            if not parent_genomes:
                logger.warning("Не указаны родительские геномы")
                return False
            
            # Получаем родительские профили
            parent_profiles = []
            for parent_id in parent_genomes:
                if parent_id in self.genome_profiles:
                    parent_profiles.append(self.genome_profiles[parent_id])
                else:
                    logger.warning(f"Родительский геном {parent_id} не найден")
            
            if not parent_profiles:
                logger.warning("Не найдено ни одного родительского генома")
                return self.create_genome_from_template(entity_id, 'basic')
            
            # Создаем профиль потомка
            profile = GenomeProfile(
                entity_id=entity_id,
                genome_id=f"genome_{entity_id}_{int(time.time() * 1000)}",
                generation=max(p.generation for p in parent_profiles) + 1
            )
            
            # Наследуем признаки от родителей
            for parent_profile in parent_profiles:
                for trait in parent_profile.traits:
                    if random.random() < 0.5:  # 50% шанс наследования
                        inherited_trait = GeneticTrait(
                            trait_id=f"inherited_{trait.trait_id}_{entity_id}",
                            name=trait.name,
                            description=trait.description,
                            gene_sequence=trait.gene_sequence,
                            expression_level=trait.expression_level * random.uniform(0.8, 1.2),
                            dominant=trait.dominant,
                            inherited=True,
                            mutation_rate=trait.mutation_rate,
                            active=trait.active
                        )
                        profile.traits.append(inherited_trait)
            
            # Создаем новые последовательности на основе родительских
            for parent_profile in parent_profiles:
                for sequence in parent_profile.gene_sequences:
                    if random.random() < 0.7:  # 70% шанс наследования последовательности
                        new_sequence = GeneSequence(
                            sequence_id=f"inherited_{sequence.sequence_id}_{entity_id}",
                            genes=sequence.genes.copy(),
                            length=sequence.length,
                            complexity=sequence.complexity * random.uniform(0.9, 1.1),
                            stability=sequence.stability * random.uniform(0.95, 1.05),
                            generation=profile.generation
                        )
                        profile.gene_sequences.append(new_sequence)
            
            # Добавляем в систему
            self.genome_profiles[entity_id] = profile
            
            logger.info(f"Создан наследуемый геном для {entity_id} от {len(parent_profiles)} родителей")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания наследуемого генома для {entity_id}: {e}")
            return False
    
    def create_offspring_genome(self, offspring_id: str, parent1_id: str, parent2_id: str) -> bool:
        """Создание генома потомка"""
        try:
            return self.create_inherited_genome(offspring_id, [parent1_id, parent2_id])
        except Exception as e:
            logger.error(f"Ошибка создания генома потомка {offspring_id}: {e}")
            return False
    
    def destroy_genome(self, entity_id: str) -> bool:
        """Уничтожение генома"""
        try:
            if entity_id not in self.genome_profiles:
                return False
            
            # Удаляем профиль
            del self.genome_profiles[entity_id]
            
            logger.info(f"Геном сущности {entity_id} уничтожен")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения генома {entity_id}: {e}")
            return False
    
    def _trigger_trait_mutation(self, entity_id: str, trait: GeneticTrait) -> None:
        """Запуск мутации признака"""
        try:
            # Создаем мутированный признак
            mutated_trait = GeneticTrait(
                trait_id=f"mutated_{trait.trait_id}",
                name=f"Мутированный {trait.name}",
                description=f"Мутированная версия {trait.description}",
                gene_sequence=trait.gene_sequence,
                expression_level=trait.expression_level * random.uniform(0.5, 2.0),
                dominant=trait.dominant,
                inherited=trait.inherited,
                mutation_rate=trait.mutation_rate * 1.5,
                active=trait.active
            )
            
            # Заменяем старый признак
            if entity_id in self.genome_profiles:
                profile = self.genome_profiles[entity_id]
                for i, old_trait in enumerate(profile.traits):
                    if old_trait.trait_id == trait.trait_id:
                        profile.traits[i] = mutated_trait
                        break
                
                profile.mutation_count += 1
            
            # Записываем в историю
            current_time = time.time()
            self.genetic_history.append({
                'timestamp': current_time,
                'action': 'trait_mutated',
                'entity_id': entity_id,
                'trait_id': trait.trait_id,
                'mutation_type': 'expression_change'
            })
            
            self.system_stats['mutations_occurred'] += 1
            logger.debug(f"Признак {trait.trait_id} мутировал у сущности {entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка мутации признака {trait.trait_id} у {entity_id}: {e}")
    
    def _trigger_sequence_mutation(self, entity_id: str, sequence: GeneSequence) -> None:
        """Запуск мутации последовательности"""
        try:
            # Мутируем последовательность
            if random.random() < 0.3:  # 30% шанс изменения длины
                new_length = max(1, sequence.length + random.randint(-2, 2))
                sequence.length = new_length
            
            if random.random() < 0.4:  # 40% шанс изменения сложности
                sequence.complexity *= random.uniform(0.8, 1.3)
            
            if random.random() < 0.5:  # 50% шанс изменения стабильности
                sequence.stability *= random.uniform(0.9, 1.1)
                sequence.stability = max(0.1, min(1.0, sequence.stability))
            
            # Добавляем или удаляем гены
            if random.random() < 0.2:  # 20% шанс изменения генов
                if random.random() < 0.5 and len(sequence.genes) < 20:
                    # Добавляем ген
                    new_gene = f"gene_{len(sequence.genes)}_{random.choice(list(GeneType)).value}"
                    sequence.genes.append(new_gene)
                elif len(sequence.genes) > 1:
                    # Удаляем ген
                    sequence.genes.pop(random.randint(0, len(sequence.genes) - 1))
            
            # Записываем в историю
            current_time = time.time()
            self.genetic_history.append({
                'timestamp': current_time,
                'action': 'sequence_mutated',
                'entity_id': entity_id,
                'sequence_id': sequence.sequence_id,
                'mutation_type': 'sequence_change'
            })
            
            logger.debug(f"Последовательность {sequence.sequence_id} мутировала у сущности {entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка мутации последовательности {sequence.sequence_id} у {entity_id}: {e}")
    
    def _adapt_to_environment(self, entity_id: str, environment_type: str) -> None:
        """Адаптация к окружению"""
        try:
            if entity_id not in self.genome_profiles:
                return
            
            profile = self.genome_profiles[entity_id]
            
            # Адаптируем признаки к окружению
            for trait in profile.traits:
                if random.random() < 0.3:  # 30% шанс адаптации
                    # Изменяем экспрессию в зависимости от окружения
                    if environment_type == "hostile":
                        trait.expression_level *= random.uniform(1.1, 1.5)
                    elif environment_type == "friendly":
                        trait.expression_level *= random.uniform(0.8, 1.2)
                    elif environment_type == "extreme":
                        trait.expression_level *= random.uniform(1.2, 2.0)
                    
                    # Ограничиваем экспрессию
                    trait.expression_level = max(0.1, min(3.0, trait.expression_level))
            
            # Создаем новый адаптационный признак
            adaptation_trait = GeneticTrait(
                trait_id=f"adaptation_{environment_type}_{entity_id}",
                name=f"Адаптация к {environment_type}",
                description=f"Адаптация к окружению типа {environment_type}",
                gene_sequence=f"adapt_seq_{entity_id}",
                expression_level=1.0,
                dominant=False,
                inherited=False,
                mutation_rate=0.02,
                active=True
            )
            
            profile.traits.append(adaptation_trait)
            
            # Записываем в историю
            current_time = time.time()
            self.genetic_history.append({
                'timestamp': current_time,
                'action': 'environment_adaptation',
                'entity_id': entity_id,
                'environment_type': environment_type,
                'new_trait_id': adaptation_trait.trait_id
            })
            
            logger.debug(f"Сущность {entity_id} адаптировалась к окружению {environment_type}")
            
        except Exception as e:
            logger.error(f"Ошибка адаптации {entity_id} к окружению {environment_type}: {e}")
    
    def get_genome_profile(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение профиля генома сущности"""
        try:
            if entity_id not in self.genome_profiles:
                return None
            
            profile = self.genome_profiles[entity_id]
            
            return {
                'entity_id': profile.entity_id,
                'genome_id': profile.genome_id,
                'mutation_count': profile.mutation_count,
                'recombination_count': profile.recombination_count,
                'last_update': profile.last_update,
                'generation': profile.generation,
                'sequences_count': len(profile.gene_sequences),
                'traits_count': len(profile.traits),
                'active_traits_count': sum(1 for trait in profile.traits if trait.active)
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения профиля генома для {entity_id}: {e}")
            return None
    
    def get_genetic_traits(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение генетических признаков сущности"""
        try:
            if entity_id not in self.genome_profiles:
                return []
            
            profile = self.genome_profiles[entity_id]
            traits_info = []
            
            for trait in profile.traits:
                traits_info.append({
                    'trait_id': trait.trait_id,
                    'name': trait.name,
                    'description': trait.description,
                    'gene_sequence': trait.gene_sequence,
                    'expression_level': trait.expression_level,
                    'dominant': trait.dominant,
                    'inherited': trait.inherited,
                    'mutation_rate': trait.mutation_rate,
                    'active': trait.active
                })
            
            return traits_info
            
        except Exception as e:
            logger.error(f"Ошибка получения генетических признаков для {entity_id}: {e}")
            return []
    
    def get_gene_sequences(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение последовательностей генов сущности"""
        try:
            if entity_id not in self.genome_profiles:
                return []
            
            profile = self.genome_profiles[entity_id]
            sequences_info = []
            
            for sequence in profile.gene_sequences:
                sequences_info.append({
                    'sequence_id': sequence.sequence_id,
                    'genes_count': len(sequence.genes),
                    'length': sequence.length,
                    'complexity': sequence.complexity,
                    'stability': sequence.stability,
                    'generation': sequence.generation
                })
            
            return sequences_info
            
        except Exception as e:
            logger.error(f"Ошибка получения последовательностей генов для {entity_id}: {e}")
            return []
    
    def activate_trait(self, entity_id: str, trait_id: str) -> bool:
        """Активация генетического признака"""
        try:
            if entity_id not in self.genome_profiles:
                return False
            
            profile = self.genome_profiles[entity_id]
            trait_to_activate = None
            
            for trait in profile.traits:
                if trait.trait_id == trait_id:
                    trait_to_activate = trait
                    break
            
            if not trait_to_activate:
                return False
            
            if trait_to_activate.active:
                logger.debug(f"Признак {trait_id} уже активен")
                return True
            
            # Активируем признак
            trait_to_activate.active = True
            
            # Записываем в историю
            current_time = time.time()
            self.genetic_history.append({
                'timestamp': current_time,
                'action': 'trait_activated',
                'entity_id': entity_id,
                'trait_id': trait_id
            })
            
            self.system_stats['traits_activated'] += 1
            logger.debug(f"Признак {trait_id} активирован у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка активации признака {trait_id} у {entity_id}: {e}")
            return False
    
    def deactivate_trait(self, entity_id: str, trait_id: str) -> bool:
        """Деактивация генетического признака"""
        try:
            if entity_id not in self.genome_profiles:
                return False
            
            profile = self.genome_profiles[entity_id]
            trait_to_deactivate = None
            
            for trait in profile.traits:
                if trait.trait_id == trait_id:
                    trait_to_deactivate = trait
                    break
            
            if not trait_to_deactivate:
                return False
            
            if not trait_to_deactivate.active:
                logger.debug(f"Признак {trait_id} уже неактивен")
                return True
            
            # Деактивируем признак
            trait_to_deactivate.active = False
            
            logger.debug(f"Признак {trait_id} деактивирован у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка деактивации признака {trait_id} у {entity_id}: {e}")
            return False
    
    def force_mutation(self, entity_id: str, trait_id: str) -> bool:
        """Принудительная мутация признака"""
        try:
            if entity_id not in self.genome_profiles:
                return False
            
            profile = self.genome_profiles[entity_id]
            trait_to_mutate = None
            
            for trait in profile.traits:
                if trait.trait_id == trait_id:
                    trait_to_mutate = trait
                    break
            
            if not trait_to_mutate:
                return False
            
            # Запускаем мутацию
            self._trigger_trait_mutation(entity_id, trait_to_mutate)
            
            logger.info(f"Принудительная мутация признака {trait_id} у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка принудительной мутации признака {trait_id} у {entity_id}: {e}")
            return False

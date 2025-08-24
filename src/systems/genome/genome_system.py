#!/usr/bin/env python3
"""
Genome System - Система генома для эволюции сущностей
Интегрирована с AI системами и системой скиллов
"""

import logging
import random
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import math
import time

logger = logging.getLogger(__name__)

class GeneType(Enum):
    """Типы генов"""
    STRENGTH = "strength"           # Сила
    AGILITY = "agility"            # Ловкость
    INTELLIGENCE = "intelligence"  # Интеллект
    VITALITY = "vitality"          # Жизнеспособность
    RESISTANCE = "resistance"      # Сопротивление
    ADAPTATION = "adaptation"      # Адаптация
    MUTATION = "mutation"          # Мутация
    EVOLUTION = "evolution"        # Эволюция

class GeneDominance(Enum):
    """Доминантность генов"""
    RECESSIVE = "recessive"    # Рецессивный
    CODOMINANT = "codominant"  # Кодоминантный
    DOMINANT = "dominant"      # Доминантный

@dataclass
class Gene:
    """Ген"""
    id: str
    name: str
    gene_type: GeneType
    dominance: GeneDominance
    value: float  # Значение гена (0.0 - 1.0)
    mutation_rate: float  # Шанс мутации
    description: str
    effects: Dict[str, float]  # Эффекты гена на характеристики
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['gene_type'] = self.gene_type.value
        data['dominance'] = self.dominance.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Gene':
        data['gene_type'] = GeneType(data['gene_type'])
        data['dominance'] = GeneDominance(data['dominance'])
        return cls(**data)

@dataclass
class Chromosome:
    """Хромосома"""
    id: str
    genes: List[Gene]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'genes': [gene.to_dict() for gene in self.genes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chromosome':
        genes = [Gene.from_dict(gene_data) for gene_data in data['genes']]
        return cls(data['id'], genes)

class Genome:
    """Геном сущности"""
    
    def __init__(self, entity_id: str, parent_genomes: Optional[List['Genome']] = None):
        self.entity_id = entity_id
        self.chromosomes: List[Chromosome] = []
        self.generation = 0
        self.mutation_count = 0
        
        if parent_genomes:
            self._inherit_from_parents(parent_genomes)
        else:
            self._generate_random_genome()
        
        logger.info(f"Геном создан для {entity_id}: {len(self.chromosomes)} хромосом")
    
    def _generate_random_genome(self):
        """Генерация случайного генома"""
        # Создаем базовые хромосомы
        chromosome_types = ['physical', 'mental', 'special']
        
        for chrom_type in chromosome_types:
            genes = []
            
            # Гены для физических характеристик
            if chrom_type == 'physical':
                genes.extend([
                    Gene(f"{chrom_type}_strength", "Физическая сила", GeneType.STRENGTH, 
                         GeneDominance.DOMINANT, random.uniform(0.3, 0.8), 0.05,
                         "Увеличивает физическую силу", {'strength': 0.1, 'health': 0.05}),
                    Gene(f"{chrom_type}_agility", "Физическая ловкость", GeneType.AGILITY,
                         GeneDominance.CODOMINANT, random.uniform(0.3, 0.8), 0.06,
                         "Увеличивает ловкость", {'agility': 0.1, 'speed': 0.05}),
                    Gene(f"{chrom_type}_vitality", "Жизнеспособность", GeneType.VITALITY,
                         GeneDominance.DOMINANT, random.uniform(0.4, 0.9), 0.04,
                         "Увеличивает здоровье", {'health': 0.15, 'regeneration': 0.02})
                ])
            
            # Гены для ментальных характеристик
            elif chrom_type == 'mental':
                genes.extend([
                    Gene(f"{chrom_type}_intelligence", "Интеллект", GeneType.INTELLIGENCE,
                         GeneDominance.DOMINANT, random.uniform(0.3, 0.8), 0.05,
                         "Увеличивает интеллект", {'intelligence': 0.1, 'mana': 0.05}),
                    Gene(f"{chrom_type}_adaptation", "Адаптация", GeneType.ADAPTATION,
                         GeneDominance.CODOMINANT, random.uniform(0.2, 0.7), 0.08,
                         "Улучшает адаптацию", {'learning_rate': 0.1, 'skill_mastery': 0.05}),
                    Gene(f"{chrom_type}_resistance", "Сопротивление", GeneType.RESISTANCE,
                         GeneDominance.RECESSIVE, random.uniform(0.3, 0.8), 0.03,
                         "Увеличивает сопротивление", {'resistance': 0.1, 'defense': 0.05})
                ])
            
            # Специальные гены
            elif chrom_type == 'special':
                genes.extend([
                    Gene(f"{chrom_type}_mutation", "Мутагенность", GeneType.MUTATION,
                         GeneDominance.RECESSIVE, random.uniform(0.1, 0.5), 0.15,
                         "Увеличивает шанс мутаций", {'mutation_rate': 0.2, 'evolution_speed': 0.1}),
                    Gene(f"{chrom_type}_evolution", "Эволюционный потенциал", GeneType.EVOLUTION,
                         GeneDominance.CODOMINANT, random.uniform(0.2, 0.6), 0.12,
                         "Ускоряет эволюцию", {'evolution_rate': 0.15, 'skill_discovery': 0.1})
                ])
            
            chromosome = Chromosome(f"{chrom_type}_chromosome", genes)
            self.chromosomes.append(chromosome)
    
    def _inherit_from_parents(self, parent_genomes: List['Genome']):
        """Наследование от родителей"""
        if not parent_genomes:
            self._generate_random_genome()
            return
        
        # Выбираем лучшие гены от родителей
        for chrom_type in ['physical', 'mental', 'special']:
            parent_genes = []
            
            # Собираем все гены данного типа от родителей
            for parent in parent_genomes:
                for chromosome in parent.chromosomes:
                    if chrom_type in chromosome.id:
                        parent_genes.extend(chromosome.genes)
            
            if not parent_genes:
                continue
            
            # Создаем новую хромосому с лучшими генами
            inherited_genes = []
            gene_types = set(gene.gene_type for gene in parent_genes)
            
            for gene_type in gene_types:
                type_genes = [g for g in parent_genes if g.gene_type == gene_type]
                
                if type_genes:
                    # Выбираем лучший ген (с наивысшим значением)
                    best_gene = max(type_genes, key=lambda g: g.value)
                    
                    # Применяем мутации
                    mutated_gene = self._mutate_gene(best_gene)
                    inherited_genes.append(mutated_gene)
            
            if inherited_genes:
                chromosome = Chromosome(f"{chrom_type}_chromosome", inherited_genes)
                self.chromosomes.append(chromosome)
        
        self.generation = max(p.generation for p in parent_genomes) + 1
        logger.info(f"Геном унаследован от {len(parent_genomes)} родителей, поколение: {self.generation}")
    
    def _mutate_gene(self, gene: Gene) -> Gene:
        """Мутация гена"""
        if random.random() < gene.mutation_rate:
            # Создаем мутировавший ген
            mutation_factor = random.uniform(0.8, 1.2)
            new_value = max(0.0, min(1.0, gene.value * mutation_factor))
            
            mutated_gene = Gene(
                id=gene.id,
                name=gene.name,
                gene_type=gene.gene_type,
                dominance=gene.dominance,
                value=new_value,
                mutation_rate=gene.mutation_rate * random.uniform(0.9, 1.1),
                description=gene.description,
                effects=gene.effects.copy()
            )
            
            self.mutation_count += 1
            logger.debug(f"Ген {gene.name} мутировал: {gene.value:.3f} -> {new_value:.3f}")
            return mutated_gene
        
        return gene
    
    def get_stat_boosts(self) -> Dict[str, float]:
        """Получение бонусов к характеристикам от генома"""
        boosts = {}
        
        for chromosome in self.chromosomes:
            for gene in chromosome.genes:
                for stat, boost in gene.effects.items():
                    if stat not in boosts:
                        boosts[stat] = 0.0
                    boosts[stat] += boost * gene.value
        
        return boosts
    
    def get_skill_genes(self) -> List[Gene]:
        """Получение генов, связанных со скиллами"""
        skill_genes = []
        
        for chromosome in self.chromosomes:
            for gene in chromosome.genes:
                if gene.gene_type in [GeneType.INTELLIGENCE, GeneType.ADAPTATION, GeneType.EVOLUTION]:
                    skill_genes.append(gene)
        
        return skill_genes
    
    def can_learn_skill(self, skill_requirements: Dict[str, float]) -> bool:
        """Проверка возможности изучения скилла"""
        stat_boosts = self.get_stat_boosts()
        
        for stat, required_value in skill_requirements.items():
            current_value = stat_boosts.get(stat, 0.0)
            if current_value < required_value:
                return False
        
        return True
    
    def get_evolution_potential(self) -> float:
        """Получение эволюционного потенциала"""
        evolution_genes = [g for g in self.get_skill_genes() if g.gene_type == GeneType.EVOLUTION]
        
        if not evolution_genes:
            return 0.0
        
        total_potential = sum(g.value for g in evolution_genes)
        return total_potential / len(evolution_genes)
    
    def get_mutation_potential(self) -> float:
        """Получение потенциала мутаций"""
        mutation_genes = []
        
        for chromosome in self.chromosomes:
            for gene in chromosome.genes:
                if gene.gene_type == GeneType.MUTATION:
                    mutation_genes.append(gene)
        
        if not mutation_genes:
            return 0.0
        
        total_potential = sum(g.value for g in mutation_genes)
        return total_potential / len(mutation_genes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сохранение генома в словарь"""
        return {
            'entity_id': self.entity_id,
            'generation': self.generation,
            'mutation_count': self.mutation_count,
            'chromosomes': [chrom.to_dict() for chrom in self.chromosomes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Genome':
        """Загрузка генома из словаря"""
        genome = cls.__new__(cls)
        genome.entity_id = data['entity_id']
        genome.generation = data['generation']
        genome.mutation_count = data['mutation_count']
        genome.chromosomes = [Chromosome.from_dict(chrom_data) for chrom_data in data['chromosomes']]
        return genome

class GenomeManager:
    """Менеджер геномов"""
    
    def __init__(self):
        self.genomes: Dict[str, Genome] = {}
        self.gene_pool: List[Gene] = []
        self.evolution_history: List[Dict[str, Any]] = []
        
        # Инициализация пула генов
        self._initialize_gene_pool()
        
        logger.info("Genome Manager инициализирован")
    
    def _initialize_gene_pool(self):
        """Инициализация пула доступных генов"""
        # Базовые гены для всех типов
        base_genes = [
            # Физические гены
            Gene("base_strength", "Базовая сила", GeneType.STRENGTH, GeneDominance.DOMINANT,
                 0.5, 0.05, "Базовая физическая сила", {'strength': 0.1}),
            Gene("base_agility", "Базовая ловкость", GeneType.AGILITY, GeneDominance.CODOMINANT,
                 0.5, 0.06, "Базовая ловкость", {'agility': 0.1}),
            Gene("base_vitality", "Базовая жизнеспособность", GeneType.VITALITY, GeneDominance.DOMINANT,
                 0.5, 0.04, "Базовая жизнеспособность", {'health': 0.1}),
            
            # Ментальные гены
            Gene("base_intelligence", "Базовый интеллект", GeneType.INTELLIGENCE, GeneDominance.DOMINANT,
                 0.5, 0.05, "Базовый интеллект", {'intelligence': 0.1}),
            Gene("base_adaptation", "Базовая адаптация", GeneType.ADAPTATION, GeneDominance.CODOMINANT,
                 0.5, 0.08, "Базовая адаптация", {'learning_rate': 0.1}),
            Gene("base_resistance", "Базовое сопротивление", GeneType.RESISTANCE, GeneDominance.RECESSIVE,
                 0.5, 0.03, "Базовое сопротивление", {'resistance': 0.1}),
            
            # Специальные гены
            Gene("base_mutation", "Базовая мутагенность", GeneType.MUTATION, GeneDominance.RECESSIVE,
                 0.3, 0.15, "Базовая мутагенность", {'mutation_rate': 0.1}),
            Gene("base_evolution", "Базовый эволюционный потенциал", GeneType.EVOLUTION, GeneDominance.CODOMINANT,
                 0.4, 0.12, "Базовый эволюционный потенциал", {'evolution_rate': 0.1})
        ]
        
        self.gene_pool.extend(base_genes)
        logger.info(f"Инициализирован пул из {len(self.gene_pool)} генов")
    
    def create_genome(self, entity_id: str, parent_ids: Optional[List[str]] = None) -> Genome:
        """Создание нового генома"""
        parent_genomes = []
        
        if parent_ids:
            for parent_id in parent_ids:
                if parent_id in self.genomes:
                    parent_genomes.append(self.genomes[parent_id])
        
        genome = Genome(entity_id, parent_genomes)
        self.genomes[entity_id] = genome
        
        # Записываем в историю эволюции
        self.evolution_history.append({
            'entity_id': entity_id,
            'generation': genome.generation,
            'mutation_count': genome.mutation_count,
            'parent_ids': parent_ids or [],
            'timestamp': time.time()
        })
        
        logger.info(f"Создан геном для {entity_id} (поколение {genome.generation})")
        return genome
    
    def get_genome(self, entity_id: str) -> Optional[Genome]:
        """Получение генома сущности"""
        return self.genomes.get(entity_id)
    
    def evolve_genome(self, entity_id: str, experience_gained: float) -> bool:
        """Эволюция генома на основе опыта"""
        genome = self.get_genome(entity_id)
        if not genome:
            return False
        
        # Проверяем возможность эволюции
        evolution_potential = genome.get_evolution_potential()
        mutation_potential = genome.get_mutation_potential()
        
        # Шанс эволюции зависит от опыта и потенциала
        evolution_chance = min(0.1 + experience_gained * 0.01 + evolution_potential * 0.2, 0.5)
        
        if random.random() < evolution_chance:
            # Эволюционируем геном
            self._evolve_genome(genome, experience_gained)
            return True
        
        # Шанс мутации
        mutation_chance = mutation_potential * 0.1
        if random.random() < mutation_chance:
            # Мутируем случайный ген
            self._mutate_random_gene(genome)
            return True
        
        return False
    
    def _evolve_genome(self, genome: Genome, experience_gained: float):
        """Эволюция генома"""
        # Улучшаем случайный ген
        all_genes = []
        for chromosome in genome.chromosomes:
            all_genes.extend(chromosome.genes)
        
        if all_genes:
            gene_to_evolve = random.choice(all_genes)
            evolution_factor = 1.0 + experience_gained * 0.01
            
            gene_to_evolve.value = min(1.0, gene_to_evolve.value * evolution_factor)
            
            logger.info(f"Геном {genome.entity_id} эволюционировал: {gene_to_evolve.name} улучшен")
    
    def _mutate_random_gene(self, genome: Genome):
        """Мутация случайного гена"""
        all_genes = []
        for chromosome in genome.chromosomes:
            all_genes.extend(chromosome.genes)
        
        if all_genes:
            gene_to_mutate = random.choice(all_genes)
            original_value = gene_to_mutate.value
            
            # Мутация
            mutation_factor = random.uniform(0.7, 1.3)
            gene_to_mutate.value = max(0.0, min(1.0, gene_to_mutate.value * mutation_factor))
            
            genome.mutation_count += 1
            
            logger.info(f"Ген {gene_to_mutate.name} в геноме {genome.entity_id} мутировал: {original_value:.3f} -> {gene_to_mutate.value:.3f}")
    
    def get_best_genomes(self, count: int = 5) -> List[Genome]:
        """Получение лучших геномов"""
        all_genomes = list(self.genomes.values())
        
        # Сортируем по поколению и количеству мутаций
        all_genomes.sort(key=lambda g: (g.generation, g.mutation_count), reverse=True)
        
        return all_genomes[:count]
    
    def save_genomes(self, save_slot: str = "default"):
        """Сохранение геномов"""
        try:
            save_dir = f"saves/genomes/{save_slot}"
            os.makedirs(save_dir, exist_ok=True)
            
            # Сохраняем геномы
            genomes_data = {
                entity_id: genome.to_dict() 
                for entity_id, genome in self.genomes.items()
            }
            
            with open(f"{save_dir}/genomes.json", 'w', encoding='utf-8') as f:
                json.dump(genomes_data, f, indent=2, ensure_ascii=False)
            
            # Сохраняем историю эволюции
            with open(f"{save_dir}/evolution_history.json", 'w', encoding='utf-8') as f:
                json.dump(self.evolution_history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Геномы сохранены в слот {save_slot}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения геномов: {e}")
    
    def load_genomes(self, save_slot: str = "default"):
        """Загрузка геномов"""
        try:
            save_dir = f"saves/genomes/{save_slot}"
            
            # Загружаем геномы
            genomes_file = f"{save_dir}/genomes.json"
            if os.path.exists(genomes_file):
                with open(genomes_file, 'r', encoding='utf-8') as f:
                    genomes_data = json.load(f)
                
                for entity_id, genome_data in genomes_data.items():
                    genome = Genome.from_dict(genome_data)
                    self.genomes[entity_id] = genome
            
            # Загружаем историю эволюции
            history_file = f"{save_dir}/evolution_history.json"
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.evolution_history = json.load(f)
            
            logger.info(f"Загружено {len(self.genomes)} геномов из слота {save_slot}")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки геномов: {e}")

# Глобальный менеджер геномов
genome_manager = GenomeManager()

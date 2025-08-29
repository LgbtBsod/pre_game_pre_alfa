#!/usr/bin/env python3
"""
Система эволюции - управление эволюционными процессами сущностей
Интегрирована с новой модульной архитектурой
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

from src.core.system_interfaces import BaseGameSystem
from src.core.architecture import Priority, LifecycleState
from src.core.state_manager import StateManager, StateType, StateScope
from src.core.repository import RepositoryManager, DataType, StorageType
from src.core.constants import constants_manager, EvolutionStage, EvolutionType, GeneType, GeneRarity, StatType, BASE_STATS, PROBABILITY_CONSTANTS, SYSTEM_LIMITS, TIME_CONSTANTS_RO, get_float

logger = logging.getLogger(__name__)

@dataclass
class EvolutionProgress:
    """Прогресс эволюции"""
    entity_id: str
    current_stage: EvolutionStage
    evolution_points: int = 0
    required_points: int = 100
    mutations_count: int = 0
    adaptations_count: int = 0
    last_evolution: float = 0.0
    evolution_history: List[str] = field(default_factory=list)

@dataclass
class Gene:
    """Генетическая информация"""
    gene_id: str
    gene_type: GeneType
    rarity: GeneRarity
    strength: float = 1.0
    mutation_chance: float = 0.01
    expression_level: float = 1.0
    dominant: bool = False
    active: bool = True
    generation: int = 1

@dataclass
class EvolutionTrigger:
    """Триггер эволюции"""
    trigger_id: str
    trigger_type: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    probability: float = 1.0
    cooldown: float = 0.0
    last_triggered: float = 0.0

class EvolutionSystem(BaseGameSystem):
    """Система управления эволюцией - интегрирована с новой архитектурой"""
    
    def __init__(self):
        super().__init__("evolution", Priority.HIGH)
        
        # Интеграция с новой архитектурой
        self.state_manager: Optional[StateManager] = None
        self.repository_manager: Optional[RepositoryManager] = None
        self.event_bus = None
        
        # Прогресс эволюции сущностей (теперь управляется через RepositoryManager)
        self.evolution_progress: Dict[str, EvolutionProgress] = {}
        
        # Гены сущностей (теперь управляются через RepositoryManager)
        self.entity_genes: Dict[str, List[Gene]] = {}
        
        # Триггеры эволюции (теперь управляются через RepositoryManager)
        self.evolution_triggers: List[EvolutionTrigger] = []
        
        # История эволюции (теперь управляется через RepositoryManager)
        self.evolution_history: List[Dict[str, Any]] = []
        
        # Настройки системы (теперь управляются через StateManager)
        self.system_settings = {
            'max_evolution_stage': EvolutionStage.LEGENDARY,
            'base_evolution_points': 100,
            'mutation_chance': PROBABILITY_CONSTANTS["base_mutation_chance"],
            'adaptation_chance': PROBABILITY_CONSTANTS["base_adaptation_chance"],
            'gene_expression_rate': 0.1,
            'evolution_cooldown': get_float(TIME_CONSTANTS_RO, "evolution_cooldown", 60.0)
        }
        
        # Статистика системы (теперь управляется через StateManager)
        self.system_stats = {
            'entities_evolving': 0,
            'total_evolutions': 0,
            'mutations_occurred': 0,
            'adaptations_occurred': 0,
            'genes_activated': 0,
            'update_time': 0.0
        }
        
        logger.info("Система эволюции инициализирована с новой архитектурой")
    
    @property
    def system_name(self) -> str:
        return self.component_id
    
    @property
    def system_priority(self) -> Priority:
        return self.priority
    
    @property
    def system_state(self) -> LifecycleState:
        return self.state
    
    def set_architecture_components(self, state_manager: StateManager, 
                                  repository_manager: RepositoryManager, 
                                  event_bus=None) -> None:
        """Установка компонентов архитектуры"""
        self.state_manager = state_manager
        self.repository_manager = repository_manager
        self.event_bus = event_bus
        
        # Регистрируем состояния системы
        if self.state_manager:
            self._register_system_states()
        
        # Регистрируем репозитории системы
        if self.repository_manager:
            self._register_system_repositories()
    
    def _register_system_states(self) -> None:
        """Регистрация состояний системы"""
        try:
            # Регистрируем настройки системы
            self.register_system_state('system_settings', self.system_settings, StateType.SYSTEM)
            
            # Регистрируем статистику системы
            self.register_system_state('system_stats', self.system_stats, StateType.SYSTEM)
            
            # Регистрируем состояние системы
            self.register_system_state('system_state', 'ready', StateType.SYSTEM)
            
            logger.info("Состояния системы эволюции зарегистрированы")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации состояний системы эволюции: {e}")
    
    def _register_system_repositories(self) -> None:
        """Регистрация репозиториев системы"""
        try:
            # Регистрируем репозиторий прогресса эволюции
            self.register_system_repository('evolution_progress', DataType.ENTITY_DATA, StorageType.MEMORY)
            
            # Регистрируем репозиторий генов
            self.register_system_repository('entity_genes', DataType.ENTITY_DATA, StorageType.MEMORY)
            
            # Регистрируем репозиторий триггеров эволюции
            self.register_system_repository('evolution_triggers', DataType.SYSTEM_DATA, StorageType.MEMORY)
            
            # Регистрируем репозиторий истории эволюции
            self.register_system_repository('evolution_history', DataType.SYSTEM_DATA, StorageType.MEMORY)
            
            logger.info("Репозитории системы эволюции зарегистрированы")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации репозиториев системы эволюции: {e}")
    
    def initialize(self) -> bool:
        """Инициализация системы эволюции"""
        try:
            logger.info("Инициализация системы эволюции...")
            
            # Настраиваем систему
            self._setup_evolution_system()
            
            # Создаем базовые триггеры эволюции
            self._create_base_triggers()
            
            # Обновляем состояние системы
            if self.state_manager:
                self.state_manager.update_state('evolution', 'system_state', 'ready')
            
            self.state = LifecycleState.READY
            logger.info("Система эволюции успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы эволюции: {e}")
            self.state = LifecycleState.ERROR
            return False
    
    def start(self) -> bool:
        """Запуск системы эволюции"""
        try:
            if self.state != LifecycleState.READY:
                return False
            
            self.state = LifecycleState.RUNNING
            logger.info("Система эволюции запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска системы эволюции: {e}")
            return False
    
    def stop(self) -> bool:
        """Остановка системы эволюции"""
        try:
            if self.state == LifecycleState.RUNNING:
                self.state = LifecycleState.STOPPED
                logger.info("Система эволюции остановлена")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка остановки системы эволюции: {e}")
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы эволюции"""
        try:
            if self.state != LifecycleState.RUNNING:
                return False
            
            start_time = time.time()
            
            # Обновляем прогресс эволюции
            self._update_evolution_progress(delta_time)
            
            # Проверяем триггеры эволюции
            self._check_evolution_triggers(delta_time)
            
            # Обновляем экспрессию генов
            self._update_gene_expression(delta_time)
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            # Обновляем время обновления в статистике
            update_time = time.time() - start_time
            self.system_stats['update_time'] = update_time
            
            # Обновляем статистику через StateManager
            if self.state_manager:
                self.state_manager.update_state('evolution', 'system_stats', self.system_stats)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы эволюции: {e}")
            self.system_stats['errors_count'] += 1
            return False
    
    def destroy(self) -> bool:
        """Уничтожение системы эволюции"""
        try:
            logger.info("Уничтожение системы эволюции...")
            
            # Очищаем все данные
            self.evolution_progress.clear()
            self.entity_genes.clear()
            self.evolution_triggers.clear()
            self.evolution_history.clear()
            
            # Сбрасываем статистику
            self.system_stats = {
                'entities_evolving': 0,
                'total_evolutions': 0,
                'mutations_occurred': 0,
                'adaptations_occurred': 0,
                'genes_activated': 0,
                'update_time': 0.0
            }
            
            self.state = LifecycleState.DESTROYED
            logger.info("Система эволюции уничтожена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения системы эволюции: {e}")
            return False
    
    def reset_stats(self) -> None:
        """Сброс статистики системы"""
        try:
            self.system_stats = {
                'entities_evolving': 0,
                'total_evolutions': 0,
                'mutations_occurred': 0,
                'adaptations_occurred': 0,
                'genes_activated': 0,
                'update_time': 0.0
            }
            
            # Обновляем статистику через StateManager
            if self.state_manager:
                self.state_manager.update_state('evolution', 'system_stats', self.system_stats)
            
            logger.info("Статистика системы эволюции сброшена")
            
        except Exception as e:
            logger.error(f"Ошибка сброса статистики системы эволюции: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'entities_evolving': len(self.evolution_progress),
            'total_genes': sum(len(genes) for genes in self.entity_genes.values()),
            'evolution_triggers': len(self.evolution_triggers),
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий - интеграция с новой архитектурой"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "entity_destroyed":
                return self._handle_entity_destroyed(event_data)
            elif event_type == "experience_gained":
                return self._handle_experience_gained(event_data)
            elif event_type == "combat_ended":
                return self._handle_combat_ended(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _setup_evolution_system(self) -> None:
        """Настройка системы эволюции"""
        try:
            # Инициализируем базовые настройки
            logger.debug("Система эволюции настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему эволюции: {e}")
    
    def _create_base_triggers(self) -> None:
        """Создание базовых триггеров эволюции"""
        try:
            # Триггер по уровню
            level_trigger = EvolutionTrigger(
                trigger_id="level_up",
                trigger_type="level",
                conditions={'min_level': 10},
                probability=0.8,
                cooldown=0.0
            )
            
            # Триггер по опыту
            experience_trigger = EvolutionTrigger(
                trigger_id="experience_milestone",
                trigger_type="experience",
                conditions={'min_experience': 1000},
                probability=0.6,
                cooldown=300.0  # 5 минут
            )
            
            # Триггер по выживанию
            survival_trigger = EvolutionTrigger(
                trigger_id="survival",
                trigger_type="combat",
                conditions={'combats_survived': 5, 'health_threshold': 0.2},
                probability=0.4,
                cooldown=600.0  # 10 минут
            )
            
            # Триггер по адаптации
            adaptation_trigger = EvolutionTrigger(
                trigger_id="environment_adaptation",
                trigger_type="environment",
                conditions={'time_in_environment': 1800},  # 30 минут
                probability=0.3,
                cooldown=900.0  # 15 минут
            )
            
            self.evolution_triggers = [
                level_trigger, experience_trigger, survival_trigger, adaptation_trigger
            ]
            
            logger.info(f"Создано {len(self.evolution_triggers)} базовых триггеров эволюции")
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых триггеров эволюции: {e}")
    
    def _update_evolution_progress(self, delta_time: float) -> None:
        """Обновление прогресса эволюции"""
        try:
            current_time = time.time()
            
            for entity_id, progress in self.evolution_progress.items():
                # Проверяем, не истек ли кулдаун эволюции
                if current_time - progress.last_evolution < self.system_settings['evolution_cooldown']:
                    continue
                
                # Проверяем, готовы ли к эволюции
                if progress.evolution_points >= progress.required_points:
                    if self._trigger_evolution(entity_id, progress):
                        progress.last_evolution = current_time
                        progress.evolution_points = 0
                        progress.required_points = int(progress.required_points * 1.5)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления прогресса эволюции: {e}")
    
    def _check_evolution_triggers(self, delta_time: float) -> None:
        """Проверка триггеров эволюции"""
        try:
            current_time = time.time()
            
            for trigger in self.evolution_triggers:
                # Проверяем кулдаун
                if current_time - trigger.last_triggered < trigger.cooldown:
                    continue
                
                # Проверяем условия
                if self._check_trigger_conditions(trigger):
                    # Пытаемся активировать триггер
                    if random.random() < trigger.probability:
                        self._activate_evolution_trigger(trigger)
                        trigger.last_triggered = current_time
                
        except Exception as e:
            logger.warning(f"Ошибка проверки триггеров эволюции: {e}")
    
    def _update_gene_expression(self, delta_time: float) -> None:
        """Обновление экспрессии генов"""
        try:
            for entity_id, genes in self.entity_genes.items():
                for gene in genes:
                    if not gene.active:
                        continue
                    
                    # Обновляем уровень экспрессии
                    expression_change = random.uniform(-0.1, 0.1) * self.system_settings['gene_expression_rate']
                    gene.expression_level = max(0.0, min(2.0, gene.expression_level + expression_change))
                    
                    # Проверяем мутации
                    if random.random() < gene.mutation_chance:
                        self._trigger_gene_mutation(entity_id, gene)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления экспрессии генов: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['entities_evolving'] = len(self.evolution_progress)
            
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            initial_genes = event_data.get('initial_genes', [])
            
            if entity_id:
                return self.create_evolution_entity(entity_id, initial_genes)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_entity_destroyed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события уничтожения сущности"""
        try:
            entity_id = event_data.get('entity_id')
            
            if entity_id:
                return self.destroy_evolution_entity(entity_id)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события уничтожения сущности: {e}")
            return False
    
    def _handle_experience_gained(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события получения опыта"""
        try:
            entity_id = event_data.get('entity_id')
            experience_amount = event_data.get('experience_amount', 0)
            
            if entity_id and experience_amount > 0:
                return self.add_evolution_points(entity_id, experience_amount // 10)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события получения опыта: {e}")
            return False
    
    def _handle_combat_ended(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события окончания боя"""
        try:
            combat_id = event_data.get('combat_id')
            participants = event_data.get('participants')
            result = event_data.get('result')
            
            if combat_id and participants and result:
                # Проверяем триггеры эволюции для участников
                for participant_id in participants:
                    if participant_id in self.evolution_progress:
                        if result == "victory":
                            # Победители получают бонусные очки эволюции
                            self.add_evolution_points(participant_id, 25)
                        else:
                            # Проигравшие получают меньше очков, но могут адаптироваться
                            self.add_evolution_points(participant_id, 5)
                            if random.random() < self.system_settings['adaptation_chance']:
                                self._trigger_adaptation(participant_id)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события окончания боя: {e}")
            return False
    
    def create_evolution_entity(self, entity_id: str, initial_genes: List[Dict[str, Any]] = None) -> bool:
        """Создание сущности для эволюции"""
        try:
            # Проверяем корректность entity_id
            if not entity_id or entity_id.strip() == "":
                logger.warning("Попытка создания сущности с пустым ID")
                return False
            
            if entity_id in self.evolution_progress:
                logger.warning(f"Сущность {entity_id} уже существует в системе эволюции")
                return False
            
            # Создаем прогресс эволюции
            progress = EvolutionProgress(
                entity_id=entity_id,
                current_stage=EvolutionStage.BASIC,
                required_points=self.system_settings['base_evolution_points']
            )
            
            # Создаем базовые гены
            base_genes = self._create_base_genes(entity_id)
            
            # Добавляем пользовательские гены
            if initial_genes:
                for gene_data in initial_genes:
                    gene = Gene(
                        gene_id=f"custom_{int(time.time() * 1000)}",
                        gene_type=GeneType(gene_data.get('gene_type', GeneType.STRENGTH.value)),
                        rarity=GeneRarity(gene_data.get('rarity', GeneRarity.COMMON.value)),
                        strength=gene_data.get('strength', 1.0),
                        mutation_chance=gene_data.get('mutation_chance', 0.01),
                        expression_level=gene_data.get('expression_level', 1.0),
                        dominant=gene_data.get('dominant', False)
                    )
                    base_genes.append(gene)
            
            # Добавляем в систему
            self.evolution_progress[entity_id] = progress
            self.entity_genes[entity_id] = base_genes
            
            # Обновляем статистику
            self.system_stats['entities_evolving'] = len(self.evolution_progress)
            
            logger.info(f"Создана сущность {entity_id} для эволюции с {len(base_genes)} генами")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания сущности {entity_id} для эволюции: {e}")
            return False
    
    def destroy_evolution_entity(self, entity_id: str) -> bool:
        """Уничтожение сущности из системы эволюции"""
        try:
            if entity_id not in self.evolution_progress:
                return False
            
            # Удаляем прогресс эволюции
            del self.evolution_progress[entity_id]
            
            # Удаляем гены
            if entity_id in self.entity_genes:
                del self.entity_genes[entity_id]
            
            # Обновляем статистику
            self.system_stats['entities_evolving'] = len(self.evolution_progress)
            
            logger.info(f"Сущность {entity_id} удалена из системы эволюции")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления сущности {entity_id} из системы эволюции: {e}")
            return False
    
    def add_evolution_points(self, entity_id: str, points: int) -> bool:
        """Добавление очков эволюции"""
        try:
            if entity_id not in self.evolution_progress:
                logger.warning(f"Сущность {entity_id} не найдена в системе эволюции")
                return False
            
            progress = self.evolution_progress[entity_id]
            progress.evolution_points += points
            
            # Проверяем, нужно ли запустить эволюцию
            if progress.evolution_points >= progress.required_points:
                if self._trigger_evolution(entity_id, progress):
                    # Сбрасываем очки и увеличиваем требуемые для следующего этапа
                    progress.evolution_points = 0
                    progress.required_points = int(progress.required_points * 1.5)
            
            # Записываем в историю
            current_time = time.time()
            self.evolution_history.append({
                'timestamp': current_time,
                'action': 'points_gained',
                'entity_id': entity_id,
                'points': points,
                'total_points': progress.evolution_points
            })
            
            logger.debug(f"Сущность {entity_id} получила {points} очков эволюции")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления очков эволюции для {entity_id}: {e}")
            return False
    
    def _create_base_genes(self, entity_id: str) -> List[Gene]:
        """Создание базовых генов для сущности"""
        try:
            base_genes = []
            
            # Физические гены
            physical_genes = [
                Gene(
                    gene_id=f"strength_{entity_id}",
                    gene_type=GeneType.STRENGTH,
                    rarity=GeneRarity.COMMON,
                    strength=1.0,
                    mutation_chance=0.01
                ),
                Gene(
                    gene_id=f"agility_{entity_id}",
                    gene_type=GeneType.AGILITY,
                    rarity=GeneRarity.COMMON,
                    strength=1.0,
                    mutation_chance=0.01
                )
            ]
            
            # Ментальные гены
            mental_genes = [
                Gene(
                    gene_id=f"intelligence_{entity_id}",
                    gene_type=GeneType.INTELLIGENCE,
                    rarity=GeneRarity.COMMON,
                    strength=1.0,
                    mutation_chance=0.01
                ),
                Gene(
                    gene_id=f"wisdom_{entity_id}",
                    gene_type=GeneType.WISDOM,
                    rarity=GeneRarity.COMMON,
                    strength=1.0,
                    mutation_chance=0.01
                )
            ]
            
            # Энергетические гены
            energy_genes = [
                Gene(
                    gene_id=f"vitality_{entity_id}",
                    gene_type=GeneType.VITALITY,
                    rarity=GeneRarity.COMMON,
                    strength=1.0,
                    mutation_chance=0.01
                )
            ]
            
            # Специальные гены
            special_genes = [
                Gene(
                    gene_id=f"adaptation_{entity_id}",
                    gene_type=GeneType.ADAPTATION,
                    rarity=GeneRarity.UNCOMMON,
                    strength=1.2,
                    mutation_chance=0.02
                )
            ]
            
            base_genes = physical_genes + mental_genes + energy_genes + special_genes
            
            return base_genes
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых генов для {entity_id}: {e}")
            return []
    
    def _trigger_evolution(self, entity_id: str, progress: EvolutionProgress) -> bool:
        """Запуск процесса эволюции"""
        try:
            current_stage = progress.current_stage
            
            # Определяем следующий этап эволюции
            if current_stage == EvolutionStage.BASIC:
                next_stage = EvolutionStage.ADVANCED
            elif current_stage == EvolutionStage.ADVANCED:
                next_stage = EvolutionStage.ELITE
            elif current_stage == EvolutionStage.ELITE:
                next_stage = EvolutionStage.MASTER
            elif current_stage == EvolutionStage.MASTER:
                next_stage = EvolutionStage.LEGENDARY
            else:
                logger.warning(f"Сущность {entity_id} уже достигла максимального этапа эволюции")
                return False
            
            # Выполняем эволюцию
            progress.current_stage = next_stage
            progress.evolution_history.append(f"Эволюция в {next_stage.value}")
            
            # Активируем новые гены
            new_genes = self._generate_evolution_genes(entity_id, next_stage)
            if entity_id in self.entity_genes:
                self.entity_genes[entity_id].extend(new_genes)
            
            # Записываем в историю
            current_time = time.time()
            self.evolution_history.append({
                'timestamp': current_time,
                'action': 'evolution_completed',
                'entity_id': entity_id,
                'old_stage': current_stage.value,
                'new_stage': next_stage.value,
                'new_genes_count': len(new_genes)
            })
            
            self.system_stats['total_evolutions'] += 1
            logger.info(f"Сущность {entity_id} эволюционировала в {next_stage.value}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска эволюции для {entity_id}: {e}")
            return False
    
    def _generate_evolution_genes(self, entity_id: str, stage: EvolutionStage) -> List[Gene]:
        """Генерация новых генов при эволюции"""
        try:
            new_genes = []
            
            # Количество новых генов зависит от этапа
            if stage == EvolutionStage.ADVANCED:
                gene_count = 2
            elif stage == EvolutionStage.ELITE:
                gene_count = 3
            elif stage == EvolutionStage.MASTER:
                gene_count = 4
            elif stage == EvolutionStage.LEGENDARY:
                gene_count = 5
            else:
                gene_count = 1
            
            for i in range(gene_count):
                # Случайно выбираем тип гена
                gene_type = random.choice(list(GeneType))
                
                # Определяем редкость на основе этапа
                if stage == EvolutionStage.LEGENDARY:
                    rarity = random.choices(
                        [GeneRarity.RARE, GeneRarity.EPIC, GeneRarity.LEGENDARY],
                        weights=[0.4, 0.4, 0.2]
                    )[0]
                elif stage == EvolutionStage.MASTER:
                    rarity = random.choices(
                        [GeneRarity.UNCOMMON, GeneRarity.RARE, GeneRarity.EPIC],
                        weights=[0.5, 0.3, 0.2]
                    )[0]
                else:
                    rarity = random.choices(
                        [GeneRarity.COMMON, GeneRarity.UNCOMMON, GeneRarity.RARE],
                        weights=[0.6, 0.3, 0.1]
                    )[0]
                
                # Создаем ген
                gene = Gene(
                    gene_id=f"evolution_{stage.value}_{i}_{entity_id}",
                    gene_type=gene_type,
                    rarity=rarity,
                    strength=1.0 + (list(EvolutionStage).index(stage) * 0.2),
                    mutation_chance=0.01 + (list(EvolutionStage).index(stage) * 0.005),
                    expression_level=1.0,
                    dominant=random.random() < 0.3,
                    generation=list(EvolutionStage).index(stage) + 1
                )
                
                new_genes.append(gene)
            
            return new_genes
            
        except Exception as e:
            logger.error(f"Ошибка генерации генов эволюции для {entity_id}: {e}")
            return []
    
    def _check_trigger_conditions(self, trigger: EvolutionTrigger) -> bool:
        """Проверка условий триггера"""
        try:
            # Здесь должна быть логика проверки условий
            # Пока просто возвращаем True для демонстрации
            return True
            
        except Exception as e:
            logger.error(f"Ошибка проверки условий триггера {trigger.trigger_id}: {e}")
            return False
    
    def _activate_evolution_trigger(self, trigger: EvolutionTrigger) -> None:
        """Активация триггера эволюции"""
        try:
            # Здесь должна быть логика активации триггера
            logger.debug(f"Активирован триггер эволюции {trigger.trigger_id}")
            
        except Exception as e:
            logger.error(f"Ошибка активации триггера {trigger.trigger_id}: {e}")
    
    def _trigger_gene_mutation(self, entity_id: str, gene: Gene) -> None:
        """Запуск мутации гена"""
        try:
            # Создаем мутированный ген
            mutated_gene = Gene(
                gene_id=f"mutated_{gene.gene_id}",
                gene_type=gene.gene_type,
                rarity=gene.rarity,
                strength=gene.strength * random.uniform(0.8, 1.5),
                mutation_chance=gene.mutation_chance * 1.5,
                expression_level=gene.expression_level * random.uniform(0.5, 2.0),
                dominant=gene.dominant,
                generation=gene.generation + 1
            )
            
            # Заменяем старый ген
            if entity_id in self.entity_genes:
                genes = self.entity_genes[entity_id]
                for i, old_gene in enumerate(genes):
                    if old_gene.gene_id == gene.gene_id:
                        genes[i] = mutated_gene
                        break
            
            # Записываем в историю
            current_time = time.time()
            self.evolution_history.append({
                'timestamp': current_time,
                'action': 'gene_mutated',
                'entity_id': entity_id,
                'gene_id': gene.gene_id,
                'mutation_strength': mutated_gene.strength / gene.strength
            })
            
            self.system_stats['mutations_occurred'] += 1
            logger.debug(f"Ген {gene.gene_id} мутировал у сущности {entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка мутации гена {gene.gene_id} у {entity_id}: {e}")
    
    def _trigger_adaptation(self, entity_id: str) -> None:
        """Запуск адаптации"""
        try:
            if entity_id not in self.entity_genes:
                return
            
            # Создаем адаптационный ген
            adaptation_gene = Gene(
                gene_id=f"adaptation_{int(time.time() * 1000)}",
                gene_type=GeneType.ADAPTATION,
                rarity=GeneRarity.UNCOMMON,
                strength=1.3,
                mutation_chance=0.015,
                expression_level=1.0,
                dominant=False,
                generation=1
            )
            
            # Добавляем ген
            self.entity_genes[entity_id].append(adaptation_gene)
            
            # Записываем в историю
            current_time = time.time()
            self.evolution_history.append({
                'timestamp': current_time,
                'action': 'adaptation_occurred',
                'entity_id': entity_id,
                'gene_id': adaptation_gene.gene_id
            })
            
            self.system_stats['adaptations_occurred'] += 1
            logger.debug(f"Произошла адаптация у сущности {entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка адаптации у сущности {entity_id}: {e}")
    
    def get_evolution_progress(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Получение прогресса эволюции сущности"""
        try:
            if entity_id not in self.evolution_progress:
                return None
            
            progress = self.evolution_progress[entity_id]
            
            return {
                'entity_id': progress.entity_id,
                'current_stage': progress.current_stage.value,
                'evolution_points': progress.evolution_points,
                'required_points': progress.required_points,
                'mutations_count': progress.mutations_count,
                'adaptations_count': progress.adaptations_count,
                'last_evolution': progress.last_evolution,
                'evolution_history': progress.evolution_history
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения прогресса эволюции для {entity_id}: {e}")
            return None
    
    def get_entity_genes(self, entity_id: str) -> List[Dict[str, Any]]:
        """Получение генов сущности"""
        try:
            if entity_id not in self.entity_genes:
                return []
            
            genes_info = []
            
            for gene in self.entity_genes[entity_id]:
                genes_info.append({
                    'gene_id': gene.gene_id,
                    'gene_type': gene.gene_type.value,
                    'rarity': gene.rarity.value,
                    'strength': gene.strength,
                    'mutation_chance': gene.mutation_chance,
                    'expression_level': gene.expression_level,
                    'dominant': gene.dominant,
                    'active': gene.active,
                    'generation': gene.generation
                })
            
            return genes_info
            
        except Exception as e:
            logger.error(f"Ошибка получения генов сущности {entity_id}: {e}")
            return []
    
    def activate_gene(self, entity_id: str, gene_id: str) -> bool:
        """Активация гена"""
        try:
            if entity_id not in self.entity_genes:
                return False
            
            genes = self.entity_genes[entity_id]
            gene_to_activate = None
            
            for gene in genes:
                if gene.gene_id == gene_id:
                    gene_to_activate = gene
                    break
            
            if not gene_to_activate:
                return False
            
            if gene_to_activate.active:
                logger.debug(f"Ген {gene_id} уже активен")
                return True
            
            # Активируем ген
            gene_to_activate.active = True
            
            # Записываем в историю
            current_time = time.time()
            self.evolution_history.append({
                'timestamp': current_time,
                'action': 'gene_activated',
                'entity_id': entity_id,
                'gene_id': gene_id
            })
            
            self.system_stats['genes_activated'] += 1
            logger.debug(f"Ген {gene_id} активирован у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка активации гена {gene_id} у {entity_id}: {e}")
            return False
    
    def deactivate_gene(self, entity_id: str, gene_id: str) -> bool:
        """Деактивация гена"""
        try:
            if entity_id not in self.entity_genes:
                return False
            
            genes = self.entity_genes[entity_id]
            gene_to_deactivate = None
            
            for gene in genes:
                if gene.gene_id == gene_id:
                    gene_to_deactivate = gene
                    break
            
            if not gene_to_deactivate:
                return False
            
            if not gene_to_deactivate.active:
                logger.debug(f"Ген {gene_id} уже неактивен")
                return True
            
            # Деактивируем ген
            gene_to_deactivate.active = False
            
            logger.debug(f"Ген {gene_id} деактивирован у сущности {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка деактивации гена {gene_id} у {entity_id}: {e}")
            return False
    


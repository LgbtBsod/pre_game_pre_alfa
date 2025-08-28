#!/usr/bin/env python3
"""
Система боя - управление боевыми взаимодействиями между сущностями
Интегрирована с новой модульной архитектурой
"""

import logging
import time
import random
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field

from ...core.system_interfaces import BaseGameSystem
from ...core.architecture import Priority, LifecycleState
from ...core.state_manager import StateManager, StateType, StateScope
from ...core.repository import RepositoryManager, DataType, StorageType
from ...core.constants import (
    DamageType, CombatState, AttackType, StatType,
    BASE_STATS, PROBABILITY_CONSTANTS, TIME_CONSTANTS, SYSTEM_LIMITS
)

logger = logging.getLogger(__name__)

@dataclass
class CombatStats:
    """Боевая статистика"""
    health: int = BASE_STATS["health"]
    max_health: int = BASE_STATS["health"]
    mana: int = BASE_STATS["mana"]
    max_mana: int = BASE_STATS["mana"]
    attack: int = BASE_STATS["attack"]
    defense: int = BASE_STATS["defense"]
    speed: float = BASE_STATS["speed"]
    critical_chance: float = PROBABILITY_CONSTANTS["base_critical_chance"]
    critical_multiplier: float = 2.0
    dodge_chance: float = PROBABILITY_CONSTANTS["base_dodge_chance"]
    block_chance: float = PROBABILITY_CONSTANTS["base_block_chance"]
    block_reduction: float = 0.5

@dataclass
class AttackResult:
    """Результат атаки"""
    damage_dealt: int = 0
    damage_type: DamageType = DamageType.PHYSICAL
    critical_hit: bool = False
    blocked: bool = False
    dodged: bool = False
    effects_applied: List[str] = field(default_factory=list)
    experience_gained: int = 0
    gold_gained: int = 0

@dataclass
class CombatAction:
    """Боевое действие"""
    action_id: str
    action_type: str
    source_entity: str
    target_entity: str
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)

class CombatSystem(BaseGameSystem):
    """Система управления боевыми взаимодействиями - интегрирована с новой архитектурой"""
    
    def __init__(self):
        super().__init__("combat", Priority.HIGH)
        
        # Интеграция с новой архитектурой
        self.state_manager: Optional[StateManager] = None
        self.repository_manager: Optional[RepositoryManager] = None
        self.event_bus = None
        
        # Активные бои (теперь управляются через RepositoryManager)
        self.active_combats: Dict[str, Dict[str, Any]] = {}
        
        # Боевые статистики сущностей (теперь управляются через RepositoryManager)
        self.entity_combat_stats: Dict[str, CombatStats] = {}
        
        # История боевых действий (теперь управляется через RepositoryManager)
        self.combat_history: List[CombatAction] = []
        
        # Настройки системы (теперь управляются через StateManager)
        self.combat_settings = {
            'max_active_combats': SYSTEM_LIMITS["max_active_combats"],
            'combat_timeout': TIME_CONSTANTS["combat_timeout"],
            'auto_resolve_delay': 60.0,  # 1 минута
            'experience_multiplier': 1.0,
            'gold_multiplier': 1.0
        }
        
        # Статистика системы (теперь управляется через StateManager)
        self.system_stats = {
            'active_combats_count': 0,
            'combats_started': 0,
            'combats_completed': 0,
            'total_damage_dealt': 0,
            'total_experience_gained': 0,
            'total_gold_gained': 0,
            'update_time': 0.0
        }
        
        logger.info("Система боя инициализирована с новой архитектурой")
    
    def initialize(self) -> bool:
        """Инициализация системы боя с новой архитектурой"""
        try:
            logger.info("Инициализация системы боя...")
            
            # Инициализация базового компонента
            if not super().initialize():
                return False
            
            # Настраиваем систему
            self._setup_combat_system()
            
            # Регистрируем состояния в StateManager
            self._register_states()
            
            # Регистрируем репозитории в RepositoryManager
            self._register_repositories()
            
            logger.info("Система боя успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы боя: {e}")
            return False
    
    def start(self) -> bool:
        """Запуск системы боя"""
        try:
            if not super().start():
                return False
            
            # Восстанавливаем данные из репозиториев
            self._restore_from_repositories()
            
            logger.info("Система боя запущена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка запуска системы боя: {e}")
            return False
    
    def stop(self) -> bool:
        """Остановка системы боя"""
        try:
            # Сохраняем данные в репозитории
            self._save_to_repositories()
            
            return super().stop()
            
        except Exception as e:
            logger.error(f"Ошибка остановки системы боя: {e}")
            return False
    
    def destroy(self) -> bool:
        """Уничтожение системы боя"""
        try:
            # Сохраняем финальные данные
            self._save_to_repositories()
            
            # Очищаем все данные
            self.active_combats.clear()
            self.entity_combat_stats.clear()
            self.combat_history.clear()
            
            return super().destroy()
            
        except Exception as e:
            logger.error(f"Ошибка уничтожения системы боя: {e}")
            return False
    
    def update(self, delta_time: float) -> bool:
        """Обновление системы боя"""
        try:
            if not super().update(delta_time):
                return False
            
            start_time = time.time()
            
            # Обновляем активные бои
            self._update_active_combats(delta_time)
            
            # Проверяем таймауты боев
            self._check_combat_timeouts()
            
            # Обновляем статистику системы
            self._update_system_stats()
            
            # Обновляем состояния в StateManager
            self._update_states()
            
            self.system_stats['update_time'] = time.time() - start_time
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления системы боя: {e}")
            return False
    
    def _register_states(self) -> None:
        """Регистрация состояний в StateManager"""
        if not self.state_manager:
            return
        
        # Регистрируем состояния системы
        self.state_manager.register_container(
            "combat_system_settings",
            StateType.CONFIGURATION,
            StateScope.SYSTEM,
            self.combat_settings
        )
        
        self.state_manager.register_container(
            "combat_system_stats",
            StateType.STATISTICS,
            StateScope.SYSTEM,
            self.system_stats
        )
        
        # Регистрируем состояния боев
        self.state_manager.register_container(
            "active_combats",
            StateType.DATA,
            StateScope.GLOBAL,
            {}
        )
        
        logger.info("Состояния системы боя зарегистрированы")
    
    def _register_repositories(self) -> None:
        """Регистрация репозиториев в RepositoryManager"""
        if not self.repository_manager:
            return
        
        # Регистрируем репозиторий активных боев
        self.repository_manager.register_repository(
            "active_combats",
            DataType.DYNAMIC_DATA,
            StorageType.MEMORY,
            self.active_combats
        )
        
        # Регистрируем репозиторий боевых статистик
        self.repository_manager.register_repository(
            "entity_combat_stats",
            DataType.ENTITY_DATA,
            StorageType.MEMORY,
            self.entity_combat_stats
        )
        
        # Регистрируем репозиторий истории боев
        self.repository_manager.register_repository(
            "combat_history",
            DataType.HISTORY,
            StorageType.MEMORY,
            self.combat_history
        )
        
        logger.info("Репозитории системы боя зарегистрированы")
    
    def _restore_from_repositories(self) -> None:
        """Восстановление данных из репозиториев"""
        if not self.repository_manager:
            return
        
        try:
            # Восстанавливаем активные бои
            combats_repo = self.repository_manager.get_repository("active_combats")
            if combats_repo:
                self.active_combats = combats_repo.get_all()
            
            # Восстанавливаем боевые статистики
            stats_repo = self.repository_manager.get_repository("entity_combat_stats")
            if stats_repo:
                self.entity_combat_stats = stats_repo.get_all()
            
            # Восстанавливаем историю
            history_repo = self.repository_manager.get_repository("combat_history")
            if history_repo:
                self.combat_history = history_repo.get_all()
            
            logger.info("Данные системы боя восстановлены из репозиториев")
            
        except Exception as e:
            logger.error(f"Ошибка восстановления данных из репозиториев: {e}")
    
    def _save_to_repositories(self) -> None:
        """Сохранение данных в репозитории"""
        if not self.repository_manager:
            return
        
        try:
            # Сохраняем активные бои
            combats_repo = self.repository_manager.get_repository("active_combats")
            if combats_repo:
                combats_repo.clear()
                for combat_id, combat_data in self.active_combats.items():
                    combats_repo.create(combat_id, combat_data)
            
            # Сохраняем боевые статистики
            stats_repo = self.repository_manager.get_repository("entity_combat_stats")
            if stats_repo:
                stats_repo.clear()
                for entity_id, stats in self.entity_combat_stats.items():
                    stats_repo.create(entity_id, stats)
            
            # Сохраняем историю
            history_repo = self.repository_manager.get_repository("combat_history")
            if history_repo:
                history_repo.clear()
                for i, action in enumerate(self.combat_history):
                    history_repo.create(f"action_{i}", action)
            
            logger.info("Данные системы боя сохранены в репозитории")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения данных в репозитории: {e}")
    
    def _update_states(self) -> None:
        """Обновление состояний в StateManager"""
        if not self.state_manager:
            return
        
        try:
            # Обновляем статистику системы
            self.state_manager.set_state_value("combat_system_stats", self.system_stats)
            
            # Обновляем активные бои
            self.state_manager.set_state_value("active_combats", self.active_combats)
            
        except Exception as e:
            logger.error(f"Ошибка обновления состояний: {e}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        return {
            **self.system_stats,
            'active_combats': len(self.active_combats),
            'entity_stats': len(self.entity_combat_stats),
            'combat_history': len(self.combat_history),
            'system_name': self.system_name,
            'system_state': self.system_state.value,
            'system_priority': self.system_priority.value
        }
    
    def reset_stats(self) -> None:
        """Сброс статистики системы"""
        self.system_stats = {
            'active_combats_count': 0,
            'combats_started': 0,
            'combats_completed': 0,
            'total_damage_dealt': 0,
            'total_experience_gained': 0,
            'total_gold_gained': 0,
            'update_time': 0.0
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Получение информации о системе"""
        return {
            'name': self.system_name,
            'state': self.system_state.value,
            'priority': self.system_priority.value,
            'active_combats': len(self.active_combats),
            'entity_stats': len(self.entity_combat_stats),
            'combat_history': len(self.combat_history),
            'stats': self.system_stats
        }
    
    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Обработка событий"""
        try:
            if event_type == "entity_created":
                return self._handle_entity_created(event_data)
            elif event_type == "combat_started":
                return self._handle_combat_started(event_data)
            elif event_type == "combat_ended":
                return self._handle_combat_ended(event_data)
            elif event_type == "attack_performed":
                return self._handle_attack_performed(event_data)
            else:
                return False
        except Exception as e:
            logger.error(f"Ошибка обработки события {event_type}: {e}")
            return False
    
    def _setup_combat_system(self) -> None:
        """Настройка системы боя"""
        try:
            # Инициализируем базовые настройки
            logger.debug("Система боя настроена")
        except Exception as e:
            logger.warning(f"Не удалось настроить систему боя: {e}")
    
    def _update_active_combats(self, delta_time: float) -> None:
        """Обновление активных боев"""
        try:
            current_time = time.time()
            
            for combat_id, combat_data in list(self.active_combats.items()):
                # Проверяем, не завершился ли бой
                if combat_data['state'] in [CombatState.VICTORY, CombatState.DEFEAT, CombatState.ESCAPED]:
                    continue
                
                # Обновляем время боя
                combat_data['duration'] += delta_time
                
                # Проверяем условия завершения
                if self._check_combat_end_conditions(combat_id, combat_data):
                    continue
                
                # Выполняем AI действия
                if combat_data.get('ai_turn', False):
                    self._process_ai_turn(combat_id, combat_data)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления активных боев: {e}")
    
    def _check_combat_timeouts(self) -> None:
        """Проверка таймаутов боев"""
        try:
            current_time = time.time()
            
            for combat_id, combat_data in list(self.active_combats.items()):
                if combat_data['state'] != CombatState.IN_COMBAT:
                    continue
                
                # Проверяем таймаут
                if current_time - combat_data['start_time'] > self.combat_settings['combat_timeout']:
                    logger.warning(f"Бой {combat_id} превысил таймаут, завершаем")
                    self._end_combat(combat_id, "timeout")
                
        except Exception as e:
            logger.warning(f"Ошибка проверки таймаутов боев: {e}")
    
    def _update_system_stats(self) -> None:
        """Обновление статистики системы"""
        try:
            self.system_stats['active_combats_count'] = len(self.active_combats)
        except Exception as e:
            logger.warning(f"Ошибка обновления статистики системы: {e}")
    
    def _handle_entity_created(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события создания сущности"""
        try:
            entity_id = event_data.get('entity_id')
            combat_stats = event_data.get('combat_stats')
            
            if entity_id and combat_stats:
                self.entity_combat_stats[entity_id] = CombatStats(**combat_stats)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события создания сущности: {e}")
            return False
    
    def _handle_combat_started(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события начала боя"""
        try:
            combat_id = event_data.get('combat_id')
            participants = event_data.get('participants')
            
            if combat_id and participants:
                return self.start_combat(combat_id, participants)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события начала боя: {e}")
            return False
    
    def _handle_combat_ended(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события окончания боя"""
        try:
            combat_id = event_data.get('combat_id')
            result = event_data.get('result')
            
            if combat_id and result:
                return self._end_combat(combat_id, result)
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события окончания боя: {e}")
            return False
    
    def _handle_attack_performed(self, event_data: Dict[str, Any]) -> bool:
        """Обработка события выполнения атаки"""
        try:
            attacker_id = event_data.get('attacker_id')
            target_id = event_data.get('target_id')
            attack_data = event_data.get('attack_data')
            
            if attacker_id and target_id and attack_data:
                return self.perform_attack(attacker_id, target_id, attack_data) is not None
            return False
            
        except Exception as e:
            logger.error(f"Ошибка обработки события выполнения атаки: {e}")
            return False
    
    def start_combat(self, combat_id: str, participants: List[str]) -> bool:
        """Начало боя между участниками"""
        try:
            if combat_id in self.active_combats:
                logger.warning(f"Бой {combat_id} уже существует")
                return False
            
            if len(self.active_combats) >= self.combat_settings['max_active_combats']:
                logger.warning("Достигнут лимит активных боев")
                return False
            
            # Создаем бой
            combat_data = {
                'id': combat_id,
                'participants': participants,
                'state': CombatState.IN_COMBAT,
                'start_time': time.time(),
                'duration': 0.0,
                'turn': 0,
                'current_attacker': participants[0],
                'ai_turn': False,
                'actions': []
            }
            
            self.active_combats[combat_id] = combat_data
            self.system_stats['combats_started'] += 1
            
            logger.info(f"Бой {combat_id} начат между {len(participants)} участниками")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка начала боя {combat_id}: {e}")
            return False
    
    def perform_attack(self, attacker_id: str, target_id: str, attack_data: Dict[str, Any]) -> Optional[AttackResult]:
        """Выполнение атаки"""
        try:
            # Проверяем, что сущности существуют
            if attacker_id not in self.entity_combat_stats or target_id not in self.entity_combat_stats:
                logger.error(f"Одна из сущностей не найдена: {attacker_id}, {target_id}")
                return None
            
            attacker_stats = self.entity_combat_stats[attacker_id]
            target_stats = self.entity_combat_stats[target_id]
            
            # Проверяем уклонение
            if random.random() < target_stats.dodge_chance:
                result = AttackResult(
                    damage_dealt=0,
                    damage_type=attack_data.get('damage_type', DamageType.PHYSICAL),
                    dodged=True
                )
                return result
            
            # Проверяем блок
            blocked = random.random() < target_stats.block_chance
            block_reduction = target_stats.block_reduction if blocked else 0.0
            
            # Рассчитываем урон
            base_damage = attacker_stats.attack
            damage_modifiers = attack_data.get('damage_modifiers', {})
            
            # Применяем модификаторы
            for modifier_type, value in damage_modifiers.items():
                if modifier_type == "multiplier":
                    base_damage *= value
                elif modifier_type == "bonus":
                    base_damage += value
            
            # Проверяем критический удар
            critical_hit = random.random() < attacker_stats.critical_chance
            if critical_hit:
                base_damage *= attacker_stats.critical_multiplier
            
            # Применяем защиту
            final_damage = max(1, int(base_damage * (1 - target_stats.defense / 100)))
            
            # Применяем блок
            if blocked:
                final_damage = int(final_damage * (1 - block_reduction))
            
            # Наносим урон
            target_stats.health = max(0, target_stats.health - final_damage)
            
            # Создаем результат
            result = AttackResult(
                damage_dealt=final_damage,
                damage_type=attack_data.get('damage_type', DamageType.PHYSICAL),
                critical_hit=critical_hit,
                blocked=blocked,
                dodged=False
            )
            
            # Обновляем статистику
            self.system_stats['total_damage_dealt'] += final_damage
            
            # Записываем действие
            action = CombatAction(
                action_id=f"attack_{int(time.time() * 1000)}",
                action_type="attack",
                source_entity=attacker_id,
                target_entity=target_id,
                timestamp=time.time(),
                data={
                    'damage': final_damage,
                    'damage_type': result.damage_type.value,
                    'critical_hit': critical_hit,
                    'blocked': blocked,
                    'dodged': False
                }
            )
            self.combat_history.append(action)
            
            logger.debug(f"Атака {attacker_id} -> {target_id}: {final_damage} урона")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка выполнения атаки: {e}")
            return None
    
    def get_combat_info(self, combat_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о бое"""
        try:
            if combat_id not in self.active_combats:
                return None
            
            combat_data = self.active_combats[combat_id]
            
            # Получаем статистику участников
            participants_info = {}
            for participant_id in combat_data['participants']:
                if participant_id in self.entity_combat_stats:
                    stats = self.entity_combat_stats[participant_id]
                    participants_info[participant_id] = {
                        'health': stats.health,
                        'max_health': stats.max_health,
                        'mana': stats.mana,
                        'max_mana': stats.max_mana,
                        'alive': stats.health > 0
                    }
            
            return {
                'id': combat_id,
                'state': combat_data['state'].value,
                'start_time': combat_data['start_time'],
                'duration': combat_data['duration'],
                'turn': combat_data['turn'],
                'current_attacker': combat_data['current_attacker'],
                'participants': participants_info,
                'actions_count': len(combat_data['actions'])
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о бое {combat_id}: {e}")
            return None
    
    def _check_combat_end_conditions(self, combat_id: str, combat_data: Dict[str, Any]) -> bool:
        """Проверка условий завершения боя"""
        try:
            participants = combat_data['participants']
            alive_participants = []
            
            # Проверяем, кто жив
            for participant_id in participants:
                if participant_id in self.entity_combat_stats:
                    stats = self.entity_combat_stats[participant_id]
                    if stats.health > 0:
                        alive_participants.append(participant_id)
            
            # Если остался только один участник - победа
            if len(alive_participants) == 1:
                winner = alive_participants[0]
                self._end_combat(combat_id, "victory", winner)
                return True
            
            # Если все мертвы - ничья
            if len(alive_participants) == 0:
                self._end_combat(combat_id, "draw")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Ошибка проверки условий завершения боя {combat_id}: {e}")
            return False
    
    def _process_ai_turn(self, combat_id: str, combat_data: Dict[str, Any]) -> None:
        """Обработка хода AI"""
        try:
            # Простая логика AI - атакуем случайную цель
            current_attacker = combat_data['current_attacker']
            participants = combat_data['participants']
            
            # Ищем живую цель
            targets = [p for p in participants if p != current_attacker and 
                      p in self.entity_combat_stats and 
                      self.entity_combat_stats[p].health > 0]
            
            if targets:
                target = random.choice(targets)
                attack_data = {
                    'damage_type': DamageType.PHYSICAL,
                    'damage_modifiers': {}
                }
                
                self.perform_attack(current_attacker, target, attack_data)
            
            # Передаем ход следующему участнику
            self._next_turn(combat_id, combat_data)
            
        except Exception as e:
            logger.error(f"Ошибка обработки хода AI в бою {combat_id}: {e}")
    
    def _next_turn(self, combat_id: str, combat_data: Dict[str, Any]) -> None:
        """Переход к следующему ходу"""
        try:
            participants = combat_data['participants']
            current_index = participants.index(combat_data['current_attacker'])
            
            # Ищем следующего живого участника
            next_index = (current_index + 1) % len(participants)
            attempts = 0
            
            while attempts < len(participants):
                next_participant = participants[next_index]
                if (next_participant in self.entity_combat_stats and 
                    self.entity_combat_stats[next_participant].health > 0):
                    combat_data['current_attacker'] = next_participant
                    combat_data['turn'] += 1
                    break
                
                next_index = (next_index + 1) % len(participants)
                attempts += 1
            
            # Проверяем, нужно ли передать ход AI
            if combat_data['current_attacker'] in participants:
                # Простая логика - каждый третий ход AI
                combat_data['ai_turn'] = (combat_data['turn'] % 3 == 0)
            
        except Exception as e:
            logger.error(f"Ошибка перехода к следующему ходу в бою {combat_id}: {e}")
    
    def _end_combat(self, combat_id: str, result: str, winner: str = None) -> bool:
        """Завершение боя"""
        try:
            if combat_id not in self.active_combats:
                return False
            
            combat_data = self.active_combats[combat_id]
            
            # Определяем состояние
            if result == "victory" and winner:
                combat_data['state'] = CombatState.VICTORY
                combat_data['winner'] = winner
            elif result == "draw":
                combat_data['state'] = CombatState.DEFEAT
            else:
                combat_data['state'] = CombatState.DEFEAT
            
            # Рассчитываем награды
            if result == "victory" and winner:
                self._calculate_combat_rewards(combat_id, winner)
            
            # Удаляем бой из активных
            del self.active_combats[combat_id]
            self.system_stats['combats_completed'] += 1
            
            logger.info(f"Бой {combat_id} завершен с результатом: {result}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка завершения боя {combat_id}: {e}")
            return False
    
    def _calculate_combat_rewards(self, combat_id: str, winner: str) -> None:
        """Расчет наград за бой"""
        try:
            # Простая система наград
            base_experience = 100
            base_gold = 50
            
            # Множители
            experience_gain = int(base_experience * self.combat_settings['experience_multiplier'])
            gold_gain = int(base_gold * self.combat_settings['gold_multiplier'])
            
            # Обновляем статистику
            self.system_stats['total_experience_gained'] += experience_gain
            self.system_stats['total_gold_gained'] += gold_gain
            
            logger.debug(f"Награды за бой {combat_id}: {experience_gain} опыта, {gold_gain} золота")
            
        except Exception as e:
            logger.error(f"Ошибка расчета наград за бой {combat_id}: {e}")
    
    def get_entity_combat_stats(self, entity_id: str) -> Optional[CombatStats]:
        """Получение боевой статистики сущности"""
        return self.entity_combat_stats.get(entity_id)
    
    def update_entity_combat_stats(self, entity_id: str, stats: CombatStats) -> bool:
        """Обновление боевой статистики сущности"""
        try:
            self.entity_combat_stats[entity_id] = stats
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления боевой статистики сущности {entity_id}: {e}")
            return False
    
    def remove_entity_combat_stats(self, entity_id: str) -> bool:
        """Удаление боевой статистики сущности"""
        try:
            if entity_id in self.entity_combat_stats:
                del self.entity_combat_stats[entity_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка удаления боевой статистики сущности {entity_id}: {e}")
            return False

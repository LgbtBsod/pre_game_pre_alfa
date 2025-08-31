#!/usr/bin/env python3
"""Система боя - интеграция всех боевых механик
Управление боем, атаками, защитой, инициативой и комбо"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import *
from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
import math
import time
import random

from src.core.architecture import BaseComponent, ComponentType, Priority, LifecycleState

logger = logging.getLogger(__name__)

# = ТИПЫ БОЯ

class CombatType(Enum):
    """Типы боя"""
    TURN_BASED = "turn_based"      # Пошаговый бой
    REAL_TIME = "real_time"        # Бой в реальном времени
    HYBRID = "hybrid"              # Гибридный бой

class AttackType(Enum):
    """Типы атак"""
    MELEE = "melee"                # Ближний бой
    RANGED = "ranged"              # Дальний бой
    MAGIC = "magic"                # Магическая атака
    AREA = "area"                  # Областная атака
    SPECIAL = "special"            # Специальная атака

class DefenseType(Enum):
    """Типы защиты"""
    ARMOR = "armor"                # Броня
    SHIELD = "shield"              # Щит
    DODGE = "dodge"                # Уклонение
    BLOCK = "block"                # Блок
    RESISTANCE = "resistance"      # Сопротивление

# = СТРУКТУРЫ ДАННЫХ

@dataclass
class CombatStats:
    """Боевые характеристики"""
    attack_power: float = 10.0
    defense: float = 5.0
    critical_chance: float = 0.05
    critical_multiplier: float = 2.0
    accuracy: float = 0.8
    dodge_chance: float = 0.1
    block_chance: float = 0.05
    initiative: float = 10.0
    attack_speed: float = 1.0
    range: float = 2.0

@dataclass
class DamageInfo:
    """Информация об уроне"""
    base_damage: float
    damage_type: str
    source: str
    target: str
    is_critical: bool = False
    is_blocked: bool = False
    is_dodged: bool = False
    final_damage: float = 0.0
    resistances_applied: Dict[str, float] = field(default_factory=dict)
    modifiers_applied: List[str] = field(default_factory=list)

@dataclass
class CombatAction:
    """Боевое действие"""
    action_id: str
    actor_id: str
    target_id: Optional[str] = None
    action_type: str  # attack, skill, item, defend
    skill_id: Optional[str] = None
    item_id: Optional[str] = None
    priority: int = 0
    initiative_cost: float = 0.0
    created_at: float = field(default_factory=time.time)

@dataclass
class CombatTurn:
    """Ход в бою"""
    turn_number: int
    actor_id: str
    actions: List[CombatAction] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    is_completed: bool = False

@dataclass
class CombatSession:
    """Сессия боя"""
    session_id: str
    participants: List[str] = field(default_factory=list)
    turn_order: List[str] = field(default_factory=list)
    current_turn: Optional[CombatTurn] = None
    turn_number: int = 1
    combat_type: CombatType = CombatType.TURN_BASED
    is_active: bool = True
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    winner: Optional[str] = None

@dataclass
class CombatResult:
    """Результат боя"""
    session_id: str
    winner: str
    participants: List[str]
    duration: float
    total_damage_dealt: Dict[str, float]
    total_damage_taken: Dict[str, float]
    critical_hits: Dict[str, int]
    skills_used: Dict[str, int]
    effects_applied: Dict[str, int]

class CombatSystem(BaseComponent):
    """Система боя"""
    
    def __init__(self):
        super().__init__(
            component_id="combat_system",
            component_type=ComponentType.SYSTEM,
            priority=Priority.HIGH
        )
        
        # Активные сессии боя
        self.active_sessions: Dict[str, CombatSession] = {}
        self.combat_stats: Dict[str, CombatStats] = {}
        
        # Интеграция с другими системами
        self.effect_system = None
        self.skill_system = None
        self.evolution_system = None
        self.ai_system = None
        
        # Статистика
        self.total_combats: int = 0
        self.total_damage_dealt: float = 0.0
        self.combat_statistics: Dict[str, int] = {}
        
        # Callbacks
        self.on_combat_start: Optional[Callable] = None
        self.on_combat_end: Optional[Callable] = None
        self.on_turn_start: Optional[Callable] = None
        self.on_turn_end: Optional[Callable] = None
        self.on_damage_dealt: Optional[Callable] = None
        self.on_entity_defeated: Optional[Callable] = None
        
        logger.info("Система боя инициализирована")
    
    def initialize(self) -> bool:
        """Инициализация системы боя"""
        try:
            logger.info("Инициализация системы боя...")
            
            # Создание базовых боевых характеристик
            if not self._create_base_combat_stats():
                return False
            
            self.state = LifecycleState.READY
            logger.info("Система боя успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации системы боя: {e}")
            self.state = LifecycleState.ERROR
            return False
    
    def _create_base_combat_stats(self) -> bool:
        """Создание базовых боевых характеристик"""
        try:
            # Базовые характеристики для разных типов сущностей
            base_stats = {
                "player": CombatStats(
                    attack_power=15.0,
                    defense=8.0,
                    critical_chance=0.08,
                    critical_multiplier=2.2,
                    accuracy=0.85,
                    dodge_chance=0.12,
                    block_chance=0.08,
                    initiative=12.0,
                    attack_speed=1.2,
                    range=3.0
                ),
                "enemy": CombatStats(
                    attack_power=12.0,
                    defense=6.0,
                    critical_chance=0.05,
                    critical_multiplier=2.0,
                    accuracy=0.75,
                    dodge_chance=0.08,
                    block_chance=0.05,
                    initiative=10.0,
                    attack_speed=1.0,
                    range=2.0
                ),
                "boss": CombatStats(
                    attack_power=25.0,
                    defense=15.0,
                    critical_chance=0.12,
                    critical_multiplier=2.5,
                    accuracy=0.9,
                    dodge_chance=0.15,
                    block_chance=0.12,
                    initiative=15.0,
                    attack_speed=0.8,
                    range=4.0
                ),
                "mutant": CombatStats(
                    attack_power=18.0,
                    defense=10.0,
                    critical_chance=0.1,
                    critical_multiplier=2.3,
                    accuracy=0.8,
                    dodge_chance=0.1,
                    block_chance=0.06,
                    initiative=11.0,
                    attack_speed=1.1,
                    range=2.5
                )
            }
            
            for entity_type, stats in base_stats.items():
                self.combat_stats[entity_type] = stats
            
            logger.info(f"Создано {len(self.combat_stats)} базовых боевых характеристик")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания базовых боевых характеристик: {e}")
            return False
    
    def set_system_integrations(self, effect_system=None, skill_system=None, 
                               evolution_system=None, ai_system=None):
        """Установка интеграций с другими системами"""
        try:
            self.effect_system = effect_system
            self.skill_system = skill_system
            self.evolution_system = evolution_system
            self.ai_system = ai_system
            
            logger.info("Интеграции с другими системами установлены")
            
        except Exception as e:
            logger.error(f"Ошибка установки интеграций: {e}")
    
    def start_combat(self, participants: List[str], combat_type: CombatType = CombatType.TURN_BASED) -> str:
        """Начало боя"""
        try:
            if len(participants) < 2:
                logger.error("Для боя нужно минимум 2 участника")
                return ""
            
            session_id = f"combat_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Создание сессии боя
            session = CombatSession(
                session_id=session_id,
                participants=participants.copy(),
                combat_type=combat_type
            )
            
            # Определение порядка ходов
            session.turn_order = self._calculate_turn_order(participants)
            
            # Создание первого хода
            if session.turn_order:
                session.current_turn = CombatTurn(
                    turn_number=1,
                    actor_id=session.turn_order[0]
                )
            
            self.active_sessions[session_id] = session
            
            # Обновление статистики
            self.total_combats += 1
            
            # Вызов callback
            if self.on_combat_start:
                self.on_combat_start(session_id, participants)
            
            logger.info(f"Бой {session_id} начат с участниками: {participants}")
            return session_id
            
        except Exception as e:
            logger.error(f"Ошибка начала боя: {e}")
            return ""
    
    def _calculate_turn_order(self, participants: List[str]) -> List[str]:
        """Расчет порядка ходов на основе инициативы"""
        try:
            # Получение инициативы участников
            initiative_data = []
            for participant in participants:
                stats = self.get_combat_stats(participant)
                initiative = stats.initiative + random.uniform(-2, 2)  # Небольшая случайность
                initiative_data.append((participant, initiative))
            
            # Сортировка по инициативе (высокая инициатива ходит первой)
            initiative_data.sort(key=lambda x: x[1], reverse=True)
            
            return [participant for participant, _ in initiative_data]
            
        except Exception as e:
            logger.error(f"Ошибка расчета порядка ходов: {e}")
            return participants.copy()
    
    def get_combat_stats(self, entity_id: str) -> CombatStats:
        """Получение боевых характеристик сущности"""
        try:
            # Определение типа сущности
            entity_type = self._get_entity_type(entity_id)
            
            if entity_type in self.combat_stats:
                base_stats = self.combat_stats[entity_type]
                
                # Применение модификаторов от эффектов
                if self.effect_system:
                    modifiers = self.effect_system.get_effect_modifiers(entity_id, "combat")
                    # Здесь должна быть логика применения модификаторов
                
                # Применение модификаторов от эволюции
                if self.evolution_system:
                    evolution_bonus = self.evolution_system.get_combat_bonus(entity_id)
                    # Здесь должна быть логика применения бонусов эволюции
                
                return base_stats
            
            # Возврат базовых характеристик если тип не определен
            return CombatStats()
            
        except Exception as e:
            logger.error(f"Ошибка получения боевых характеристик: {e}")
            return CombatStats()
    
    def _get_entity_type(self, entity_id: str) -> str:
        """Определение типа сущности"""
        try:
            # Здесь должна быть логика определения типа сущности
            # Пока возвращаем базовый тип
            if "player" in entity_id.lower():
                return "player"
            elif "boss" in entity_id.lower():
                return "boss"
            elif "mutant" in entity_id.lower():
                return "mutant"
            else:
                return "enemy"
                
        except Exception as e:
            logger.error(f"Ошибка определения типа сущности: {e}")
            return "enemy"
    
    def perform_attack(self, session_id: str, attacker_id: str, target_id: str, 
                      attack_type: AttackType = AttackType.MELEE) -> Optional[DamageInfo]:
        """Выполнение атаки"""
        try:
            if session_id not in self.active_sessions:
                logger.error(f"Сессия боя {session_id} не найдена")
                return None
            
            session = self.active_sessions[session_id]
            
            if not session.is_active:
                logger.error(f"Бой {session_id} уже завершен")
                return None
            
            # Получение боевых характеристик
            attacker_stats = self.get_combat_stats(attacker_id)
            target_stats = self.get_combat_stats(target_id)
            
            # Проверка точности
            if not self._check_accuracy(attacker_stats, target_stats):
                logger.info(f"Атака {attacker_id} промахнулась по {target_id}")
                return DamageInfo(
                    base_damage=0,
                    damage_type="miss",
                    source=attacker_id,
                    target=target_id,
                    final_damage=0
                )
            
            # Проверка уклонения
            if self._check_dodge(target_stats):
                logger.info(f"Цель {target_id} уклонилась от атаки {attacker_id}")
                return DamageInfo(
                    base_damage=0,
                    damage_type="dodge",
                    source=attacker_id,
                    target=target_id,
                    is_dodged=True,
                    final_damage=0
                )
            
            # Проверка блока
            is_blocked = self._check_block(target_stats)
            
            # Расчет базового урона
            base_damage = self._calculate_base_damage(attacker_stats, attack_type)
            
            # Проверка критического удара
            is_critical = self._check_critical_hit(attacker_stats)
            if is_critical:
                base_damage *= attacker_stats.critical_multiplier
            
            # Применение защиты
            final_damage = self._apply_defense(base_damage, target_stats, is_blocked)
            
            # Создание информации об уроне
            damage_info = DamageInfo(
                base_damage=base_damage,
                damage_type=attack_type.value,
                source=attacker_id,
                target=target_id,
                is_critical=is_critical,
                is_blocked=is_blocked,
                final_damage=final_damage
            )
            
            # Применение урона к цели
            self._apply_damage(target_id, damage_info)
            
            # Применение эффектов атаки
            self._apply_attack_effects(attacker_id, target_id, damage_info)
            
            # Обновление статистики
            self.total_damage_dealt += final_damage
            self.combat_statistics["attacks"] = self.combat_statistics.get("attacks", 0) + 1
            
            # Вызов callback
            if self.on_damage_dealt:
                self.on_damage_dealt(attacker_id, target_id, damage_info)
            
            logger.info(f"Атака {attacker_id} -> {target_id}: {final_damage} урона")
            return damage_info
            
        except Exception as e:
            logger.error(f"Ошибка выполнения атаки: {e}")
            return None
    
    def _check_accuracy(self, attacker_stats: CombatStats, target_stats: CombatStats) -> bool:
        """Проверка точности атаки"""
        try:
            accuracy = attacker_stats.accuracy
            dodge = target_stats.dodge_chance
            
            # Базовая проверка точности
            hit_chance = accuracy - dodge
            return random.random() < hit_chance
            
        except Exception as e:
            logger.error(f"Ошибка проверки точности: {e}")
            return True
    
    def _check_dodge(self, target_stats: CombatStats) -> bool:
        """Проверка уклонения"""
        try:
            return random.random() < target_stats.dodge_chance
            
        except Exception as e:
            logger.error(f"Ошибка проверки уклонения: {e}")
            return False
    
    def _check_block(self, target_stats: CombatStats) -> bool:
        """Проверка блока"""
        try:
            return random.random() < target_stats.block_chance
            
        except Exception as e:
            logger.error(f"Ошибка проверки блока: {e}")
            return False
    
    def _check_critical_hit(self, attacker_stats: CombatStats) -> bool:
        """Проверка критического удара"""
        try:
            return random.random() < attacker_stats.critical_chance
            
        except Exception as e:
            logger.error(f"Ошибка проверки критического удара: {e}")
            return False
    
    def _calculate_base_damage(self, attacker_stats: CombatStats, attack_type: AttackType) -> float:
        """Расчет базового урона"""
        try:
            base_damage = attacker_stats.attack_power
            
            # Модификаторы по типу атаки
            type_modifiers = {
                AttackType.MELEE: 1.0,
                AttackType.RANGED: 0.8,
                AttackType.MAGIC: 1.2,
                AttackType.AREA: 0.6,
                AttackType.SPECIAL: 1.5
            }
            
            base_damage *= type_modifiers.get(attack_type, 1.0)
            
            # Добавление случайности
            variation = random.uniform(0.8, 1.2)
            base_damage *= variation
            
            return max(1, base_damage)
            
        except Exception as e:
            logger.error(f"Ошибка расчета базового урона: {e}")
            return 10.0
    
    def _apply_defense(self, damage: float, target_stats: CombatStats, is_blocked: bool) -> float:
        """Применение защиты"""
        try:
            final_damage = damage
            
            # Применение брони
            armor_reduction = target_stats.defense * 0.1  # 1 защита = 10% снижение урона
            final_damage *= (1 - armor_reduction)
            
            # Применение блока
            if is_blocked:
                final_damage *= 0.5  # Блок снижает урон на 50%
            
            return max(1, final_damage)
            
        except Exception as e:
            logger.error(f"Ошибка применения защиты: {e}")
            return damage
    
    def _apply_damage(self, target_id: str, damage_info: DamageInfo):
        """Применение урона к цели"""
        try:
            # Здесь должна быть интеграция с системой здоровья сущности
            # Например: target.take_damage(damage_info.final_damage)
            
            # Проверка поражения
            if self._is_entity_defeated(target_id):
                self._handle_entity_defeat(target_id, damage_info.source)
            
        except Exception as e:
            logger.error(f"Ошибка применения урона: {e}")
    
    def _apply_attack_effects(self, attacker_id: str, target_id: str, damage_info: DamageInfo):
        """Применение эффектов атаки"""
        try:
            # Применение эффектов от навыков
            if self.skill_system:
                # Здесь должна быть логика применения эффектов навыков
                pass
            
            # Применение эффектов от эволюции
            if self.evolution_system:
                evolution_effects = self.evolution_system.get_attack_effects(attacker_id)
                # Здесь должна быть логика применения эффектов эволюции
                pass
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов атаки: {e}")
    
    def _is_entity_defeated(self, entity_id: str) -> bool:
        """Проверка поражения сущности"""
        try:
            # Здесь должна быть проверка здоровья сущности
            # Пока возвращаем False
            return False
            
        except Exception as e:
            logger.error(f"Ошибка проверки поражения: {e}")
            return False
    
    def _handle_entity_defeat(self, defeated_id: str, killer_id: str):
        """Обработка поражения сущности"""
        try:
            # Обновление статистики
            self.combat_statistics["defeats"] = self.combat_statistics.get("defeats", 0) + 1
            
            # Вызов callback
            if self.on_entity_defeated:
                self.on_entity_defeated(defeated_id, killer_id)
            
            logger.info(f"Сущность {defeated_id} поражена {killer_id}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки поражения: {e}")
    
    def use_skill_in_combat(self, session_id: str, user_id: str, skill_id: str, 
                           target_id: Optional[str] = None) -> bool:
        """Использование навыка в бою"""
        try:
            if not self.skill_system:
                logger.error("Система навыков не интегрирована")
                return False
            
            if not self.skill_system.has_skill(user_id, skill_id):
                logger.error(f"Сущность {user_id} не знает навык {skill_id}")
                return False
            
            # Использование навыка
            success = self.skill_system.use_skill(user_id, skill_id, target_id)
            
            if success:
                # Обновление статистики
                self.combat_statistics["skills_used"] = self.combat_statistics.get("skills_used", 0) + 1
                
                logger.info(f"Навык {skill_id} использован в бою {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Ошибка использования навыка в бою: {e}")
            return False
    
    def end_turn(self, session_id: str) -> bool:
        """Завершение хода"""
        try:
            if session_id not in self.active_sessions:
                return False
            
            session = self.active_sessions[session_id]
            
            if not session.current_turn:
                return False
            
            # Завершение текущего хода
            session.current_turn.end_time = time.time()
            session.current_turn.is_completed = True
            
            # Вызов callback
            if self.on_turn_end:
                self.on_turn_end(session_id, session.current_turn)
            
            # Переход к следующему ходу
            self._next_turn(session)
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка завершения хода: {e}")
            return False
    
    def _next_turn(self, session: CombatSession):
        """Переход к следующему ходу"""
        try:
            # Поиск следующего участника
            current_index = session.turn_order.index(session.current_turn.actor_id)
            next_index = (current_index + 1) % len(session.turn_order)
            next_actor = session.turn_order[next_index]
            
            # Проверка завершения раунда
            if next_index == 0:
                session.turn_number += 1
            
            # Создание нового хода
            session.current_turn = CombatTurn(
                turn_number=session.turn_number,
                actor_id=next_actor
            )
            
            # Вызов callback
            if self.on_turn_start:
                self.on_turn_start(session.session_id, session.current_turn)
            
            logger.debug(f"Переход к ходу {session.turn_number}, актор: {next_actor}")
            
        except Exception as e:
            logger.error(f"Ошибка перехода к следующему ходу: {e}")
    
    def end_combat(self, session_id: str, winner: Optional[str] = None) -> Optional[CombatResult]:
        """Завершение боя"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            if not session.is_active:
                return None
            
            # Завершение сессии
            session.is_active = False
            session.end_time = time.time()
            session.winner = winner
            
            # Создание результата боя
            result = CombatResult(
                session_id=session_id,
                winner=winner or "unknown",
                participants=session.participants.copy(),
                duration=session.end_time - session.start_time,
                total_damage_dealt={},  # Здесь должна быть статистика урона
                total_damage_taken={},  # Здесь должна быть статистика полученного урона
                critical_hits={},       # Здесь должна быть статистика критических ударов
                skills_used={},         # Здесь должна быть статистика использованных навыков
                effects_applied={}      # Здесь должна быть статистика примененных эффектов
            )
            
            # Вызов callback
            if self.on_combat_end:
                self.on_combat_end(session_id, result)
            
            # Удаление сессии
            del self.active_sessions[session_id]
            
            logger.info(f"Бой {session_id} завершен, победитель: {winner}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка завершения боя: {e}")
            return None
    
    def get_active_combats(self) -> List[str]:
        """Получение списка активных боев"""
        try:
            return list(self.active_sessions.keys())
            
        except Exception as e:
            logger.error(f"Ошибка получения активных боев: {e}")
            return []
    
    def get_combat_session(self, session_id: str) -> Optional[CombatSession]:
        """Получение сессии боя"""
        try:
            return self.active_sessions.get(session_id)
            
        except Exception as e:
            logger.error(f"Ошибка получения сессии боя: {e}")
            return None
    
    def get_combat_statistics(self) -> Dict[str, Any]:
        """Получение статистики боев"""
        try:
            return {
                "total_combats": self.total_combats,
                "total_damage_dealt": self.total_damage_dealt,
                "active_combats": len(self.active_sessions),
                "combat_statistics": self.combat_statistics.copy()
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики боев: {e}")
            return {}
    
    def cleanup(self):
        """Очистка системы боя"""
        try:
            # Завершение всех активных боев
            for session_id in list(self.active_sessions.keys()):
                self.end_combat(session_id, "system_cleanup")
            
            # Очистка данных
            self.combat_stats.clear()
            self.combat_statistics.clear()
            
            logger.info("Система боя очищена")
            
        except Exception as e:
            logger.error(f"Ошибка очистки системы боя: {e}")

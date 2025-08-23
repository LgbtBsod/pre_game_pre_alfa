#!/usr/bin/env python3
"""
Система обучения сражениям для эволюционной адаптации.
Обучает ИИ эффективно сражаться, находить уязвимости и выбирать оружие.
"""

import random
import math
import json
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import numpy as np

logger = logging.getLogger(__name__)


class CombatAction(Enum):
    """Типы боевых действий"""
    ATTACK_MELEE = "attack_melee"
    ATTACK_RANGED = "attack_ranged"
    ATTACK_MAGIC = "attack_magic"
    DEFEND = "defend"
    DODGE = "dodge"
    USE_ITEM = "use_item"
    SWITCH_WEAPON = "switch_weapon"
    RETREAT = "retreat"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"


class VulnerabilityType(Enum):
    """Типы уязвимостей"""
    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    MAGIC = "magic"
    RADIATION = "radiation"
    COSMIC = "cosmic"
    NONE = "none"


@dataclass
class EnemyVulnerability:
    """Уязвимость врага"""
    enemy_type: str
    damage_type: str
    vulnerability_multiplier: float
    discovered_by: str
    discovery_time: float
    confidence: float = 0.5  # Уверенность в уязвимости (0.0 - 1.0)
    
    def update_confidence(self, success: bool, damage_dealt: float):
        """Обновление уверенности в уязвимости"""
        if success:
            self.confidence = min(1.0, self.confidence + 0.1)
        else:
            self.confidence = max(0.0, self.confidence - 0.05)


@dataclass
class WeaponEffectiveness:
    """Эффективность оружия против типа врага"""
    weapon_type: str
    enemy_type: str
    effectiveness_score: float
    damage_dealt: float
    battles_won: int
    battles_lost: int
    last_updated: float
    
    def update_effectiveness(self, damage_dealt: float, battle_won: bool):
        """Обновление эффективности оружия"""
        self.damage_dealt = (self.damage_dealt + damage_dealt) / 2
        if battle_won:
            self.battles_won += 1
        else:
            self.battles_lost += 1
        
        # Пересчёт общего счёта
        total_battles = self.battles_won + self.battles_lost
        if total_battles > 0:
            win_rate = self.battles_won / total_battles
            self.effectiveness_score = (win_rate * 0.6 + 
                                      (self.damage_dealt / 100.0) * 0.4)


@dataclass
class ItemUsagePattern:
    """Паттерн использования предметов"""
    item_type: str
    situation: str  # "low_health", "low_stamina", "enemy_debuff", etc.
    success_rate: float
    usage_count: int
    last_used: float
    
    def update_pattern(self, success: bool):
        """Обновление паттерна использования"""
        self.usage_count += 1
        if success:
            self.success_rate = (self.success_rate * (self.usage_count - 1) + 1.0) / self.usage_count
        else:
            self.success_rate = (self.success_rate * (self.usage_count - 1) + 0.0) / self.usage_count


class CombatLearningSystem:
    """Система обучения сражениям"""
    
    def __init__(self, entity_id: str):
        self.entity_id = entity_id
        
        # Обнаруженные уязвимости врагов
        self.enemy_vulnerabilities: Dict[str, List[EnemyVulnerability]] = {}
        
        # Эффективность оружия
        self.weapon_effectiveness: Dict[str, List[WeaponEffectiveness]] = {}
        
        # Паттерны использования предметов
        self.item_usage_patterns: Dict[str, List[ItemUsagePattern]] = {}
        
        # История боёв
        self.combat_history: List[Dict[str, Any]] = []
        
        # Статистика обучения
        self.learning_stats = {
            "total_battles": 0,
            "battles_won": 0,
            "vulnerabilities_discovered": 0,
            "weapon_mastery": 0.0,
            "item_efficiency": 0.0
        }
        
        # Q-learning для боевых решений
        self.combat_q_table = {}
        
        logger.info(f"Система обучения сражениям инициализирована для {entity_id}")
    
    def learn_from_combat(self, combat_data: Dict[str, Any]):
        """Обучение на основе данных боя"""
        try:
            # Запись в историю
            self.combat_history.append(combat_data)
            
            # Обновление статистики
            self.learning_stats["total_battles"] += 1
            if combat_data.get("victory", False):
                self.learning_stats["battles_won"] += 1
            
            # Анализ эффективности оружия
            self._analyze_weapon_effectiveness(combat_data)
            
            # Анализ уязвимостей
            self._analyze_vulnerabilities(combat_data)
            
            # Анализ использования предметов
            self._analyze_item_usage(combat_data)
            
            # Обновление общих статистик
            self._update_learning_stats()
            
            logger.info(f"Обучение на основе боя завершено для {self.entity_id}")
            
        except Exception as e:
            logger.error(f"Ошибка обучения на основе боя: {e}")
    
    def _analyze_weapon_effectiveness(self, combat_data: Dict[str, Any]):
        """Анализ эффективности оружия"""
        weapon_used = combat_data.get("weapon_used")
        enemy_type = combat_data.get("enemy_type")
        damage_dealt = combat_data.get("damage_dealt", 0)
        battle_won = combat_data.get("victory", False)
        
        if not all([weapon_used, enemy_type]):
            return
        
        # Поиск существующей записи
        weapon_key = f"{weapon_used}_{enemy_type}"
        if weapon_key not in self.weapon_effectiveness:
            self.weapon_effectiveness[weapon_key] = []
        
        # Обновление или создание записи
        existing = None
        for record in self.weapon_effectiveness[weapon_key]:
            if record.weapon_type == weapon_used and record.enemy_type == enemy_type:
                existing = record
                break
        
        if existing:
            existing.update_effectiveness(damage_dealt, battle_won)
        else:
            new_record = WeaponEffectiveness(
                weapon_type=weapon_used,
                enemy_type=enemy_type,
                effectiveness_score=0.5,
                damage_dealt=damage_dealt,
                battles_won=1 if battle_won else 0,
                battles_lost=0 if battle_won else 1,
                last_updated=combat_data.get("timestamp", 0)
            )
            self.weapon_effectiveness[weapon_key].append(new_record)
    
    def _analyze_vulnerabilities(self, combat_data: Dict[str, Any]):
        """Анализ уязвимостей врагов"""
        enemy_type = combat_data.get("enemy_type")
        damage_type = combat_data.get("damage_type")
        damage_dealt = combat_data.get("damage_dealt", 0)
        expected_damage = combat_data.get("expected_damage", 0)
        
        if not all([enemy_type, damage_type]):
            return
        
        # Определение уязвимости на основе превышения ожидаемого урона
        if expected_damage > 0 and damage_dealt > expected_damage * 1.5:
            vulnerability_multiplier = damage_dealt / expected_damage
            
            # Поиск существующей уязвимости
            existing_vulnerability = None
            if enemy_type in self.enemy_vulnerabilities:
                for vuln in self.enemy_vulnerabilities[enemy_type]:
                    if vuln.damage_type == damage_type:
                        existing_vulnerability = vuln
                        break
            
            if existing_vulnerability:
                # Обновление существующей уязвимости
                existing_vulnerability.update_confidence(True, damage_dealt)
                existing_vulnerability.vulnerability_multiplier = (
                    existing_vulnerability.vulnerability_multiplier * 0.9 + 
                    vulnerability_multiplier * 0.1
                )
            else:
                # Создание новой уязвимости
                new_vulnerability = EnemyVulnerability(
                    enemy_type=enemy_type,
                    damage_type=damage_type,
                    vulnerability_multiplier=vulnerability_multiplier,
                    discovered_by=self.entity_id,
                    discovery_time=combat_data.get("timestamp", 0),
                    confidence=0.7
                )
                
                if enemy_type not in self.enemy_vulnerabilities:
                    self.enemy_vulnerabilities[enemy_type] = []
                
                self.enemy_vulnerabilities[enemy_type].append(new_vulnerability)
                self.learning_stats["vulnerabilities_discovered"] += 1
    
    def _analyze_item_usage(self, combat_data: Dict[str, Any]):
        """Анализ использования предметов"""
        items_used = combat_data.get("items_used", [])
        situation = combat_data.get("situation", "unknown")
        
        for item_data in items_used:
            item_type = item_data.get("type")
            success = item_data.get("success", True)
            
            if not item_type:
                continue
            
            # Поиск существующего паттерна
            existing_pattern = None
            if item_type in self.item_usage_patterns:
                for pattern in self.item_usage_patterns[item_type]:
                    if pattern.situation == situation:
                        existing_pattern = pattern
                        break
            
            if existing_pattern:
                existing_pattern.update_pattern(success)
            else:
                new_pattern = ItemUsagePattern(
                    item_type=item_type,
                    situation=situation,
                    success_rate=1.0 if success else 0.0,
                    usage_count=1,
                    last_used=combat_data.get("timestamp", 0)
                )
                
                if item_type not in self.item_usage_patterns:
                    self.item_usage_patterns[item_type] = []
                
                self.item_usage_patterns[item_type].append(new_pattern)
    
    def _update_learning_stats(self):
        """Обновление общих статистик обучения"""
        # Мастерство оружия
        total_weapon_score = 0
        weapon_count = 0
        
        for weapon_records in self.weapon_effectiveness.values():
            for record in weapon_records:
                total_weapon_score += record.effectiveness_score
                weapon_count += 1
        
        if weapon_count > 0:
            self.learning_stats["weapon_mastery"] = total_weapon_score / weapon_count
        
        # Эффективность предметов
        total_item_score = 0
        item_count = 0
        
        for item_records in self.item_usage_patterns.values():
            for record in item_records:
                total_item_score += record.success_rate
                item_count += 1
        
        if item_count > 0:
            self.learning_stats["item_efficiency"] = total_item_score / item_count
    
    def get_best_weapon_against(self, enemy_type: str) -> Optional[str]:
        """Получение лучшего оружия против конкретного врага"""
        best_weapon = None
        best_score = 0.0
        
        for weapon_key, records in self.weapon_effectiveness.items():
            for record in records:
                if record.enemy_type == enemy_type and record.effectiveness_score > best_score:
                    best_score = record.effectiveness_score
                    best_weapon = record.weapon_type
        
        return best_weapon
    
    def get_enemy_vulnerabilities(self, enemy_type: str) -> List[EnemyVulnerability]:
        """Получение уязвимостей врага"""
        return self.enemy_vulnerabilities.get(enemy_type, [])
    
    def get_best_item_for_situation(self, situation: str) -> Optional[str]:
        """Получение лучшего предмета для конкретной ситуации"""
        best_item = None
        best_score = 0.0
        
        for item_type, patterns in self.item_usage_patterns.items():
            for pattern in patterns:
                if pattern.situation == situation and pattern.success_rate > best_score:
                    best_score = pattern.success_rate
                    best_item = item_type
        
        return best_item
    
    def recommend_combat_action(self, enemy_type: str, current_health: float, 
                              available_weapons: List[str], available_items: List[str]) -> CombatAction:
        """Рекомендация боевого действия"""
        # Приоритеты действий
        if current_health < 0.3:  # Низкое здоровье
            if available_items:
                return CombatAction.USE_ITEM
        
        # Поиск лучшего оружия
        best_weapon = self.get_best_weapon_against(enemy_type)
        if best_weapon and best_weapon in available_weapons:
            return CombatAction.SWITCH_WEAPON
        
        # Проверка уязвимостей
        vulnerabilities = self.get_enemy_vulnerabilities(enemy_type)
        if vulnerabilities:
            # Выбор атаки на основе уязвимости
            best_vulnerability = max(vulnerabilities, key=lambda v: v.confidence * v.vulnerability_multiplier)
            if best_vulnerability.damage_type == "physical":
                return CombatAction.ATTACK_MELEE
            elif best_vulnerability.damage_type in ["fire", "ice", "lightning"]:
                return CombatAction.ATTACK_MAGIC
            else:
                return CombatAction.ATTACK_RANGED
        
        # По умолчанию
        return CombatAction.ATTACK_MELEE
    
    def get_learning_report(self) -> Dict[str, Any]:
        """Получение отчёта об обучении"""
        return {
            "entity_id": self.entity_id,
            "learning_stats": self.learning_stats.copy(),
            "vulnerabilities_discovered": sum(len(vulns) for vulns in self.enemy_vulnerabilities.values()),
            "weapons_mastered": len(self.weapon_effectiveness),
            "items_mastered": len(self.item_usage_patterns),
            "combat_history_length": len(self.combat_history)
        }
    
    def save_combat_knowledge(self, filepath: str) -> bool:
        """Сохранение боевых знаний"""
        try:
            combat_knowledge = {
                "enemy_vulnerabilities": {
                    enemy_type: [vuln.__dict__ for vuln in vulns]
                    for enemy_type, vulns in self.enemy_vulnerabilities.items()
                },
                "weapon_effectiveness": {
                    weapon_key: [record.__dict__ for record in records]
                    for weapon_key, records in self.weapon_effectiveness.items()
                },
                "item_usage_patterns": {
                    item_type: [pattern.__dict__ for pattern in patterns]
                    for item_type, patterns in self.item_usage_patterns.items()
                },
                "learning_stats": self.learning_stats,
                "combat_history": self.combat_history[-100:]  # Последние 100 боёв
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(combat_knowledge, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Боевые знания сохранены в {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения боевых знаний: {e}")
            return False
    
    def load_combat_knowledge(self, filepath: str) -> bool:
        """Загрузка боевых знаний"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                combat_knowledge = json.load(f)
            
            # Восстановление уязвимостей
            self.enemy_vulnerabilities = {}
            for enemy_type, vulns_data in combat_knowledge.get("enemy_vulnerabilities", {}).items():
                self.enemy_vulnerabilities[enemy_type] = [
                    EnemyVulnerability(**vuln_data) for vuln_data in vulns_data
                ]
            
            # Восстановление эффективности оружия
            self.weapon_effectiveness = {}
            for weapon_key, records_data in combat_knowledge.get("weapon_effectiveness", {}).items():
                self.weapon_effectiveness[weapon_key] = [
                    WeaponEffectiveness(**record_data) for record_data in records_data
                ]
            
            # Восстановление паттернов предметов
            self.item_usage_patterns = {}
            for item_type, patterns_data in combat_knowledge.get("item_usage_patterns", {}).items():
                self.item_usage_patterns[item_type] = [
                    ItemUsagePattern(**pattern_data) for pattern_data in patterns_data
                ]
            
            # Восстановление статистик
            self.learning_stats = combat_knowledge.get("learning_stats", self.learning_stats)
            self.combat_history = combat_knowledge.get("combat_history", [])
            
            logger.info(f"Боевые знания загружены из {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки боевых знаний: {e}")
            return False

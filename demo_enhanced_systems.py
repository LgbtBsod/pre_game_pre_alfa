#!/usr/bin/env python3
"""
Демонстрация улучшенных систем AI-EVOLVE.
Показывает работу новых механик: памяти поколений, эмоционального влияния,
улучшенного боевого обучения и системы ловушек.
"""

import time
import random
import logging
from typing import Dict, List, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Импорт новых систем
from core.generational_memory_system import (
    GenerationalMemorySystem, MemoryType, MemoryIntensity
)
from core.emotional_ai_influence import (
    EmotionalAIInfluenceSystem, EmotionalInfluenceType
)
from core.enhanced_combat_learning import (
    EnhancedCombatLearningAI, CombatContext, CombatPhase, PlayerStyle
)
from core.trap_and_hazard_system import (
    TrapAndHazardSystem, HazardType, TrapType, ChestType
)


def demo_generational_memory():
    """Демонстрация системы памяти поколений"""
    logger.info("=== ДЕМОНСТРАЦИЯ СИСТЕМЫ ПАМЯТИ ПОКОЛЕНИЙ ===")
    
    # Инициализация системы
    memory_system = GenerationalMemorySystem()
    
    # Добавление различных типов воспоминаний
    logger.info("Добавление боевых воспоминаний...")
    
    # Боевой опыт
    memory_system.add_memory(
        MemoryType.COMBAT_EXPERIENCE,
        {
            "enemy_type": "boss",
            "weapon_used": "sword",
            "victory": True,
            "damage_dealt": 150,
            "damage_taken": 30
        },
        intensity=0.8,
        emotional_impact=0.7
    )
    
    # Паттерны врагов
    memory_system.add_memory(
        MemoryType.ENEMY_PATTERNS,
        {
            "enemy_type": "boss",
            "effective_counter": "fire_magic",
            "weakness": "ice",
            "attack_pattern": "circular_sweep"
        },
        intensity=0.9,
        emotional_impact=0.6
    )
    
    # Эмоциональная травма
    memory_system.add_memory(
        MemoryType.EMOTIONAL_TRAUMA,
        {
            "near_death": True,
            "enemy_type": "boss",
            "escape_method": "teleport",
            "lesson_learned": "always_have_escape_plan"
        },
        intensity=0.95,
        emotional_impact=0.9
    )
    
    # Получение релевантных воспоминаний
    context = {
        "enemy_type": "boss",
        "weapon_type": "sword",
        "emotional_state": 0.7
    }
    
    relevant_memories = memory_system.get_relevant_memories(context)
    logger.info(f"Найдено {len(relevant_memories)} релевантных воспоминаний")
    
    # Влияние на принятие решений
    available_actions = ["attack", "defend", "retreat", "use_magic"]
    decision_weights = memory_system.influence_decision(context, available_actions)
    
    logger.info("Влияние памяти на решения:")
    for action, weight in decision_weights.items():
        logger.info(f"  {action}: {weight:.3f}")
    
    # Переход к следующему поколению
    logger.info("Переход к следующему поколению...")
    memory_system.advance_generation(survival_rate=0.8, achievements=["boss_defeated"])
    
    # Статистика
    stats = memory_system.get_memory_statistics()
    logger.info(f"Статистика памяти: {stats['total_memories']} воспоминаний, "
                f"поколение {stats['current_generation']}")
    
    return memory_system


def demo_emotional_ai_influence(memory_system):
    """Демонстрация эмоционального влияния на ИИ"""
    logger.info("\n=== ДЕМОНСТРАЦИЯ ЭМОЦИОНАЛЬНОГО ВЛИЯНИЯ НА ИИ ===")
    
    # Инициализация системы
    emotional_system = EmotionalAIInfluenceSystem(memory_system)
    
    # Обработка эмоциональных триггеров
    entity_id = "player_001"
    current_time = time.time()
    
    logger.info("Обработка эмоциональных триггеров...")
    
    # Триггер победы
    emotional_system.process_emotion_trigger(
        entity_id, "victory", {
            "enemy_difficulty": 0.9,
            "battle_duration": 180,
            "health_percent": 0.3
        }, current_time
    )
    
    # Триггер обнаружения
    emotional_system.process_emotion_trigger(
        entity_id, "discovery", {
            "item_rarity": 0.8,
            "location_danger": 0.6
        }, current_time
    )
    
    # Получение эмоционально влияющих действий
    available_actions = ["attack", "defend", "explore", "retreat", "use_item"]
    context = {
        "emotional_state": 0.7,
        "health_percent": 0.3,
        "enemy_strength": 0.8
    }
    
    emotional_weights = emotional_system.get_emotionally_influenced_actions(
        entity_id, available_actions, context, current_time
    )
    
    logger.info("Действия с эмоциональным влиянием:")
    for action, weight in emotional_weights.items():
        logger.info(f"  {action}: {weight:.3f}")
    
    # Статистика эмоционального состояния
    emotional_stats = emotional_system.get_emotional_statistics(entity_id)
    logger.info(f"Эмоциональное состояние ИИ: стабильность {emotional_stats['emotional_stability']:.2f}, "
                f"травма {emotional_stats['emotional_trauma_level']:.2f}")
    
    return emotional_system


def demo_enhanced_combat_learning(memory_system, emotional_system):
    """Демонстрация улучшенного боевого обучения"""
    logger.info("\n=== ДЕМОНСТРАЦИЯ УЛУЧШЕННОГО БОЕВОГО ОБУЧЕНИЯ ===")
    
    # Инициализация системы
    combat_ai = EnhancedCombatLearningAI(memory_system, emotional_system)
    
    # Анализ стиля игрока
    combat_data = [
        {"attack_frequency": 0.8, "block_frequency": 0.2, "movement_frequency": 0.6,
         "weapon_used": "sword", "tactic_used": "aggressive_rush", "success_rate": 0.7},
        {"attack_frequency": 0.7, "block_frequency": 0.3, "movement_frequency": 0.5,
         "weapon_used": "sword", "tactic_used": "aggressive_rush", "success_rate": 0.8},
        {"attack_frequency": 0.9, "block_frequency": 0.1, "movement_frequency": 0.7,
         "weapon_used": "axe", "tactic_used": "mobile_harassment", "success_rate": 0.9}
    ]
    
    player_pattern = combat_ai.analyze_player_style(combat_data)
    logger.info(f"Анализ стиля игрока: {player_pattern.style.value}")
    logger.info(f"Агрессивность: {player_pattern.aggression_level:.2f}")
    logger.info(f"Осторожность: {player_pattern.caution_level:.2f}")
    logger.info(f"Мобильность: {player_pattern.mobility_score:.2f}")
    
    # Создание боевого контекста
    combat_context = CombatContext(
        combat_phase=CombatPhase.ENGAGEMENT,
        player_style=player_pattern.style,
        player_health_percent=0.7,
        player_stamina_percent=0.8,
        player_weapon_type="sword",
        player_armor_type="medium",
        player_buffs=["strength_boost"],
        player_debuffs=[],
        enemy_count=2,
        enemy_types=["goblin", "orc"],
        environmental_hazards=["spike_trap"],
        available_cover=["rock", "tree"],
        escape_routes=["north", "south"],
        tactical_advantages=["high_ground"]
    )
    
    # Принятие боевого решения
    available_actions = ["attack", "defend", "retreat", "use_magic", "flank"]
    current_time = time.time()
    
    decision = combat_ai.make_combat_decision(
        "enemy_001", combat_context, available_actions, current_time
    )
    
    logger.info(f"Боевое решение ИИ: {decision.action}")
    logger.info(f"Цель: {decision.target}")
    logger.info(f"Уверенность: {decision.confidence:.2f}")
    logger.info(f"Обоснование: {decision.reasoning}")
    logger.info(f"Ожидаемый результат: {decision.expected_outcome}")
    logger.info(f"Оценка риска: {decision.risk_assessment:.2f}")
    
    # Обучение на основе результата
    combat_result = {
        "success": True,
        "damage_dealt": 45,
        "damage_taken": 15,
        "tactic_effectiveness": 0.8
    }
    
    combat_ai.learn_from_combat_result("enemy_001", decision, combat_context, combat_result)
    logger.info("ИИ извлек урок из боевого результата")
    
    # Статистика ИИ
    ai_stats = combat_ai.get_ai_statistics("enemy_001")
    logger.info(f"Статистика ИИ: {ai_stats['total_decisions']} решений, "
                f"средняя успешность {ai_stats['average_success_rate']:.2f}")
    
    return combat_ai


def demo_trap_and_hazard_system():
    """Демонстрация системы ловушек и опасностей"""
    logger.info("\n=== ДЕМОНСТРАЦИЯ СИСТЕМЫ ЛОВУШЕК И ОПАСТНОСТЕЙ ===")
    
    # Инициализация системы
    world_seed = random.randint(1, 999999)
    trap_system = TrapAndHazardSystem(world_seed)
    
    # Генерация опасностей для мира
    world_size = (100, 100)
    hazards = trap_system.generate_world_hazards(world_size, hazard_density=0.15)
    logger.info(f"Сгенерировано {len(hazards)} опасностей")
    
    # Генерация сундуков
    chests = trap_system.generate_world_chests(world_size, chest_density=0.08)
    logger.info(f"Сгенерировано {len(chests)} сундуков")
    
    # Демонстрация различных типов опасностей
    logger.info("\nТипы опасностей:")
    hazard_types = {}
    for hazard in hazards:
        hazard_type = hazard.pattern.hazard_type.value
        hazard_types[hazard_type] = hazard_types.get(hazard_type, 0) + 1
    
    for hazard_type, count in hazard_types.items():
        logger.info(f"  {hazard_type}: {count}")
    
    # Демонстрация различных типов сундуков
    logger.info("\nТипы сундуков:")
    chest_types = {}
    for chest in chests:
        chest_type = chest.chest_type.value
        chest_types[chest_type] = chest_types.get(chest_type, 0) + 1
    
    for chest_type, count in chest_types.items():
        logger.info(f"  {chest_type}: {count}")
    
    # Проверка столкновения с опасностью
    entity_position = (50.0, 50.0, 0.0)
    entity_id = "player_001"
    current_time = time.time()
    
    hazard = trap_system.check_hazard_collision(entity_position, entity_id, current_time)
    if hazard:
        logger.info(f"Обнаружена опасность: {hazard.pattern.hazard_type.value}")
        
        # Срабатывание опасности
        result = trap_system.trigger_hazard(hazard, entity_id, current_time)
        logger.info(f"Опасность сработала: урон {result['damage']}, эффекты {result['effects']}")
    
    # Взаимодействие с сундуком
    if chests:
        chest = chests[0]
        logger.info(f"\nВзаимодействие с сундуком типа {chest.chest_type.value}")
        
        entity_skills = {
            "lockpicking": 0.6,
            "trap_detection": 0.7,
            "detection": 0.8
        }
        
        result = trap_system.attempt_chest_interaction(chest, entity_id, entity_skills)
        logger.info(f"Результат: {result['message']}")
        
        if result.get("success"):
            logger.info(f"Награды: {len(result['rewards'])} предметов")
    
    # Статистика системы
    system_stats = trap_system.get_system_statistics()
    logger.info(f"\nСтатистика системы: {system_stats['total_hazards']} опасностей, "
                f"{system_stats['total_chests']} сундуков, seed: {system_stats['world_seed']}")
    
    return trap_system


def demo_integration():
    """Демонстрация интеграции всех систем"""
    logger.info("\n=== ДЕМОНСТРАЦИЯ ИНТЕГРАЦИИ СИСТЕМ ===")
    
    # Инициализация всех систем
    memory_system = demo_generational_memory()
    emotional_system = demo_emotional_ai_influence(memory_system)
    combat_ai = demo_enhanced_combat_learning(memory_system, emotional_system)
    trap_system = demo_trap_and_hazard_system()
    
    # Демонстрация взаимодействия систем
    logger.info("\n--- Взаимодействие систем ---")
    
    # Создание комплексного сценария
    entity_id = "player_001"
    current_time = time.time()
    
    # 1. Игрок сталкивается с опасностью
    hazard_position = (25.0, 25.0, 0.0)
    hazard = trap_system.check_hazard_collision(hazard_position, entity_id, current_time)
    
    if hazard:
        # 2. Срабатывание опасности
        hazard_result = trap_system.trigger_hazard(hazard, entity_id, current_time)
        
        # 3. Эмоциональный триггер
        emotional_system.process_emotion_trigger(
            entity_id, "environmental_hazard", {
                "hazard_damage": hazard_result["damage"],
                "escape_difficulty": 0.7
            }, current_time
        )
        
        # 4. Запись в память поколений
        memory_system.add_memory(
            MemoryType.ENVIRONMENTAL_HAZARDS,
            {
                "hazard_type": hazard.pattern.hazard_type.value,
                "damage_taken": hazard_result["damage"],
                "location": hazard_position,
                "lesson_learned": "watch_for_traps"
            },
            intensity=0.8,
            emotional_impact=0.7
        )
        
        # 5. Влияние на боевые решения
        combat_context = CombatContext(
            combat_phase=CombatPhase.ENGAGEMENT,
            player_style=PlayerStyle.AGGRESSIVE,
            player_health_percent=0.6,
            player_stamina_percent=0.8,
            player_weapon_type="sword",
            player_armor_type="medium",
            player_buffs=[],
            player_debuffs=["poisoned"],
            enemy_count=1,
            enemy_types=["goblin"],
            environmental_hazards=["spike_trap"],
            available_cover=["rock"],
            escape_routes=["north"],
            tactical_advantages=[]
        )
        
        available_actions = ["attack", "defend", "retreat", "use_consumable"]
        decision = combat_ai.make_combat_decision(
            entity_id, combat_context, available_actions, current_time
        )
        
        logger.info(f"Комплексное решение ИИ после столкновения с опасностью:")
        logger.info(f"  Действие: {decision.action}")
        logger.info(f"  Обоснование: {decision.reasoning}")
        logger.info(f"  Оценка риска: {decision.risk_assessment:.2f}")
    
    logger.info("\nВсе системы успешно интегрированы и работают вместе!")


def main():
    """Главная функция демонстрации"""
    logger.info("🎮 ДЕМОНСТРАЦИЯ УЛУЧШЕННЫХ СИСТЕМ AI-EVOLVE")
    logger.info("=" * 60)
    
    try:
        # Запуск демонстраций
        demo_integration()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Демонстрация завершена успешно!")
        logger.info("🎯 Все новые системы работают корректно")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

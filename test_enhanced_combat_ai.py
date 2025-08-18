#!/usr/bin/env python3
"""
Демонстрация расширенной системы боевого ИИ для эволюционной адаптации.
Тестирует систему навыков, их комбинирование и умное принятие решений в бою.
"""

import sys
import os
import random
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent))

from core.skill_system import (
    SkillManager, SkillLearningAI, SkillFactory, 
    SkillType, SkillElement, SkillTarget
)
from core.enhanced_combat_ai import (
    EnhancedCombatAI, EnhancedCombatContext, 
    CombatPhase, CombatTactic
)
from core.advanced_weapon_system import WeaponFactory, WeaponManager
from core.combat_learning_system import CombatLearningSystem


def test_skill_system():
    """Тестирует систему навыков"""
    print("🔮 ТЕСТИРОВАНИЕ СИСТЕМЫ НАВЫКОВ")
    print("=" * 60)
    
    # Создаем менеджер навыков
    skill_manager = SkillManager()
    
    # Создаем дополнительные навыки через фабрику
    ice_shard = SkillFactory.create_magic_skill(
        "ice_shard", "Ледяной осколок", 20.0, SkillElement.ICE, 12.0
    )
    
    lightning_bolt = SkillFactory.create_magic_skill(
        "lightning_bolt", "Удар молнии", 35.0, SkillElement.LIGHTNING, 18.0
    )
    
    poison_dart = SkillFactory.create_magic_skill(
        "poison_dart", "Отравленный дротик", 15.0, SkillElement.POISON, 10.0
    )
    
    # Добавляем навыки
    skill_manager.add_skill(ice_shard)
    skill_manager.add_skill(lightning_bolt)
    skill_manager.add_skill(poison_dart)
    
    # Создаем комбинацию огня и льда
    fire_ice_combo = skill_manager.get_skill_combo("fire_ice_combo")
    if fire_ice_combo:
        print(f"✅ Комбинация навыков: {fire_ice_combo.name}")
        print(f"   Описание: {fire_ice_combo.description}")
        print(f"   Навыки: {', '.join(fire_ice_combo.skills)}")
        print(f"   Бонус комбинации: x{fire_ice_combo.combo_bonus}")
        print()
    
    # Показываем все доступные навыки
    print("📚 Доступные навыки:")
    for skill_id, skill in skill_manager.skills.items():
        print(f"   {skill.name} ({skill.skill_type.value})")
        print(f"     Элемент: {skill.element.value}")
        print(f"     Урон: {skill.base_damage}")
        print(f"     Мана: {skill.mana_cost}")
        print(f"     Перезарядка: {skill.cooldown}с")
        print()
    
    return skill_manager


def test_skill_learning():
    """Тестирует изучение навыков ИИ"""
    print("🧠 ТЕСТИРОВАНИЕ ИЗУЧЕНИЯ НАВЫКОВ")
    print("=" * 60)
    
    # Создаем ИИ для изучения навыков
    skill_ai = SkillLearningAI("test_entity")
    
    # Симулируем изучение навыков
    skills_to_learn = ["basic_attack", "fire_ball", "heal", "ice_shard"]
    
    for skill_id in skills_to_learn:
        success_rate = 0.6 + (hash(skill_id) % 40) / 100.0  # Случайная эффективность
        skill_ai.learn_skill(skill_id, success_rate)
        print(f"✅ Изучен навык: {skill_id} (эффективность: {success_rate:.2f})")
    
    # Симулируем открытие комбинации
    skill_ai.discover_combo(["fire_ball", "ice_shard"], 0.85)
    print(f"🎯 Открыта комбинация: огненный шар + ледяной осколок")
    
    # Показываем прогресс изучения
    progress = skill_ai.get_learning_progress()
    print(f"\n📊 Прогресс изучения:")
    print(f"   Изучено навыков: {progress['learned_skills']}")
    print(f"   Открыто комбинаций: {progress['discovered_combos']}")
    print(f"   Всего использований: {progress['learning_stats']['total_skill_usage']}")
    
    print()
    return skill_ai


def test_enhanced_combat_ai():
    """Тестирует расширенную систему боевого ИИ"""
    print("⚔️ ТЕСТИРОВАНИЕ РАСШИРЕННОГО БОЕВОГО ИИ")
    print("=" * 60)
    
    # Создаем расширенный боевой ИИ
    combat_ai = EnhancedCombatAI("test_combat_entity")
    
    # Создаем контекст боя
    combat_context = EnhancedCombatContext(
        enemy_type="огненный демон",
        enemy_health=80.0,
        enemy_max_health=100.0,
        enemy_distance=3.0,
        enemy_behavior="aggressive",
        enemy_element="fire",
        enemy_resistances={"fire": 0.5, "ice": -0.3, "lightning": 0.0, "physical": 0.2},
        
        own_health=70.0,
        own_max_health=100.0,
        own_stamina=80.0,
        own_max_stamina=100.0,
        own_mana=60.0,
        own_max_mana=100.0,
        
        available_weapons=["sword", "bow", "staff"],
        available_skills=["basic_attack", "fire_ball", "ice_shard", "heal"],
        available_items=["health_potion", "mana_potion"],
        available_combos=["fire_ice_combo"],
        
        allies_nearby=1,
        enemies_nearby=2,
        terrain_type="volcanic",
        time_of_day="day",
        weather="clear",
        
        combat_phase=CombatPhase.ENGAGEMENT,
        current_tactic=CombatTactic.ADAPTIVE_RESPONSE,
        threat_level=0.0,
        advantage_ratio=0.0,
        
        recent_actions=[],
        successful_attacks=[],
        failed_attacks=[],
        damage_taken=0.0,
        damage_dealt=0.0
    )
    
    # Принимаем решение о боевом действии
    decision = combat_ai.make_combat_decision(combat_context)
    
    print(f"🎯 Принято решение: {decision}")
    print(f"   Тактика: {decision.tactic.value}")
    print(f"   Действие: {decision.action_type}")
    print(f"   Цель: {decision.target}")
    print(f"   Приоритет: {decision.priority}")
    print(f"   Уверенность: {decision.confidence}")
    print(f"   Обоснование: {decision.reasoning}")
    print(f"   Ожидаемый результат: {decision.expected_outcome}")
    
    # Симулируем результат боя
    outcome = {
        "damage_dealt": 45.0,
        "success": True,
        "critical_hit": False,
        "enemy_status": "normal"
    }
    
    # ИИ учится на результате
    combat_ai.learn_from_combat_result(decision, True, outcome)
    
    print(f"\n📈 Результат боя:")
    print(f"   Нанесено урона: {outcome['damage_dealt']}")
    print(f"   Успех: {outcome['success']}")
    
    # Показываем состояние ИИ
    ai_state = combat_ai.get_combat_ai_state()
    print(f"\n🤖 Состояние боевого ИИ:")
    print(f"   Фаза боя: {ai_state['combat_phase']}")
    print(f"   Текущая тактика: {ai_state['current_tactic']}")
    print(f"   Уровень агрессии: {ai_state['aggression_level']}")
    print(f"   Уровень осторожности: {ai_state['caution_level']}")
    print(f"   Адаптивность: {ai_state['adaptability']}")
    
    print()
    return combat_ai


def test_tactical_decision_making():
    """Тестирует тактическое принятие решений"""
    print("🎖️ ТЕСТИРОВАНИЕ ТАКТИЧЕСКОГО ПРИНЯТИЯ РЕШЕНИЙ")
    print("=" * 60)
    
    combat_ai = EnhancedCombatAI("tactical_test_entity")
    
    # Тестируем различные боевые ситуации
    scenarios = [
        {
            "name": "Высокая угроза - низкое здоровье",
            "context": EnhancedCombatContext(
                enemy_type="сильный враг",
                enemy_health=90.0,
                enemy_max_health=100.0,
                enemy_distance=2.0,
                enemy_behavior="aggressive",
                enemy_element="physical",
                enemy_resistances={},
                own_health=25.0,
                own_max_health=100.0,
                own_stamina=30.0,
                own_max_stamina=100.0,
                own_mana=20.0,
                own_max_mana=100.0,
                available_weapons=["sword"],
                available_skills=["heal", "defend"],
                available_items=["health_potion"],
                available_combos=[],
                allies_nearby=0,
                enemies_nearby=2,
                terrain_type="cave",
                time_of_day="night",
                weather="dark",
                combat_phase=CombatPhase.PREPARATION,
                current_tactic=CombatTactic.ADAPTIVE_RESPONSE,
                threat_level=0.0,
                advantage_ratio=0.0,
                recent_actions=[],
                successful_attacks=[],
                failed_attacks=[],
                damage_taken=0.0,
                damage_dealt=0.0
            )
        },
        {
            "name": "Преимущество - много навыков",
            "context": EnhancedCombatContext(
                enemy_type="слабый враг",
                enemy_health=30.0,
                enemy_max_health=100.0,
                enemy_distance=5.0,
                enemy_behavior="defensive",
                enemy_element="ice",
                enemy_resistances={"ice": 0.3, "fire": -0.2},
                own_health=90.0,
                own_max_health=100.0,
                own_stamina=85.0,
                own_max_stamina=100.0,
                own_mana=80.0,
                own_max_mana=100.0,
                available_weapons=["sword", "bow", "staff"],
                available_skills=["fire_ball", "ice_shard", "lightning_bolt", "basic_attack"],
                available_items=["mana_potion"],
                available_combos=["fire_ice_combo"],
                allies_nearby=1,
                enemies_nearby=1,
                terrain_type="forest",
                time_of_day="day",
                weather="clear",
                combat_phase=CombatPhase.PREPARATION,
                current_tactic=CombatTactic.ADAPTIVE_RESPONSE,
                threat_level=0.0,
                advantage_ratio=0.0,
                recent_actions=[],
                successful_attacks=[],
                failed_attacks=[],
                damage_taken=0.0,
                damage_dealt=0.0
            )
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Сценарий {i}: {scenario['name']}")
        print("-" * 40)
        
        context = scenario['context']
        decision = combat_ai.make_combat_decision(context)
        
        print(f"   Фаза боя: {context.combat_phase.value}")
        print(f"   Уровень угрозы: {context.threat_level:.2f}")
        print(f"   Соотношение преимуществ: {context.advantage_ratio:.2f}")
        print(f"   Выбранная тактика: {decision.tactic.value}")
        print(f"   Действие: {decision.action_type}")
        print(f"   Обоснование: {decision.reasoning}")
    
    print()


def test_skill_combinations():
    """Тестирует комбинации навыков"""
    print("🔗 ТЕСТИРОВАНИЕ КОМБИНАЦИЙ НАВЫКОВ")
    print("=" * 60)
    
    skill_manager = SkillManager()
    
    # Создаем дополнительные навыки для комбинаций
    wind_slash = SkillFactory.create_combat_skill(
        "wind_slash", "Ветряной удар", 18.0, SkillElement.COSMIC
    )
    
    earth_shield = SkillFactory.create_support_skill(
        "earth_shield", "Земляной щит", 25.0, 15.0
    )
    
    skill_manager.add_skill(wind_slash)
    skill_manager.add_skill(earth_shield)
    
    # Создаем новые комбинации
    from core.skill_system import SkillCombo, SkillRequirement, SkillEffect
    
    # Комбинация ветра и земли
    wind_earth_combo = SkillCombo(
        combo_id="wind_earth_combo",
        name="Буря",
        description="Комбинация ветра и земли создает разрушительную бурю",
        skills=["wind_slash", "earth_shield"],
        requirements=SkillRequirement(intelligence=10, magic=20),
        effects=[
            SkillEffect("damage", 60.0, element=SkillElement.COSMIC),
            SkillEffect("stun", 3.0, duration=3.0, element=SkillElement.COSMIC)
        ],
        cooldown=15.0,
        mana_cost=40.0,
        combo_bonus=2.5
    )
    
    skill_manager.add_skill_combo(wind_earth_combo)
    
    # Показываем все комбинации
    print("🎭 Доступные комбинации навыков:")
    for combo_id, combo in skill_manager.skill_combos.items():
        print(f"\n   {combo.name}")
        print(f"     Описание: {combo.description}")
        print(f"     Навыки: {', '.join(combo.skills)}")
        print(f"     Бонус: x{combo.combo_bonus}")
        print(f"     Перезарядка: {combo.cooldown}с")
        print(f"     Стоимость маны: {combo.mana_cost}")
        
        # Рассчитываем урон комбинации
        entity_stats = {"intelligence": 15, "magic": 25}
        combo_damage = skill_manager.calculate_combo_damage(combo, entity_stats)
        print(f"     Ожидаемый урон: {combo_damage:.1f}")
    
    print()


def test_evolutionary_learning():
    """Тестирует эволюционное обучение"""
    print("🧬 ТЕСТИРОВАНИЕ ЭВОЛЮЦИОННОГО ОБУЧЕНИЯ")
    print("=" * 60)
    
    # Создаем несколько ИИ для симуляции эволюции
    ai_entities = []
    
    for i in range(3):
        entity_id = f"evolutionary_ai_{i}"
        combat_ai = EnhancedCombatAI(entity_id)
        
        # Устанавливаем разные начальные параметры
        if i == 0:
            combat_ai.aggression_level = 0.8
            combat_ai.caution_level = 0.2
        elif i == 1:
            combat_ai.aggression_level = 0.3
            combat_ai.caution_level = 0.8
        else:
            combat_ai.aggression_level = 0.5
            combat_ai.caution_level = 0.5
        
        ai_entities.append(combat_ai)
    
    # Симулируем несколько боев для каждого ИИ
    battle_scenarios = [
        {"enemy_type": "огненный демон", "difficulty": "hard"},
        {"enemy_type": "ледяной голем", "difficulty": "medium"},
        {"enemy_type": "электрический дух", "difficulty": "easy"}
    ]
    
    for i, ai in enumerate(ai_entities):
        print(f"\n🤖 ИИ {i+1} (Агрессия: {ai.aggression_level:.1f}, Осторожность: {ai.caution_level:.1f})")
        print("-" * 50)
        
        for j, scenario in enumerate(battle_scenarios):
            # Создаем контекст боя
            context = EnhancedCombatContext(
                enemy_type=scenario["enemy_type"],
                enemy_health=80.0,
                enemy_max_health=100.0,
                enemy_distance=4.0,
                enemy_behavior="aggressive",
                enemy_element="fire",
                enemy_resistances={},
                own_health=70.0,
                own_max_health=100.0,
                own_stamina=80.0,
                own_max_stamina=100.0,
                own_mana=60.0,
                own_max_mana=100.0,
                available_weapons=["sword", "bow"],
                available_skills=["basic_attack", "fire_ball", "heal"],
                available_items=["health_potion"],
                available_combos=[],
                allies_nearby=0,
                enemies_nearby=1,
                terrain_type="plains",
                time_of_day="day",
                weather="clear",
                combat_phase=CombatPhase.PREPARATION,
                current_tactic=CombatTactic.ADAPTIVE_RESPONSE,
                threat_level=0.0,
                advantage_ratio=0.0,
                recent_actions=[],
                successful_attacks=[],
                failed_attacks=[],
                damage_taken=0.0,
                damage_dealt=0.0
            )
            
            # Принимаем решение
            decision = ai.make_combat_decision(context)
            
            # Симулируем результат (упрощенно)
            success = random.random() > 0.3  # 70% успех
            damage = random.uniform(20.0, 60.0) if success else random.uniform(5.0, 15.0)
            
            outcome = {"damage_dealt": damage, "success": success}
            
            # ИИ учится
            ai.learn_from_combat_result(decision, success, outcome)
            
            print(f"   Бой {j+1} против {scenario['enemy_type']}:")
            print(f"     Тактика: {decision.tactic.value}")
            print(f"     Действие: {decision.action_type}")
            print(f"     Успех: {'✅' if success else '❌'}")
            print(f"     Урон: {damage:.1f}")
    
    # Показываем результаты эволюции
    print(f"\n📊 РЕЗУЛЬТАТЫ ЭВОЛЮЦИОННОГО ОБУЧЕНИЯ")
    print("=" * 60)
    
    for i, ai in enumerate(ai_entities):
        ai_state = ai.get_combat_ai_state()
        print(f"\n🤖 ИИ {i+1}:")
        print(f"   Успешных тактик: {sum(ai_state['successful_tactics'].values())}")
        print(f"   Принято решений: {ai_state['decision_history_length']}")
        print(f"   Прогресс изучения навыков: {ai_state['skill_learning_progress']['learned_skills']}")
        print(f"   Прогресс изучения боя: {ai_state['combat_learning_progress']['combat_history_length']}")
    
    print()


def main():
    """Главная функция тестирования"""
    print("ЭВОЛЮЦИОННАЯ АДАПТАЦИЯ: ТЕСТИРОВАНИЕ РАСШИРЕННОГО БОЕВОГО ИИ")
    print("=" * 80)
    
    try:
        # Тестируем систему навыков
        skill_manager = test_skill_system()
        
        # Тестируем изучение навыков
        skill_ai = test_skill_learning()
        
        # Тестируем расширенный боевой ИИ
        combat_ai = test_enhanced_combat_ai()
        
        # Тестируем тактическое принятие решений
        test_tactical_decision_making()
        
        # Тестируем комбинации навыков
        test_skill_combinations()
        
        # Тестируем эволюционное обучение
        test_evolutionary_learning()
        
        print("\n" + "=" * 80)
        print("🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("=" * 80)
        
        # Сохраняем состояния для демонстрации
        print("\n💾 Сохранение состояний...")
        
        skill_ai.save_learning_state("test_skill_learning_state.json")
        combat_ai.save_combat_ai_state("test_enhanced_combat_ai_state.json")
        
        print("✅ Состояния сохранены:")
        print("   - test_skill_learning_state.json")
        print("   - test_enhanced_combat_ai_state.json")
        
        print("\n🚀 Система готова к использованию в игре!")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

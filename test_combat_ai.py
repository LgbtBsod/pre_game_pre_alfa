#!/usr/bin/env python3
"""
Демонстрация систем боевого ИИ для эволюционной адаптации.
Тестирует обучение сражениям, выбор оружия и принятие решений.
"""

import sys
import time
import random
from pathlib import Path

# Добавление корневой директории в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

from core.combat_learning_system import CombatLearningSystem, CombatAction
from core.advanced_weapon_system import WeaponFactory, WeaponType, WeaponRarity, WeaponManager
from core.integrated_combat_ai import IntegratedCombatAI, CombatContext, CombatStrategy


def test_weapon_system():
    """Тестирование системы оружия"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ ОРУЖИЯ")
    print("=" * 60)
    
    # Создание фабрики оружия
    factory = WeaponFactory()
    weapon_manager = WeaponManager()
    
    # Создание различных типов оружия
    weapon_types = [
        WeaponType.SWORD,
        WeaponType.AXE, 
        WeaponType.SPEAR,
        WeaponType.BOW,
        WeaponType.STAFF,
        WeaponType.DAGGER
    ]
    
    rarities = [
        WeaponRarity.COMMON,
        WeaponRarity.UNCOMMON,
        WeaponRarity.RARE,
        WeaponRarity.EPIC
    ]
    
    print("Создание оружия различных типов и редкости:")
    for weapon_type in weapon_types:
        for rarity in rarities:
            weapon = factory.create_weapon(weapon_type, rarity)
            weapon_manager.add_weapon(weapon)
            
            print(f"  {weapon.name} ({weapon.weapon_type.value})")
            print(f"    Урон: {weapon.stats.base_damage:.1f}")
            print(f"    Скорость: {weapon.stats.attack_speed:.1f}")
            print(f"    Дальность: {weapon.stats.range:.1f}")
            print(f"    Прочность: {weapon.stats.durability:.1f}/{weapon.stats.max_durability:.1f}")
            
            if weapon.enhancements:
                print(f"    Улучшения: {len(weapon.enhancements)}")
                for enh in weapon.enhancements:
                    print(f"      {enh.description}: +{enh.value:.1%}")
            print()
    
    # Тестирование эффективности против врагов
    print("Тестирование эффективности оружия против врагов:")
    enemy_types = ["goblin", "orc", "troll", "dragon", "undead", "demon"]
    
    for enemy_type in enemy_types:
        best_weapon = weapon_manager.get_best_weapon_against(enemy_type)
        if best_weapon:
            effectiveness = best_weapon.get_effectiveness_against(enemy_type)
            print(f"  Лучшее оружие против {enemy_type}: {best_weapon.name} (эффективность: {effectiveness:.2f})")
    
    # Статистика коллекции
    stats = weapon_manager.get_collection_stats()
    print(f"\nСтатистика коллекции оружия:")
    print(f"  Всего оружия: {stats['total_weapons']}")
    print(f"  Средний урон: {stats['average_damage']:.1f}")
    
    return weapon_manager


def test_combat_learning():
    """Тестирование системы обучения сражениям"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ ОБУЧЕНИЯ СРАЖЕНИЯМ")
    print("=" * 60)
    
    # Создание системы обучения
    combat_ai = IntegratedCombatAI("test_player")
    
    # Симуляция боёв для обучения
    print("Симуляция боёв для обучения ИИ:")
    
    combat_scenarios = [
        {
            "enemy_type": "goblin",
            "weapon_used": "sword",
            "damage_dealt": 45,
            "expected_damage": 30,
            "victory": True,
            "items_used": [{"type": "health_potion", "success": True}]
        },
        {
            "enemy_type": "orc",
            "weapon_used": "axe",
            "damage_dealt": 35,
            "expected_damage": 40,
            "victory": False,
            "items_used": [{"type": "stamina_potion", "success": True}]
        },
        {
            "enemy_type": "undead",
            "weapon_used": "fire_staff",
            "damage_dealt": 80,
            "expected_damage": 25,
            "victory": True,
            "items_used": []
        },
        {
            "enemy_type": "troll",
            "weapon_used": "sword",
            "damage_dealt": 20,
            "expected_damage": 30,
            "victory": False,
            "items_used": [{"type": "heal_potion", "success": False}]
        }
    ]
    
    for i, scenario in enumerate(combat_scenarios, 1):
        print(f"  Бой {i}: {scenario['enemy_type']} - {'Победа' if scenario['victory'] else 'Поражение'}")
        
        # Обновление знаний на основе результата боя
        combat_ai.update_combat_knowledge(scenario)
        
        # Получение рекомендаций
        context = CombatContext(
            enemy_type=scenario["enemy_type"],
            enemy_health=50,
            enemy_max_health=100,
            enemy_distance=3.0,
            enemy_behavior="aggressive",
            own_health=70,
            own_max_health=100,
            own_stamina=60,
            own_max_stamina=100,
            available_weapons=["sword", "axe", "bow"],
            available_items=["health_potion", "stamina_potion"],
            allies_nearby=0,
            enemies_nearby=1,
            terrain_type="forest",
            time_of_day="day",
            weather="clear"
        )
        
        decision = combat_ai.make_combat_decision(context)
        print(f"    Рекомендация: {decision}")
    
    # Отчёт об обучении
    report = combat_ai.get_combat_ai_report()
    print(f"\nОтчёт об обучении:")
    print(f"  Принято решений: {report['decisions_made']}")
    print(f"  Стратегия: {report['combat_strategy']}")
    print(f"  Уровень агрессии: {report['aggression_level']:.2f}")
    print(f"  Уровень осторожности: {report['caution_level']:.2f}")
    
    return combat_ai


def test_combat_decisions():
    """Тестирование принятия боевых решений"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ПРИНЯТИЯ БОЕВЫХ РЕШЕНИЙ")
    print("=" * 60)
    
    combat_ai = IntegratedCombatAI("test_combatant")
    
    # Различные боевые ситуации
    combat_situations = [
        {
            "name": "Критическое здоровье",
            "context": CombatContext(
                enemy_type="dragon",
                enemy_health=200,
                enemy_max_health=200,
                enemy_distance=5.0,
                enemy_behavior="aggressive",
                own_health=20,
                own_max_health=100,
                own_stamina=30,
                own_max_stamina=100,
                available_weapons=["sword", "bow"],
                available_items=["health_potion", "escape_scroll"],
                allies_nearby=0,
                enemies_nearby=1,
                terrain_type="mountain",
                time_of_day="night",
                weather="storm"
            )
        },
        {
            "name": "Тактическое преимущество",
            "context": CombatContext(
                enemy_type="goblin",
                enemy_health=30,
                enemy_max_health=50,
                enemy_distance=8.0,
                enemy_behavior="cautious",
                own_health=90,
                own_max_health=100,
                own_stamina=80,
                own_max_stamina=100,
                available_weapons=["bow", "spear"],
                available_items=["strength_potion", "speed_potion"],
                allies_nearby=2,
                enemies_nearby=1,
                terrain_type="forest",
                time_of_day="day",
                weather="clear"
            )
        },
        {
            "name": "Окружение врагами",
            "context": CombatContext(
                enemy_type="orc",
                enemy_health=80,
                enemy_max_health=100,
                enemy_distance=2.0,
                enemy_behavior="aggressive",
                own_health=60,
                own_max_health=100,
                own_stamina=40,
                own_max_stamina=100,
                available_weapons=["sword", "dagger"],
                available_items=["heal_potion", "defense_potion"],
                allies_nearby=0,
                enemies_nearby=3,
                terrain_type="urban",
                time_of_day="dusk",
                weather="fog"
            )
        }
    ]
    
    for situation in combat_situations:
        print(f"\nСитуация: {situation['name']}")
        
        # Анализ ситуации
        analysis = combat_ai._analyze_combat_situation(situation['context'])
        print(f"  Уровень угрозы: {analysis['threat_level']:.2f}")
        print(f"  Соотношение сил: {analysis['advantage_ratio']:.2f}")
        print(f"  Преимущество местности: {analysis['terrain_advantage']:.2f}")
        print(f"  Тактическая позиция: {analysis['tactical_position']}")
        
        # Принятие решения
        decision = combat_ai.make_combat_decision(situation['context'])
        print(f"  Решение: {decision.action.value}")
        print(f"  Обоснование: {decision.reasoning}")
        print(f"  Уверенность: {decision.confidence:.2f}")


def test_evolutionary_learning():
    """Тестирование эволюционного обучения"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЭВОЛЮЦИОННОГО ОБУЧЕНИЯ")
    print("=" * 60)
    
    # Создание нескольких ИИ с разными начальными параметрами
    ai_entities = []
    
    for i in range(3):
        ai = IntegratedCombatAI(f"evolutionary_ai_{i}")
        
        # Разные начальные настройки
        if i == 0:
            ai.aggression_level = 0.8  # Агрессивный
            ai.caution_level = 0.2
        elif i == 1:
            ai.aggression_level = 0.2  # Осторожный
            ai.caution_level = 0.8
        else:
            ai.aggression_level = 0.5  # Сбалансированный
            ai.caution_level = 0.5
        
        ai_entities.append(ai)
    
    # Симуляция эволюции через несколько поколений
    print("Симуляция эволюционного обучения:")
    
    for generation in range(5):
        print(f"\nПоколение {generation + 1}:")
        
        for i, ai in enumerate(ai_entities):
            # Симуляция боёв
            victories = 0
            total_battles = 10
            
            for battle in range(total_battles):
                # Случайный враг
                enemy_types = ["goblin", "orc", "troll", "undead"]
                enemy_type = random.choice(enemy_types)
                
                # Случайный результат боя
                victory = random.random() < (0.4 + ai.aggression_level * 0.3)
                if victory:
                    victories += 1
                
                # Обновление знаний
                combat_result = {
                    "enemy_type": enemy_type,
                    "victory": victory,
                    "weapon_used": "sword",
                    "damage_dealt": random.randint(20, 60),
                    "expected_damage": 30,
                    "timestamp": time.time()
                }
                
                ai.update_combat_knowledge(combat_result)
            
            win_rate = victories / total_battles
            print(f"  ИИ {i}: Победы {victories}/{total_battles} ({win_rate:.1%})")
            print(f"    Агрессия: {ai.aggression_level:.2f}, Осторожность: {ai.caution_level:.2f}")
        
        # Эволюция: лучшие ИИ "размножаются"
        if generation < 4:
            # Сортировка по результатам
            ai_entities.sort(key=lambda x: x.combat_learning.learning_stats["battles_won"], reverse=True)
            
            # Создание новых ИИ на основе лучших
            new_ai = IntegratedCombatAI(f"evolutionary_ai_gen_{generation + 1}")
            
            # Наследование параметров от лучшего ИИ
            best_ai = ai_entities[0]
            new_ai.aggression_level = best_ai.aggression_level + random.uniform(-0.1, 0.1)
            new_ai.caution_level = best_ai.caution_level + random.uniform(-0.1, 0.1)
            
            # Ограничение значений
            new_ai.aggression_level = max(0.0, min(1.0, new_ai.aggression_level))
            new_ai.caution_level = max(0.0, min(1.0, new_ai.caution_level))
            
            # Замена худшего ИИ
            ai_entities[-1] = new_ai
            
            print(f"  Эволюция: создан новый ИИ с параметрами агрессии {new_ai.aggression_level:.2f}, осторожности {new_ai.caution_level:.2f}")


def main():
    """Главная функция тестирования"""
    print("ЭВОЛЮЦИОННАЯ АДАПТАЦИЯ: ТЕСТИРОВАНИЕ БОЕВОГО ИИ")
    print("=" * 80)
    
    try:
        # Тестирование системы оружия
        weapon_manager = test_weapon_system()
        
        # Тестирование системы обучения
        combat_ai = test_combat_learning()
        
        # Тестирование принятия решений
        test_combat_decisions()
        
        # Тестирование эволюционного обучения
        test_evolutionary_learning()
        
        print("\n" + "=" * 80)
        print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("=" * 80)
        
        # Сохранение состояния для демонстрации
        print("\nСохранение состояния боевого ИИ...")
        combat_ai.save_combat_ai_state("test_combat_ai_state.json")
        print("Состояние сохранено в test_combat_ai_state.json")
        
    except Exception as e:
        print(f"\nОшибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

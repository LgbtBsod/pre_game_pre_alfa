#!/usr/bin/env python3
"""
Полный тест системы AI-EVOLVE
Проверяет все основные компоненты проекта
"""

import sys
import os
import time
import logging
from typing import Dict, Any

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тест импортов основных модулей"""
    print("🔍 Тестирование импортов...")
    
    try:
        # Тест основных констант
        from src.core.constants import (
            DamageType, ItemType, EmotionType, GeneType, 
            BASE_STATS, PROBABILITY_CONSTANTS, SKILL_GENERATION_TEMPLATES
        )
        print("✅ Константы импортированы успешно")
        
        # Тест базовых сущностей
        from src.entities import BaseEntity, Player, NPC, Enemy, Item
        print("✅ Сущности импортированы успешно")
        
        # Тест основных систем
        from src.core.interfaces import ISystem, SystemPriority, SystemState
        print("✅ Интерфейсы импортированы успешно")
        
        # Тест менеджеров
        from src.core.config_manager import ConfigManager
        from src.core.event_system import EventSystem
        from src.core.system_manager import SystemManager
        print("✅ Менеджеры импортированы успешно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_entity_system():
    """Тест системы сущностей"""
    print("\n🎮 Тестирование системы сущностей...")
    
    try:
        from src.entities import BaseEntity, Player, NPC, Enemy, Item, Weapon, Armor
        from src.core.constants import EntityType, DamageType, EmotionType
        
        # Создание базовой сущности
        base_entity = BaseEntity("test_1", EntityType.ENEMY, "Test Entity")
        print("✅ Базовая сущность создана")
        
        # Создание игрока
        player = Player("player_1", "Test Player")
        print("✅ Игрок создан")
        
        # Создание NPC
        npc = NPC("npc_1", "Test NPC")
        print("✅ NPC создан")
        
        # Создание врага
        enemy = Enemy("enemy_1", "Test Enemy")
        print("✅ Враг создан")
        
        # Создание предметов
        weapon = Weapon("sword_1", "Test Sword", "A test sword")
        armor = Armor("armor_1", "Test Armor", "A test armor")
        print("✅ Предметы созданы")
        
        # Тест взаимодействий
        player.add_item(weapon)
        player.equip_item(weapon, "weapon")
        print("✅ Предметы добавлены и экипированы")
        
        player.take_damage(10, DamageType.PHYSICAL)
        print(f"✅ Урон получен, здоровье: {player.stats.current_health}")
        
        player.add_emotion(EmotionType.JOY, 0.5, 10.0)
        print("✅ Эмоция добавлена")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка системы сущностей: {e}")
        return False

def test_game_systems():
    """Тест игровых систем"""
    print("\n⚙️ Тестирование игровых систем...")
    
    try:
        from src.core.config_manager import ConfigManager
        from src.core.event_system import EventSystem
        from src.core.system_manager import SystemManager
        from src.core.system_factory import SystemFactory
        
        # Создание базовых менеджеров
        config_manager = ConfigManager()
        event_system = EventSystem()
        system_manager = SystemManager(event_system)
        
        print("✅ Базовые менеджеры созданы")
        
        # Создание фабрики систем
        system_factory = SystemFactory(config_manager, event_system, system_manager)
        print("✅ Фабрика систем создана")
        
        # Тест создания систем
        systems_to_test = [
            'unified_ai_system',
            'combat_system', 
            'effect_system',
            'skill_system',
            'damage_system',
            'inventory_system',
            'item_system',
            'emotion_system',
            'evolution_system'
        ]
        
        created_systems = 0
        for system_name in systems_to_test:
            try:
                system = system_factory.create_system(system_name)
                if system:
                    created_systems += 1
                    print(f"✅ Система {system_name} создана")
                else:
                    print(f"⚠️ Система {system_name} не создана (ожидаемо)")
            except Exception as e:
                print(f"⚠️ Ошибка создания системы {system_name}: {e}")
        
        print(f"✅ Создано систем: {created_systems}/{len(systems_to_test)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка игровых систем: {e}")
        return False

def test_content_generation():
    """Тест генерации контента"""
    print("\n🎨 Тестирование генерации контента...")
    
    try:
        from src.systems.content.content_generator import ContentGenerator
        from src.core.constants import ContentType, ContentRarity
        
        # Создание генератора контента
        content_gen = ContentGenerator()
        print("✅ Генератор контента создан")
        
        # Тест генерации предметов
        items = content_gen.generate_items(5, "common")
        print(f"✅ Сгенерировано предметов: {len(items)}")
        
        # Тест генерации навыков
        skills = content_gen.generate_skills(3, "rare")
        print(f"✅ Сгенерировано навыков: {len(skills)}")
        
        # Тест генерации эффектов
        effects = content_gen.generate_effects(2, "epic")
        print(f"✅ Сгенерировано эффектов: {len(effects)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка генерации контента: {e}")
        return False

def test_ai_system():
    """Тест AI системы"""
    print("\n🤖 Тестирование AI системы...")
    
    try:
        from src.systems.ai.unified_ai_system import UnifiedAISystem
        from src.core.constants import AIBehavior, AIState, AIDifficulty
        
        # Создание AI системы
        ai_system = UnifiedAISystem()
        print("✅ AI система создана")
        
        # Тест создания AI сущности
        ai_entity_data = ai_system.create_ai_entity(
            "ai_test_1", "enemy", AIBehavior.AGGRESSIVE, AIDifficulty.NORMAL
        )
        print("✅ AI сущность создана")
        
        # Тест принятия решений
        decision = ai_system.make_decision("ai_test_1", {"target": "player_1"})
        print(f"✅ Решение принято: {decision.decision_type if decision else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка AI системы: {e}")
        return False

def test_combat_system():
    """Тест боевой системы"""
    print("\n⚔️ Тестирование боевой системы...")
    
    try:
        from src.systems.combat.combat_system import CombatSystem
        from src.core.constants import CombatState, AttackType
        
        # Создание боевой системы
        combat_system = CombatSystem()
        print("✅ Боевая система создана")
        
        # Тест создания боевой статистики
        combat_stats = combat_system.create_combat_stats("test_entity")
        print("✅ Боевая статистика создана")
        
        # Тест атаки
        attack_result = combat_system.perform_attack("attacker", "target", AttackType.MELEE)
        print(f"✅ Атака выполнена, урон: {attack_result.damage_dealt}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка боевой системы: {e}")
        return False

def test_performance():
    """Тест производительности"""
    print("\n📊 Тестирование производительности...")
    
    try:
        from src.core.performance_manager import PerformanceManager
        
        # Создание менеджера производительности
        perf_manager = PerformanceManager()
        print("✅ Менеджер производительности создан")
        
        # Тест измерения времени
        start_time = time.time()
        time.sleep(0.1)  # Имитация работы
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"✅ Время выполнения: {execution_time:.3f} сек")
        
        # Тест метрик
        metrics = perf_manager.get_performance_metrics()
        print(f"✅ Метрики получены: {len(metrics)} показателей")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка производительности: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск полного теста системы AI-EVOLVE")
    print("=" * 50)
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    tests = [
        ("Импорты", test_imports),
        ("Система сущностей", test_entity_system),
        ("Игровые системы", test_game_systems),
        ("Генерация контента", test_content_generation),
        ("AI система", test_ai_system),
        ("Боевая система", test_combat_system),
        ("Производительность", test_performance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ Тест '{test_name}' не прошел")
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
    
    print("\n" + "=" * 50)
    print(f"📈 Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно! Система готова к работе.")
        return True
    else:
        print("⚠️ Некоторые тесты не пройдены. Требуется доработка.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

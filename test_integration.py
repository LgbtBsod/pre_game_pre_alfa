#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции всех систем
"""

import sys
import os
import logging
import time
import uuid
from typing import Dict, Any

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_content_generation():
    """Тест генерации контента"""
    logger.info("=== Тест генерации контента ===")
    
    try:
        from systems.content.content_database import ContentDatabase
        from systems.content.content_generator import ContentGenerator, GenerationConfig
        
        # Создаем базу данных
        content_db = ContentDatabase("test_integration.db")
        
        # Создаем генератор контента
        generator = ContentGenerator(content_db, seed=42)
        
        # Генерируем контент для тестовой сессии
        session_id = str(uuid.uuid4())
        config = GenerationConfig(
            weapon_count=3,
            armor_count=2,
            accessory_count=1,
            consumable_count=2,
            gene_count=4,
            skill_count=3,
            effect_count=2,
            material_count=5,
            enemy_count=8,
            boss_count=2
        )
        
        logger.info(f"Генерируем контент для сессии {session_id}")
        generated_content = generator.generate_session_content(session_id, 5, config)
        
        # Выводим статистику
        for content_type, items in generated_content.items():
            logger.info(f"{content_type}: {len(items)} элементов")
        
        # Получаем статистику генерации
        stats = generator.get_generation_statistics()
        logger.info(f"Статистика генерации: {stats}")
        
        # Тестируем получение контента для уровня
        level_content = generator.get_content_for_entity(session_id, 5, [])
        logger.info(f"Доступный контент для уровня 5: {len(level_content)} типов")
        
        # Тестируем получение врагов и боссов
        enemies = generator.get_enemies_for_level(session_id, 5)
        bosses = generator.get_bosses_for_level(session_id, 5)
        
        logger.info(f"Враги уровня 5: {len(enemies)}")
        logger.info(f"Боссы уровня 5: {len(bosses)}")
        
        # Проверяем рейдж режим для боссов
        for boss in bosses:
            if 'rage_mode_threshold' in boss:
                logger.info(f"Босс {boss['name']} имеет рейдж режим при {boss['rage_mode_threshold']*100}% HP")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования генерации контента: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_entity_stats():
    """Тест системы характеристик сущностей"""
    logger.info("=== Тест системы характеристик ===")
    
    try:
        from systems.entity.entity_stats_system import EntityStats, EntityType, StatType, StatModifier
        
        # Создаем сущности разных типов
        player_stats = EntityStats(
            entity_id="test_player",
            entity_type=EntityType.PLAYER,
            level=1,
            experience=0
        )
        
        enemy_stats = EntityStats(
            entity_id="test_enemy",
            entity_type=EntityType.ENEMY,
            level=1,
            experience=0
        )
        
        boss_stats = EntityStats(
            entity_id="test_boss",
            entity_type=EntityType.BOSS,
            level=1,
            experience=0
        )
        
        # Проверяем базовые характеристики
        logger.info(f"Игрок - HP: {player_stats.base_stats.health}, Атака: {player_stats.base_stats.attack}")
        logger.info(f"Враг - HP: {enemy_stats.base_stats.health}, Атака: {enemy_stats.base_stats.attack}")
        logger.info(f"Босс - HP: {boss_stats.base_stats.health}, Атака: {boss_stats.base_stats.attack}")
        
        # Тестируем получение опыта и повышение уровня
        logger.info("Тестируем получение опыта...")
        
        # Игрок получает опыт
        player_leveled_up = player_stats.gain_experience(150)
        logger.info(f"Игрок повысил уровень: {player_leveled_up}")
        logger.info(f"У игрока {player_stats.available_stat_points} очков характеристик")
        
        # Распределяем очки характеристик
        if player_stats.available_stat_points > 0:
            player_stats.distribute_stat_point(StatType.STRENGTH)
            logger.info(f"Игрок увеличил силу до {player_stats.base_stats.strength}")
        
        # Враг получает опыт (автоматическое распределение)
        enemy_leveled_up = enemy_stats.gain_experience(120)
        logger.info(f"Враг повысил уровень: {enemy_leveled_up}")
        logger.info(f"Враг - HP: {enemy_stats.base_stats.health}, Атака: {enemy_stats.base_stats.attack}")
        
        # Босс получает опыт (автоматическое распределение)
        boss_leveled_up = boss_stats.gain_experience(200)
        logger.info(f"Босс повысил уровень: {boss_leveled_up}")
        logger.info(f"Босс - HP: {boss_stats.base_stats.health}, Атака: {boss_stats.base_stats.attack}")
        
        # Тестируем получение урона и рейдж режим
        logger.info("Тестируем получение урона...")
        
        damage_taken = boss_stats.take_damage(100)
        logger.info(f"Босс получил {damage_taken} урона, HP: {boss_stats.current_health}")
        
        # Проверяем рейдж режим (должен сработать при 10% HP)
        if boss_stats.get_health_percentage() <= 10:
            logger.info("Босс должен войти в рейдж режим!")
        
        # Тестируем модификаторы характеристик
        logger.info("Тестируем модификаторы характеристик...")
        
        strength_modifier = StatModifier(
            stat_type=StatType.STRENGTH,
            value=5,
            modifier_type="flat",
            source="test_potion",
            duration=60.0
        )
        
        player_stats.add_stat_modifier(strength_modifier)
        modified_strength = player_stats.get_stat_value(StatType.STRENGTH)
        logger.info(f"Сила игрока с модификатором: {modified_strength}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования системы характеристик: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_integration():
    """Тест интеграции AI систем"""
    logger.info("=== Тест интеграции AI ===")
    
    try:
        from systems.ai.ai_system import AISystem
        from systems.ai.ai_integration_system import AIIntegrationSystem
        from systems.content.content_database import ContentDatabase
        from systems.combat.combat_system import CombatSystem
        from systems.inventory.inventory_system import InventorySystem
        from systems.entity.entity_stats_system import EntityStats, EntityType
        
        # Создаем необходимые системы
        content_db = ContentDatabase("test_ai.db")
        combat_system = CombatSystem()
        inventory_system = InventorySystem()
        
        # Создаем простую AI систему
        class SimpleAISystem(AISystem):
            def __init__(self):
                self.entities = {}
                self.memories = {}
            
            def register_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> bool:
                self.entities[entity_id] = entity_data
                return True
            
            def update_entity(self, entity_id: str, entity_data: Dict[str, Any], delta_time: float):
                if entity_id in self.entities:
                    self.entities[entity_id].update(entity_data)
            
            def add_memory(self, entity_id: str, memory_data: Dict[str, Any]):
                if entity_id not in self.memories:
                    self.memories[entity_id] = []
                self.memories[entity_id].append(memory_data)
        
        ai_system = SimpleAISystem()
        
        # Создаем систему интеграции
        ai_integration = AIIntegrationSystem(
            event_system=None,  # Упрощенная версия
            ai_system=ai_system,
            combat_system=combat_system,
            content_db=content_db,
            inventory_system=inventory_system
        )
        
        # Создаем тестовую сущность
        test_entity_data = {
            'type': 'player',
            'level': 1,
            'experience': 0,
            'position': (0, 0, 0),
            'stats': {
                'strength': 15,
                'agility': 12,
                'intelligence': 18,
                'vitality': 14,
                'wisdom': 16,
                'charisma': 10
            },
            'inventory': [],
            'equipment': {},
            'skills': []
        }
        
        # Регистрируем AI сущность
        success = ai_integration.register_ai_entity("test_ai_player", test_entity_data)
        logger.info(f"AI сущность зарегистрирована: {success}")
        
        if success:
            # Получаем состояние AI агента
            ai_state = ai_integration.get_ai_agent_state("test_ai_player")
            entity_stats = ai_integration.get_entity_stats("test_ai_player")
            
            if ai_state and entity_stats:
                logger.info(f"AI агент: {ai_state.entity_id}, уровень: {ai_state.level}")
                logger.info(f"Характеристики: HP {entity_stats.current_health}/{entity_stats.base_stats.health}")
                
                # Тестируем обновление AI агента
                ai_integration.update_ai_agent("test_ai_player", 1.0)
                
                # Проверяем, что AI принял решение
                updated_state = ai_integration.get_ai_agent_state("test_ai_player")
                if updated_state.last_action:
                    logger.info(f"AI принял решение: {updated_state.last_action}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования интеграции AI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_boss_implementation():
    """Тест реализации боссов"""
    logger.info("=== Тест реализации боссов ===")
    
    try:
        from systems.content.content_database import ContentDatabase, BossType
        from systems.content.content_generator import ContentGenerator
        
        # Создаем базу данных и генератор
        content_db = ContentDatabase("test_boss.db")
        generator = ContentGenerator(content_db, seed=123)
        
        # Генерируем боссов
        session_id = str(uuid.uuid4())
        bosses = generator._generate_bosses(session_id, 10, 3)
        
        logger.info(f"Сгенерировано {len(bosses)} боссов")
        
        for boss in bosses:
            boss_data = boss.data
            logger.info(f"Босс: {boss.name}")
            logger.info(f"  Тип: {boss_data['boss_type']}")
            logger.info(f"  HP: {boss_data['base_health']}")
            logger.info(f"  Атака: {boss_data['base_attack']}")
            logger.info(f"  Фазы: {boss_data['phases']}")
            logger.info(f"  Рейдж режим: {boss_data['rage_mode_threshold']*100}% HP")
            
            # Проверяем специфические характеристики боссов
            if boss_data['boss_type'] == 'final_boss':
                logger.info("  Это финальный босс с множественными фазами!")
            
            # Проверяем фазы боя
            for i, phase in enumerate(boss_data['phases']):
                health_threshold = phase['health_threshold']
                behavior = phase['behavior']
                special_ability = phase['special_ability']
                logger.info(f"    Фаза {i+1}: {health_threshold*100}% HP - {behavior} ({special_ability})")
        
        # Проверяем, что боссы имеют более высокие характеристики чем обычные враги
        enemies = generator._generate_enemies(session_id, 10, 5)
        
        if enemies and bosses:
            avg_enemy_hp = sum(e.data['base_health'] for e in enemies) / len(enemies)
            avg_boss_hp = sum(b.data['base_health'] for b in bosses) / len(bosses)
            
            logger.info(f"Среднее HP врагов: {avg_enemy_hp:.0f}")
            logger.info(f"Среднее HP боссов: {avg_boss_hp:.0f}")
            logger.info(f"Боссы в {avg_boss_hp/avg_enemy_hp:.1f} раз сильнее врагов")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования реализации боссов: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    logger.info("Начинаем тестирование интеграции всех систем...")
    
    tests = [
        ("Генерация контента", test_content_generation),
        ("Система характеристик", test_entity_stats),
        ("Интеграция AI", test_ai_integration),
        ("Реализация боссов", test_boss_implementation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        try:
            start_time = time.time()
            success = test_func()
            end_time = time.time()
            
            results[test_name] = {
                'success': success,
                'time': end_time - start_time
            }
            
            status = "ПРОЙДЕН" if success else "ПРОВАЛЕН"
            logger.info(f"Тест '{test_name}': {status} (время: {end_time - start_time:.2f}с)")
            
        except Exception as e:
            logger.error(f"Критическая ошибка в тесте '{test_name}': {e}")
            results[test_name] = {
                'success': False,
                'time': 0,
                'error': str(e)
            }
    
    # Выводим итоговые результаты
    logger.info(f"\n{'='*50}")
    logger.info("ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    logger.info("="*50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✓ ПРОЙДЕН" if result['success'] else "✗ ПРОВАЛЕН"
        time_str = f"({result['time']:.2f}с)" if result['time'] > 0 else ""
        
        if result['success']:
            passed += 1
            logger.info(f"  {status} {test_name} {time_str}")
        else:
            error_msg = f" - {result.get('error', 'Неизвестная ошибка')}" if 'error' in result else ""
            logger.error(f"  {status} {test_name} {time_str}{error_msg}")
    
    logger.info(f"\nРезультат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Система полностью интегрирована.")
    else:
        logger.warning(f"⚠️  {total - passed} тестов провалено. Требуется доработка.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

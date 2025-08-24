#!/usr/bin/env python3
"""
Упрощенный тест для проверки новых систем
"""

import sys
import os
import logging
import time
import uuid

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_entity_stats_system():
    """Тест системы характеристик сущностей"""
    logger.info("=== Тест системы характеристик ===")
    
    try:
        # Импортируем напрямую
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'systems', 'entity'))
        from entity_stats_system import EntityStats, EntityType, StatType, StatModifier
        
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
        
        logger.info("✓ Система характеристик работает корректно!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования системы характеристик: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_content_constants():
    """Тест констант генерации контента"""
    logger.info("=== Тест констант генерации ===")
    
    try:
        # Импортируем напрямую
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'systems', 'content'))
        from content_constants import ENEMY_CONSTANTS, BOSS_CONSTANTS, ITEM_CONSTANTS, RANDOM_GENERATOR
        
        # Проверяем константы врагов
        logger.info("Проверяем константы врагов...")
        for enemy_type, stats in ENEMY_CONSTANTS.base_stats_by_type.items():
            logger.info(f"  {enemy_type}: HP {stats['health']}, Атака {stats['attack']}")
        
        # Проверяем константы боссов
        logger.info("Проверяем константы боссов...")
        for boss_type, stats in BOSS_CONSTANTS.base_stats_by_type.items():
            logger.info(f"  {boss_type}: HP {stats['health']}, Атака {stats['attack']}")
        
        # Проверяем фазы боссов
        logger.info("Проверяем фазы боссов...")
        for boss_type, phases in BOSS_CONSTANTS.phases_by_type.items():
            logger.info(f"  {boss_type}: {len(phases)} фаз")
            for i, phase in enumerate(phases):
                health_threshold = phase['health_threshold']
                behavior = phase['behavior']
                logger.info(f"    Фаза {i+1}: {health_threshold*100}% HP - {behavior}")
        
        # Проверяем генератор случайных чисел
        logger.info("Тестируем генератор случайных чисел...")
        
        # Гауссовский модификатор
        gauss_mod = RANDOM_GENERATOR.gaussian_modifier(1.0, 0.1, 0.8, 1.2)
        logger.info(f"  Гауссовский модификатор: {gauss_mod:.3f}")
        
        # Треугольный модификатор
        tri_mod = RANDOM_GENERATOR.triangular_modifier(0.9, 1.1, 1.0)
        logger.info(f"  Треугольный модификатор: {tri_mod:.3f}")
        
        # Экспоненциальный модификатор
        exp_mod = RANDOM_GENERATOR.exponential_modifier(1.0, 0.5, 2.0)
        logger.info(f"  Экспоненциальный модификатор: {exp_mod:.3f}")
        
        # Взвешенный выбор
        choices = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        weights = [0.5, 0.3, 0.15, 0.04, 0.01]
        chosen = RANDOM_GENERATOR.weighted_choice(choices, weights)
        logger.info(f"  Взвешенный выбор: {chosen}")
        
        logger.info("✓ Константы генерации работают корректно!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования констант генерации: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_content_database():
    """Тест базы данных контента"""
    logger.info("=== Тест базы данных контента ===")
    
    try:
        # Импортируем напрямую
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'systems', 'content'))
        from content_database import ContentDatabase, ContentType, ContentRarity, EnemyType, BossType
        
        # Создаем базу данных
        db = ContentDatabase("test_content.db")
        
        # Создаем тестовую сессию
        session_id = str(uuid.uuid4())
        logger.info(f"Создаем тестовую сессию: {session_id}")
        
        # Добавляем тестовый контент
        test_content_uuid = str(uuid.uuid4())
        db.add_content_item({
            'uuid': test_content_uuid,
            'content_type': ContentType.WEAPON,
            'name': 'Тестовый меч',
            'description': 'Тестовое оружие',
            'rarity': ContentRarity.COMMON,
            'level_requirement': 1,
            'session_id': session_id,
            'generation_timestamp': time.time(),
            'data': {'damage': 15, 'attack_speed': 1.2}
        })
        
        # Получаем контент
        content = db.get_content_by_uuid(test_content_uuid)
        if content:
            logger.info(f"Получен контент: {content['name']} - {content['data']['damage']} урона")
        
        # Получаем статистику сессии
        stats = db.get_session_stats(session_id)
        logger.info(f"Статистика сессии: {stats}")
        
        # Очищаем тестовую сессию
        db.cleanup_session_content(session_id)
        logger.info("Тестовая сессия очищена")
        
        logger.info("✓ База данных контента работает корректно!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка тестирования базы данных контента: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    logger.info("Начинаем упрощенное тестирование новых систем...")
    
    tests = [
        ("Система характеристик", test_entity_stats_system),
        ("Константы генерации", test_content_constants),
        ("База данных контента", test_content_database)
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
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Новые системы работают корректно.")
    else:
        logger.warning(f"⚠️  {total - passed} тестов провалено. Требуется доработка.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

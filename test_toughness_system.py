#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы стойкости и характеристик предметов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_toughness_system():
    """Тестирование системы стойкости"""
    print("=== Тестирование системы стойкости ===")
    
    try:
        print("1. Импорт констант...")
        from src.core.constants import (
            BASE_STATS, ITEM_STATS, TOUGHNESS_MECHANICS, ENEMY_WEAKNESSES,
            DamageType, WeaponType, ArmorType, AccessoryType
        )
        print("   ✓ Константы импортированы")
        
        print("2. Проверка базовых характеристик...")
        print(f"   ✓ Базовые характеристики: {len(BASE_STATS)} параметров")
        print(f"      - Здоровье: {BASE_STATS['health']}")
        print(f"      - Стойкость: {BASE_STATS['toughness']}")
        print(f"      - Сопротивление стойкости: {BASE_STATS['toughness_resistance']}")
        print(f"      - Сопротивление оглушению: {BASE_STATS['stun_resistance']}")
        print(f"      - Эффективность пробития: {BASE_STATS['break_efficiency']}")
        
        print("3. Проверка характеристик предметов...")
        print(f"   ✓ Характеристики оружия: {len(ITEM_STATS['weapon'])} параметров")
        print(f"      - Урон по стойкости: {ITEM_STATS['weapon']['toughness_damage']}")
        print(f"      - Эффективность пробития: {ITEM_STATS['weapon']['break_efficiency']}")
        
        print(f"   ✓ Характеристики брони: {len(ITEM_STATS['armor'])} параметров")
        print(f"      - Сопротивление стойкости: {ITEM_STATS['armor']['toughness_resistance']}")
        print(f"      - Сопротивление оглушению: {ITEM_STATS['armor']['stun_resistance']}")
        
        print(f"   ✓ Характеристики аксессуаров: {len(ITEM_STATS['accessory'])} параметров")
        print(f"      - Бонус к интеллекту: {ITEM_STATS['accessory']['intelligence']}")
        print(f"      - Бонус к силе: {ITEM_STATS['accessory']['strength']}")
        
        print("4. Проверка механики стойкости...")
        print(f"   ✓ Параметры стойкости: {len(TOUGHNESS_MECHANICS)} настроек")
        print(f"      - Базовая стойкость: {TOUGHNESS_MECHANICS['base_toughness']}")
        print(f"      - Скорость восстановления: {TOUGHNESS_MECHANICS['toughness_regen_rate']}")
        print(f"      - Длительность оглушения: {TOUGHNESS_MECHANICS['stun_duration']}")
        print(f"      - Множитель слабости: {TOUGHNESS_MECHANICS['weakness_multiplier']}")
        
        print("5. Проверка слабостей врагов...")
        print(f"   ✓ Типы слабостей: {len(ENEMY_WEAKNESSES)} категорий")
        for weakness_type, damage_types in list(ENEMY_WEAKNESSES.items())[:5]:
            print(f"      - {weakness_type}: {[dt.value for dt in damage_types]}")
        
        print("6. Тестирование генерации предметов...")
        from src.systems.content.content_generator import ContentGenerator
        
        # Создаем генератор контента
        generator = ContentGenerator()
        if generator.initialize():
            print("   ✓ ContentGenerator инициализирован")
            
            # Генерируем оружие
            weapon = generator._generate_weapon(5)
            if weapon:
                print(f"   ✓ Оружие сгенерировано: {weapon.name}")
                props = weapon.properties
                print(f"      - Урон по стойкости: {props.get('toughness_damage', 'N/A')}")
                print(f"      - Эффективность пробития: {props.get('break_efficiency', 'N/A')}")
                print(f"      - Атака: {props.get('attack', 'N/A')}")
                print(f"      - Скорость: {props.get('speed', 'N/A')}")
            else:
                print("   ✗ Ошибка генерации оружия")
            
            # Генерируем броню
            armor = generator._generate_armor(5)
            if armor:
                print(f"   ✓ Броня сгенерирована: {armor.name}")
                props = armor.properties
                print(f"      - Сопротивление стойкости: {props.get('toughness_resistance', 'N/A')}")
                print(f"      - Сопротивление оглушению: {props.get('stun_resistance', 'N/A')}")
                print(f"      - Защита: {props.get('defense', 'N/A')}")
            else:
                print("   ✗ Ошибка генерации брони")
        else:
            print("   ✗ ContentGenerator не инициализирован")
        
        print("\n=== Тестирование завершено успешно ===")
        
    except Exception as e:
        print(f"✗ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_toughness_system()

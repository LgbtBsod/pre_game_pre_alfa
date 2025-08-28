#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обновленной структуры констант
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_new_constants():
    """Тестирование новой структуры констант"""
    print("=== Тестирование новой структуры констант ===")
    
    try:
        print("1. Импорт констант...")
        from src.core.constants import (
            WeaponType, ArmorType, AccessoryType, ConsumableType,
            DamageType, DEFAULT_RESISTANCES, DAMAGE_BOOSTS, DAMAGE_MULTIPLIERS
        )
        print("   ✓ Константы импортированы")
        
        print("2. Проверка типов оружия...")
        weapon_types = list(WeaponType)
        print(f"   ✓ Найдено {len(weapon_types)} типов оружия:")
        for wt in weapon_types[:5]:  # Показываем первые 5
            print(f"      - {wt.name}: {wt.value}")
        
        print("3. Проверка типов брони...")
        armor_types = list(ArmorType)
        print(f"   ✓ Найдено {len(armor_types)} типов брони:")
        for at in armor_types[:5]:  # Показываем первые 5
            print(f"      - {at.name}: {at.value}")
        
        print("4. Проверка типов аксессуаров...")
        accessory_types = list(AccessoryType)
        print(f"   ✓ Найдено {len(accessory_types)} типов аксессуаров:")
        for at in accessory_types[:5]:  # Показываем первые 5
            print(f"      - {at.name}: {at.value}")
        
        print("5. Проверка типов расходников...")
        consumable_types = list(ConsumableType)
        print(f"   ✓ Найдено {len(consumable_types)} типов расходников:")
        for ct in consumable_types[:5]:  # Показываем первые 5
            print(f"      - {ct.name}: {ct.value}")
        
        print("6. Проверка типов урона...")
        damage_types = list(DamageType)
        print(f"   ✓ Найдено {len(damage_types)} типов урона:")
        for dt in damage_types[:8]:  # Показываем первые 8
            print(f"      - {dt.name}: {dt.value}")
        
        print("7. Проверка сопротивлений...")
        print(f"   ✓ Сопротивления сгенерированы для {len(DEFAULT_RESISTANCES)} типов урона")
        print(f"      - Физический урон: {DEFAULT_RESISTANCES[DamageType.PHYSICAL]}")
        print(f"      - Истинный урон: {DEFAULT_RESISTANCES[DamageType.TRUE]}")
        print(f"      - Генетический урон: {DEFAULT_RESISTANCES[DamageType.GENETIC]}")
        
        print("8. Проверка бустов...")
        print(f"   ✓ Бусты сгенерированы для {len(DAMAGE_BOOSTS)} типов урона")
        print(f"      - Физический урон: {DAMAGE_BOOSTS[DamageType.PHYSICAL]}")
        print(f"      - Истинный урон: {DAMAGE_BOOSTS[DamageType.TRUE]}")
        print(f"      - Эмоциональный урон: {DAMAGE_BOOSTS[DamageType.EMOTIONAL]}")
        
        print("9. Проверка множителей...")
        print(f"   ✓ Множители определены для {len(DAMAGE_MULTIPLIERS)} типов урона")
        print(f"      - Физический урон: {DAMAGE_MULTIPLIERS[DamageType.PHYSICAL]}")
        print(f"      - Истинный урон: {DAMAGE_MULTIPLIERS[DamageType.TRUE]}")
        print(f"      - Генетический урон: {DAMAGE_MULTIPLIERS[DamageType.GENETIC]}")
        
        print("\n=== Тестирование завершено успешно ===")
        
    except Exception as e:
        print(f"✗ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_constants()

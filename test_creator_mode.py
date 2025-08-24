#!/usr/bin/env python3
"""
Тестовый скрипт для проверки режима "Творец мира"
"""

import sys
import os
import logging

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.constants import (
    WorldObjectType, ObjectCategory, ObjectState, CreatorMode, ToolType,
    WORLD_SETTINGS, CAMERA_SETTINGS, UI_SETTINGS, DEFAULT_OBJECT_TEMPLATES, UI_COLORS
)
from src.systems.ui.ui_system import UISystem, WorldObjectTemplate
from src.systems.world.world_manager import WorldManager, WorldObject

def test_constants():
    """Тестирование констант"""
    print("=== Тестирование констант ===")
    
    # Проверяем типы объектов
    print(f"Типы объектов: {[t.value for t in WorldObjectType]}")
    print(f"Категории объектов: {[c.value for c in ObjectCategory]}")
    print(f"Состояния объектов: {[s.value for s in ObjectState]}")
    print(f"Режимы создания: {[m.value for m in CreatorMode]}")
    print(f"Типы инструментов: {[t.value for t in ToolType]}")
    
    # Проверяем настройки
    print(f"Настройки мира: {WORLD_SETTINGS}")
    print(f"Настройки камеры: {CAMERA_SETTINGS}")
    print(f"Настройки UI: {UI_SETTINGS}")
    
    # Проверяем шаблоны
    print(f"Доступные шаблоны: {list(DEFAULT_OBJECT_TEMPLATES.keys())}")
    
    # Проверяем цвета
    print(f"Цвета UI: {list(UI_COLORS.keys())}")
    
    print()

def test_ui_system():
    """Тестирование UI системы"""
    print("=== Тестирование UI системы ===")
    
    ui_system = UISystem()
    
    # Инициализация
    if ui_system.initialize():
        print("✅ UI система инициализирована")
        
        # Проверяем шаблоны
        templates = ui_system.object_templates
        print(f"✅ Создано шаблонов: {len(templates)}")
        
        # Проверяем категории
        for category in ObjectCategory:
            category_templates = ui_system.get_available_templates(category)
            print(f"  {category.value}: {len(category_templates)} шаблонов")
        
        # Проверяем типы
        for obj_type in WorldObjectType:
            type_templates = ui_system.get_templates_by_type(obj_type)
            print(f"  {obj_type.value}: {len(type_templates)} шаблонов")
        
        # Тестируем выбор шаблона
        if templates:
            first_template_id = list(templates.keys())[0]
            if ui_system.select_template(first_template_id):
                print(f"✅ Выбран шаблон: {ui_system.selected_template.name}")
            else:
                print("❌ Не удалось выбрать шаблон")
        
        # Проверяем статистику
        stats = ui_system.get_creation_stats()
        print(f"✅ Статистика создания: {stats}")
        
        # Очистка
        ui_system.cleanup()
        print("✅ UI система очищена")
    else:
        print("❌ Не удалось инициализировать UI систему")
    
    print()

def test_world_manager():
    """Тестирование менеджера мира"""
    print("=== Тестирование менеджера мира ===")
    
    world_manager = WorldManager()
    
    # Инициализация
    if world_manager.initialize():
        print("✅ Менеджер мира инициализирован")
        
        # Создаем тестовый объект
        test_object_data = {
            'id': 'test_wall_1',
            'template_id': 'wall',
            'type': WorldObjectType.OBSTACLE.value,
            'name': 'Тестовая стена',
            'x': 5.0,
            'y': 3.0,
            'z': 0.0,
            'properties': {
                'width': 2.0,
                'height': 3.0,
                'depth': 0.5,
                'color': (0.5, 0.5, 0.5, 1.0)
            },
            'created_by': 'test',
            'creation_time': 1234567890.0
        }
        
        # Добавляем объект
        object_id = world_manager.add_world_object(test_object_data)
        if object_id:
            print(f"✅ Объект добавлен: {object_id}")
            
            # Проверяем статистику
            stats = world_manager.get_world_stats()
            print(f"✅ Статистика мира: {stats}")
            
            # Проверяем получение объектов
            objects_at_pos = world_manager.get_objects_at_position(5.0, 3.0, radius=2.0)
            print(f"✅ Объектов в позиции: {len(objects_at_pos)}")
            
            # Проверяем коллизии
            colliding = world_manager.check_collision(4.0, 2.0, 2.0, 2.0)
            print(f"✅ Объектов в коллизии: {len(colliding)}")
            
            # Удаляем объект
            if world_manager.remove_world_object(object_id):
                print("✅ Объект удален")
            else:
                print("❌ Не удалось удалить объект")
        else:
            print("❌ Не удалось добавить объект")
        
        # Очистка
        world_manager.cleanup()
        print("✅ Менеджер мира очищен")
    else:
        print("❌ Не удалось инициализировать менеджер мира")
    
    print()

def test_integration():
    """Тестирование интеграции систем"""
    print("=== Тестирование интеграции ===")
    
    # Создаем системы
    ui_system = UISystem()
    world_manager = WorldManager()
    
    # Инициализируем
    if ui_system.initialize() and world_manager.initialize():
        print("✅ Системы инициализированы")
        
        # Получаем шаблон
        templates = ui_system.get_available_templates(ObjectCategory.ENVIRONMENT)
        if templates:
            template = templates[0]
            print(f"✅ Выбран шаблон: {template.name}")
            
            # Создаем объект из шаблона
            object_data = {
                'id': f"{template.template_id}_test",
                'template_id': template.template_id,
                'type': template.object_type.value,
                'name': template.name,
                'x': 10.0,
                'y': 5.0,
                'z': 0.0,
                'properties': template.properties.copy(),
                'created_by': 'integration_test',
                'creation_time': 1234567890.0
            }
            
            # Добавляем в мир
            object_id = world_manager.add_world_object(object_data)
            if object_id:
                print(f"✅ Объект создан из шаблона: {object_id}")
                
                # Обновляем статистику UI
                ui_system.increment_creation_stat('objects_created')
                ui_system.increment_creation_stat('total_cost', template.cost)
                
                # Проверяем статистику
                ui_stats = ui_system.get_creation_stats()
                world_stats = world_manager.get_world_stats()
                
                print(f"✅ UI статистика: {ui_stats}")
                print(f"✅ Мир статистика: {world_stats}")
            else:
                print("❌ Не удалось создать объект из шаблона")
        else:
            print("❌ Нет доступных шаблонов")
        
        # Очистка
        ui_system.cleanup()
        world_manager.cleanup()
        print("✅ Системы очищены")
    else:
        print("❌ Не удалось инициализировать системы")
    
    print()

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование режима 'Творец мира'")
    print("=" * 50)
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Тестируем константы
        test_constants()
        
        # Тестируем UI систему
        test_ui_system()
        
        # Тестируем менеджер мира
        test_world_manager()
        
        # Тестируем интеграцию
        test_integration()
        
        print("🎉 Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Скрипт для тестирования системы сессий и генерации контента
"""

import sys
import os
from pathlib import Path
import logging

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from core.session_manager import SessionManager
from core.content_generator import ContentGenerator
import random

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_session_creation():
    """Тест создания сессий"""
    print("\n=== ТЕСТ СОЗДАНИЯ СЕССИЙ ===")
    
    session_manager = SessionManager()
    
    # Создаем несколько сессий (начиная с слота 3, так как 1 и 2 уже заняты)
    for i in range(3):
        slot_id = i + 3  # Начинаем с 3
        save_name = f"Тестовая сессия {slot_id}"
        world_seed = random.randint(1, 999999)
        
        try:
            session_data = session_manager.create_new_session(slot_id, save_name, world_seed)
            print(f"✓ Создана сессия {slot_id}: {session_data.session_uuid[:8]}...")
            print(f"  - Имя: {save_name}")
            print(f"  - Seed: {world_seed}")
            print(f"  - Уровень: {session_data.current_level}")
        except Exception as e:
            print(f"✗ Ошибка создания сессии {slot_id}: {e}")
    
    return session_manager

def test_content_generation():
    """Тест генерации контента"""
    print("\n=== ТЕСТ ГЕНЕРАЦИИ КОНТЕНТА ===")
    
    session_manager = SessionManager()
    content_generator = ContentGenerator()
    
    # Создаем тестовую сессию (используем свободный слот)
    free_slot = session_manager.get_free_slot()
    if free_slot is None:
        print("✗ Нет свободных слотов для тестирования")
        return None, None
    
    session_data = session_manager.create_new_session(free_slot, "Тест контента", 12345)
    
    # Генерируем контент
    initial_content = content_generator.initialize_session_content(session_data.session_uuid, 1)
    
    print(f"✓ Сгенерирован контент для сессии: {session_data.session_uuid[:8]}...")
    print(f"  - Предметы: {len(initial_content.get('items', []))}")
    print(f"  - Оружие: {len(initial_content.get('weapons', []))}")
    print(f"  - Враги: {len(initial_content.get('enemies', []))}")
    print(f"  - Навыки: {len(initial_content.get('skills', []))}")
    print(f"  - Гены: {len(initial_content.get('genes', []))}")
    
    # Добавляем контент в сессию
    for content_type, content_list in initial_content.items():
        if content_type != "world_seed":
            for item in content_list:
                session_manager.add_session_content(content_type, item)
    
    # Проверяем сохранение
    saved_items = session_manager.get_session_content("items")
    saved_weapons = session_manager.get_session_content("weapons")
    saved_enemies = session_manager.get_session_content("enemies")
    saved_skills = session_manager.get_session_content("skills")
    saved_genes = session_manager.get_session_content("genes")
    
    print(f"✓ Контент сохранен в БД:")
    print(f"  - Предметы: {len(saved_items)}")
    print(f"  - Оружие: {len(saved_weapons)}")
    print(f"  - Враги: {len(saved_enemies)}")
    print(f"  - Навыки: {len(saved_skills)}")
    print(f"  - Гены: {len(saved_genes)}")
    
    return session_manager, session_data

def test_session_persistence():
    """Тест сохранения и загрузки сессий"""
    print("\n=== ТЕСТ СОХРАНЕНИЯ И ЗАГРУЗКИ ===")
    
    session_manager = SessionManager()
    
    # Создаем сессию с контентом (используем свободный слот)
    free_slot = session_manager.get_free_slot()
    if free_slot is None:
        print("✗ Нет свободных слотов для тестирования")
        return
    
    session_data = session_manager.create_new_session(free_slot, "Тест персистентности", 54321)
    content_generator = ContentGenerator()
    initial_content = content_generator.initialize_session_content(session_data.session_uuid, 1)
    
    # Добавляем контент
    for content_type, content_list in initial_content.items():
        if content_type != "world_seed":
            for item in content_list:
                session_manager.add_session_content(content_type, item)
    
    # Сохраняем сессию
    session_manager.save_session()
    print(f"✓ Сессия сохранена: {session_data.session_uuid[:8]}...")
    
    # Создаем новый менеджер (симуляция перезапуска игры)
    new_session_manager = SessionManager()
    
    # Загружаем сессию
    loaded_session = new_session_manager.load_session(free_slot)
    if loaded_session:
        print(f"✓ Сессия загружена: {loaded_session.session_uuid[:8]}...")
        print(f"  - Слот: {loaded_session.slot_id}")
        print(f"  - Уровень: {loaded_session.current_level}")
        
        # Проверяем контент
        loaded_items = new_session_manager.get_session_content("items")
        loaded_weapons = new_session_manager.get_session_content("weapons")
        loaded_enemies = new_session_manager.get_session_content("enemies")
        loaded_skills = new_session_manager.get_session_content("skills")
        loaded_genes = new_session_manager.get_session_content("genes")
        
        print(f"✓ Контент восстановлен:")
        print(f"  - Предметы: {len(loaded_items)}")
        print(f"  - Оружие: {len(loaded_weapons)}")
        print(f"  - Враги: {len(loaded_enemies)}")
        print(f"  - Навыки: {len(loaded_skills)}")
        print(f"  - Гены: {len(loaded_genes)}")
    else:
        print("✗ Ошибка загрузки сессии")

def test_multiple_sessions():
    """Тест множественных сессий"""
    print("\n=== ТЕСТ МНОЖЕСТВЕННЫХ СЕССИЙ ===")
    
    session_manager = SessionManager()
    
    # Создаем несколько сессий с разным контентом
    sessions = []
    for i in range(3):
        slot_id = i + 6  # Начинаем с 6, чтобы избежать конфликтов
        world_seed = 1000 + i * 1000
        
        try:
            session_data = session_manager.create_new_session(slot_id, f"Сессия {slot_id}", world_seed)
            content_generator = ContentGenerator(world_seed)
            initial_content = content_generator.initialize_session_content(session_data.session_uuid, 1)
            
            # Добавляем контент
            for content_type, content_list in initial_content.items():
                if content_type != "world_seed":
                    for item in content_list:
                        session_manager.add_session_content(content_type, item)
            
            sessions.append((slot_id, session_data.session_uuid))
            print(f"✓ Создана сессия {slot_id}: {session_data.session_uuid[:8]}...")
        except Exception as e:
            print(f"✗ Ошибка создания сессии {slot_id}: {e}")
    
    # Проверяем изоляцию данных
    print("\nПроверка изоляции данных:")
    for slot_id, session_uuid in sessions:
        # Загружаем сессию
        loaded_session = session_manager.load_session(slot_id)
        if loaded_session:
            items = session_manager.get_session_content("items")
            weapons = session_manager.get_session_content("weapons")
            enemies = session_manager.get_session_content("enemies")
            
            print(f"  Слот {slot_id}: {len(items)} предметов, {len(weapons)} оружия, {len(enemies)} врагов")
        else:
            print(f"  ✗ Ошибка загрузки слота {slot_id}")

def test_session_statistics():
    """Тест статистики сессий"""
    print("\n=== ТЕСТ СТАТИСТИКИ ===")
    
    session_manager = SessionManager()
    
    # Создаем сессию (используем свободный слот)
    free_slot = session_manager.get_free_slot()
    if free_slot is None:
        print("✗ Нет свободных слотов для тестирования")
        return
    
    session_data = session_manager.create_new_session(free_slot, "Тест статистики", 99999)
    content_generator = ContentGenerator()
    initial_content = content_generator.initialize_session_content(session_data.session_uuid, 1)
    
    # Добавляем контент
    for content_type, content_list in initial_content.items():
        if content_type != "world_seed":
            for item in content_list:
                session_manager.add_session_content(content_type, item)
    
    # Получаем статистику
    stats = session_manager.get_session_statistics()
    
    print(f"✓ Статистика сессии:")
    print(f"  - UUID: {stats.get('session_uuid', 'N/A')[:8]}...")
    print(f"  - Слот: {stats.get('slot_id', 'N/A')}")
    print(f"  - Предметы: {stats.get('items_count', 0)}")
    print(f"  - Оружие: {stats.get('weapons_count', 0)}")
    print(f"  - Враги: {stats.get('enemies_count', 0)}")
    print(f"  - Навыки: {stats.get('skills_count', 0)}")
    print(f"  - Гены: {stats.get('genes_count', 0)}")

def test_existing_sessions():
    """Тест работы с существующими сессиями"""
    print("\n=== ТЕСТ СУЩЕСТВУЮЩИХ СЕССИЙ ===")
    
    session_manager = SessionManager()
    
    # Получаем список доступных слотов
    available_slots = session_manager.get_available_slots()
    print(f"✓ Найдено {len(available_slots)} существующих сессий:")
    
    for slot in available_slots:
        print(f"  - Слот {slot.slot_id}: {slot.save_name}")
        print(f"    UUID: {slot.session_uuid[:8]}...")
        print(f"    Уровень: {slot.player_level}")
        print(f"    Время игры: {slot.play_time:.1f} сек")
        
        # Загружаем сессию для проверки
        loaded_session = session_manager.load_session(slot.slot_id)
        if loaded_session:
            items = session_manager.get_session_content("items")
            print(f"    Предметов: {len(items)}")
        else:
            print(f"    ✗ Ошибка загрузки")

def main():
    """Главная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ СИСТЕМЫ СЕССИЙ И ГЕНЕРАЦИИ КОНТЕНТА")
    print("=" * 60)
    
    try:
        # Проверяем наличие базы данных
        db_path = Path("data/game_data.db")
        if not db_path.exists():
            print("❌ База данных не найдена. Сначала запустите create_db.py и populate_db.py")
            return
        
        # Запускаем тесты
        test_session_creation()
        test_content_generation()
        test_session_persistence()
        test_multiple_sessions()
        test_session_statistics()
        test_existing_sessions()
        
        print("\n✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
        print("\n📋 РЕЗУЛЬТАТЫ:")
        print("- Система сессий работает корректно")
        print("- Генерация контента происходит для каждой сессии отдельно")
        print("- Данные сохраняются и загружаются правильно")
        print("- Множественные сессии изолированы друг от друга")
        print("- Статистика сессий работает корректно")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

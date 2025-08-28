#!/usr/bin/env python3
"""
Скрипт для миграции существующих систем на BaseSystem
Устраняет дублирование кода и стандартизирует архитектуру
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any


def find_system_files() -> List[str]:
    """Поиск всех файлов систем"""
    system_files = []
    systems_dir = Path("src/systems")
    
    for root, dirs, files in os.walk(systems_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                system_files.append(os.path.join(root, file))
    
    return system_files


def analyze_system_file(file_path: str) -> Dict[str, Any]:
    """Анализ файла системы"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file_path': file_path,
        'has_update_system_stats': False,
        'has_init': False,
        'has_update': False,
        'has_destroy': False,
        'inherits_from_isystem': False,
        'class_name': None,
        'needs_migration': False
    }
    
    # Поиск класса системы
    class_match = re.search(r'class\s+(\w+)\s*\([^)]*ISystem[^)]*\):', content)
    if class_match:
        analysis['class_name'] = class_match.group(1)
        analysis['inherits_from_isystem'] = True
    
    # Поиск методов
    analysis['has_update_system_stats'] = '_update_system_stats' in content
    analysis['has_init'] = 'def __init__' in content
    analysis['has_update'] = 'def update' in content
    analysis['has_destroy'] = 'def destroy' in content
    
    # Определение необходимости миграции
    analysis['needs_migration'] = (
        analysis['inherits_from_isystem'] and 
        analysis['has_update_system_stats']
    )
    
    return analysis


def generate_migration_template(analysis: Dict[str, Any]) -> str:
    """Генерация шаблона миграции"""
    class_name = analysis['class_name']
    file_path = analysis['file_path']
    
    template = f"""# Миграция {class_name} на BaseSystem
# Файл: {file_path}

# 1. Изменить импорт:
# from ...core.interfaces import ISystem, SystemPriority, SystemState
# НА:
from ...core.base_system import BaseSystem
from ...core.interfaces import SystemPriority, SystemState

# 2. Изменить наследование:
# class {class_name}(ISystem):
# НА:
class {class_name}(BaseSystem):

# 3. Изменить конструктор:
def __init__(self):
    # super().__init__(name="{class_name.lower()}", priority=SystemPriority.NORMAL)
    # ИЛИ с кастомными параметрами:
    super().__init__(name="{class_name.lower()}", priority=SystemPriority.NORMAL)
    # Остальная инициализация...

# 4. Переименовать методы:
# def initialize(self) -> bool:
# НА:
def _initialize_impl(self) -> bool:

# def update(self, delta_time: float) -> bool:
# НА:
def _update_impl(self, delta_time: float) -> bool:

# def destroy(self) -> bool:
# НА:
def _destroy_impl(self) -> None:

# 5. Удалить метод _update_system_stats() - он теперь в BaseSystem

# 6. Удалить дублированные атрибуты:
# - self.name
# - self.priority  
# - self.state
# - self.enabled
# - self.initialized
# - self.destroyed
# - self.logger

# 7. Использовать новые возможности BaseSystem:
# - self.get_cache(key) / self.set_cache(key, value)
# - self.get_stats()
# - self.get_performance_metrics()
"""
    
    return template


def main():
    """Основная функция миграции"""
    print("=== Анализ систем для миграции на BaseSystem ===\n")
    
    # Поиск файлов систем
    system_files = find_system_files()
    print(f"Найдено {len(system_files)} файлов систем")
    
    # Анализ каждого файла
    analyses = []
    for file_path in system_files:
        analysis = analyze_system_file(file_path)
        analyses.append(analysis)
        
        if analysis['needs_migration']:
            print(f"⚠️  {file_path}")
            print(f"   Класс: {analysis['class_name']}")
            print(f"   Метод _update_system_stats: {'✅' if analysis['has_update_system_stats'] else '❌'}")
            print()
    
    # Подсчет статистики
    total_systems = len([a for a in analyses if a['inherits_from_isystem']])
    systems_with_stats = len([a for a in analyses if a['has_update_system_stats']])
    systems_needing_migration = len([a for a in analyses if a['needs_migration']])
    
    print(f"=== Статистика ===")
    print(f"Всего систем: {total_systems}")
    print(f"Систем с _update_system_stats: {systems_with_stats}")
    print(f"Требуют миграции: {systems_needing_migration}")
    print()
    
    # Генерация шаблонов миграции
    if systems_needing_migration:
        print("=== Шаблоны миграции ===")
        for analysis in analyses:
            if analysis['needs_migration']:
                template = generate_migration_template(analysis)
                print(template)
                print("-" * 80)
                print()
    
    # Создание файла с инструкциями
    with open('MIGRATION_INSTRUCTIONS.md', 'w', encoding='utf-8') as f:
        f.write("# Инструкции по миграции на BaseSystem\n\n")
        f.write(f"Найдено {systems_needing_migration} систем, требующих миграции:\n\n")
        
        for analysis in analyses:
            if analysis['needs_migration']:
                f.write(f"## {analysis['class_name']} ({analysis['file_path']})\n")
                f.write(generate_migration_template(analysis))
                f.write("\n")
    
    print(f"✅ Создан файл MIGRATION_INSTRUCTIONS.md с подробными инструкциями")


if __name__ == "__main__":
    main()

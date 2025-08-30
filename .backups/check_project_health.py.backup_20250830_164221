#!/usr/bin/env python3
"""
Скрипт для проверки состояния проекта и выявления поврежденных файлов
"""

import os
import subprocess
import sys
from pathlib import Path

def check_file_syntax(file_path):
    """Проверяет синтаксис Python файла"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', str(file_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stderr
    except subprocess.TimeoutExpired:
        return False, "Timeout при проверке файла"
    except Exception as e:
        return False, str(e)

def scan_project():
    """Сканирует проект и проверяет все Python файлы"""
    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ Директория 'src' не найдена!")
        return
    
    python_files = list(src_dir.rglob("*.py"))
    print(f"🔍 Найдено Python файлов: {len(python_files)}")
    
    broken_files = []
    working_files = []
    
    for file_path in python_files:
        print(f"  Проверяю: {file_path.relative_to('.')}", end=" ")
        
        is_valid, error = check_file_syntax(file_path)
        
        if is_valid:
            print("✅")
            working_files.append(file_path)
        else:
            print("❌")
            broken_files.append(file_path)
            print(f"    Ошибка: {error.strip()}")
    
    print(f"\n📊 Результаты проверки:")
    print(f"  ✅ Рабочих файлов: {len(working_files)}")
    print(f"  ❌ Поврежденных файлов: {len(broken_files)}")
    
    if broken_files:
        print(f"\n🚨 Список поврежденных файлов:")
        for file_path in broken_files:
            print(f"  - {file_path.relative_to('.')}")
    
    return broken_files, working_files

if __name__ == "__main__":
    print("🔍 Проверка состояния проекта AI-EVOLVE...")
    print("=" * 50)
    
    broken, working = scan_project()
    
    if broken:
        print(f"\n⚠️  Проект требует восстановления!")
        print(f"   Рекомендуется запустить улучшенную утилиту fix_python_files.py")
    else:
        print(f"\n🎉 Проект в хорошем состоянии!")
    
    print("=" * 50)

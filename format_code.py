#!/usr/bin/env python3
"""
Скрипт для автоматического форматирования кода проекта.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"Выполняется: {description}")
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, encoding="utf-8"
        )
        if result.returncode == 0:
            print(f"✓ {description} - успешно")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"✗ {description} - ошибка")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ {description} - исключение: {e}")
        return False


def main():
    """Основная функция"""
    print("Начинается форматирование кода...")

    # Получаем корневую директорию проекта
    project_root = Path(__file__).parent

    # Форматируем код с помощью black
    success = run_command(
        f"python -m black {project_root}", "Форматирование кода с помощью black"
    )

    # Сортируем импорты с помощью isort
    success &= run_command(
        f"python -m isort {project_root}", "Сортировка импортов с помощью isort"
    )

    # Проверяем код с помощью flake8
    success &= run_command(
        f"python -m flake8 {project_root} --count --statistics",
        "Проверка стиля кода с помощью flake8",
    )

    if success:
        print("\n✓ Форматирование завершено успешно!")
    else:
        print("\n✗ Форматирование завершено с ошибками!")
        sys.exit(1)


if __name__ == "__main__":
    main()

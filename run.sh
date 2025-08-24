#!/bin/bash

echo "🎮 AI-EVOLVE Enhanced Edition"
echo "================================"
echo

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден!"
    echo "Установите Python 3.8+ с https://python.org"
    exit 1
fi

# Проверяем версию Python
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Требуется Python $required_version+, найдена версия $python_version"
    exit 1
fi

echo "✅ Python $python_version найден"

# Проверяем наличие зависимостей
echo "🔍 Проверка зависимостей..."
if ! python3 -c "import pygame, numpy, psutil" &> /dev/null; then
    echo "⚠️  Не все зависимости установлены"
    echo "Устанавливаем зависимости..."
    python3 install_dependencies.py
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка установки зависимостей"
        exit 1
    fi
fi

echo "✅ Все готово! Запускаем игру..."
echo

# Запускаем игру
python3 launcher.py

if [ $? -ne 0 ]; then
    echo
    echo "❌ Игра завершилась с ошибкой"
    read -p "Нажмите Enter для продолжения..."
fi

@echo off
chcp 65001 >nul
echo 🎮 AI-EVOLVE Enhanced Edition
echo ================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo Установите Python 3.8+ с https://python.org
    pause
    exit /b 1
)

REM Проверяем наличие зависимостей
echo 🔍 Проверка зависимостей...
python -c "import pygame, numpy, psutil" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Не все зависимости установлены
    echo Устанавливаем зависимости...
    python install_dependencies.py
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей
        pause
        exit /b 1
    )
)

echo ✅ Все готово! Запускаем игру...
echo.
python launcher.py

if errorlevel 1 (
    echo.
    echo ❌ Игра завершилась с ошибкой
    pause
)

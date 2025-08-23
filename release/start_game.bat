@echo off
title AI-EVOLVE: Эволюционная Адаптация
echo 🎮 Запуск игры AI-EVOLVE...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Ошибка запуска игры
    echo Попробуйте запустить install_dependencies.bat
    pause
)

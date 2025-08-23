#!/bin/bash
echo "🎮 Запуск игры AI-EVOLVE..."
python3 main.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Ошибка запуска игры"
    echo "Попробуйте запустить ./install_dependencies.sh"
    read -p "Нажмите Enter для выхода..."
fi

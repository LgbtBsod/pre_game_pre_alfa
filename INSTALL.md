# Установка AI-EVOLVE Enhanced Edition

## Требования

- **Python 3.8+** - основная среда выполнения
- **Pygame 2.5.0+** - игровой движок
- **Numpy 1.24.0+** - математические вычисления
- **psutil 5.9.0+** - системная информация

## Быстрая установка

### Windows
1. Убедитесь, что Python 3.8+ установлен
2. Дважды кликните на `run.bat`
3. Скрипт автоматически установит зависимости и запустит игру

### Linux/Mac
1. Убедитесь, что Python 3.8+ установлен
2. Сделайте скрипт исполняемым: `chmod +x run.sh`
3. Запустите: `./run.sh`

## Ручная установка

### 1. Установка Python
- Скачайте Python 3.8+ с [python.org](https://python.org)
- Убедитесь, что Python добавлен в PATH

### 2. Установка зависимостей
```bash
# Автоматическая установка
python install_dependencies.py

# Или вручную
pip install -r requirements.txt
```

### 3. Запуск игры
```bash
python launcher.py
```

## Структура проекта

```
NEW_BUILD/
├── src/                    # Исходный код
│   ├── core/              # Основные компоненты
│   ├── scenes/            # Игровые сцены
│   ├── systems/           # Игровые системы
│   ├── entities/          # Игровые сущности
│   └── ui/                # Пользовательский интерфейс
├── config/                 # Конфигурационные файлы
├── assets/                 # Игровые ресурсы
├── launcher.py             # Основной файл запуска
├── requirements.txt        # Зависимости
└── README.md              # Документация
```

## Решение проблем

### Ошибка "pygame module not found"
```bash
pip install pygame
```

### Ошибка "numpy module not found"
```bash
pip install numpy
```

### Ошибка "psutil module not found"
```bash
pip install psutil
```

### Проблемы с правами доступа (Linux/Mac)
```bash
sudo pip install -r requirements.txt
```

### Проблемы с версией Python
- Убедитесь, что используете Python 3.8+
- Проверьте версию: `python --version`

## Разработка

### Установка инструментов разработки
```bash
pip install -r requirements.txt
pip install pytest black flake8 mypy
```

### Запуск тестов
```bash
pytest tests/
```

### Форматирование кода
```bash
black src/
flake8 src/
```

## Поддержка

При возникновении проблем:
1. Проверьте версию Python
2. Убедитесь, что все зависимости установлены
3. Проверьте логи в папке `logs/`
4. Создайте issue в репозитории проекта

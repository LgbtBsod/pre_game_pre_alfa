#!/usr/bin/env python3
"""
Главный файл запуска игры "Эволюционная Адаптация: Генетический Резонанс"
Интегрирует все системы и предоставляет интерфейс для запуска игры.
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Добавление корневой директории в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

# Импорт основных систем
from core.game_loop import GameLoop, main_game_loop
from core.effect_system import EffectDatabase
from core.genetic_system import AdvancedGeneticSystem
from core.emotion_system import AdvancedEmotionSystem
from core.ai_system import AdaptiveAISystem
from core.content_generator import ContentGenerator
from core.evolution_system import EvolutionCycleSystem
from core.global_event_system import GlobalEventSystem
from core.dynamic_difficulty import DynamicDifficultySystem
from entities.advanced_entity import AdvancedGameEntity

# Настройка логирования
def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Настройка системы логирования"""
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    level = log_levels.get(log_level.upper(), logging.INFO)
    
    # Формат логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Добавление файлового хендлера если указан
    if log_file:
        log_file_path = Path(log_file)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        logging.getLogger().addHandler(file_handler)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено (уровень: {log_level})")
    
    if log_file:
        logger.info(f"Логи сохраняются в файл: {log_file}")


def create_directories():
    """Создание необходимых директорий"""
    directories = [
        "save",
        "logs",
        "data",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Директория создана/проверена: {directory}")


def test_systems():
    """Тестирование основных систем"""
    print("Тестирование основных систем...")
    
    try:
        # Тест системы эффектов
        print("  - Тестирование системы эффектов...")
        effect_db = EffectDatabase()
        print(f"    ✓ База данных эффектов: {len(effect_db.get_all_effects())} эффектов")
        
        # Тест генетической системы
        print("  - Тестирование генетической системы...")
        genetic_system = AdvancedGeneticSystem(effect_db)
        print(f"    ✓ Генетическая система: {len(genetic_system.unlocked_genes)} разблокированных генов")
        
        # Тест эмоциональной системы
        print("  - Тестирование эмоциональной системы...")
        emotion_system = AdvancedEmotionSystem(effect_db)
        print(f"    ✓ Эмоциональная система: {len(emotion_system.emotion_templates)} эмоций")
        
        # Тест ИИ системы
        print("  - Тестирование ИИ системы...")
        ai_system = AdaptiveAISystem("TEST_ENTITY", effect_db)
        print(f"    ✓ ИИ система: Q-агент инициализирован")
        
        # Тест генератора контента
        print("  - Тестирование генератора контента...")
        content_gen = ContentGenerator()
        print(f"    ✓ Генератор контента: seed установлен")
        
        # Тест системы эволюции
        print("  - Тестирование системы эволюции...")
        evolution_system = EvolutionCycleSystem(effect_db)
        print(f"    ✓ Система эволюции: цикл {evolution_system.current_cycle}")
        
        # Тест системы глобальных событий
        print("  - Тестирование системы глобальных событий...")
        event_system = GlobalEventSystem(effect_db)
        print(f"    ✓ Система событий: {len(event_system.event_triggers)} триггеров")
        
        # Тест системы динамической сложности
        print("  - Тестирование системы динамической сложности...")
        difficulty_system = DynamicDifficultySystem()
        print(f"    ✓ Система сложности: профиль '{difficulty_system.get_current_difficulty_level()}'")
        
        print("✓ Все системы успешно протестированы!")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка тестирования систем: {e}")
        logging.error(f"Ошибка тестирования систем: {e}")
        return False


def run_demo_mode():
    """Запуск демо-режима"""
    print("Запуск демо-режима...")
    
    try:
        # Создание игрового цикла
        game_loop = GameLoop()
        
        # Запуск демо-игры на 30 секунд
        if game_loop.start_new_game():
            print("Демо-игра запущена. Нажмите Ctrl+C для остановки...")
            
            # Демо-цикл
            import time
            start_time = time.time()
            demo_duration = 30  # 30 секунд
            
            while time.time() - start_time < demo_duration:
                try:
                    # Обновление игры
                    game_loop._update_game(0.016)  # ~60 FPS
                    
                    # Получение статистики
                    stats = game_loop.get_game_stats()
                    
                    # Вывод прогресса
                    elapsed = time.time() - start_time
                    progress = elapsed / demo_duration
                    print(f"\rДемо-режим: {progress:.1%} ({elapsed:.1f}s/{demo_duration}s)", end="", flush=True)
                    
                    time.sleep(0.016)
                    
                except KeyboardInterrupt:
                    print("\nДемо-режим прерван пользователем")
                    break
            
            print(f"\nДемо-режим завершён за {time.time() - start_time:.1f} секунд")
            
            # Вывод финальной статистики
            final_stats = game_loop.get_game_stats()
            print("\nФинальная статистика:")
            print(f"  - Время игры: {final_stats.get('game_time', 0):.1f}s")
            print(f"  - Кадры отрендерены: {final_stats.get('frames_rendered', 0)}")
            print(f"  - Сущности в мире: {final_stats.get('total_entities', 0)}")
            print(f"  - Прогресс исследования: {final_stats.get('explored_percent', 0):.1%}")
            
        else:
            print("✗ Не удалось запустить демо-игру")
            
    except Exception as e:
        print(f"✗ Ошибка демо-режима: {e}")
        logging.error(f"Ошибка демо-режима: {e}")


def run_full_game():
    """Запуск полной игры"""
    print("Запуск полной игры...")
    
    try:
        # Запуск основного игрового цикла
        main_game_loop()
        
    except Exception as e:
        print(f"✗ Ошибка запуска игры: {e}")
        logging.error(f"Ошибка запуска игры: {e}")


def show_system_info():
    """Показать информацию о системах"""
    print("\n=== ИНФОРМАЦИЯ О СИСТЕМАХ ===")
    
    try:
        # Система эффектов
        effect_db = EffectDatabase()
        effects = effect_db.get_all_effects()
        effect_types = {}
        for effect in effects:
            effect_type = effect.effect_type
            effect_types[effect_type] = effect_types.get(effect_type, 0) + 1
        
        print(f"Система эффектов:")
        print(f"  - Всего эффектов: {len(effects)}")
        for effect_type, count in effect_types.items():
            print(f"  - {effect_type}: {count}")
        
        # Генетическая система
        genetic_system = AdvancedGeneticSystem(effect_db)
        print(f"\nГенетическая система:")
        print(f"  - Разблокированных генов: {len(genetic_system.unlocked_genes)}")
        print(f"  - Активных генов: {len(genetic_system.active_genes)}")
        print(f"  - Слотов для генов: {genetic_system.gene_slots}")
        print(f"  - Сопротивление мутациям: {genetic_system.mutation_resistance:.2f}")
        
        # Эмоциональная система
        emotion_system = AdvancedEmotionSystem(effect_db)
        print(f"\nЭмоциональная система:")
        print(f"  - Шаблонов эмоций: {len(emotion_system.emotion_templates)}")
        print(f"  - Комбинаций эмоций: {len(emotion_system.emotion_combos)}")
        
        # ИИ система
        ai_system = AdaptiveAISystem("INFO_ENTITY", effect_db)
        print(f"\nИИ система:")
        print(f"  - Размер Q-таблицы: {len(ai_system.q_agent.q_table)}")
        print(f"  - Скорость обучения: {ai_system.q_agent.adaptive_learning_rate:.3f}")
        
        # Система эволюции
        evolution_system = EvolutionCycleSystem(effect_db)
        print(f"\nСистема эволюции:")
        print(f"  - Текущий цикл: {evolution_system.current_cycle}")
        print(f"  - Всего циклов: {evolution_system.total_cycles}")
        print(f"  - История эволюции: {len(evolution_system.evolution_history)} записей")
        
        # Система событий
        event_system = GlobalEventSystem(effect_db)
        print(f"\nСистема глобальных событий:")
        print(f"  - Триггеров событий: {len(event_system.event_triggers)}")
        print(f"  - Активных событий: {len(event_system.active_events)}")
        print(f"  - История событий: {len(event_system.event_history)}")
        
        # Система сложности
        difficulty_system = DynamicDifficultySystem()
        print(f"\nСистема динамической сложности:")
        print(f"  - Текущий профиль: {difficulty_system.get_current_difficulty_level()}")
        print(f"  - Всего адаптаций: {difficulty_system.total_adaptations}")
        print(f"  - Изменений сложности: {difficulty_system.difficulty_changes}")
        
    except Exception as e:
        print(f"✗ Ошибка получения информации о системах: {e}")
        logging.error(f"Ошибка получения информации о системах: {e}")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Эволюционная Адаптация: Генетический Резонанс",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main_game.py                    # Запуск полной игры
  python main_game.py --demo            # Запуск демо-режима
  python main_game.py --test            # Тестирование систем
  python main_game.py --info            # Информация о системах
  python main_game.py --log-level DEBUG # Подробное логирование
        """
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Запуск демо-режима (30 секунд)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Тестирование всех систем"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Показать информацию о системах"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Уровень логирования (по умолчанию: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Файл для сохранения логов"
    )
    
    parser.add_argument(
        "--create-dirs",
        action="store_true",
        help="Создать необходимые директории"
    )
    
    args = parser.parse_args()
    
    # Настройка логирования
    setup_logging(args.log_level, args.log_file)
    
    # Создание директорий
    if args.create_dirs:
        create_directories()
    
    # Вывод заголовка
    print("=" * 60)
    print("  ЭВОЛЮЦИОННАЯ АДАПТАЦИЯ: ГЕНЕТИЧЕСКИЙ РЕЗОНАНС")
    print("=" * 60)
    print("  Версия: 1.0.0")
    print("  Автор: AI Assistant")
    print("  Описание: Инновационная игра с эволюционными циклами")
    print("=" * 60)
    
    try:
        # Обработка аргументов
        if args.test:
            # Тестирование систем
            if test_systems():
                print("\n✓ Все системы работают корректно!")
            else:
                print("\n✗ Обнаружены проблемы в системах!")
                sys.exit(1)
                
        elif args.info:
            # Показать информацию о системах
            show_system_info()
            
        elif args.demo:
            # Запуск демо-режима
            run_demo_mode()
            
        else:
            # Запуск полной игры
            print("\nЗапуск игры...")
            print("Нажмите Ctrl+C для выхода")
            print("-" * 60)
            
            run_full_game()
            
    except KeyboardInterrupt:
        print("\n\nИгра прервана пользователем")
        logging.info("Игра прервана пользователем")
        
    except Exception as e:
        print(f"\n\n✗ Критическая ошибка: {e}")
        logging.critical(f"Критическая ошибка: {e}")
        sys.exit(1)
        
    finally:
        print("\nСпасибо за игру!")
        print("=" * 60)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Тест интеграции оптимизированных систем
Проверяет работу всех основных компонентов после оптимизации
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any
import logging

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTester:
    """Тестер интеграции систем"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    def run_all_tests(self) -> bool:
        """Запуск всех тестов"""
        logger.info("=== НАЧАЛО ТЕСТИРОВАНИЯ ИНТЕГРАЦИИ ===")
        
        tests = [
            ("База данных", self.test_database),
            ("Менеджер ресурсов", self.test_resource_manager),
            ("Система событий", self.test_event_system),
            ("Пространственная система", self.test_spatial_system),
            ("Валидатор конфигурации", self.test_config_validator),
            ("UI компоненты", self.test_ui_components),
            ("Игровые системы", self.test_game_systems),
            ("Производительность", self.test_performance)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Тест: {test_name} ---")
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result:
                    logger.info(f"✓ {test_name}: ПРОЙДЕН")
                else:
                    logger.error(f"✗ {test_name}: ПРОВАЛЕН")
                    all_passed = False
            except Exception as e:
                logger.error(f"✗ {test_name}: ОШИБКА - {e}")
                self.test_results[test_name] = False
                all_passed = False
        
        self.print_summary()
        return all_passed
    
    def test_database(self):
        """Тест системы базы данных"""
        try:
            from core.database_initializer import DatabaseInitializer
            
            # Создаем инициализатор БД
            db_init = DatabaseInitializer()
            
            # Инициализируем БД
            success = db_init.initialize_database()
            assert success, "Ошибка инициализации БД"
            
            # Тестируем создание сессии
            session = db_init.create_session("test_session")
            assert session is not None, "Ошибка создания сессии"
            
            # Тестируем сохранение данных
            test_data = {"test": "data"}
            success = db_init.save_session_data("test_session", test_data)
            assert success, "Ошибка сохранения данных сессии"
            
            # Тестируем загрузку данных
            loaded_data = db_init.load_session_data("test_session")
            assert loaded_data == test_data, "Ошибка загрузки данных сессии"
            
            logger.info("База данных: все операции выполнены успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка теста базы данных: {e}")
            return False
    
    def test_resource_manager(self) -> bool:
        """Тест менеджера ресурсов"""
        try:
            from core.resource_manager import resource_manager
            
            # Тест загрузки ресурса
            test_resource = resource_manager.get_resource("test_image", "image")
            if test_resource is None:
                logger.info("Тестовый ресурс не найден (ожидаемо)")
            
            # Тест кэширования
            cache_size_before = len(resource_manager._image_cache)
            resource_manager.get_resource("test_image", "image")
            cache_size_after = len(resource_manager._image_cache)
            
            # Тест статистики
            stats = resource_manager.get_statistics()
            if not isinstance(stats, dict):
                return False
            
            # Тест очистки кэша
            resource_manager.clear_cache()
            if len(resource_manager._image_cache) != 0:
                return False
            
            logger.info("Менеджер ресурсов: все операции выполнены успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка теста менеджера ресурсов: {e}")
            return False
    
    def test_event_system(self):
        """Тест системы событий"""
        try:
            from core.event_system import event_system, GameEvents, EventPriority
            
            # Тест отправки события
            success = event_system.emit_simple(GameEvents.TEST_EVENT, {"test": "data"})
            assert success, "Ошибка отправки события"
            
            # Тест обработки событий
            event_system.process_events()
            
            # Тест получения события из очереди
            event = event_system._event_queue.get_nowait()
            if event is not None:
                assert hasattr(event, 'event_type'), "Событие не имеет атрибута event_type"
                assert event.event_type == GameEvents.TEST_EVENT, "Неверный тип события"
            
            # Тест статистики
            stats = event_system.get_stats()
            assert isinstance(stats, dict), "Статистика должна быть словарем"
            
            logger.info("Система событий: все операции выполнены успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка теста системы событий: {e}")
            return False
    
    def test_spatial_system(self) -> bool:
        """Тест пространственной системы"""
        try:
            from core.spatial_system import SpatialSystem, BoundingBox, SpatialObjectType
            
            # Создание системы
            spatial_system = SpatialSystem()
            
            # Тест добавления объектов
            test_objects = [
                {"id": "obj1", "x": 100, "y": 100, "width": 50, "height": 50, "type": SpatialObjectType.ENTITY},
                {"id": "obj2", "x": 200, "y": 200, "width": 30, "height": 30, "type": SpatialObjectType.ITEM},
                {"id": "obj3", "x": 150, "y": 150, "width": 20, "height": 20, "type": SpatialObjectType.PROJECTILE}
            ]
            
            for obj in test_objects:
                bbox = BoundingBox(obj["x"], obj["y"], obj["width"], obj["height"])
                spatial_system.add_object(obj["id"], bbox, obj["type"])
            
            # Тест поиска объектов
            search_bbox = BoundingBox(120, 120, 100, 100)
            found_objects = spatial_system.query_area(search_bbox)
            
            if len(found_objects) < 2:  # Должны найти как минимум 2 объекта
                return False
            
            # Тест удаления объекта
            spatial_system.remove_object("obj1")
            remaining_objects = spatial_system.query_area(search_bbox)
            
            if len(remaining_objects) >= len(found_objects):
                return False
            
            # Тест производительности
            start_time = time.time()
            for i in range(1000):
                spatial_system.query_area(search_bbox)
            end_time = time.time()
            
            query_time = end_time - start_time
            if query_time > 1.0:  # Не более 1 секунды на 1000 запросов
                return False
            
            logger.info(f"Пространственная система: все операции выполнены успешно (время запросов: {query_time:.3f}s)")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка теста пространственной системы: {e}")
            return False
    
    def test_config_validator(self) -> bool:
        """Тест валидатора конфигурации"""
        try:
            from config.config_validator import config_validator
            
            # Тест валидации корректной конфигурации
            valid_config = {
                "game": {
                    "display": {
                        "window_width": 1280,
                        "window_height": 720,
                        "fullscreen": False
                    }
                }
            }
            
            result = config_validator.validate_config(valid_config)
            if not result.is_valid:
                return False
            
            # Тест валидации некорректной конфигурации
            invalid_config = {
                "game": {
                    "display": {
                        "window_width": -1,  # Некорректное значение
                        "window_height": 720
                    }
                }
            }
            
            result = config_validator.validate_config(invalid_config)
            if result.is_valid:  # Должна быть невалидной
                return False
            
            # Тест автокоррекции
            corrected_config = config_validator.auto_correct_config(invalid_config)
            if not corrected_config:
                return False
            
            # Проверяем, что исправлено
            if corrected_config["game"]["display"]["window_width"] <= 0:
                return False
            
            logger.info("Валидатор конфигурации: все операции выполнены успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка теста валидатора конфигурации: {e}")
            return False
    
    def test_ui_components(self) -> bool:
        """Тест UI компонентов"""
        try:
            import pygame
            
            # Инициализация pygame для тестов
            pygame.init()
            test_screen = pygame.Surface((800, 600))
            
            # Тест кнопок
            from ui.buttons import Button, ButtonGroup, ToggleButton
            
            # Создание кнопки
            button = Button(100, 100, 200, 50, "Test Button")
            button.render(test_screen)
            
            # Создание группы кнопок
            button_group = ButtonGroup()
            button_group.add_button(button)
            
            # Создание переключателя
            toggle = ToggleButton(100, 200, 200, 50, "Toggle")
            toggle.render(test_screen)
            
            # Тест HUD компонентов
            from ui.hud import StatusHUD, InventoryHUD, GeneticsHUD, AILearningHUD, DebugHUD
            
            # Создание HUD компонентов
            test_fonts = {
                "main": pygame.font.Font(None, 24),
                "small": pygame.font.Font(None, 18)
            }
            
            test_colors = type('Colors', (), {
                'DARK_GRAY': (50, 50, 50),
                'WHITE': (255, 255, 255),
                'HEALTH_COLOR': (255, 0, 0),
                'ENERGY_COLOR': (0, 255, 0),
                'STAMINA_COLOR': (0, 0, 255),
                'GENETIC_COLOR': (255, 0, 255),
                'LIGHT_GRAY': (200, 200, 200)
            })()
            
            test_rect = pygame.Rect(10, 10, 200, 150)
            
            status_hud = StatusHUD(test_screen, test_fonts, test_rect, test_colors)
            inventory_hud = InventoryHUD(test_screen, test_fonts, test_rect, test_colors)
            genetics_hud = GeneticsHUD(test_screen, test_fonts, test_rect, test_colors)
            ai_hud = AILearningHUD(test_screen, test_fonts, test_rect, test_colors)
            debug_hud = DebugHUD(test_screen)
            
            # Тест рендеринга
            status_hud.render(None)
            inventory_hud.render(None, None)
            genetics_hud.render(None)
            ai_hud.render(None)
            debug_hud.render_debug({"fps": 60}, False)
            
            pygame.quit()
            
            logger.info("UI компоненты: все операции выполнены успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка теста UI компонентов: {e}")
            return False
    
    def test_game_systems(self):
        """Тест игровых систем"""
        try:
            from core.game_systems import GameSystems
            
            # Создаем игровые системы
            game_systems = GameSystems()
            
            # Инициализируем системы
            success = game_systems.initialize()
            assert success, "Ошибка инициализации игровых систем"
            
            # Тест обновления
            game_systems.update(0.016)  # 60 FPS
            
            # Тест рендеринга
            game_systems.render()
            
            # Тест статистики
            stats = game_systems.get_statistics()
            assert isinstance(stats, dict), "Статистика должна быть словарем"
            assert 'game_time' in stats, "Статистика должна содержать game_time"
            assert 'fps' in stats, "Статистика должна содержать fps"
            
            # Тест очистки
            game_systems.cleanup()
            
            logger.info("Игровые системы: все операции выполнены успешно")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка теста игровых систем: {e}")
            return False
    
    def test_performance(self) -> bool:
        """Тест производительности"""
        try:
            from core.spatial_system import SpatialSystem, BoundingBox, SpatialObjectType
            from core.event_system import event_system, GameEvents
            
            # Тест производительности пространственной системы
            spatial_system = SpatialSystem()
            
            # Добавляем много объектов
            start_time = time.time()
            for i in range(1000):
                bbox = BoundingBox(i * 10, i * 10, 50, 50)
                spatial_system.add_object(f"obj_{i}", bbox, SpatialObjectType.ENTITY)
            add_time = time.time() - start_time
            
            # Тест поиска
            search_bbox = BoundingBox(0, 0, 500, 500)
            start_time = time.time()
            for i in range(100):
                spatial_system.query_area(search_bbox)
            query_time = time.time() - start_time
            
            # Тест производительности событий
            event_count = 1000
            start_time = time.time()
            for i in range(event_count):
                event_system.emit_event(GameEvents.TEST_EVENT, {"id": i})
            emit_time = time.time() - start_time
            
            start_time = time.time()
            event_system.process_events()
            process_time = time.time() - start_time
            
            # Проверяем производительность
            performance_ok = (
                add_time < 1.0 and      # Добавление 1000 объектов менее 1 секунды
                query_time < 0.1 and    # 100 запросов менее 0.1 секунды
                emit_time < 0.1 and     # 1000 событий менее 0.1 секунды
                process_time < 0.1      # Обработка 1000 событий менее 0.1 секунды
            )
            
            logger.info(f"Производительность:")
            logger.info(f"  Добавление объектов: {add_time:.3f}s")
            logger.info(f"  Поиск объектов: {query_time:.3f}s")
            logger.info(f"  Отправка событий: {emit_time:.3f}s")
            logger.info(f"  Обработка событий: {process_time:.3f}s")
            
            return performance_ok
            
        except Exception as e:
            logger.error(f"Ошибка теста производительности: {e}")
            return False
    
    def print_summary(self):
        """Вывод итогов тестирования"""
        end_time = time.time()
        total_time = end_time - self.start_time
        
        logger.info("\n=== ИТОГИ ТЕСТИРОВАНИЯ ===")
        logger.info(f"Общее время: {total_time:.2f} секунд")
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        logger.info(f"Пройдено тестов: {passed}/{total}")
        
        for test_name, result in self.test_results.items():
            status = "✓ ПРОЙДЕН" if result else "✗ ПРОВАЛЕН"
            logger.info(f"  {test_name}: {status}")
        
        if passed == total:
            logger.info("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            logger.error(f"\n❌ ПРОВАЛЕНО ТЕСТОВ: {total - passed}")
        
        logger.info("================================")


def main():
    """Главная функция"""
    tester = IntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Интеграционное тестирование завершено успешно!")
        return 0
    else:
        print("\n❌ Интеграционное тестирование завершено с ошибками!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

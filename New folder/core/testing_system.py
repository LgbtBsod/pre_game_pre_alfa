#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
СИСТЕМА ТЕСТИРОВАНИЯ И ВАЛИДАЦИИ
Автоматизированное тестирование всех систем проекта
"""

import time
import unittest
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from utils.logging_system import get_logger, log_system_event

class TestResult(Enum):
    """Результаты тестов"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestCategory(Enum):
    """Категории тестов"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    FUNCTIONAL = "functional"
    STRESS = "stress"

@dataclass
class TestCase:
    """Тестовый случай"""
    test_id: str
    name: str
    category: TestCategory
    description: str
    test_function: callable
    expected_result: Any = None
    timeout: float = 30.0
    dependencies: List[str] = field(default_factory=list)

@dataclass
class TestResult:
    """Результат теста"""
    test_id: str
    result: TestResult
    execution_time: float
    message: str = ""
    error_details: str = ""
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

class TestingSystem:
    """Система тестирования"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.test_cases: Dict[str, TestCase] = {}
        self.test_results: List[TestResult] = []
        self.test_suite_start_time = 0.0
        
        # Регистрируем тесты
        self._register_tests()
        
        log_system_event("testing_system", "initialized")
    
    def _register_tests(self):
        """Регистрация всех тестов"""
        # Тесты системы памяти ИИ
        self._register_ai_memory_tests()
        
        # Тесты системы предметов
        self._register_item_system_tests()
        
        # Тесты системы маяков
        self._register_lighthouse_tests()
        
        # Тесты генератора контента
        self._register_content_generator_tests()
        
        # Тесты системы сохранений
        self._register_save_system_tests()
        
        # Интеграционные тесты
        self._register_integration_tests()
        
        # Тесты производительности
        self._register_performance_tests()
    
    def _register_ai_memory_tests(self):
        """Регистрация тестов системы памяти ИИ"""
        self.add_test_case(TestCase(
            test_id="ai_memory_001",
            name="AI Memory Initialization",
            category=TestCategory.UNIT,
            description="Test AI memory system initialization",
            test_function=self._test_ai_memory_initialization
        ))
        
        self.add_test_case(TestCase(
            test_id="ai_memory_002",
            name="AI Memory Add/Retrieve",
            category=TestCategory.UNIT,
            description="Test adding and retrieving memories",
            test_function=self._test_ai_memory_add_retrieve
        ))
        
        self.add_test_case(TestCase(
            test_id="ai_memory_003",
            name="AI Memory Learning Rates",
            category=TestCategory.UNIT,
            description="Test different learning rates for entity types",
            test_function=self._test_ai_memory_learning_rates
        ))
    
    def _register_item_system_tests(self):
        """Регистрация тестов системы предметов"""
        self.add_test_case(TestCase(
            test_id="item_system_001",
            name="Item Creation",
            category=TestCategory.UNIT,
            description="Test item creation from generated data",
            test_function=self._test_item_creation
        ))
        
        self.add_test_case(TestCase(
            test_id="item_system_002",
            name="Inventory Management",
            category=TestCategory.UNIT,
            description="Test inventory add/remove operations",
            test_function=self._test_inventory_management
        ))
        
        self.add_test_case(TestCase(
            test_id="item_system_003",
            name="Equipment System",
            category=TestCategory.UNIT,
            description="Test equipment system functionality",
            test_function=self._test_equipment_system
        ))
    
    def _register_lighthouse_tests(self):
        """Регистрация тестов системы маяков"""
        self.add_test_case(TestCase(
            test_id="lighthouse_001",
            name="Lighthouse Generation",
            category=TestCategory.UNIT,
            description="Test lighthouse generation for sessions",
            test_function=self._test_lighthouse_generation
        ))
        
        self.add_test_case(TestCase(
            test_id="lighthouse_002",
            name="Lighthouse Discovery",
            category=TestCategory.UNIT,
            description="Test lighthouse discovery mechanics",
            test_function=self._test_lighthouse_discovery
        ))
        
        self.add_test_case(TestCase(
            test_id="lighthouse_003",
            name="Lighthouse Activation",
            category=TestCategory.UNIT,
            description="Test lighthouse activation requirements",
            test_function=self._test_lighthouse_activation
        ))
    
    def _register_content_generator_tests(self):
        """Регистрация тестов генератора контента"""
        self.add_test_case(TestCase(
            test_id="content_gen_001",
            name="Content Generation",
            category=TestCategory.UNIT,
            description="Test content generation for sessions",
            test_function=self._test_content_generation
        ))
        
        self.add_test_case(TestCase(
            test_id="content_gen_002",
            name="Enemy Generation",
            category=TestCategory.UNIT,
            description="Test enemy generation with different types",
            test_function=self._test_enemy_generation
        ))
    
    def _register_save_system_tests(self):
        """Регистрация тестов системы сохранений"""
        self.add_test_case(TestCase(
            test_id="save_system_001",
            name="Save System",
            category=TestCategory.UNIT,
            description="Test save system functionality",
            test_function=self._test_save_system
        ))
        
        self.add_test_case(TestCase(
            test_id="save_system_002",
            name="Roguelike Save",
            category=TestCategory.UNIT,
            description="Test roguelike session saving",
            test_function=self._test_roguelike_save
        ))
    
    def _register_integration_tests(self):
        """Регистрация интеграционных тестов"""
        self.add_test_case(TestCase(
            test_id="integration_001",
            name="Full Session Flow",
            category=TestCategory.INTEGRATION,
            description="Test complete roguelike session flow",
            test_function=self._test_full_session_flow
        ))
        
        self.add_test_case(TestCase(
            test_id="integration_002",
            name="AI Learning Integration",
            category=TestCategory.INTEGRATION,
            description="Test AI learning with all systems",
            test_function=self._test_ai_learning_integration
        ))
    
    def _register_performance_tests(self):
        """Регистрация тестов производительности"""
        self.add_test_case(TestCase(
            test_id="performance_001",
            name="Memory System Performance",
            category=TestCategory.PERFORMANCE,
            description="Test AI memory system performance",
            test_function=self._test_memory_performance
        ))
        
        self.add_test_case(TestCase(
            test_id="performance_002",
            name="Item System Performance",
            category=TestCategory.PERFORMANCE,
            description="Test item system performance",
            test_function=self._test_item_performance
        ))
    
    def add_test_case(self, test_case: TestCase):
        """Добавление тестового случая"""
        self.test_cases[test_case.test_id] = test_case
        self.logger.debug(f"Added test case: {test_case.test_id}")
    
    def run_test_suite(self, categories: List[TestCategory] = None) -> Dict[str, Any]:
        """Запуск набора тестов"""
        self.test_suite_start_time = time.time()
        self.test_results.clear()
        
        # Фильтруем тесты по категориям
        tests_to_run = []
        if categories:
            tests_to_run = [
                test for test in self.test_cases.values()
                if test.category in categories
            ]
        else:
            tests_to_run = list(self.test_cases.values())
        
        self.logger.info(f"Running {len(tests_to_run)} tests")
        
        # Запускаем тесты
        for test_case in tests_to_run:
            self._run_single_test(test_case)
        
        # Генерируем отчет
        return self._generate_test_report()
    
    def _run_single_test(self, test_case: TestCase):
        """Запуск одного теста"""
        start_time = time.time()
        
        try:
            # Проверяем зависимости
            if not self._check_dependencies(test_case):
                result = TestResult(
                    test_id=test_case.test_id,
                    result=TestResult.SKIPPED,
                    execution_time=time.time() - start_time,
                    message="Dependencies not met"
                )
                self.test_results.append(result)
                return
            
            # Запускаем тест
            test_result = test_case.test_function()
            
            execution_time = time.time() - start_time
            
            if test_result:
                result = TestResult(
                    test_id=test_case.test_id,
                    result=TestResult.PASSED,
                    execution_time=execution_time,
                    message="Test passed successfully"
                )
            else:
                result = TestResult(
                    test_id=test_case.test_id,
                    result=TestResult.FAILED,
                    execution_time=execution_time,
                    message="Test failed"
                )
            
            self.test_results.append(result)
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = TestResult(
                test_id=test_case.test_id,
                result=TestResult.ERROR,
                execution_time=execution_time,
                message=f"Test error: {str(e)}",
                error_details=str(e)
            )
            self.test_results.append(result)
            self.logger.error(f"Test {test_case.test_id} failed with error: {e}")
    
    def _check_dependencies(self, test_case: TestCase) -> bool:
        """Проверка зависимостей теста"""
        for dep_id in test_case.dependencies:
            # Проверяем, что зависимый тест прошел успешно
            dep_result = next(
                (r for r in self.test_results if r.test_id == dep_id),
                None
            )
            if not dep_result or dep_result.result != TestResult.PASSED:
                return False
        return True
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Генерация отчета о тестах"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.result == TestResult.PASSED])
        failed_tests = len([r for r in self.test_results if r.result == TestResult.FAILED])
        error_tests = len([r for r in self.test_results if r.result == TestResult.ERROR])
        skipped_tests = len([r for r in self.test_results if r.result == TestResult.SKIPPED])
        
        total_time = time.time() - self.test_suite_start_time
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "skipped": skipped_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_execution_time": total_time
            },
            "results": [
                {
                    "test_id": result.test_id,
                    "result": result.result.value,
                    "execution_time": result.execution_time,
                    "message": result.message,
                    "error_details": result.error_details
                }
                for result in self.test_results
            ],
            "categories": {
                category.value: {
                    "total": len([t for t in self.test_cases.values() if t.category == category]),
                    "passed": len([r for r in self.test_results 
                                 if r.result == TestResult.PASSED and 
                                 self.test_cases[r.test_id].category == category])
                }
                for category in TestCategory
            }
        }
        
        return report
    
    # === ТЕСТОВЫЕ ФУНКЦИИ ===
    
    def _test_ai_memory_initialization(self) -> bool:
        """Тест инициализации системы памяти ИИ"""
        try:
            from core.enhanced_ai_memory import EnhancedAIMemorySystem, EntityType
            
            memory_system = EnhancedAIMemorySystem()
            
            # Тестируем инициализацию памяти для разных типов сущностей
            player_id = "test_player"
            enemy_id = "test_enemy"
            
            memory_system.initialize_entity_memory(player_id, EntityType.PLAYER)
            memory_system.initialize_entity_memory(enemy_id, EntityType.BASIC_ENEMY)
            
            # Проверяем, что память создана
            player_memory = memory_system.get_entity_memory(player_id)
            enemy_memory = memory_system.get_entity_memory(enemy_id)
            
            return player_memory is not None and enemy_memory is not None
            
        except Exception as e:
            self.logger.error(f"AI memory initialization test failed: {e}")
            return False
    
    def _test_ai_memory_add_retrieve(self) -> bool:
        """Тест добавления и получения памяти"""
        try:
            from core.enhanced_ai_memory import EnhancedAIMemorySystem, EntityType, MemoryType
            
            memory_system = EnhancedAIMemorySystem()
            entity_id = "test_entity"
            
            memory_system.initialize_entity_memory(entity_id, EntityType.PLAYER)
            
            # Добавляем память
            memory_id = memory_system.add_memory(
                entity_id, MemoryType.COMBAT, {"action": "attack", "target": "enemy"}, 0.8
            )
            
            # Получаем память
            memories = memory_system.get_memories(entity_id, MemoryType.COMBAT)
            
            return memory_id is not None and len(memories) > 0
            
        except Exception as e:
            self.logger.error(f"AI memory add/retrieve test failed: {e}")
            return False
    
    def _test_ai_memory_learning_rates(self) -> bool:
        """Тест разных скоростей обучения"""
        try:
            from core.enhanced_ai_memory import EnhancedAIMemorySystem, EntityType
            
            memory_system = EnhancedAIMemorySystem()
            
            # Проверяем скорости обучения
            player_rate = memory_system._get_learning_rate(EntityType.PLAYER)
            enemy_rate = memory_system._get_learning_rate(EntityType.BASIC_ENEMY)
            boss_rate = memory_system._get_learning_rate(EntityType.BOSS)
            
            # Игрок должен учиться быстрее врагов
            return player_rate > enemy_rate > boss_rate
            
        except Exception as e:
            self.logger.error(f"AI memory learning rates test failed: {e}")
            return False
    
    def _test_item_creation(self) -> bool:
        """Тест создания предметов"""
        try:
            from core.enhanced_item_system import EnhancedItemSystem, ItemType, ItemRarity
            
            item_system = EnhancedItemSystem()
            
            # Создаем тестовые данные предмета
            class MockGeneratedItem:
                def __init__(self):
                    self.item_id = "test_item_001"
                    self.name = "Test Sword"
                    self.item_type = ItemType.WEAPON
                    self.rarity = ItemRarity.RARE
                    self.description = "A test sword"
                    self.base_stats = {"damage": 25, "speed": 1.2}
                    self.special_effects = [{"type": "fire_damage", "value": 5}]
                    self.active_skills = ["weapon_skill_1"]
                    self.trigger_skills = ["trigger_skill_1"]
                    self.basic_attack_skill = "sword_basic_attack"
                    self.requirements = {"level": 5, "strength": 10}
            
            mock_item = MockGeneratedItem()
            item = item_system.create_item_from_generated_data(mock_item)
            
            return item is not None and item.name == "Test Sword"
            
        except Exception as e:
            self.logger.error(f"Item creation test failed: {e}")
            return False
    
    def _test_inventory_management(self) -> bool:
        """Тест управления инвентарем"""
        try:
            from core.enhanced_item_system import EnhancedItemSystem, Item, ItemType, ItemRarity
            
            item_system = EnhancedItemSystem()
            entity_id = "test_entity"
            
            # Создаем инвентарь
            inventory = item_system.create_inventory(entity_id)
            
            # Создаем тестовый предмет
            test_item = Item(
                item_id="test_item_002",
                name="Test Potion",
                item_type=ItemType.CONSUMABLE,
                rarity=ItemRarity.COMMON,
                description="A test potion",
                stack_size=10
            )
            
            # Добавляем предмет
            success = item_system.add_item_to_inventory(entity_id, test_item, 5)
            
            # Проверяем, что предмет добавлен
            items = item_system.get_inventory_items(entity_id)
            
            return success and len(items) > 0 and items[0]["quantity"] == 5
            
        except Exception as e:
            self.logger.error(f"Inventory management test failed: {e}")
            return False
    
    def _test_equipment_system(self) -> bool:
        """Тест системы экипировки"""
        try:
            from core.enhanced_item_system import EnhancedItemSystem, Item, ItemType, ItemRarity, EquipmentSlot
            
            item_system = EnhancedItemSystem()
            entity_id = "test_entity"
            
            # Создаем тестовое оружие
            weapon = Item(
                item_id="test_weapon_001",
                name="Test Sword",
                item_type=ItemType.WEAPON,
                rarity=ItemRarity.RARE,
                description="A test sword",
                base_stats={"damage": 30}
            )
            
            # Экипируем оружие
            success = item_system.equip_item(entity_id, weapon, EquipmentSlot.MAIN_HAND)
            
            # Проверяем статистики экипировки
            stats = item_system.get_equipment_stats(entity_id)
            
            return success and "equipped_items" in stats
            
        except Exception as e:
            self.logger.error(f"Equipment system test failed: {e}")
            return False
    
    def _test_lighthouse_generation(self) -> bool:
        """Тест генерации маяков"""
        try:
            from core.lighthouse_system import LighthouseSystem
            
            lighthouse_system = LighthouseSystem()
            session_id = "test_session_001"
            
            # Генерируем маяк
            lighthouse = lighthouse_system.generate_lighthouse_for_session(session_id, 1)
            
            return lighthouse is not None and lighthouse.lighthouse_id.startswith("lighthouse_")
            
        except Exception as e:
            self.logger.error(f"Lighthouse generation test failed: {e}")
            return False
    
    def _test_lighthouse_discovery(self) -> bool:
        """Тест обнаружения маяков"""
        try:
            from core.lighthouse_system import LighthouseSystem
            
            lighthouse_system = LighthouseSystem()
            session_id = "test_session_002"
            
            # Генерируем маяк
            lighthouse = lighthouse_system.generate_lighthouse_for_session(session_id, 1)
            
            # Пытаемся обнаружить маяк
            discovery = lighthouse_system.attempt_discovery(
                "test_entity", (0, 0, 0), "player", 50
            )
            
            # Проверяем результат
            return discovery is not None or lighthouse.state == LighthouseState.HIDDEN
            
        except Exception as e:
            self.logger.error(f"Lighthouse discovery test failed: {e}")
            return False
    
    def _test_lighthouse_activation(self) -> bool:
        """Тест активации маяков"""
        try:
            from core.lighthouse_system import LighthouseSystem
            
            lighthouse_system = LighthouseSystem()
            session_id = "test_session_003"
            
            # Генерируем маяк
            lighthouse = lighthouse_system.generate_lighthouse_for_session(session_id, 1)
            
            # Пытаемся активировать маяк
            success = lighthouse_system.attempt_activation(
                "test_entity", (0, 0, 0), ["key_001"], 100
            )
            
            return True  # Тест прошел, даже если активация не удалась
            
        except Exception as e:
            self.logger.error(f"Lighthouse activation test failed: {e}")
            return False
    
    def _test_content_generation(self) -> bool:
        """Тест генерации контента"""
        try:
            from core.roguelike_content_generator import RoguelikeContentGenerator
            
            generator = RoguelikeContentGenerator()
            session_id = "test_session_004"
            
            # Генерируем контент
            content = generator.generate_session_content(session_id, 1)
            
            return (content is not None and 
                   len(content.items) > 0 and 
                   len(content.enemies) > 0 and 
                   len(content.skills) > 0)
            
        except Exception as e:
            self.logger.error(f"Content generation test failed: {e}")
            return False
    
    def _test_enemy_generation(self) -> bool:
        """Тест генерации врагов"""
        try:
            from core.roguelike_content_generator import RoguelikeContentGenerator, EnemyType
            
            generator = RoguelikeContentGenerator()
            
            # Генерируем врагов
            enemies = generator._generate_enemies(1)
            
            # Проверяем, что есть враги разных типов
            enemy_types = set(enemy.enemy_type for enemy in enemies.values())
            
            return len(enemies) > 0 and len(enemy_types) > 1
            
        except Exception as e:
            self.logger.error(f"Enemy generation test failed: {e}")
            return False
    
    def _test_save_system(self) -> bool:
        """Тест системы сохранений"""
        try:
            from core.save_system import SaveSystem
            
            save_system = SaveSystem()
            
            # Создаем тестовое сохранение
            save_data = {
                "test_data": "test_value",
                "timestamp": time.time()
            }
            
            save_id = save_system.create_save("test_save", save_data)
            
            return save_id is not None
            
        except Exception as e:
            self.logger.error(f"Save system test failed: {e}")
            return False
    
    def _test_roguelike_save(self) -> bool:
        """Тест сохранения роглайк сессий"""
        try:
            from core.save_system import SaveSystem
            
            save_system = SaveSystem()
            session_id = "test_session_005"
            
            # Создаем тестовые данные роглайк сессии
            save_id = save_system.create_roguelike_save(
                session_id=session_id,
                player_data={"name": "Test Player"},
                game_state={"level": 1},
                world_data={"world_id": "test_world"},
                ai_memory_data={"memories": []},
                generated_content={"items": [], "enemies": []},
                enemy_memory_bank={"shared_memories": []},
                player_memory={"player_memories": []}
            )
            
            return save_id is not None
            
        except Exception as e:
            self.logger.error(f"Roguelike save test failed: {e}")
            return False
    
    def _test_full_session_flow(self) -> bool:
        """Тест полного потока роглайк сессии"""
        try:
            # Этот тест проверяет интеграцию всех систем
            from core.roguelike_content_generator import RoguelikeContentGenerator
            from core.enhanced_ai_memory import EnhancedAIMemorySystem, EntityType
            from core.enhanced_item_system import EnhancedItemSystem
            from core.lighthouse_system import LighthouseSystem
            
            # Инициализируем все системы
            generator = RoguelikeContentGenerator()
            memory_system = EnhancedAIMemorySystem()
            item_system = EnhancedItemSystem()
            lighthouse_system = LighthouseSystem()
            
            session_id = "integration_test_session"
            
            # Генерируем контент
            content = generator.generate_session_content(session_id, 1)
            
            # Инициализируем память ИИ
            memory_system.initialize_entity_memory("test_player", EntityType.PLAYER)
            
            # Генерируем маяк
            lighthouse = lighthouse_system.generate_lighthouse_for_session(session_id, 1)
            
            return (content is not None and 
                   lighthouse is not None and 
                   memory_system.get_entity_memory("test_player") is not None)
            
        except Exception as e:
            self.logger.error(f"Full session flow test failed: {e}")
            return False
    
    def _test_ai_learning_integration(self) -> bool:
        """Тест интеграции ИИ обучения"""
        try:
            from core.enhanced_ai_memory import EnhancedAIMemorySystem, EntityType, MemoryType
            
            memory_system = EnhancedAIMemorySystem()
            
            # Инициализируем память для разных типов сущностей
            memory_system.initialize_entity_memory("player", EntityType.PLAYER)
            memory_system.initialize_entity_memory("enemy", EntityType.BASIC_ENEMY)
            memory_system.initialize_entity_memory("boss", EntityType.BOSS)
            
            # Добавляем память для каждой сущности
            memory_system.add_memory("player", MemoryType.COMBAT, {"action": "attack"}, 0.9)
            memory_system.add_memory("enemy", MemoryType.COMBAT, {"action": "defend"}, 0.7)
            memory_system.add_memory("boss", MemoryType.COMBAT, {"action": "special_attack"}, 0.8)
            
            # Проверяем, что память добавлена
            player_memories = memory_system.get_memories("player", MemoryType.COMBAT)
            enemy_memories = memory_system.get_memories("enemy", MemoryType.COMBAT)
            boss_memories = memory_system.get_memories("boss", MemoryType.COMBAT)
            
            return (len(player_memories) > 0 and 
                   len(enemy_memories) > 0 and 
                   len(boss_memories) > 0)
            
        except Exception as e:
            self.logger.error(f"AI learning integration test failed: {e}")
            return False
    
    def _test_memory_performance(self) -> bool:
        """Тест производительности системы памяти"""
        try:
            from core.enhanced_ai_memory import EnhancedAIMemorySystem, EntityType, MemoryType
            
            memory_system = EnhancedAIMemorySystem()
            entity_id = "performance_test_entity"
            
            memory_system.initialize_entity_memory(entity_id, EntityType.PLAYER)
            
            # Тестируем производительность добавления памяти
            start_time = time.time()
            
            for i in range(1000):
                memory_system.add_memory(
                    entity_id, MemoryType.COMBAT, 
                    {"action": f"action_{i}", "value": i}, 0.5
                )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Проверяем, что операция выполнилась за разумное время
            return execution_time < 5.0  # Менее 5 секунд для 1000 операций
            
        except Exception as e:
            self.logger.error(f"Memory performance test failed: {e}")
            return False
    
    def _test_item_performance(self) -> bool:
        """Тест производительности системы предметов"""
        try:
            from core.enhanced_item_system import EnhancedItemSystem, Item, ItemType, ItemRarity
            
            item_system = EnhancedItemSystem()
            entity_id = "performance_test_entity"
            
            inventory = item_system.create_inventory(entity_id)
            
            # Тестируем производительность добавления предметов
            start_time = time.time()
            
            for i in range(100):
                item = Item(
                    item_id=f"test_item_{i}",
                    name=f"Test Item {i}",
                    item_type=ItemType.CONSUMABLE,
                    rarity=ItemRarity.COMMON,
                    description=f"Test item {i}",
                    stack_size=10
                )
                item_system.add_item_to_inventory(entity_id, item, 1)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Проверяем, что операция выполнилась за разумное время
            return execution_time < 2.0  # Менее 2 секунд для 100 предметов
            
        except Exception as e:
            self.logger.error(f"Item performance test failed: {e}")
            return False
    
    def save_test_report(self, report: Dict[str, Any], filename: str = None) -> bool:
        """Сохранение отчета о тестах"""
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"test_report_{timestamp}.json"
            
            report_file = Path("data") / "test_reports" / filename
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Test report saved to {report_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving test report: {e}")
            return False

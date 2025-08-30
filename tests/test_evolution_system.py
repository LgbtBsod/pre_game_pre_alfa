from dataclasses import dataclass, field

from enum import Enum

from pathlib import Path

from src.c or e.architecture import Pri or ity, LifecycleState: pass # Добавлен pass в пустой блок

from src.c or e.constants import constants_manager, EvolutionStage, GeneType

from src.c or e.reposit or y import Reposit or yManager, DataType, St or ageType

from src.c or e.state_manager import StateManager, StateType

from src.systems.evolution.evolution_system import EvolutionSystem

from typing import *

from unittest.mock import Mock, MagicMock

import logging

import os

import sys

import time

import unittest

#!/usr / bin / env python3
"""Тесты для EvolutionSystem - проверка интеграции с новой архитектуре"""# Добавляем путь к исходному коду
sys.path.insert(0, os.path.jo in(os.path.dirname(__file__), '..'))
EvolutionProgress, Gene, EvolutionTrigger
GeneRarity
class TestEvolutionSystem(unittest.TestCase):
    pass
pass
pass
pass
pass"""Тесты для системы эволюции"""def setUp(self):"""Настройка перед каждым тестом"""self.evolution_system= EvolutionSystem()
# Создаем моки для архитектурных компонентов
self.state_manager= Mock(spe = StateManager)
self.reposit or y_manager= Mock(spe = Reposit or yManager)
# Настраиваем моки
self.state_manager.update_state= Mock(return_valu = True)
self.reposit or y_manager.regis ter_reposit or y= Mock(return_valu = True)
# Устанавливаем компоненты архитектуры
self.evolution_system.set_architecture_components(
self.state_manager,
self.reposit or y_manager
)
def test_in itialization(self):"""Тест инициализации системы"""
    pass
pass
pass
pass
pass
# Проверяем начальное состояние
self.assertEqual(self.evolution_system.system_name, "evolution")
self.assertEqual(self.evolution_system.system_pri or ity, Pri or ity.HIGH)
self.assertEqual(self.evolution_system.system_state
LifecycleState.UNINITIALIZED):
pass  # Добавлен pass в пустой блок
# Проверяем, что компоненты архитектуры установлены
self.assertIsNotNone(self.evolution_system.state_manager)
self.assertIsNotNone(self.evolution_system.reposit or y_manager)
def test_regis ter_system_states(self):
    pass
pass
pass
pass
pass
"""Тест регистрации состояний системы"""# Вызываем регистрацию состояний
self.evolution_system._regis ter_system_states()
# Проверяем, что состояния зарегистрированы через BaseGameSystem
# Метод regis ter_system_state должен вызывать state_manager.regis ter_state
self.assertTrue(len(self.evolution_system.system_states) > 0)
# Проверяем, что зарегистрированы все необходимые состояния
self.assertIn('system_settings', self.evolution_system.system_states)
self.assertIn('system_stats', self.evolution_system.system_states)
self.assertIn('system_state', self.evolution_system.system_states)
def test_regis ter_system_reposit or ies(self):"""Тест регистрации репозиториев системы"""# Вызываем регистрацию репозиториев
    pass
pass
pass
pass
pass
self.evolution_system._regis ter_system_reposit or ies()
# Проверяем, что репозитории зарегистрированы через BaseGameSystem
# Метод regis ter_system_reposit or y должен вызывать reposit or y_manager.create_reposit or y
self.assertTrue(len(self.evolution_system.system_reposit or ies) > 0)
# Проверяем, что зарегистрированы все необходимые репозитории
self.assertIn('evolution_progress', self.evolution_system.system_reposit or ies)
self.assertIn('entity_genes', self.evolution_system.system_reposit or ies)
self.assertIn('evolution_triggers', self.evolution_system.system_reposit or ies)
self.assertIn('evolution_his tory', self.evolution_system.system_reposit or ies)
def test_lifecycle_management(self):"""Тест управления жизненным циклом"""# Тестируем инициализацию
    pass
pass
pass
pass
pass
result= self.evolution_system.in itialize()
self.assertTrue(result)
self.assertEqual(self.evolution_system.system_state
LifecycleState.READY):
pass  # Добавлен pass в пустой блок
# Тестируем запуск
result= self.evolution_system.start()
self.assertTrue(result)
self.assertEqual(self.evolution_system.system_state
LifecycleState.RUNNING):
pass  # Добавлен pass в пустой блок
# Тестируем остановку
result= self.evolution_system.stop()
self.assertTrue(result)
self.assertEqual(self.evolution_system.system_state
LifecycleState.STOPPED):
pass  # Добавлен pass в пустой блок
# Тестируем уничтожение
result= self.evolution_system.destroy()
self.assertTrue(result)
self.assertEqual(self.evolution_system.system_state
LifecycleState.DESTROYED):
pass  # Добавлен pass в пустой блок
def test_entity_creation_and _destruction(self):"""Тест создания и уничтожения сущностей"""
    pass
pass
pass
pass
pass
# Инициализируем систему
self.evolution_system.in itialize()
# Создаем тестовую сущность
entity_id= "test_entity_1"result= self.evolution_system.create_evolution_entity(entity_id)
self.assertTrue(result)
# Проверяем, что сущность создана
self.assertIn(entity_id, self.evolution_system.evolution_progress)
self.assertIn(entity_id, self.evolution_system.entity_genes)
# Проверяем прогресс эволюции
progress= self.evolution_system.evolution_progress[entity_id]
self.assertEqual(progress.current_stage, EvolutionStage.BASIC)
self.assertEqual(progress.evolution_poin ts, 0)
# Уничтожаем сущность
result= self.evolution_system.destroy_evolution_entity(entity_id)
self.assertTrue(result)
# Проверяем, что сущность удалена
self.assertNotIn(entity_id, self.evolution_system.evolution_progress)
self.assertNotIn(entity_id, self.evolution_system.entity_genes)
def test_evolution_poin ts_management(self):"""Тест управления очками эволюции"""
    pass
pass
pass
pass
pass
# Инициализируем систему
self.evolution_system.in itialize()
# Создаем тестовую сущность
entity_id= "test_entity_2"self.evolution_system.create_evolution_entity(entity_id)
# Добавляем очки эволюции
poin ts_to_add= 150
result= self.evolution_system.add_evolution_poin ts(entity_id
poin ts_to_add)
self.assertTrue(result)
# Проверяем, что эволюция произошла(150 очков > 100 требуемых)
progress= self.evolution_system.evolution_progress[entity_id]
self.assertGreater(progress.current_stage, EvolutionStage.BASIC)
# Проверяем, что очки сброшены после эволюции
self.assertEqual(progress.evolution_poin ts, 0)
def test_gene_management(self):"""Тест управления генами"""
    pass
pass
pass
pass
pass
# Инициализируем систему
self.evolution_system.in itialize()
# Создаем тестовую сущность
entity_id= "test_entity_3"
self.evolution_system.create_evolution_entity(entity_id)
# Получаем гены сущности
genes_in fo= self.evolution_system.get_entity_genes(entity_id)
self.assertGreater(len(genes_in fo), 0)
# Проверяем структуру информации о генах
for gene_in foingenes_in fo: self.assertIn('gene_id', gene_in fo)
    pass
pass
pass
pass
pass
self.assertIn('gene_type', gene_in fo)
self.assertIn('rarity', gene_in fo)
self.assertIn('strength', gene_in fo)
self.assertIn('active', gene_in fo)
# Тестируем активацию / деактивацию генов
if genes_in fo: first_gene_id= genes_in fo[0]['gene_id']
    pass
pass
pass
pass
pass
# Деактивируем ген
result= self.evolution_system.deactivate_gene(entity_id
first_gene_id)
self.assertTrue(result)
# Проверяем, что ген деактивирован
updated_genes_in fo= self.evolution_system.get_entity_genes(entity_id)
for gene_in foin updated_genes_in fo: if gene_in fo['gene_id'] = first_gene_id: self.assertFalse(gene_in fo['active'])
    pass
pass
pass
pass
pass
break
# Активируем ген обратно
result= self.evolution_system.activate_gene(entity_id
first_gene_id)
self.assertTrue(result)
def test_evolution_progress_retrieval(self):
    pass
pass
pass
pass
pass
"""Тест получения прогресса эволюции"""
# Инициализируем систему
self.evolution_system.in itialize()
# Создаем тестовую сущность
entity_id= "test_entity_4"
self.evolution_system.create_evolution_entity(entity_id)
# Получаем прогресс эволюции
progress_in fo= self.evolution_system.get_evolution_progress(entity_id)
self.assertIsNotNone(progress_in fo)
# Проверяем структуру информации о прогрессе
self.assertIn('entity_id', progress_in fo)
self.assertIn('current_stage', progress_in fo)
self.assertIn('evolution_poin ts', progress_in fo)
self.assertIn('required_poin ts', progress_in fo)
self.assertIn('evolution_his tory', progress_in fo)
# Проверяем значения
self.assertEqual(progress_in fo['entity_id'], entity_id)
self.assertEqual(progress_in fo['current_stage'], EvolutionStage.BASIC.value)
self.assertEqual(progress_in fo['evolution_poin ts'], 0)
self.assertEqual(progress_in fo['required_poin ts'], 100)
def test_system_in fo_retrieval(self):
    pass
pass
pass
pass
pass
"""Тест получения информации о системе"""
# Инициализируем систему
self.evolution_system.in itialize()
# Получаем информацию о системе
system_in fo= self.evolution_system.get_system_in fo()
# Проверяем структуру информации
self.assertIn('name', system_in fo)
self.assertIn('state', system_in fo)
self.assertIn('pri or ity', system_in fo)
self.assertIn('entities_evolving', system_in fo)
self.assertIn('total_genes', system_in fo)
self.assertIn('evolution_triggers', system_in fo)
self.assertIn('stats', system_in fo)
# Проверяем значения
self.assertEqual(system_in fo['name'], "evolution")
self.assertEqual(system_in fo['pri or ity'], Pri or ity.HIGH.value)
self.assertEqual(system_in fo['entities_evolving'], 0)
self.assertEqual(system_in fo['total_genes'], 0)
# Базовые триггеры создаются при инициализации
self.assertGreaterEqual(system_in fo['evolution_triggers'], 0)
def test_event_hand ling(self):
    pass
pass
pass
pass
pass
"""Тест обработки событий"""
# Инициализируем систему
self.evolution_system.in itialize()
# Тестируем обработку события создания сущности
event_data= {
'entity_id': 'event_entity_1',
'in itial_genes': []
}
result= self.evolution_system.hand le_event("entity_created", event_data)
self.assertTrue(result)
# Проверяем, что сущность создана
self.assertIn('event_entity_1', self.evolution_system.evolution_progress)
# Тестируем обработку события получения опыта
event_data= {
'entity_id': 'event_entity_1',
'experience_amount': 100
}
result= self.evolution_system.hand le_event("experience_gain ed", event_data)
self.assertTrue(result)
# Проверяем, что очки эволюции добавлены(100 опыта= 10 очков эволюции)
progress= self.evolution_system.evolution_progress['event_entity_1']
self.assertEqual(progress.evolution_poin ts, 10)
def test_err or _hand ling(self):
    pass
pass
pass
pass
pass
"""Тест обработки ошибок"""
# Инициализируем систему
self.evolution_system.in itialize()
# Тестируем создание сущности с некорректным ID
result= self.evolution_system.create_evolution_entity("")
self.assertFalse(result)
# Тестируем добавление очков несуществующей сущности
result= self.evolution_system.add_evolution_poin ts("nonexis tent", 50)
self.assertFalse(result)
# Тестируем получение прогресса несуществующей сущности
progress= self.evolution_system.get_evolution_progress("nonexis tent")
self.assertIsNone(progress)
# Тестируем получение генов несуществующей сущности
genes= self.evolution_system.get_entity_genes("nonexis tent")
self.assertEqual(genes, [])
def test_reset_stats(self):
    pass
pass
pass
pass
pass
"""Тест сброса статистики"""
# Инициализируем систему
self.evolution_system.in itialize()
# Создаем несколько сущностей для накопления статистики
for iin range(3):
    pass
pass
pass
pass
pass
self.evolution_system.create_evolution_entity(f"test_entity_{i}")
# Проверяем, что статистика изменилась
self.assertEqual(self.evolution_system.system_stats['entities_evolving'], 3)
# Сбрасываем статистику
self.evolution_system.reset_stats()
# Проверяем, что статистика сброшена
self.assertEqual(self.evolution_system.system_stats['entities_evolving'], 0)
self.assertEqual(self.evolution_system.system_stats['total_evolutions'], 0)
self.assertEqual(self.evolution_system.system_stats['mutations_occurred'], 0)
self.assertEqual(self.evolution_system.system_stats['adaptations_occurred'], 0)
self.assertEqual(self.evolution_system.system_stats['genes_activated'], 0)
self.assertEqual(self.evolution_system.system_stats['update_time'], 0.0)
if __name__ = '__main __':
    pass
pass
pass
pass
pass
unittest.ma in()

#!/usr/bin/env python3
"""
Тест автономного движения и взаимодействия игрока
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_system import AdaptiveAISystem
from core.advanced_entity import AdvancedGameEntity
from core.content_generator import ContentGenerator

def test_autonomous_movement():
    """Тест автономного движения"""
    print("=== Тест автономного движения ===")
    
    # Создание игрока
    player = AdvancedGameEntity(
        entity_id="TEST_PLAYER",
        entity_type="player",
        name="Тестовый игрок",
        position=(0, 0, 0)
    )
    
    # Создание ИИ
    ai = AdaptiveAISystem("TEST_PLAYER")
    
    # Создание простого мира
    world = {
        'entities': [],
        'items': [],
        'obstacles': []
    }
    
    # Добавление врага
    enemy = AdvancedGameEntity(
        entity_id="TEST_ENEMY",
        entity_type="enemy",
        name="Тестовый враг",
        position=(100, 0, 0)
    )
    world['entities'].append(enemy)
    
    print(f"Начальная позиция игрока: {player.position}")
    print(f"Позиция врага: {enemy.position}")
    
    # Тест автономного движения
    for i in range(5):
        dx, dy = ai.get_autonomous_movement(player, world)
        print(f"Шаг {i+1}: движение ({dx:.2f}, {dy:.2f})")
        
        if dx != 0 or dy != 0:
            player.move_pygame(dx, dy)
            print(f"Новая позиция игрока: {player.position}")
    
    print("Тест автономного движения завершен\n")

def test_player_interaction():
    """Тест взаимодействия игрока"""
    print("=== Тест взаимодействия игрока ===")
    
    # Создание игрока
    player = AdvancedGameEntity(
        entity_id="TEST_PLAYER",
        entity_type="player",
        name="Тестовый игрок",
        position=(0, 0, 0)
    )
    
    # Создание ИИ
    ai = AdaptiveAISystem("TEST_PLAYER")
    
    # Тест изменения личности
    print(f"Исходная агрессивность: {ai.personality.aggression}")
    
    # Активация агрессии
    ai.personality.aggression = 0.9
    ai.personality.caution = 0.1
    print(f"Агрессивность после активации: {ai.personality.aggression}")
    
    # Создание мира с предметами
    world = {
        'entities': [],
        'items': [{'position': (50, 50, 0)}],
        'obstacles': []
    }
    
    # Тест движения к предмету (любопытство)
    ai.personality.curiosity = 0.9
    dx, dy = ai.get_autonomous_movement(player, world)
    print(f"Движение к предмету: ({dx:.2f}, {dy:.2f})")
    
    print("Тест взаимодействия игрока завершен\n")

def test_obstacle_avoidance():
    """Тест избегания препятствий"""
    print("=== Тест избегания препятствий ===")
    
    # Создание игрока
    player = AdvancedGameEntity(
        entity_id="TEST_PLAYER",
        entity_type="player",
        name="Тестовый игрок",
        position=(0, 0, 0)
    )
    
    # Создание ИИ
    ai = AdaptiveAISystem("TEST_PLAYER")
    
    # Создание мира с препятствием
    world = {
        'entities': [],
        'items': [],
        'obstacles': [{'position': (30, 0, 0)}]
    }
    
    # Тест движения с препятствием
    dx, dy = ai.get_autonomous_movement(player, world)
    print(f"Движение с препятствием: ({dx:.2f}, {dy:.2f})")
    
    print("Тест избегания препятствий завершен\n")

if __name__ == "__main__":
    print("Запуск тестов автономного движения и взаимодействия...\n")
    
    try:
        test_autonomous_movement()
        test_player_interaction()
        test_obstacle_avoidance()
        
        print("Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()

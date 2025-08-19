#!/usr/bin/env python3
"""
Тест изометрической проекции и навигации к маякам
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.isometric_system import (
    IsometricProjection, BeaconNavigationSystem, BeaconType, 
    AStarPathfinder, IsometricRenderer
)
from core.advanced_entity import AdvancedGameEntity
from core.ai_system import AdaptiveAISystem

def test_isometric_projection():
    """Тест изометрической проекции"""
    print("=== Тест изометрической проекции ===")
    
    projection = IsometricProjection(tile_width=64, tile_height=32)
    
    # Тест преобразования координат
    world_coords = [(0, 0, 0), (10, 5, 0), (-5, 10, 2)]
    
    for world_x, world_y, world_z in world_coords:
        iso_x, iso_y = projection.world_to_iso(world_x, world_y, world_z)
        back_x, back_y = projection.iso_to_world(iso_x, iso_y, world_z)
        
        print(f"Мир ({world_x}, {world_y}, {world_z}) -> Изо ({iso_x:.1f}, {iso_y:.1f}) -> Обратно ({back_x:.1f}, {back_y:.1f})")
    
    # Тест масштабирования
    projection.set_zoom(2.0)
    iso_x, iso_y = projection.world_to_iso(10, 10, 0)
    print(f"С масштабом 2.0: (10, 10, 0) -> ({iso_x:.1f}, {iso_y:.1f})")
    
    print("Тест изометрической проекции завершен\n")

def test_beacon_navigation():
    """Тест системы навигации по маякам"""
    print("=== Тест системы навигации по маякам ===")
    
    nav_system = BeaconNavigationSystem(world_width=1000, world_height=1000)
    
    # Начальная позиция игрока
    player_pos = (50, 50, 0)
    
    print(f"Начальная позиция игрока: {player_pos}")
    print(f"Количество маяков: {len(nav_system.beacons)}")
    
    # Обнаружение маяков
    discovered_beacon = nav_system.discover_beacon(player_pos)
    if discovered_beacon:
        print(f"Обнаружен маяк: {discovered_beacon.id}")
    
    # Поиск ближайшего навигационного маяка
    nearest_beacon = nav_system.get_nearest_beacon(player_pos, BeaconType.NAVIGATION)
    if nearest_beacon:
        print(f"Ближайший навигационный маяк: {nearest_beacon.id} в позиции {nearest_beacon.position}")
        
        # Установка цели навигации
        success = nav_system.set_navigation_target(nearest_beacon.id)
        print(f"Установка цели навигации: {'Успешно' if success else 'Неудачно'}")
        
        # Получение направления
        direction = nav_system.get_navigation_direction(player_pos)
        if direction:
            print(f"Направление к маяку: ({direction[0]:.2f}, {direction[1]:.2f})")
    
    # Информация о маяках
    beacon_info = nav_system.get_beacon_info()
    print(f"Обнаружено маяков: {beacon_info['discovered_beacons']}/{beacon_info['total_beacons']}")
    
    print("Тест системы навигации завершен\n")

def test_pathfinding():
    """Тест алгоритма поиска пути A*"""
    print("=== Тест алгоритма поиска пути A* ===")
    
    pathfinder = AStarPathfinder(20, 20)
    
    # Добавление препятствий
    obstacles = [(5, 5), (5, 6), (5, 7), (6, 7), (7, 7)]
    for obs_x, obs_y in obstacles:
        pathfinder.add_obstacle(obs_x, obs_y)
    
    print(f"Добавлено препятствий: {len(obstacles)}")
    
    # Поиск пути
    start = (3, 3)
    target = (8, 8)
    
    path = pathfinder.find_path(start[0], start[1], target[0], target[1])
    
    if path:
        print(f"Путь найден от {start} до {target}:")
        print(f"Длина пути: {len(path)} шагов")
        print(f"Путь: {path[:5]}..." if len(path) > 5 else f"Путь: {path}")
    else:
        print(f"Путь от {start} до {target} не найден")
    
    print("Тест алгоритма поиска пути завершен\n")

def test_ai_beacon_integration():
    """Тест интеграции ИИ с системой маяков"""
    print("=== Тест интеграции ИИ с системой маяков ===")
    
    # Создание игрока
    player = AdvancedGameEntity(
        entity_id="TEST_PLAYER",
        entity_type="player",
        name="Тестовый игрок",
        position=(100, 100, 0)
    )
    
    # Создание ИИ
    ai = AdaptiveAISystem("TEST_PLAYER")
    
    # Создание мира с системой маяков
    world = type('MockWorld', (), {})()
    world.beacon_system = BeaconNavigationSystem(world_width=1000, world_height=1000)
    world.entities = []
    world.items = []
    world.obstacles = []
    
    # Установка цели навигации
    world.beacon_system.set_navigation_target("BEACON_MAIN")
    
    print(f"Начальная позиция игрока: {player.position}")
    print(f"Активная цель: {world.beacon_system.active_target}")
    
    # Тест автономного движения с навигацией
    for i in range(3):
        dx, dy = ai.get_autonomous_movement(player, world)
        print(f"Шаг {i+1}: движение ({dx:.2f}, {dy:.2f})")
        
        if dx != 0 or dy != 0:
            player.move_pygame(dx, dy)
            print(f"Новая позиция игрока: {player.position}")
    
    print("Тест интеграции ИИ с маяками завершен\n")

def test_beacon_discovery():
    """Тест обнаружения маяков"""
    print("=== Тест обнаружения маяков ===")
    
    nav_system = BeaconNavigationSystem()
    
    # Позиции для тестирования
    test_positions = [
        (50, 50, 0),    # Далеко от маяков
        (500, 500, 0),  # Рядом с главным маяком
        (200, 300, 0),  # Рядом с эволюционным маяком
        (800, 200, 0),  # Рядом с ресурсным маяком
    ]
    
    for pos in test_positions:
        discovered = nav_system.discover_beacon(pos)
        if discovered:
            print(f"В позиции {pos} обнаружен маяк: {discovered.id} ({discovered.beacon_type.value})")
        else:
            print(f"В позиции {pos} маяки не обнаружены")
    
    # Итоговая статистика
    beacon_info = nav_system.get_beacon_info()
    print(f"\nИтого обнаружено: {beacon_info['discovered_beacons']}/{beacon_info['total_beacons']} маяков")
    
    print("Тест обнаружения маяков завершен\n")

if __name__ == "__main__":
    print("Запуск тестов изометрической проекции и навигации...\n")
    
    try:
        test_isometric_projection()
        test_beacon_navigation()
        test_pathfinding()
        test_ai_beacon_integration()
        test_beacon_discovery()
        
        print("🎯 Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()

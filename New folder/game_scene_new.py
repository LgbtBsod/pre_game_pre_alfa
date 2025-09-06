#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import random
from direct.task import Task
from panda3d.core import CardMaker, TransparencyAttrib

from utils.camera import CameraController
from utils.lighting import LightingManager
from utils.geometry import GeometryUtils
from character import Character
from game_systems.game_manager import GameManager
from game_systems.input_manager import InputManager
from hud import HUD

class GameScene:
    """Улучшенная игровая сцена"""
    
    def __init__(self, game):
        self.game = game
        self.objects = []
        
        # Системы
        self.camera_controller = CameraController(game)
        self.lighting_manager = LightingManager(game)
        self.game_manager = GameManager(game)
        self.input_manager = InputManager(game)
        
        # HUD
        self.hud = None
        
    def enter(self):
        """Вход в игровую сцену"""
        self.setup_lighting()
        self.setup_camera()
        self.create_ground()
        self.create_geometric_objects()
        
        # Проверяем, есть ли сохраненное состояние
        if self.game_manager.saved_state and self.game_manager.is_paused:
            self.create_player()
            self.game_manager.restore_state()
        else:
            self.create_player()
            self.game_manager.clear_state()
        
        self.setup_controls()
        self.setup_game_loop()
        
        # Создаем HUD
        self.hud = HUD(self.game)
        self.hud.create_hud()
        
    def exit(self):
        """Выход из игровой сцены"""
        # Сохраняем состояние только если переходим в паузу
        if self.game.state_manager.current_state == "pause":
            self.game_manager.save_state()
            self.game_manager.is_paused = True
        
        # Очистка объектов
        for obj in self.objects:
            obj.removeNode()
        self.objects.clear()
        
        # Очистка игровых систем
        self.game_manager.cleanup()
        
        # Очищаем освещение
        self.lighting_manager.clear_lighting()
        
        # Уничтожаем HUD
        if self.hud:
            self.hud.destroy()
            self.hud = None
        
        # Очистка задач
        self.game.taskMgr.remove("camera_control")
        self.game.taskMgr.remove("game_loop")
        
    def setup_lighting(self):
        """Настройка освещения"""
        self.lighting_manager.setup_basic_lighting()
        
    def setup_camera(self):
        """Настройка камеры"""
        self.camera_controller.setup_isometric_camera()
        
    def create_ground(self):
        """Создание земли"""
        cm = CardMaker("ground")
        cm.setFrame(-200, 200, -200, 200)
        ground = self.game.render.attachNewNode(cm.generate())
        ground.setColor(0.3, 0.5, 0.3, 1)
        ground.setPos(0, 0, 0)
        self.objects.append(ground)
        
        # Создаем сетку
        self.create_grid()
        
    def create_grid(self):
        """Создание сетки на земле"""
        grid_step = 0.25
        cm = CardMaker("grid_line")
        
        # Вертикальные линии
        for x in range(-200, 201, int(grid_step * 4)):
            cm.setFrame(-0.01, 0.01, -200, 200)
            line = self.game.render.attachNewNode(cm.generate())
            line.setColor(0.2, 0.2, 0.2, 0.5)
            line.setPos(x, 0, 0.01)
            self.objects.append(line)
            
        # Горизонтальные линии
        for y in range(-200, 201, int(grid_step * 4)):
            cm.setFrame(-200, 200, -0.01, 0.01)
            line = self.game.render.attachNewNode(cm.generate())
            line.setColor(0.2, 0.2, 0.2, 0.5)
            line.setPos(0, y, 0.01)
            self.objects.append(line)
            
    def create_geometric_objects(self):
        """Создание геометрических объектов"""
        colors = [
            (1, 0, 0, 1),    # Красный
            (0, 1, 0, 1),    # Зеленый
            (0, 0, 1, 1),    # Синий
            (1, 1, 0, 1),    # Желтый
            (1, 0, 1, 1),    # Пурпурный
            (0, 1, 1, 1)     # Голубой
        ]
        
        for i in range(20):
            x = random.uniform(-150, 150)
            y = random.uniform(-150, 150)
            z = random.uniform(1, 5)
            color = random.choice(colors)
            
            # Случайный тип объекта
            obj_type = random.choice(["cube", "sphere", "cylinder"])
            
            if obj_type == "cube":
                obj = GeometryUtils.create_simple_cube(
                    self.game.render, f"obj_{i}", x, y, z, 2, 2, 2, color
                )
            elif obj_type == "sphere":
                obj = GeometryUtils.create_sphere(
                    self.game.render, f"obj_{i}", x, y, z, 1, color
                )
            else:  # cylinder
                obj = GeometryUtils.create_cylinder(
                    self.game.render, f"obj_{i}", x, y, z, 1, 2, color
                )
                
            self.objects.append(obj)
            
    def create_player(self):
        """Создание игрока через CharacterManager"""
        if hasattr(self.game, 'character_manager'):
            self.game_manager.player = self.game.character_manager.create_player(0, 0, 1)
            self.game_manager.player.create_character()
            self.game_manager.set_player(self.game_manager.player)
        else:
            # Fallback для обратной совместимости
            self.game_manager.player = Character(self.game, 0, 0, 1)
            self.game_manager.player.create_character()
            self.game_manager.set_player(self.game_manager.player)
        
    def setup_controls(self):
        """Настройка управления"""
        # Отключаем ручное управление - теперь персонаж управляется ИИ
        # self.input_manager.register_key("w", lambda dt: self.move_player(0, 1), "hold")
        # self.input_manager.register_key("s", lambda dt: self.move_player(0, -1), "hold")
        # self.input_manager.register_key("a", lambda dt: self.move_player(-1, 0), "hold")
        # self.input_manager.register_key("d", lambda dt: self.move_player(1, 0), "hold")
        
        # Поворот камеры
        self.input_manager.register_key("arrow_left", lambda dt: self.camera_controller.rotate_camera(-1), "hold")
        self.input_manager.register_key("arrow_right", lambda dt: self.camera_controller.rotate_camera(1), "hold")
        
        # Переключение режима камеры
        self.input_manager.register_key("c", self.camera_controller.toggle_mode)
        
        # Свободное движение камеры
        self.input_manager.register_key("i", lambda dt: self.camera_controller.move_free_camera("forward"), "hold")
        self.input_manager.register_key("k", lambda dt: self.camera_controller.move_free_camera("backward"), "hold")
        self.input_manager.register_key("j", lambda dt: self.camera_controller.move_free_camera("left"), "hold")
        self.input_manager.register_key("l", lambda dt: self.camera_controller.move_free_camera("right"), "hold")
        
        # Отключаем ручную атаку - теперь ИИ сам решает когда атаковать
        # self.input_manager.register_key("space", self.player_attack)
        
        # Добавляем клавиши для отладки ИИ
        self.input_manager.register_key("f1", self.show_ai_info)
        self.input_manager.register_key("f2", self.show_memory_info)
        self.input_manager.register_key("f3", self.toggle_ai_debug)
        
    def move_player(self, dx, dy):
        """Движение игрока"""
        if self.game_manager.player:
            self.game_manager.player.move_by(dx, dy, 0, 0.016)
            
    def player_attack(self):
        """Атака игрока"""
        if not self.game_manager.player:
            return
            
        # Находим ближайшего врага
        closest_enemy = None
        closest_distance = float('inf')
        
        for enemy in self.game_manager.enemies:
            if enemy.is_alive():
                distance = self.game_manager.player.get_distance_to(enemy)
                if distance < closest_distance and distance <= self.game_manager.player.attack_range:
                    closest_distance = distance
                    closest_enemy = enemy
                    
        if closest_enemy:
            self.game_manager.player.attack(closest_enemy)
            
    def setup_game_loop(self):
        """Настройка игрового цикла"""
        self.game.taskMgr.add(self.game_loop, "game_loop")
        
    def game_loop(self, task):
        """Основной игровой цикл"""
        dt = 0.016  # Фиксированная скорость
        
        # Обновление ввода
        self.input_manager.update(dt)
        
        # Обновление игровой логики
        self.game_manager.update(dt)
        
        # Обновление камеры
        if self.game_manager.player:
            from panda3d.core import Point3
            player_pos = Point3(self.game_manager.player.x, self.game_manager.player.y, self.game_manager.player.z)
            self.camera_controller.update(player_pos)
        
        # Обновление HUD
        if self.hud and self.game_manager.player:
            self.hud.update_hud(self.game_manager.player)
            
        # Проверка смерти игрока
        if self.game_manager.player and not self.game_manager.player.is_alive():
            self.game.state_manager.change_state("death")
        
        return task.cont
    
    def show_ai_info(self):
        """Показать информацию об ИИ"""
        if self.game_manager.player:
            ai_stats = self.game_manager.player.get_ai_stats()
            emotional_state = self.game_manager.player.get_ai_emotional_state()
            
            print("\n=== AI Information ===")
            print(f"Entity ID: {self.game_manager.player.entity_id}")
            print(f"Current Emotion: {emotional_state['current_emotion']}")
            print(f"Active Emotions: {emotional_state['active_emotions']}")
            print(f"Personality: {ai_stats['personality']}")
            print(f"Decision Count: {ai_stats['decision_count']}")
            print(f"Last Decision: {ai_stats['last_decision']}")
            print("=====================\n")
    
    def show_memory_info(self):
        """Показать информацию о памяти"""
        if self.game_manager.player:
            memories = self.game_manager.player.get_memories(limit=5)
            memory_stats = self.game_manager.player.get_memory_stats()
            
            print("\n=== Memory Information ===")
            print(f"Total Memories: {memory_stats['total_memories']}")
            print(f"Memory Types: {memory_stats['memory_types']}")
            print(f"Recent Memories:")
            for memory in memories:
                print(f"  - {memory['title']}: {memory['description'][:50]}...")
            print("==========================\n")
    
    def toggle_ai_debug(self):
        """Переключить режим отладки ИИ"""
        if not hasattr(self, 'ai_debug_mode'):
            self.ai_debug_mode = False
        
        self.ai_debug_mode = not self.ai_debug_mode
        print(f"AI Debug Mode: {'ON' if self.ai_debug_mode else 'OFF'}")
        
        if self.ai_debug_mode and self.game_manager.player:
            # Добавляем эмоцию для тестирования
            from systems.ai_agent import EmotionType
            self.game_manager.player.add_ai_emotion(
                EmotionType.EXCITED, 0.8, 5.0, "debug_test"
            )
            print("Added test emotion: EXCITED")

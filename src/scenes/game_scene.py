#!/usr/bin/env python3
"""
Game Scene - Основная игровая сцена на Panda3D
Отвечает только за игровой процесс и управление игровыми системами
"""

import logging
import math
import random
from typing import List, Optional, Dict, Any, Tuple
from panda3d.core import NodePath, PandaNode, Vec3, Point3, LVector3
from panda3d.core import OrthographicLens, PerspectiveLens
from panda3d.core import DirectionalLight, AmbientLight
from panda3d.core import TransparencyAttrib, AntialiasAttrib
from panda3d.core import TextNode, PandaNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage

from ..core.scene_manager import Scene
from ..systems import (
    EvolutionSystem, CombatSystem,
    CraftingSystem, InventorySystem
)
from ..systems.ai.ai_interface import AISystemFactory, AISystemManager, AIDecision

logger = logging.getLogger(__name__)

class IsometricCamera:
    """Изометрическая камера для Panda3D"""
    
    def __init__(self, camera_node: NodePath):
        self.camera_node = camera_node
        
        # Позиция камеры в мировых координатах
        self.world_x = 0.0
        self.world_y = 0.0
        self.world_z = 20.0
        
        # Масштаб
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        
        # Изометрические углы (стандартные 30 градусов)
        self.iso_angle = math.radians(30)
        self.cos_angle = math.cos(self.iso_angle)
        self.sin_angle = math.sin(self.iso_angle)
        
        # Настройка изометрической проекции
        self._setup_isometric_projection()
    
    def _setup_isometric_projection(self):
        """Настройка изометрической проекции"""
        lens = OrthographicLens()
        lens.setFilmSize(40, 30)
        lens.setNearFar(-100, 100)
        self.camera_node.node().setLens(lens)
        
        # Устанавливаем начальную позицию камеры
        self.camera_node.setPos(self.world_x, self.world_y, self.world_z)
        self.camera_node.lookAt(0, 0, 0)
    
    def world_to_screen(self, world_x: float, world_y: float, world_z: float = 0) -> Tuple[float, float, float]:
        """Преобразование мировых координат в экранные (изометрическая проекция)"""
        # Смещение относительно камеры
        rel_x = world_x - self.world_x
        rel_y = world_y - self.world_y
        rel_z = world_z
        
        # Изометрическая проекция
        iso_x = (rel_x - rel_y) * self.cos_angle
        iso_y = (rel_x + rel_y) * self.sin_angle
        iso_z = rel_z
        
        # Применяем масштаб
        iso_x *= self.zoom
        iso_y *= self.zoom
        iso_z *= self.zoom
        
        return iso_x, iso_y, iso_z
    
    def screen_to_world(self, screen_x: float, screen_y: float, screen_z: float = 0) -> Tuple[float, float, float]:
        """Преобразование экранных координат в мировые"""
        # Обратная изометрическая проекция
        world_x = (screen_x / self.cos_angle + screen_y / self.sin_angle) / 2 + self.world_x
        world_y = (screen_y / self.sin_angle - screen_x / self.cos_angle) / 2 + self.world_y
        world_z = screen_z / self.zoom
        
        return world_x, world_y, world_z
    
    def move(self, dx: float, dy: float, dz: float = 0):
        """Перемещение камеры"""
        self.world_x += dx
        self.world_y += dy
        self.world_z += dz
        
        # Обновляем позицию камеры
        self.camera_node.setPos(self.world_x, self.world_y, self.world_z)
    
    def set_zoom(self, zoom: float):
        """Установка масштаба"""
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom))
        
        # Обновляем проекцию
        lens = self.camera_node.node().getLens()
        if isinstance(lens, OrthographicLens):
            lens.setFilmSize(40 / self.zoom, 30 / self.zoom)
    
    def follow_entity(self, entity: Dict[str, Any], smooth: float = 0.1):
        """Следование за сущностью"""
        target_x = entity.get('x', 0)
        target_y = entity.get('y', 0)
        target_z = entity.get('z', 0)
        
        # Плавное следование
        self.world_x += (target_x - self.world_x) * smooth
        self.world_y += (target_y - self.world_y) * smooth
        self.world_z += (target_z - self.world_z) * smooth
        
        # Обновляем позицию камеры
        self.camera_node.setPos(self.world_x, self.world_y, self.world_z)

class GameScene(Scene):
    """Основная игровая сцена на Panda3D"""
    
    def __init__(self):
        super().__init__("game")
        
        # Игровые системы
        self.systems = {}
        
        # AI система
        self.ai_manager = AISystemManager()
        
        # Игровые объекты
        self.entities: List[Dict[str, Any]] = []
        self.particles: List[Dict[str, Any]] = []
        self.ui_elements: List[Dict[str, Any]] = []
        
        # Panda3D узлы
        self.scene_root = None
        self.entities_root = None
        self.particles_root = None
        self.ui_root = None
        
        # Изометрическая камера
        self.camera: Optional[IsometricCamera] = None
        
        # Игровое состояние
        self.game_paused = False
        self.game_time = 0.0
        self.day_night_cycle = 0.0
        
        # UI элементы Panda3D
        self.health_bar_text = None
        self.ai_info_text = None
        self.debug_text = None
        
        # Отладочная информация
        self.show_debug = True
        
        logger.info("Игровая сцена Panda3D создана")
    
    def initialize(self) -> bool:
        """Инициализация игровой сцены"""
        try:
            logger.info("Начало инициализации игровой сцены Panda3D...")
            
            # Создание корневых узлов
            self._create_scene_nodes()
            
            # Создаем изометрическую камеру
            if hasattr(self, 'scene_manager') and self.scene_manager:
                # Используем основную камеру Panda3D
                from panda3d.core import Camera
                camera_node = self.scene_manager.render_node.find("**/+Camera")
                if camera_node.isEmpty():
                    # Если камера не найдена, создаем новую
                    camera = Camera('game_camera')
                    camera_node = self.scene_manager.render_node.attachNewNode(camera)
                self.camera = IsometricCamera(camera_node)
            
            # Инициализируем игровые системы
            self._initialize_game_systems()
            
            # Создаем начальные объекты
            self._create_initial_objects()
            
            # Настройка освещения
            self._setup_lighting()
            
            # Создание UI элементов
            self._create_ui_elements()
            
            logger.info("Игровая сцена Panda3D успешно инициализирована")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации игровой сцены: {e}")
            return False
    
    def _create_scene_nodes(self):
        """Создание корневых узлов сцены"""
        if hasattr(self, 'scene_manager') and self.scene_manager:
            self.scene_root = self.scene_manager.render_node.attachNewNode("game_scene")
            self.entities_root = self.scene_root.attachNewNode("entities")
            self.particles_root = self.scene_root.attachNewNode("particles")
            self.ui_root = self.scene_root.attachNewNode("ui")
    
    def _initialize_game_systems(self):
        """Инициализация игровых систем"""
        try:
            # Создаем системы
            self.systems['evolution'] = EvolutionSystem()
            self.systems['combat'] = CombatSystem()
            self.systems['crafting'] = CraftingSystem()
            self.systems['inventory'] = InventorySystem()
            
            # Инициализируем каждую систему
            for system_name, system in self.systems.items():
                if hasattr(system, 'initialize'):
                    system.initialize()
            
            # Инициализируем AI систему
            ai_system = AISystemFactory.create_ai_system("auto")
            self.ai_manager.add_system("default", ai_system)
            
            logger.debug("Игровые системы инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось инициализировать некоторые системы: {e}")
    
    def _create_initial_objects(self):
        """Создание начальных игровых объектов"""
        try:
            # Создаем тестового игрока
            self._create_test_player()
            
            # Создаем тестовых NPC
            self._create_test_npcs()
            
            # Создаем UI элементы
            self._create_ui_elements()
            
            logger.debug("Начальные объекты созданы")
            
        except Exception as e:
            logger.warning(f"Не удалось создать некоторые объекты: {e}")
    
    def _create_test_player(self):
        """Создание тестового игрока с AI-управлением"""
        player = {
            'id': 'player_1',
            'type': 'player',
            'x': 0,
            'y': 0,
            'z': 0,
            'width': 2,
            'height': 2,
            'depth': 2,
            'color': (1, 1, 0, 1),  # Желтый
            'health': 100,
            'max_health': 100,
            'speed': 5.0,
            'level': 1,
            'experience': 0,
            'ai_personality': 'curious',  # Личность AI
            'stats': {
                'strength': 15,
                'agility': 12,
                'intelligence': 18,
                'vitality': 14
            },
            'node': None  # Panda3D узел
        }
        
        # Создаем Panda3D узел для игрока
        if self.entities_root:
            player['node'] = self._create_entity_node(player)
        
        self.entities.append(player)
        
        # Регистрируем игрока в AI системе
        self.ai_manager.register_entity('player_1', player, "default", 'player')
        
        logger.debug("Тестовый игрок с AI создан")
    
    def _create_test_npcs(self):
        """Создание тестовых NPC с AI"""
        npc_configs = [
            {
                'id': 'npc_1',
                'x': -5, 'y': -5, 'z': 0, 'color': (1, 0, 0, 1),  # Красный
                'ai_personality': 'aggressive',
                'memory_group': 'enemies'
            },
            {
                'id': 'npc_2', 
                'x': 5, 'y': 5, 'z': 0, 'color': (0, 0, 1, 1),  # Синий
                'ai_personality': 'defensive',
                'memory_group': 'npcs'
            },
            {
                'id': 'npc_3',
                'x': 0, 'y': 5, 'z': 0, 'color': (0, 1, 0, 1),  # Зеленый
                'ai_personality': 'curious',
                'memory_group': 'npcs'
            }
        ]
        
        for config in npc_configs:
            npc = {
                'id': config['id'],
                'type': 'npc',
                'x': config['x'],
                'y': config['y'],
                'z': config['z'],
                'width': 1.5,
                'height': 1.5,
                'depth': 1.5,
                'color': config['color'],
                'health': 50,
                'max_health': 50,
                'speed': 2.0,
                'ai_state': 'idle',
                'level': 1,
                'experience': 0,
                'ai_personality': config['ai_personality'],
                'stats': {
                    'strength': 10,
                    'agility': 8,
                    'intelligence': 6,
                    'vitality': 12
                },
                'node': None
            }
            
            # Создаем Panda3D узел для NPC
            if self.entities_root:
                npc['node'] = self._create_entity_node(npc)
            
            self.entities.append(npc)
            
            # Регистрируем NPC в AI системе
            self.ai_manager.register_entity(
                config['id'], 
                npc, 
                "default",
                config['memory_group']
            )
        
        logger.debug(f"Создано {len(npc_configs)} тестовых NPC с AI")
    
    def _create_entity_node(self, entity: Dict[str, Any]) -> NodePath:
        """Создание Panda3D узла для сущности"""
        # Создаем простой куб для сущности
        from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
        from panda3d.core import GeomVertexWriter, GeomTriangles, GeomNode
        
        # Создаем геометрию куба
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('cube', format, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        # Вершины куба
        size = entity.get('width', 1) / 2
        vertices = [
            (-size, -size, -size), (size, -size, -size), (size, size, -size), (-size, size, -size),
            (-size, -size, size), (size, -size, size), (size, size, size), (-size, size, size)
        ]
        
        # Добавляем вершины
        for v in vertices:
            vertex.addData3(*v)
            color.addData4(*entity['color'])
        
        # Создаем треугольники
        prim = GeomTriangles(Geom.UHStatic)
        
        # Грани куба
        faces = [
            (0, 1, 2), (2, 3, 0),  # Передняя грань
            (1, 5, 6), (6, 2, 1),  # Правая грань
            (5, 4, 7), (7, 6, 5),  # Задняя грань
            (4, 0, 3), (3, 7, 4),  # Левая грань
            (3, 2, 6), (6, 7, 3),  # Верхняя грань
            (4, 5, 1), (1, 0, 4)   # Нижняя грань
        ]
        
        for face in faces:
            prim.addVertices(*face)
            prim.closePrimitive()
        
        # Создаем геометрию
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        # Создаем узел
        node = GeomNode('entity')
        node.addGeom(geom)
        
        # Создаем NodePath и устанавливаем позицию
        np = self.entities_root.attachNewNode(node)
        np.setPos(entity['x'], entity['y'], entity['z'])
        
        return np
    
    def _setup_lighting(self):
        """Настройка освещения для сцены"""
        if not self.scene_root:
            return
        
        # Основное направленное освещение
        dlight = DirectionalLight('game_dlight')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.scene_root.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.scene_root.setLight(dlnp)
        
        # Фоновое освещение
        alight = AmbientLight('game_alight')
        alight.setColor((0.3, 0.3, 0.3, 1))
        alnp = self.scene_root.attachNewNode(alight)
        self.scene_root.setLight(alnp)
        
        logger.debug("Освещение игровой сцены настроено")
    
    def _create_ui_elements(self):
        """Создание UI элементов Panda3D"""
        # Полоска здоровья
        self.health_bar_text = OnscreenText(
            text="HP: 100/100",
            pos=(-1.3, 0.7),
            scale=0.04,
            fg=(1, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Информация об AI
        self.ai_info_text = OnscreenText(
            text="AI: Initializing...",
            pos=(-1.3, 0.6),
            scale=0.03,
            fg=(0, 1, 1, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        # Отладочная информация
        self.debug_text = OnscreenText(
            text="Debug: Enabled",
            pos=(-1.3, 0.5),
            scale=0.03,
            fg=(1, 1, 0, 1),
            align=TextNode.ALeft,
            mayChange=True
        )
        
        logger.debug("UI элементы Panda3D созданы")
    
    def update(self, delta_time: float):
        """Обновление игровой сцены"""
        if self.game_paused:
            return
        
        # Обновление игрового времени
        self.game_time += delta_time
        self.day_night_cycle = (self.game_time / 300.0) % 1.0  # 5 минут на цикл
        
        # Обновление игровых систем
        self._update_game_systems(delta_time)
        
        # Обновление сущностей
        self._update_entities(delta_time)
        
        # Обновление частиц
        self._update_particles(delta_time)
        
        # Обновление UI
        self._update_ui(delta_time)
        
        # Обновление камеры
        self._update_camera(delta_time)
    
    def _update_game_systems(self, delta_time: float):
        """Обновление игровых систем"""
        try:
            # Обновляем AI систему
            self.ai_manager.update_all_systems(delta_time)
            
            # Обновляем систему боя
            if 'combat' in self.systems and hasattr(self.systems['combat'], 'update_combat'):
                self.systems['combat'].update_combat(delta_time)
            
            # Обновляем систему крафтинга
            if 'crafting' in self.systems and hasattr(self.systems['crafting'], 'update_crafting'):
                self.systems['crafting'].update_crafting(delta_time)
                
        except Exception as e:
            logger.warning(f"Ошибка обновления игровых систем: {e}")
    
    def _update_entities(self, delta_time: float):
        """Обновление игровых сущностей"""
        for entity in self.entities:
            if entity['type'] == 'player':
                self._update_player_ai(entity, delta_time)  # Игрок управляется AI
            elif entity['type'] == 'npc':
                self._update_npc_ai(entity, delta_time)  # NPC управляются AI
            
            # Обновляем позицию Panda3D узла
            if entity.get('node'):
                entity['node'].setPos(entity['x'], entity['y'], entity['z'])
    
    def _update_player_ai(self, player: dict, delta_time: float):
        """Обновление игрока через AI"""
        # Получаем решение AI для игрока
        context = {
            'entities': self.entities,
            'delta_time': delta_time,
            'world_state': self._get_world_state()
        }
        decision = self.ai_manager.get_decision(player['id'], context)
        if decision:
            # AI принимает решение о движении
            self._execute_ai_decision(player, decision, delta_time)
    
    def _update_npc_ai(self, npc: dict, delta_time: float):
        """Обновление NPC через AI"""
        # AI уже обновляется в _update_game_systems
        # Здесь можно добавить дополнительную логику для NPC
        pass
    
    def _execute_ai_decision(self, entity: dict, decision: AIDecision, delta_time: float):
        """Выполнение решения AI для движения"""
        from ..systems.ai.ai_interface import ActionType
        
        if decision.action_type == ActionType.MOVE:
            # Движение к цели
            if decision.parameters and 'target_x' in decision.parameters and 'target_y' in decision.parameters:
                target_x = decision.parameters['target_x']
                target_y = decision.parameters['target_y']
                
                dx = target_x - entity['x']
                dy = target_y - entity['y']
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0.5:
                    # Нормализуем вектор движения
                    dx = dx / distance * entity['speed'] * delta_time
                    dy = dy / distance * entity['speed'] * delta_time
                    
                    entity['x'] += dx
                    entity['y'] += dy
        
        elif decision.action_type == ActionType.ATTACK:
            # Атака цели
            if decision.target:
                target_entity = next((e for e in self.entities if e.get('id') == decision.target), None)
                if target_entity:
                    # Простая логика атаки
                    dx = target_entity['x'] - entity['x']
                    dy = target_entity['y'] - entity['y']
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance <= 3:  # Дистанция атаки
                        # Наносим урон
                        if 'health' in target_entity:
                            target_entity['health'] = max(0, target_entity['health'] - 10)
        
        elif decision.action_type == ActionType.EXPLORE:
            # Исследование
            if random.random() < 0.1:  # 10% шанс изменить направление
                entity['target_x'] = random.uniform(-10, 10)
                entity['target_y'] = random.uniform(-10, 10)
                entity['target_z'] = 0
    
    def _find_nearest_enemy(self, entity: dict) -> Optional[dict]:
        """Поиск ближайшего врага"""
        enemies = [e for e in self.entities if e['type'] == 'npc' and e != entity]
        if not enemies:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for enemy in enemies:
            dx = enemy['x'] - entity['x']
            dy = enemy['y'] - entity['y']
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < min_distance:
                min_distance = distance
                nearest = enemy
        
        return nearest
    
    def _get_world_state(self) -> Dict[str, Any]:
        """Получение состояния игрового мира"""
        return {
            'entity_count': len(self.entities),
            'player_count': len([e for e in self.entities if e['type'] == 'player']),
            'npc_count': len([e for e in self.entities if e['type'] == 'npc']),
            'world_bounds': {'x': (-20, 20), 'y': (-20, 20), 'z': (-10, 10)}
        }
    
    def _update_particles(self, delta_time: float):
        """Обновление частиц"""
        # Удаляем устаревшие частицы
        self.particles = [p for p in self.particles if p.get('life', 0) > 0]
        
        # Обновляем оставшиеся частицы
        for particle in self.particles:
            particle['life'] -= delta_time
            particle['x'] += particle.get('vx', 0) * delta_time
            particle['y'] += particle.get('vy', 0) * delta_time
            particle['z'] += particle.get('vz', 0) * delta_time
    
    def _update_ui(self, delta_time: float):
        """Обновление UI"""
        # Обновление полоски здоровья
        player = next((e for e in self.entities if e['type'] == 'player'), None)
        if player and self.health_bar_text:
            health = player.get('health', 100)
            max_health = player.get('max_health', 100)
            self.health_bar_text.setText(f"HP: {health}/{max_health}")
        
        # Обновление информации об AI
        if player and self.ai_info_text:
            # Получаем информацию о состоянии AI
            context = {'entities': self.entities, 'delta_time': delta_time}
            decision = self.ai_manager.get_decision(player['id'], context)
            if decision:
                self.ai_info_text.setText(f"AI: {decision.action_type.value} (conf: {decision.confidence:.2f})")
            else:
                self.ai_info_text.setText("AI: No decision")
        
        # Обновление отладочной информации
        if self.debug_text and self.show_debug:
            entities_count = len(self.entities)
            particles_count = len(self.particles)
            self.debug_text.setText(f"Debug: Entities={entities_count}, Particles={particles_count}")
    
    def _update_camera(self, delta_time: float):
        """Обновление изометрической камеры"""
        if not self.camera:
            return
            
        # Находим игрока для следования
        player = next((e for e in self.entities if e['type'] == 'player'), None)
        if player:
            # Плавно следуем за игроком
            self.camera.follow_entity(player, smooth=0.05)
    
    def render(self, render_node):
        """Отрисовка игровой сцены"""
        # Panda3D автоматически отрисовывает сцену
        # Здесь можно добавить дополнительную логику рендеринга
        pass
    
    def handle_event(self, event):
        """Обработка событий"""
        # Обработка событий Panda3D
        pass
    
    def cleanup(self):
        """Очистка игровой сцены"""
        logger.info("Очистка игровой сцены Panda3D...")
        
        # Очистка AI системы
        self.ai_manager.cleanup()
        
        # Очищаем системы
        for system in self.systems.values():
            if hasattr(system, 'cleanup'):
                system.cleanup()
        
        # Очищаем Panda3D узлы
        if self.scene_root:
            self.scene_root.removeNode()
        
        # Очищаем UI элементы
        if self.health_bar_text:
            self.health_bar_text.destroy()
        if self.ai_info_text:
            self.ai_info_text.destroy()
        if self.debug_text:
            self.debug_text.destroy()
        
        logger.info("Игровая сцена Panda3D очищена")

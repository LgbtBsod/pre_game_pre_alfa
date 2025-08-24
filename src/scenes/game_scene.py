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
    CraftingSystem, InventorySystem,
    AIEntity, EntityType, MemoryType,
    genome_manager, emotion_manager
)
from ..systems.ai.ai_interface import AISystemFactory, AISystemManager, AIDecision
from ..systems.effects.effect_system import OptimizedTriggerSystem, EffectStatistics, TriggerType
from ..systems.items.item_system import ItemFactory
from ..systems.skills.skill_system import SkillTree
from ..systems.content.content_generator import ContentGenerator

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
            
            # Регистрируем сущности в AI системе после создания
            self._register_entities_in_ai()
            
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
        # Используем корневые узлы, созданные менеджером сцен
        if self.scene_root:
            self.entities_root = self.scene_root.attachNewNode("entities")
            self.particles_root = self.scene_root.attachNewNode("particles")
            self.ui_root = self.scene_root.attachNewNode("ui") # Создаем корневой узел UI
        else:
            # Fallback если корневые узлы не созданы
            if hasattr(self, 'scene_manager') and self.scene_manager:
                self.scene_root = self.scene_manager.render_node.attachNewNode("game_scene")
                self.entities_root = self.scene_root.attachNewNode("entities")
                self.particles_root = self.scene_root.attachNewNode("particles")
                self.ui_root = self.scene_root.attachNewNode("ui") # Создаем корневой узел UI
    
    def _initialize_game_systems(self):
        """Инициализация игровых систем"""
        try:
            # Создаем системы
            self.systems['evolution'] = EvolutionSystem()
            self.systems['combat'] = CombatSystem()
            self.systems['crafting'] = CraftingSystem()
            self.systems['inventory'] = InventorySystem()
            
            # Инициализируем системы эффектов и предметов
            from ..systems.effects.effect_system import OptimizedTriggerSystem, EffectStatistics
            from ..systems.items.item_system import ItemFactory
            from ..systems.skills.skill_system import SkillTree
            from ..systems.content.content_generator import ContentGenerator
            
            # Система триггеров эффектов
            self.trigger_system = OptimizedTriggerSystem()
            
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
            # Создаем тестового игрока с системами
            self._create_test_player()
            
            # Создаем тестовых NPC с системами
            self._create_test_npcs()
            
            # Создаем тестовые предметы и скиллы
            self._create_test_items_and_skills()
            
            # Создаем UI элементы
            self._create_ui_elements()
            
            logger.debug("Начальные объекты созданы")
            
        except Exception as e:
            logger.warning(f"Не удалось создать некоторые объекты: {e}")
    
    def _create_test_player(self):
        """Создание тестового игрока с AI-управлением и системами"""
        from ..systems.effects.effect_system import EffectStatistics
        from ..systems.skills.skill_system import SkillTree
        from ..systems.content.content_generator import ContentGenerator
        from ..systems.items.item_system import ItemFactory
        
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
            'mana': 100,
            'max_mana': 100,
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
            'node': None,  # Panda3D узел
            
            # Системы
            'effect_statistics': EffectStatistics(),
            'skill_tree': SkillTree('player_1'),
            'equipment': {},
            'inventory': [],
            
            # AI Entity система
            'ai_entity': AIEntity('player_1', EntityType.PLAYER, save_slot='default'),
            
            # Геном
            'genome': genome_manager.create_genome('player_1'),
            
            # Система эмоций
            'emotion_system': emotion_manager.get_emotion_system('player_1')
        }
        
        # Создаем Panda3D узел для игрока
        if self.entities_root:
            player['node'] = self._create_entity_node(player)
        
        # Применяем бонусы от генома к характеристикам
        if 'genome' in player:
            stat_boosts = player['genome'].get_stat_boosts()
            for stat, boost in stat_boosts.items():
                if stat in player['stats']:
                    player['stats'][stat] += int(boost * 10)  # Увеличиваем характеристики
                if stat == 'health' and 'max_health' in player:
                    player['max_health'] += int(boost * 20)
                    player['health'] = player['max_health']
                if stat == 'mana' and 'max_mana' in player:
                    player['max_mana'] += int(boost * 10)
                    player['mana'] = player['max_mana']
        
        # Устанавливаем очки скиллов
        player['skill_tree'].skill_points = 10
        
        # Добавляем базовые скиллы
        # Используем ContentGenerator для создания скиллов
        content_gen = ContentGenerator()
        fireball_skill = content_gen.generate_unique_skill('default', 1, 'combat')
        heal_skill = content_gen.generate_unique_skill('default', 1, 'utility')
        player['skill_tree'].add_skill(fireball_skill)
        player['skill_tree'].add_skill(heal_skill)
        
        # Пытаемся изучить скиллы (с учетом генома)
        if player['skill_tree'].learn_skill("Огненный шар", player):
            logger.info("Игрок изучил Огненный шар")
        else:
            logger.info("Игрок не смог изучить Огненный шар (ограничения генома)")
        
        if player['skill_tree'].learn_skill("Исцеление", player):
            logger.info("Игрок изучил Исцеление")
        else:
            logger.info("Игрок не смог изучить Исцеление (ограничения генома)")
        
        # Добавляем предметы
        fire_sword = ItemFactory.create_enhanced_fire_sword()
        lightning_ring = ItemFactory.create_lightning_ring()
        player['equipment']['main_hand'] = fire_sword
        player['equipment']['ring'] = lightning_ring
        player['inventory'].append(fire_sword)
        player['inventory'].append(lightning_ring)
        
        # Регистрируем эффекты предметов в системе триггеров
        self.trigger_system.register_item_effects(fire_sword)
        self.trigger_system.register_item_effects(lightning_ring)
        
        self.entities.append(player)
        
        logger.debug("Тестовый игрок создан с системами")
    
    def _create_test_npcs(self):
        """Создание тестовых NPC с AI и системами"""
        from ..systems.effects.effect_system import EffectStatistics
        from ..systems.skills.skill_system import SkillTree
        from ..systems.content.content_generator import ContentGenerator
        from ..systems.items.item_system import ItemFactory
        
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
                'mana': 50,
                'max_mana': 50,
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
                'node': None,
                
                # Системы
                'effect_statistics': EffectStatistics(),
                'skill_tree': SkillTree(config['id']),
                'equipment': {},
                'inventory': [],
                
                # AI Entity система
                'ai_entity': AIEntity(config['id'], EntityType.ENEMY if config['ai_personality'] == 'aggressive' else EntityType.NPC, save_slot='default'),
                
                # Геном
                'genome': genome_manager.create_genome(config['id']),
                
                # Система эмоций
                'emotion_system': emotion_manager.get_emotion_system(config['id'])
            }
            
            # Создаем Panda3D узел для NPC
            if self.entities_root:
                npc['node'] = self._create_entity_node(npc)
            
            # Применяем бонусы от генома к характеристикам
            if 'genome' in npc:
                stat_boosts = npc['genome'].get_stat_boosts()
                for stat, boost in stat_boosts.items():
                    if stat in npc['stats']:
                        npc['stats'][stat] += int(boost * 8)  # Увеличиваем характеристики
                    if stat == 'health' and 'max_health' in npc:
                        npc['max_health'] += int(boost * 15)
                        npc['health'] = npc['max_health']
                    if stat == 'mana' and 'max_mana' in npc:
                        npc['max_mana'] += int(boost * 8)
                        npc['mana'] = npc['max_mana']
            
            # Устанавливаем очки скиллов
            npc['skill_tree'].skill_points = 5
            
            # Добавляем скиллы в зависимости от личности
            if config['ai_personality'] == 'aggressive':
                # Используем ContentGenerator для создания скиллов
                content_gen = ContentGenerator()
                fireball_skill = content_gen.generate_unique_skill('default', 1, 'combat')
                npc['skill_tree'].add_skill(fireball_skill)
                if npc['skill_tree'].learn_skill("Огненный шар", npc):
                    logger.info(f"NPC {config['id']} изучил Огненный шар")
                else:
                    logger.info(f"NPC {config['id']} не смог изучить Огненный шар (ограничения генома)")
            elif config['ai_personality'] == 'defensive':
                # Используем ContentGenerator для создания скиллов
                content_gen = ContentGenerator()
                heal_skill = content_gen.generate_unique_skill('default', 1, 'utility')
                npc['skill_tree'].add_skill(heal_skill)
                if npc['skill_tree'].learn_skill("Исцеление", npc):
                    logger.info(f"NPC {config['id']} изучил Исцеление")
                else:
                    logger.info(f"NPC {config['id']} не смог изучить Исцеление (ограничения генома)")
            
            self.entities.append(npc)
            
        logger.debug(f"Создано {len(npc_configs)} тестовых NPC с системами")
    
    def _create_test_items_and_skills(self):
        """Создание тестовых предметов и скиллов"""
        from ..systems.items.item_system import ItemFactory
        from ..systems.content.content_generator import ContentGenerator
        
        # Создаем тестовые предметы
        self.test_items = {
            'fire_sword': ItemFactory.create_enhanced_fire_sword(),
            'lightning_ring': ItemFactory.create_lightning_ring()
        }
        
        # Создаем тестовые скиллы
        content_gen = ContentGenerator()
        self.test_skills = {
            'fireball': content_gen.generate_unique_skill('default', 1, 'combat'),
            'heal': content_gen.generate_unique_skill('default', 1, 'utility')
        }
        
        logger.debug("Тестовые предметы и скиллы созданы")
    
    def _register_entities_in_ai(self):
        """Регистрация всех сущностей в AI системе"""
        try:
            for entity in self.entities:
                entity_id = entity.get('id')
                if entity_id:
                    memory_group = 'player' if entity['type'] == 'player' else 'npc'
                    self.ai_manager.register_entity(entity_id, entity, "default", memory_group)
                    logger.debug(f"Сущность '{entity_id}' зарегистрирована в AI системе")
            
            logger.info(f"Зарегистрировано {len(self.entities)} сущностей в AI системе")
            
        except Exception as e:
            logger.error(f"Ошибка регистрации сущностей в AI системе: {e}")
    
    def _create_entity_node(self, entity: Dict[str, Any]) -> NodePath:
        """Создание Panda3D узла для сущности с проверкой ассетов"""
        # Проверяем наличие ассетов
        asset_path = entity.get('asset_path', '')
        if asset_path and self._asset_exists(asset_path):
            # Загружаем модель из ассета
            try:
                model = self.loader.loadModel(asset_path)
                if model:
                    np = self.entities_root.attachNewNode(model)
                    np.setPos(entity['x'], entity['y'], entity['z'])
                    np.setScale(entity.get('scale', 1))
                    return np
            except Exception as e:
                logger.warning(f"Не удалось загрузить ассет {asset_path}: {e}")
        
        # Если ассетов нет или не удалось загрузить, создаем базовую геометрию
        return self._create_basic_geometry(entity)
    
    def _asset_exists(self, asset_path: str) -> bool:
        """Проверка существования ассета"""
        import os
        return os.path.exists(asset_path)
    
    def _create_basic_geometry(self, entity: Dict[str, Any]) -> NodePath:
        """Создание базовой геометрии для сущности"""
        from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
        from panda3d.core import GeomVertexWriter, GeomTriangles, GeomNode
        
        entity_type = entity.get('type', 'unknown')
        
        # Выбираем геометрию в зависимости от типа сущности
        if entity_type == 'player':
            return self._create_player_geometry(entity)
        elif entity_type == 'npc':
            return self._create_npc_geometry(entity)
        else:
            return self._create_cube_geometry(entity)
    
    def _create_player_geometry(self, entity: Dict[str, Any]) -> NodePath:
        """Создание геометрии игрока (цилиндр с неоновым эффектом)"""
        from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
        from panda3d.core import GeomVertexWriter, GeomTriangles, GeomNode
        
        # Создаем цилиндр для игрока
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('player_cylinder', format, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        # Параметры цилиндра
        radius = entity.get('width', 0.5) / 2
        height = entity.get('height', 1.0)
        segments = 12
        
        # Создаем вершины цилиндра
        vertices = []
        colors = []
        
        # Верхняя крышка
        for i in range(segments):
            angle = (i / segments) * 2 * 3.14159
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append((x, y, height/2))
            colors.append((0, 255, 255, 1))  # Неоновый голубой для игрока
        
        # Нижняя крышка
        for i in range(segments):
            angle = (i / segments) * 2 * 3.14159
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append((x, y, -height/2))
            colors.append((0, 255, 255, 1))
        
        # Добавляем вершины
        for v, c in zip(vertices, colors):
            vertex.addData3(*v)
            color.addData4(*c)
        
        # Создаем треугольники
        prim = GeomTriangles(Geom.UHStatic)
        
        # Боковые грани цилиндра
        for i in range(segments):
            next_i = (i + 1) % segments
            
            # Первый треугольник
            prim.addVertices(i, next_i, i + segments)
            prim.addVertices(next_i, next_i + segments, i + segments)
        
        # Верхняя и нижняя крышки
        for i in range(1, segments - 1):
            # Верхняя крышка
            prim.addVertices(0, i, i + 1)
            # Нижняя крышка
            prim.addVertices(segments, segments + i + 1, segments + i)
        
        # Создаем геометрию
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        # Создаем узел
        node = GeomNode('player_cylinder')
        node.addGeom(geom)
        
        # Создаем NodePath и позиционируем
        np = self.entities_root.attachNewNode(node)
        np.setPos(entity['x'], entity['y'], entity['z'])
        
        # Добавляем неоновый эффект
        np.setTransparency(True)
        np.setColor(0, 1, 1, 0.8)  # Неоновый голубой
        
        return np
        for i in range(segments):
            i1 = i
            i2 = (i + 1) % segments
            i3 = i + segments
            i4 = (i + 1) % segments + segments
            
            # Первый треугольник
            prim.addVertices(i1, i2, i3)
            prim.closePrimitive()
            # Второй треугольник
            prim.addVertices(i2, i4, i3)
            prim.closePrimitive()
        
        # Создаем геометрию
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        
        # Создаем узел
        node = GeomNode('player')
        node.addGeom(geom)
        
        # Создаем NodePath и устанавливаем позицию
        np = self.entities_root.attachNewNode(node)
        np.setPos(entity['x'], entity['y'], entity['z'])
        
        return np
    
    def _create_npc_geometry(self, entity: Dict[str, Any]) -> NodePath:
        """Создание геометрии NPC (куб с неоновым эффектом)"""
        from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
        from panda3d.core import GeomVertexWriter, GeomTriangles, GeomNode
        
        # Создаем куб для NPC
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('npc_cube', format, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')
        
        # Вершины куба
        size = entity.get('width', 0.8) / 2
        vertices = [
            (-size, -size, -size), (size, -size, -size), (size, size, -size), (-size, size, -size),
            (-size, -size, size), (size, -size, size), (size, size, size), (-size, size, size)
        ]
        
        # Цвет в зависимости от личности NPC
        personality = entity.get('ai_personality', 'neutral')
        if personality == 'aggressive':
            npc_color = (255, 100, 100, 1)  # Неоновый красный
        elif personality == 'defensive':
            npc_color = (100, 255, 100, 1)  # Неоновый зеленый
        else:
            npc_color = (255, 255, 100, 1)  # Неоновый желтый
        
        # Добавляем вершины
        for v in vertices:
            vertex.addData3(*v)
            color.addData4(npc_color)
        
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
        node = GeomNode('npc')
        node.addGeom(geom)
        
        # Создаем NodePath и устанавливаем позицию
        np = self.entities_root.attachNewNode(node)
        np.setPos(entity['x'], entity['y'], entity['z'])
        
        return np
    
    def _create_cube_geometry(self, entity: Dict[str, Any]) -> NodePath:
        """Создание базовой кубической геометрии"""
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
        # Используем корневой узел UI сцены
        parent_node = self.ui_root if self.ui_root else None
        
        # Современный неоновый заголовок
        self.game_title_text = OnscreenText(
            text="🎮 GAME SESSION",
            pos=(0, 0.9),
            scale=0.06,
            fg=(0, 255, 255, 1),  # Неоновый голубой
            align=TextNode.ACenter,
            mayChange=False,
            parent=parent_node,
            shadow=(0, 0, 0, 0.8),
            shadowOffset=(0.01, 0.01)
        )
        
        # Полоска здоровья
        self.health_bar_text = OnscreenText(
            text="❤️ HP: 100/100",
            pos=(-1.3, 0.7),
            scale=0.045,
            fg=(255, 100, 100, 1),  # Неоновый красный
            align=TextNode.ALeft,
            mayChange=True,
            parent=parent_node,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01)
        )
        
        # Полоска маны
        self.mana_bar_text = OnscreenText(
            text="🔮 MP: 100/100",
            pos=(-1.3, 0.6),
            scale=0.045,
            fg=(100, 100, 255, 1),  # Неоновый синий
            align=TextNode.ALeft,
            mayChange=True,
            parent=parent_node,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01)
        )
        
        # Информация об AI
        self.ai_info_text = OnscreenText(
            text="🤖 AI: Initializing...",
            pos=(-1.3, 0.5),
            scale=0.035,
            fg=(0, 255, 255, 1),  # Неоновый голубой
            align=TextNode.ALeft,
            mayChange=True,
            parent=parent_node,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01)
        )
        
        # Информация о скиллах
        self.skills_info_text = OnscreenText(
            text="⚡ Skills: None",
            pos=(-1.3, 0.4),
            scale=0.035,
            fg=(255, 100, 255, 1),  # Неоновый розовый
            align=TextNode.ALeft,
            mayChange=True,
            parent=parent_node,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01)
        )
        
        # Информация о предметах
        self.items_info_text = OnscreenText(
            text="🎒 Items: None",
            pos=(-1.3, 0.3),
            scale=0.035,
            fg=(255, 255, 100, 1),  # Неоновый желтый
            align=TextNode.ALeft,
            mayChange=True,
            parent=parent_node,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01)
        )
        
        # Информация об эффектах
        self.effects_info_text = OnscreenText(
            text="✨ Effects: None",
            pos=(-1.3, 0.2),
            scale=0.035,
            fg=(100, 255, 100, 1),  # Неоновый зеленый
            align=TextNode.ALeft,
            mayChange=True,
            parent=parent_node,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01)
        )
        
        # Информация о геноме
        self.genome_info_text = OnscreenText(
            text="🧬 Genome: Loading...",
            pos=(-1.3, 0.1),
            scale=0.035,
            fg=(255, 100, 255, 1),  # Неоновый фиолетовый
            align=TextNode.ALeft,
            mayChange=True,
            parent=parent_node,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01)
        )
        
        # Полоска эмоций
        self.emotion_bar_text = OnscreenText(
            text="😊 Emotions: Neutral",
            pos=(-1.3, 0.0),
            scale=0.035,
            fg=(255, 150, 100, 1),  # Неоновый оранжевый
            align=TextNode.ALeft,
            mayChange=True,
            parent=parent_node,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01)
        )
        
        # Отладочная информация
        self.debug_text = OnscreenText(
            text="🐛 Debug: Enabled",
            pos=(-1.3, -0.1),
            scale=0.035,
            fg=(255, 150, 50, 1),  # Неоновый оранжевый
            align=TextNode.ALeft,
            mayChange=True,
            parent=parent_node,
            shadow=(0, 0, 0, 0.6),
            shadowOffset=(0.01, 0.01)
        )
        
        # Кнопки эмоций
        self.emotion_buttons = {}
        emotion_configs = [
            ("joy", "😊", (0.8, 0.8, 0.2, 1)),      # Желтый
            ("sadness", "😢", (0.2, 0.2, 0.8, 1)),  # Синий
            ("anger", "😠", (0.8, 0.2, 0.2, 1)),    # Красный
            ("fear", "😨", (0.8, 0.2, 0.8, 1)),     # Фиолетовый
            ("surprise", "😲", (0.2, 0.8, 0.8, 1)), # Голубой
            ("disgust", "🤢", (0.2, 0.8, 0.2, 1))   # Зеленый
        ]
        
        for i, (emotion_type, emoji, color) in enumerate(emotion_configs):
            button = DirectButton(
                text=emoji,
                pos=(0.8 + i * 0.15, 0, 0.8),
                scale=0.04,
                frameColor=color,
                text_fg=(1, 1, 1, 1),
                relief=1,
                command=self._apply_emotion,
                extraArgs=[emotion_type],
                parent=parent_node
            )
            self.emotion_buttons[emotion_type] = button
        
        logger.debug("UI элементы Panda3D созданы")
    
    def _apply_emotion(self, emotion_type: str):
        """Применяет эмоцию к игроку"""
        player = next((e for e in self.entities if e['type'] == 'player'), None)
        if player and 'emotion_system' in player:
            from ..systems import EmotionType
            
            # Преобразуем строку в EmotionType
            emotion_enum = EmotionType(emotion_type)
            
            # Применяем эмоцию
            player['emotion_system'].add_emotion(
                emotion_enum,
                intensity=0.8,  # Высокая интенсивность
                duration=30.0,  # 30 секунд
                source="player_input"
            )
            
            logger.info(f"Игрок применил эмоцию: {emotion_type}")
    
    def update(self, delta_time: float):
        """Обновление игровой сцены"""
        if self.game_paused:
            return
        
        # Обновление игрового времени
        self.game_time += delta_time
        self.day_night_cycle = (self.game_time / 300.0) % 1.0  # 5 минут на цикл
        
        # Обновление игровых систем
        self._update_game_systems(delta_time)
        
        # Обновление системы эмоций
        emotion_manager.update_all(delta_time)
        
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
                
            # Обновляем систему эффектов
            if 'evolution' in self.systems and hasattr(self.systems['evolution'], 'update_effects'):
                self.systems['evolution'].update_effects(delta_time)
                self.trigger_system.update(delta_time)
            
        except Exception as e:
            logger.warning(f"Ошибка обновления игровых систем: {e}")
    
    def _update_entities(self, delta_time: float):
        """Обновление игровых сущностей"""
        for entity in self.entities:
            # Обновляем системы сущности
            if 'skill_tree' in entity:
                entity['skill_tree'].update(delta_time)
            
            if entity['type'] == 'player':
                self._update_player_ai(entity, delta_time)  # Игрок управляется AI
            elif entity['type'] == 'npc':
                self._update_npc_ai(entity, delta_time)  # NPC управляются AI
            
            # Обновляем позицию Panda3D узла
            if entity.get('node'):
                entity['node'].setPos(entity['x'], entity['y'], entity['z'])
    
    def _update_player_ai(self, player: dict, delta_time: float):
        """Обновление игрока через AI с использованием скиллов и предметов"""
        # Получаем решение AI для игрока
        context = {
            'entities': self.entities,
            'delta_time': delta_time,
            'world_state': self._get_world_state(),
            'skills': player.get('skill_tree'),
            'equipment': player.get('equipment', {}),
            'ai_entity': player.get('ai_entity')
        }
        
        decision = self.ai_manager.get_decision(player['id'], context)
        if decision:
            # AI принимает решение о движении и использовании скиллов
            self._execute_ai_decision(player, decision, delta_time)
    
    def _update_npc_ai(self, npc: dict, delta_time: float):
        """Обновление NPC через AI с использованием скиллов"""
        # Получаем решение AI для NPC
        context = {
            'entities': self.entities,
            'delta_time': delta_time,
            'world_state': self._get_world_state(),
            'skills': npc.get('skill_tree'),
            'equipment': npc.get('equipment', {}),
            'ai_entity': npc.get('ai_entity')
        }
        
        decision = self.ai_manager.get_decision(npc['id'], context)
        if decision:
            # AI принимает решение о движении и использовании скиллов
            self._execute_ai_decision(npc, decision, delta_time)
    
    def _execute_ai_decision(self, entity: dict, decision: AIDecision, delta_time: float):
        """Выполнение решения AI для движения и скиллов"""
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
            # Атака цели с использованием скиллов и предметов
            if decision.target:
                target_entity = next((e for e in self.entities if e.get('id') == decision.target), None)
                if target_entity:
                    # Проверяем, есть ли готовые скиллы
                    if 'skill_tree' in entity:
                        recommended_skill = entity['skill_tree'].get_ai_recommended_skill(entity, {
                            'target': target_entity,
                            'entities': self.entities
                        })
                        
                        if recommended_skill and recommended_skill.can_use(entity, target_entity):
                            # Используем скилл
                            context = {'target': target_entity, 'entities': self.entities}
                            recommended_skill.use(entity, target_entity, context)
                            
                            # Записываем в память AI
                            if 'ai_entity' in entity:
                                ai_entity = entity['ai_entity']
                                ai_entity.add_memory(
                                    MemoryType.SKILL_USAGE,
                                    {'skill_name': recommended_skill.name, 'target': target_entity['id']},
                                    f"use_skill_{recommended_skill.name}",
                                    {'damage_dealt': recommended_skill.damage if hasattr(recommended_skill, 'damage') else 0},
                                    True
                                )
                            
                            # Активируем триггеры эффектов
                            self.trigger_system.trigger(
                                TriggerType.ON_SPELL_CAST, 
                                entity, 
                                target_entity, 
                                context
                            )
                        else:
                            # Обычная атака
                            dx = target_entity['x'] - entity['x']
                            dy = target_entity['y'] - entity['y']
                            distance = math.sqrt(dx*dx + dy*dy)
                            
                            if distance <= 3:  # Дистанция атаки
                                # Наносим урон
                                if 'health' in target_entity:
                                    damage = 10
                                    target_entity['health'] = max(0, target_entity['health'] - damage)
                                    
                                    # Записываем в память AI
                                    if 'ai_entity' in entity:
                                        ai_entity = entity['ai_entity']
                                        ai_entity.add_memory(
                                            MemoryType.COMBAT,
                                            {'target': target_entity['id'], 'distance': distance},
                                            'physical_attack',
                                            {'damage_dealt': damage, 'target_health_remaining': target_entity['health']},
                                            True
                                        )
                                    
                                    # Эволюционируем геном
                                    if 'genome' in entity:
                                        experience_gained = damage * 0.1  # Опыт пропорционален урону
                                        if genome_manager.evolve_genome(entity['id'], experience_gained):
                                            logger.info(f"Геном {entity['id']} эволюционировал после атаки")
                                    
                                    # Активируем триггеры эффектов оружия
                                    context = {'damage_dealt': damage, 'damage_type': 'physical'}
                                    self.trigger_system.trigger(
                                        TriggerType.ON_HIT, 
                                        entity, 
                                        target_entity, 
                                        context
                                    )
        
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
        
        # Обновление полоски маны
        if player and self.mana_bar_text:
            mana = player.get('mana', 100)
            max_mana = player.get('max_mana', 100)
            self.mana_bar_text.setText(f"MP: {mana}/{max_mana}")
        
        # Обновление информации об AI
        if player and self.ai_info_text:
            # Получаем информацию о состоянии AI
            context = {'entities': self.entities, 'delta_time': delta_time}
            decision = self.ai_manager.get_decision(player['id'], context)
            
            # Получаем информацию о памяти AI
            ai_entity = player.get('ai_entity')
            if ai_entity:
                memory_summary = ai_entity.get_memory_summary()
                generation_info = f"Gen: {memory_summary['current_generation']}"
                experience_info = f"Exp: {memory_summary['total_experience']:.1f}"
                success_rate = f"Success: {memory_summary['success_rate']:.1%}"
                
                if decision:
                    self.ai_info_text.setText(f"AI: {decision.action_type.value} | {generation_info} | {experience_info} | {success_rate}")
                else:
                    self.ai_info_text.setText(f"AI: No decision | {generation_info} | {experience_info} | {success_rate}")
            else:
                if decision:
                    self.ai_info_text.setText(f"AI: {decision.action_type.value} (conf: {decision.confidence:.2f})")
                else:
                    self.ai_info_text.setText("AI: No decision")
        
        # Обновление информации о скиллах
        if player and self.skills_info_text:
            skill_tree = player.get('skill_tree')
            if skill_tree:
                learned_skills = skill_tree.learned_skills
                ready_skills = [s for s in learned_skills if skill_tree.skills[s].can_use(player)]
                self.skills_info_text.setText(f"Skills: {len(ready_skills)}/{len(learned_skills)} ready")
            else:
                self.skills_info_text.setText("Skills: None")
        
        # Обновление информации о предметах
        if player and self.items_info_text:
            equipment = player.get('equipment', {})
            inventory = player.get('inventory', [])
            self.items_info_text.setText(f"Items: {len(equipment)} equipped, {len(inventory)} in inventory")
        
        # Обновление информации об эффектах
        if player and self.effects_info_text:
            effect_stats = player.get('effect_statistics')
            if effect_stats:
                total_triggers = sum(effect_stats.effect_triggers.values())
                self.effects_info_text.setText(f"Effects: {total_triggers} triggers")
            else:
                self.effects_info_text.setText("Effects: None")
        
        # Обновление информации о геноме
        if player and self.genome_info_text:
            genome = player.get('genome')
            if genome:
                generation = genome.generation
                mutations = genome.mutation_count
                evolution_potential = genome.get_evolution_potential()
                self.genome_info_text.setText(f"Genome: Gen{generation} Mut{mutations} Evo{evolution_potential:.1f}")
            else:
                self.genome_info_text.setText("Genome: None")
        
        # Обновление информации об эмоциях
        if player and self.emotion_bar_text:
            emotion_system = player.get('emotion_system')
            if emotion_system:
                emotion_summary = emotion_system.get_emotion_summary()
                dominant_emotion = emotion_summary['dominant_emotion']
                intensity = emotion_summary['dominant_intensity']
                
                # Эмодзи для эмоций
                emotion_emojis = {
                    'joy': '😊',
                    'sadness': '😢',
                    'anger': '😠',
                    'fear': '😨',
                    'surprise': '😲',
                    'disgust': '🤢',
                    'neutral': '😐'
                }
                
                emoji = emotion_emojis.get(dominant_emotion, '😐')
                self.emotion_bar_text.setText(f"{emoji} Emotions: {dominant_emotion.title()} ({intensity:.1f})")
            else:
                self.emotion_bar_text.setText("😐 Emotions: None")
        
        # Обновление отладочной информации
        if self.debug_text and self.show_debug:
            entities_count = len(self.entities)
            particles_count = len(self.particles)
            self.debug_text.setText(f"Debug: Entities={entities_count}, Particles={particles_count}")
        
        # Проверяем смерть сущностей и завершаем поколения
        self._check_entity_deaths()
    
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
        if self.game_title_text:
            self.game_title_text.destroy()
        if self.health_bar_text:
            self.health_bar_text.destroy()
        if self.mana_bar_text:
            self.mana_bar_text.destroy()
        if self.ai_info_text:
            self.ai_info_text.destroy()
        if self.skills_info_text:
            self.skills_info_text.destroy()
        if self.items_info_text:
            self.items_info_text.destroy()
        if self.effects_info_text:
            self.effects_info_text.destroy()
        if self.genome_info_text:
            self.genome_info_text.destroy()
        if self.emotion_bar_text:
            self.emotion_bar_text.destroy()
        
        # Уничтожаем кнопки эмоций
        for button in self.emotion_buttons.values():
            if button:
                button.destroy()
        
        if self.debug_text:
            self.debug_text.destroy()
        
        logger.info("Игровая сцена Panda3D очищена")
    
    def _check_entity_deaths(self):
        """Проверка смерти сущностей и завершение поколений"""
        entities_to_remove = []
        
        for entity in self.entities:
            if entity.get('health', 0) <= 0 and 'ai_entity' in entity:
                # Сущность умерла, завершаем поколение
                ai_entity = entity['ai_entity']
                cause_of_death = "combat" if entity.get('last_damage_source') else "natural"
                
                # Завершаем поколение
                ai_entity.end_generation(
                    cause_of_death=cause_of_death,
                    final_stats={
                        'health': entity.get('health', 0),
                        'level': entity.get('level', 1),
                        'experience': entity.get('experience', 0),
                        'total_actions': ai_entity.stats['total_memories']
                    }
                )
                
                logger.info(f"Поколение завершено для {entity['id']}: {cause_of_death}")
                entities_to_remove.append(entity)
        
        # Удаляем мертвые сущности
        for entity in entities_to_remove:
            if entity['node']:
                entity['node'].removeNode()
            self.entities.remove(entity)
            
            # Создаем новую сущность того же типа (реинкарнация)
            if entity['type'] == 'player':
                self._create_test_player()
            elif entity['type'] == 'npc':
                self._create_test_npcs()

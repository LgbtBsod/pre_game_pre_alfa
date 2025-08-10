# -*- coding: utf-8 -*-
import random
import time
import json
import os
import sys
import logging
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
# Fix imports for Panda3D 1.10.15
from direct.gui.DirectGui import DirectButton, DirectLabel, DirectEntry, DirectOptionMenu
from direct.gui.OnscreenText import OnscreenText

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Aliases for compatibility
OnscreenButton = DirectButton

from panda3d.core import (
    WindowProperties, Vec3, Vec2, Point3, Point2, 
    TextNode, TransparencyAttrib, AntialiasAttrib,
    DirectionalLight, AmbientLight, Spotlight, PerspectiveLens,
    CollisionTraverser, CollisionHandlerQueue, CollisionNode,
    CollisionSphere, CollisionBox, CollisionRay, CollisionHandlerPusher,
    BitMask32, PandaNode, NodePath
)
from entities.player import Player
from entities.enemy import Enemy, EnemyGenerator
from entities.boss import Boss, BossGenerator
from entities.entity_factory import EntityFactory
from items.weapon import WeaponGenerator
from ai.cooperation import AICoordinator
from map.tiled_map import TiledMap
from ai.advanced_ai import AdvancedAIController
from ai.behavior_tree import BehaviorTree
from ai.memory import AIMemory, LearningController
from ai.emotion_genetics import EmotionGeneticSynthesizer
from ai.pattern_recognizer import PatternRecognizer
from ai.learning import PlayerLearning
from ai.decision_maker import PlayerDecisionMaker
from core.skill_system import SkillSystem
from core.leveling_system import LevelingSystem
from core.ai_update_scheduler import AIUpdateScheduler
from config.game_constants import (
    ENEMY_COUNT_EASY, ENEMY_COUNT_NORMAL, ENEMY_COUNT_HARD,
    ENEMY_LEVEL_MIN_EASY, ENEMY_LEVEL_MAX_EASY,
    ENEMY_LEVEL_MIN_NORMAL, ENEMY_LEVEL_MAX_NORMAL,
    ENEMY_LEVEL_MIN_HARD, ENEMY_LEVEL_MAX_HARD,
    BOSS_LEVEL_EASY, BOSS_LEVEL_NORMAL, BOSS_LEVEL_HARD
)
from utils.game_utils import (
    calculate_distance, normalize_vector, clamp_value, 
    interpolate_values, random_point_in_circle, rgb_to_hex, 
    format_time, format_number
)


class Panda3DGame(ShowBase):
    def __init__(self):
        super().__init__()
        
        # Game variables
        self.show_menu = True
        self.paused = False
        self.save_file = "save_game.json"
        self.running = True
        self.last_time = time.time()
        self.victory_shown = False
        self.reincarnation_count = 0
        self.generation_count = 0
        self.session_start_time = time.time()
        
        # Game settings
        self.settings = {
            "difficulty": "normal",
            "learning_rate": 1.0,
            "window_size": (1024, 768),
        }
        
        # Game objects
        self.player = None
        self.enemies = []
        self.boss = None
        self.tiled_map = None
        self.user_obstacles = set()
        self.chests = []
        
        # AI systems
        self.coordinator = None
        self.ai_scheduler = None
        self.skill_system = None
        self.leveling_system = None
        self.player_leveling = None
        self.player_ai_memory = None
        self.player_learning = None
        self.player_decision_maker = None
        self.emotion_synthesizer = None
        self.pattern_recognizer = None
        
        # UI elements
        self.menu_buttons = []
        self.settings_controls = []
        self.ui_elements = []
        
        # Load items
        self.load_items()
        
        # Setup lighting
        self.setup_lighting()
        
        # Setup camera
        self.setup_camera()
        
        # Setup window
        self.setup_window()
        
        # Setup collisions
        self.setup_collisions()
        
        # Setup controls
        self.setup_controls()
        
        # Show main menu
        self.show_main_menu()
        
        # Setup AI update scheduler
        self.ai_scheduler = AIUpdateScheduler()
        
        # Register AI systems
        if hasattr(self, 'ai_scheduler') and self.ai_scheduler:
            self.ai_scheduler.register_system("player_ai", self._update_player_ai, 0.1)
            self.ai_scheduler.register_system("enemy_ai", self._update_enemy_ai, 0.2)
            self.ai_scheduler.register_system("boss_ai", self._update_boss_ai, 0.3)
            self.ai_scheduler.register_system("coordination", self._update_coordination, 0.5)
            self.ai_scheduler.register_system("pattern_analysis", self._update_patterns, 1.0)
            self.ai_scheduler.register_system("emotion_synthesis", self._update_emotions, 2.0)
    
    def setup_window(self):
        """Setup game window"""
        props = WindowProperties()
        props.setTitle("Autonomous AI Survivor (Panda3D)")
        props.setSize(self.settings["window_size"][0], self.settings["window_size"][1])
        props.setCursorHidden(False)
        props.setIconFilename("icon.ico")  # if icon exists
        
        self.win.requestProperties(props)
        
        # Setup renderer
        self.render.setAntialias(AntialiasAttrib.MAuto)
    
    def setup_lighting(self):
        """Setup scene lighting"""
        # Main directional light
        dlight = DirectionalLight('dlight')
        dlight.setColor((0.8, 0.8, 0.8, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(45, -45, 0)
        self.render.setLight(dlnp)
        
        # Ambient light
        alight = AmbientLight('alight')
        alight.setColor((0.2, 0.2, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)
    
    def setup_camera(self):
        """Setup camera"""
        # Camera follows player
        self.camera.setPos(0, -50, 30)
        self.camera.lookAt(0, 0, 0)
        
        # Setup lens
        lens = self.cam.node().getLens()
        lens.setFov(60)
        lens.setNear(0.1)
        lens.setFar(1000)
    
    def setup_collisions(self):
        """Setup collision system"""
        self.cTrav = CollisionTraverser()
        self.cHandler = CollisionHandlerQueue()
        
        # Collision groups
        self.player_collision_group = BitMask32.bit(0)
        self.enemy_collision_group = BitMask32.bit(1)
        self.obstacle_collision_group = BitMask32.bit(2)
        self.chest_collision_group = BitMask32.bit(3)
    
    def load_items(self):
        """Load items from JSON"""
        try:
            with open("items/items.json", "r", encoding="utf-8") as f:
                self.items_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading items: {e}")
            self.items_data = {}
    
    def show_main_menu(self):
        """Show main menu"""
        self.clear_ui()
        
        # Title
        title = DirectLabel(
            text="Autonomous AI Survivor",
            pos=(0, 0, 0.7),
            scale=0.08,
            text_fg=(1, 0.84, 0, 1),  # Gold color
            text_align=TextNode.ACenter
        )
        self.ui_elements.append(title)
        
        # Menu buttons
        button_data = [
            ("New Game", self.start_new_game, (0.2, 0.6, 0.2, 1)),
            ("Load Game", self.load_game, (0.4, 0.4, 0.8, 1)),
            ("Settings", self.show_settings, (0.8, 0.6, 0.2, 1)),
            ("Exit", self.stop, (0.8, 0.2, 0.2, 1))
        ]
        
        for i, (text, command, color) in enumerate(button_data):
            button = OnscreenButton(
                text=text,
                pos=(0, 0, 0.3 - i * 0.15),
                scale=0.05,
                command=command,
                frameColor=color,
                text_fg=(1, 1, 1, 1),
                text_scale=0.8
            )
            self.ui_elements.append(button)
    
    def clear_ui(self):
        """Clear all UI elements"""
        for element in self.ui_elements:
            element.destroy()
        self.ui_elements.clear()
    
    def start_new_game(self):
        """Start new game"""
        self.show_menu = False
        self.clear_ui()
        self.init_game()
    
    def show_settings(self):
        """Show settings"""
        self.clear_ui()
        
        # Settings title
        title = DirectLabel(
            text="Settings",
            pos=(0, 0, 0.7),
            scale=0.06,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter
        )
        self.ui_elements.append(title)
        
        # Difficulty
        difficulty_label = DirectLabel(
            text="Difficulty:",
            pos=(-0.6, 0, 0.5),
            scale=0.04,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft
        )
        self.ui_elements.append(difficulty_label)
        
        difficulties = ["easy", "normal", "hard"]
        current_idx = max(0, difficulties.index(self.settings.get("difficulty", "normal")))
        
        if DirectOptionMenu:
            difficulty_menu = DirectOptionMenu(
                pos=(0, 0, 0.5),
                scale=0.04,
                items=difficulties,
                initialitem=current_idx,
                command=self.set_difficulty
            )
            self.ui_elements.append(difficulty_menu)
        else:
            # Alternative if DirectOptionMenu is not available
            difficulty_text = DirectLabel(
                text=f"Difficulty: {self.settings.get('difficulty', 'normal')}",
                pos=(0, 0, 0.5),
                scale=0.04,
                text_fg=(1, 1, 1, 1),
                text_align=TextNode.ACenter
            )
            self.ui_elements.append(difficulty_text)
        
        # Learning rate
        learning_label = DirectLabel(
            text="Learning Rate:",
            pos=(-0.6, 0, 0.3),
            scale=0.04,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft
        )
        self.ui_elements.append(learning_label)
        
        if DirectEntry:
            learning_entry = DirectEntry(
                pos=(0, 0, 0.3),
                scale=0.04,
                width=10,
                text=str(self.settings.get("learning_rate", 1.0)),
                command=self.set_learning_rate
            )
            self.ui_elements.append(learning_entry)
        else:
            # Alternative if DirectEntry is not available
            learning_text = DirectLabel(
                text=f"Speed: {self.settings.get('learning_rate', 1.0)}",
                pos=(0, 0, 0.3),
                scale=0.04,
                text_fg=(1, 1, 1, 1),
                text_align=TextNode.ACenter
            )
            self.ui_elements.append(learning_text)
        
        # Control buttons
        apply_button = OnscreenButton(
            text="Apply",
            pos=(-0.2, 0, -0.2),
            scale=0.04,
            command=self.apply_settings,
            frameColor=(0.2, 0.6, 0.2, 1)
        )
        self.ui_elements.append(apply_button)
        
        back_button = OnscreenButton(
            text="Back",
            pos=(0.2, 0, -0.2),
            scale=0.04,
            command=self.show_main_menu,
            frameColor=(0.6, 0.4, 0.2, 1)
        )
        self.ui_elements.append(back_button)
    
    def set_difficulty(self, difficulty):
        """Set difficulty"""
        self.settings["difficulty"] = difficulty
    
    def set_learning_rate(self, rate):
        """Set learning rate"""
        try:
            self.settings["learning_rate"] = float(rate)
        except ValueError:
            pass
    
    def apply_settings(self):
        """Apply settings"""
        # Add logic for applying settings here
        self.show_main_menu()
    
    def init_game(self):
        """Game initialization"""
        try:
            # User map
            self.tiled_map = TiledMap("map/map.json")
        except Exception as e:
            logger.error(f"Error initializing game map: {e}")
            self.tiled_map = None

        # Entities
        self.player = self._create_player()
        self.enemies = self._create_enemies()
        self.boss = self._create_boss()

        # Weapon for player
        if not self.player.equipment.get("weapon"):
            starter_weapon = WeaponGenerator.generate_weapon(1)
            self.player.equip_item(starter_weapon, "weapon")

        # AI coordinator
        self.coordinator = AICoordinator()
        for enemy in self.enemies:
            self.coordinator.register_entity(enemy, "enemy_group")
        if self.boss:
            self.coordinator.register_entity(self.boss, "boss_group")

        # Initialize AI modules
        self.skill_system = SkillSystem()
        self.leveling_system = LevelingSystem()
        
        # Initialize leveling system for player
        self.player_leveling = LevelingSystem(self.player)
        
        # Initialize AI for player
        self.player_ai_memory = AIMemory()
        self.player_learning = PlayerLearning(self.player, self.player_ai_memory)
        self.player_decision_maker = PlayerDecisionMaker(self.player, self.player_ai_memory)
        
        # Initialize emotions and patterns
        self.emotion_synthesizer = EmotionGeneticSynthesizer(self.player, {}, {}, {})
        self.pattern_recognizer = PatternRecognizer()
        
        # Register AI updates
        self.ai_scheduler.register_entity(self.player, self.player_learning.update)
        self.ai_scheduler.register_entity(self.player, self.player_decision_maker.update)
        
        # Initialize skills for player
        self.skill_system.add_skill_to_entity(self.player, "whirlwind_attack")
        self.skill_system.add_skill_to_entity(self.player, "healing_light")

        # Create 3D representations of entities
        self._create_3d_entities()
        
        # Setup controls
        self.setup_controls()
        
        # Start game loop
        self.taskMgr.add(self.game_loop, "game_loop")
    
    def _create_3d_entities(self):
        """Create 3D representations for entities"""
        # Create simple geometric shapes for entities
        
        # Player (blue cube)
        player_model = self.loader.loadModel("models/box")  # Load base model
        if not player_model:
            # If model not found, create a simple cube
            player_model = self.create_simple_cube()
        
        player_model.setColor(0, 0.4, 1, 1)  # Blue color
        player_model.setPos(self.player.position[0], self.player.position[1], 0)
        player_model.reparentTo(self.render)
        self.player.model = player_model
        
        # Enemies (red cubes)
        for enemy in self.enemies:
            enemy_model = self.loader.loadModel("models/box")
            if not enemy_model:
                enemy_model = self.create_simple_cube()
            
            if enemy.enemy_type == "warrior":
                enemy_model.setColor(1, 0.2, 0.2, 1)  # Red
            elif enemy.enemy_type == "archer":
                enemy_model.setColor(0.8, 0.2, 0.6, 1)  # Pink
            else:
                enemy_model.setColor(0.2, 0.6, 1, 1)  # Cyan
            
            enemy_model.setPos(enemy.position[0], enemy.position[1], 0)
            enemy_model.reparentTo(self.render)
            enemy.model = enemy_model
        
        # Boss (larger orange cube)
        if self.boss:
            boss_model = self.loader.loadModel("models/box")
            if not boss_model:
                boss_model = self.create_simple_cube()
            
            boss_model.setColor(1, 0.65, 0, 1)  # Orange
            boss_model.setScale(1.5)  # Larger than regular enemies
            boss_model.setPos(self.boss.position[0], self.boss.position[1], 0)
            boss_model.reparentTo(self.render)
            self.boss.model = boss_model
    
    def create_simple_cube(self):
        """Create a simple cube if models are not found"""
        # Create simple cube geometry
        from panda3d.core import GeomNode, Geom, GeomVertexData, GeomVertexFormat
        from panda3d.core import GeomVertexWriter, GeomTriangles, GeomNode
        
        # Cube vertices
        vertices = [
            -0.5, -0.5, -0.5,  # 0
             0.5, -0.5, -0.5,  # 1
             0.5,  0.5, -0.5,  # 2
            -0.5,  0.5, -0.5,  # 3
            -0.5, -0.5,  0.5,  # 4
             0.5, -0.5,  0.5,  # 5
             0.5,  0.5,  0.5,  # 6
            -0.5,  0.5,  0.5   # 7
        ]
        
        # Indices for triangles
        indices = [
            0, 1, 2, 0, 2, 3,  # front face
            1, 5, 6, 1, 6, 2,  # right face
            5, 4, 7, 5, 7, 6,  # back face
            4, 0, 3, 4, 3, 7,  # left face
            3, 2, 6, 3, 6, 7,  # top face
            4, 5, 1, 4, 1, 0   # bottom face
        ]
        
        # Create geometry
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData('cube', format, Geom.UHStatic)
        vertex = GeomVertexWriter(vdata, 'vertex')
        
        for i in range(0, len(vertices), 3):
            vertex.addData3(vertices[i], vertices[i+1], vertices[i+2])
        
        # Create triangles
        tris = GeomTriangles(Geom.UHStatic)
        for i in range(0, len(indices), 3):
            tris.addVertices(indices[i], indices[i+1], indices[i+2])
        
        tris.closePrimitive()
        
        # Create geometry
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        
        # Create node
        node = GeomNode('cube')
        node.addGeom(geom)
        
        return NodePath(node)
    
    def setup_controls(self):
        """Setup controls"""
        # Keyboard handling
        self.accept("escape", self.stop)
        self.accept("space", self.soft_restart)
        self.accept("p", self.toggle_pause)
        self.accept("1", lambda: self._use_skill("whirlwind_attack"))
        self.accept("2", lambda: self._use_skill("healing_light"))
        
        # Mouse handling
        self.accept("mouse1", self._on_left_click)
        self.accept("mouse3", self._on_right_click)
    
    def _create_player(self) -> Player:
        """Create player"""
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
            map_px_h = self.tiled_map.height * self.tiled_map.tileheight
            start_x = map_px_w // 2
            start_y = map_px_h // 2
        else:
            start_x = 0
            start_y = 0
        
        player = EntityFactory.create_player("player_ai", (start_x, start_y))
        player.learning_rate = float(self.settings.get("learning_rate", 1.0))
        
        # Set base health values via component
        combat_component = player.component_manager.get_component("CombatStatsComponent")
        if combat_component:
            combat_component.stats.max_health = 100
            combat_component.stats.health = 100
        
        return player
    
    def _create_enemies(self) -> list:
        """Create enemies"""
        enemy_list = []
        enemy_types = ["warrior", "archer", "mage"]
        
        map_width = self.tiled_map.width * self.tiled_map.tilewidth if self.tiled_map else 800
        map_height = self.tiled_map.height * self.tiled_map.tileheight if self.tiled_map else 600
        
        if map_width <= 200:
            map_width = 800
        if map_height <= 200:
            map_height = 600
        
        difficulty = self.settings.get("difficulty", "normal")
        if difficulty == "easy":
            num_enemies, lvl_min, lvl_max = ENEMY_COUNT_EASY, ENEMY_LEVEL_MIN_EASY, ENEMY_LEVEL_MAX_EASY
        elif difficulty == "hard":
            num_enemies, lvl_min, lvl_max = ENEMY_COUNT_HARD, ENEMY_LEVEL_MIN_HARD, ENEMY_LEVEL_MAX_HARD
        else:
            num_enemies, lvl_min, lvl_max = ENEMY_COUNT_NORMAL, ENEMY_LEVEL_MIN_NORMAL, ENEMY_LEVEL_MAX_NORMAL
        
        for _ in range(num_enemies):
            e = EntityFactory.create_enemy(level=random.randint(lvl_min, lvl_max))
            x = random.randint(-map_width//2, map_width//2)
            y = random.randint(-map_height//2, map_height//2)
            e.position = [x, y]
            e.player_ref = self.player
            enemy_list.append(e)
        
        return enemy_list
    
    def _create_boss(self) -> Boss:
        """Create boss"""
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            bx = self.tiled_map.width * self.tiled_map.tilewidth // 2 - 300
            by = 300
        else:
            bx, by = 300, 300
        
        difficulty = self.settings.get("difficulty", "normal")
        boss_level = BOSS_LEVEL_EASY if difficulty == "easy" else (BOSS_LEVEL_HARD if difficulty == "hard" else BOSS_LEVEL_NORMAL)
        boss = EntityFactory.create_boss(level=boss_level, position=(bx, by))
        boss.player_ref = self.player
        return boss
    
    def game_loop(self, task):
        """Main game loop"""
        if not self.running:
            return task.done
        
        if self.paused:
            return task.cont
        
        # Check if game is initialized
        if self.show_menu or not self.player:
            return task.cont
        
        now = time.time()
        delta_time = now - self.last_time
        
        # Limit delta_time for stability
        delta_time = min(delta_time, 0.1)  # Max 100ms
        
        self.last_time = now
        
        # Update AI
        self._update_player_ai(delta_time)
        if self.player:
            self.player.update(delta_time)
        
        # Optimize: update only nearby enemies
        if self.player:
            player_pos = self.player.position
            for enemy in self.enemies:
                if enemy.alive:
                    distance = self._dist2(player_pos, enemy.position)
                    if distance < 1000:  # Update only within 1000 pixels radius
                        enemy.update(delta_time)
                        self._move_entity_toward(enemy, player_pos, enemy.movement_speed, delta_time)
                        self._process_chest_interactions(enemy)
            
            if self.boss and self.boss.alive:
                boss_distance = self._dist2(player_pos, self.boss.position)
                if boss_distance < 1500:  # Boss active in a larger radius
                    self.boss.update(delta_time)
                    self._move_entity_toward(self.boss, player_pos, self.boss.movement_speed, delta_time)
                    self._process_chest_interactions(self.boss)
        
        # Group logic
        if hasattr(self, 'coordinator') and self.coordinator and self.player:
            self.coordinator.update_group_behavior("enemy_group")
            self.coordinator.update_group_behavior("boss_group")
        
        # Update AI modules (optimized)
        if hasattr(self, 'ai_scheduler') and self.ai_scheduler and self.player:
            self.ai_scheduler.update_all(delta_time)
        
        # Update skills and leveling
        if hasattr(self, 'skill_system') and self.skill_system and self.player:
            self.skill_system.update(delta_time)
        if hasattr(self, 'leveling_system') and self.leveling_system and self.player:
            self.leveling_system.update(delta_time)
        
        # Pattern analysis and emotions (less frequently for optimization)
        if hasattr(self, 'pattern_recognizer') and self.pattern_recognizer and self.player:
            if random.random() < 0.1:  # 10% chance to update
                self.pattern_recognizer.analyze_combat_patterns([self.player] + self.enemies + ([self.boss] if self.boss else []))
        if hasattr(self, 'emotion_synthesizer') and self.emotion_synthesizer and self.player:
            self.emotion_synthesizer.update_emotions(delta_time)
        
        # Effect handling (optimized)
        try:
            from combat.damage_system import DamageSystem
            # Process effects only for active entities
            if self.player and self.player.alive:
                DamageSystem.process_entity_effects(self.player, delta_time)
            
            for enemy in self.enemies:
                if enemy.alive and hasattr(enemy, 'effects') and enemy.effects:
                    DamageSystem.process_entity_effects(enemy, delta_time)
            
            if self.boss and self.boss.alive and hasattr(self.boss, 'effects') and self.boss.effects:
                DamageSystem.process_entity_effects(self.boss, delta_time)
        except ImportError:
            pass
        
        # Collisions
        if self.player:
            self.check_collisions()
        
        # Check victory over enemies
        if self.player and hasattr(self, 'player_leveling'):
            for enemy in self.enemies[:]:
                if not enemy.alive:
                    enemy_level = getattr(enemy, 'level', 1)
                    exp_gain = enemy_level * 10 + random.randint(5, 15)
                    self.player_leveling.gain_experience(exp_gain)
                    
                    if hasattr(self, 'player_ai_memory'):
                        self.player_ai_memory.record_event("ENEMY_DEFEATED", {
                            "enemy_type": getattr(enemy, 'enemy_type', 'unknown'),
                            "enemy_level": enemy_level,
                            "exp_gained": exp_gain,
                            "player_health": self.player.health,
                            "player_level": self.player_leveling.level
                        })
                    
                    # Remove 3D model
                    if hasattr(enemy, 'model'):
                        enemy.model.removeNode()
                    
                    self.enemies.remove(enemy)
            
            # Check victory over boss
            if self.boss and not self.boss.alive and not hasattr(self.boss, 'exp_given'):
                boss_level = getattr(self.boss, 'level', 15)
                exp_gain = boss_level * 50 + random.randint(100, 200)
                self.player_leveling.gain_experience(exp_gain)
                
                if hasattr(self, 'player_ai_memory'):
                    self.player_ai_memory.record_event("BOSS_DEFEATED", {
                        "boss_type": getattr(self.boss, 'boss_type', 'unknown'),
                        "boss_level": boss_level,
                        "exp_gained": exp_gain,
                        "player_health": self.player.health,
                        "player_level": self.player_leveling.level
                    })
                
                self.boss.exp_given = True
        
        # Update 3D positions
        if self.player:
            self._update_3d_positions()
        
        # Update UI
        self._update_ui()
        
        # Player death
        if self.player and not self.player.alive:
            self._respawn_player()
        
        # Victory
        if self.player and (not self.enemies) and (not self.boss or not self.boss.alive):
            if not self.victory_shown:
                self._show_victory()
                self.victory_shown = True
        
        return task.cont
    
    def _update_3d_positions(self):
        """Update 3D positions of entities"""
        # Player
        if self.player and hasattr(self.player, 'model'):
            self.player.model.setPos(self.player.position[0], self.player.position[1], 0)
        
        # Enemies
        for enemy in self.enemies:
            if hasattr(enemy, 'model') and enemy.alive:
                enemy.model.setPos(enemy.position[0], enemy.position[1], 0)
        
        # Boss
        if self.boss and hasattr(self.boss, 'model') and self.boss.alive:
            self.boss.model.setPos(self.boss.position[0], self.boss.position[1], 0)
    
    def _update_ui(self):
        """Update UI elements"""
        # Add logic to update UI elements here
        pass
    
    def _show_victory(self):
        """Show victory screen"""
        victory_text = DirectLabel(
            text="Victory! All defeated.",
            pos=(0, 0, 0),
            scale=0.06,
            text_fg=(1, 0.84, 0, 1),
            text_align=TextNode.ACenter
        )
        self.ui_elements.append(victory_text)
    
    def check_collisions(self):
        """Check collisions (optimized)"""
        if not self.player or not self.player.alive:
            return
            
        px, py = self.player.position
        collision_radius_player = 20
        collision_radius_enemy = 15
        collision_radius_boss = 30
        
        # Enemies (optimized with caching)
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            ex, ey = enemy.position
            dx = px - ex
            dy = py - ey
            distance_squared = dx * dx + dy * dy
            collision_threshold = (collision_radius_player + collision_radius_enemy) ** 2
            
            if distance_squared <= collision_threshold:
                # Check if player recently took damage
                if not hasattr(self.player, 'last_damage_time') or \
                   time.time() - getattr(self.player, 'last_damage_time', 0) > 0.5:
                    damage = getattr(enemy, 'damage_output', 10) * random.uniform(0.8, 1.2)
                    self.player.take_damage(damage, "physical")
                    self.player.last_damage_time = time.time()
        
        # Boss (optimized)
        if self.boss and self.boss.alive:
            bx, by = self.boss.position
            dx = px - bx
            dy = py - by
            distance_squared = dx * dx + dy * dy
            collision_threshold = (collision_radius_player + collision_radius_boss) ** 2
            
            if distance_squared <= collision_threshold:
                if not hasattr(self.player, 'last_damage_time') or \
                   time.time() - getattr(self.player, 'last_damage_time', 0) > 0.5:
                    damage = getattr(self.boss, 'damage_output', 20) * random.uniform(0.9, 1.5)
                    self.player.take_damage(damage, "physical")
                    self.player.last_damage_time = time.time()
    
    def _update_player_ai(self, dt: float):
        """Update player AI"""
        if not self.player:
            return
            
        target_pos = None
        if self.chests and self.player.health < self.player.max_health * 0.7:
            target_pos = self._nearest_chest_world_pos(self.player.position)
        if target_pos is None:
            if self.boss and self.boss.alive:
                target_pos = self.boss.position
            else:
                alive_enemies = [e for e in self.enemies if e.alive]
                if alive_enemies:
                    target = min(alive_enemies, key=lambda e: self._dist2(self.player.position, e.position))
                    target_pos = target.position
        
        if target_pos is None:
            return
        
        speed = float(self.player.movement_speed)
        self._move_entity_toward(self.player, target_pos, speed, dt)
        self._process_chest_interactions(self.player)
    
    def _move_entity_toward(self, entity, target_pos, speed: float, dt: float):
        """Move entity towards target (optimized)"""
        if not entity or not hasattr(entity, 'position') or not entity.position or not target_pos:
            return
            
        ex, ey = entity.position
        tx, ty = target_pos
        
        # Check distance to target
        dx = tx - ex
        dy = ty - ey
        distance_squared = dx * dx + dy * dy
        
        # If target too close, don't move
        if distance_squared < 1.0:
            return
            
        dist = max(1e-6, distance_squared ** 0.5)
        nx, ny = dx / dist, dy / dist
        
        # Calculate new step
        step_size = speed * dt
        step_x = ex + nx * step_size
        step_y = ey + ny * step_size
        
        # Check for blocking
        if self._is_blocked_pixel(step_x, step_y):
            # Try to bypass obstacle
            ax, ay = ny, -nx
            step1_x = ex + ax * step_size
            step1_y = ey + ay * step_size
            
            if not self._is_blocked_pixel(step1_x, step1_y):
                entity.position[0], entity.position[1] = step1_x, step1_y
                return
                
            bx, by = -ny, nx
            step2_x = ex + bx * step_size
            step2_y = ey + by * step_size
            
            if not self._is_blocked_pixel(step2_x, step2_y):
                entity.position[0], entity.position[1] = step2_x, step2_y
                return
                
            # If cannot bypass, stay in place
            return
        
        # Update position
        entity.position[0], entity.position[1] = step_x, step_y
    
    def _is_blocked_pixel(self, x: float, y: float) -> bool:
        """Check if pixel is blocked (optimized)"""
        if not self.tiled_map or not self.user_obstacles:
            return False
            
        # Cache tile sizes
        if not hasattr(self, '_tile_cache'):
            self._tile_cache = {
                'width': self.tiled_map.tilewidth,
                'height': self.tiled_map.tileheight
            }
        
        tw, th = self._tile_cache['width'], self._tile_cache['height']
        
        # Check map boundaries
        if x < 0 or y < 0:
            return True
            
        # Calculate tile coordinates
        tx, ty = int(x // tw), int(y // th)
        
        # Check for blocking
        return (tx, ty) in self.user_obstacles
    
    def _nearest_chest_world_pos(self, from_pos):
        """Find nearest chest (optimized)"""
        if not self.chests or not from_pos:
            return None
            
        fx, fy = from_pos
        best, best_d2 = None, float('inf')
        
        # Cache tile sizes
        if not hasattr(self, '_tile_cache'):
            self._tile_cache = {
                'width': self.tiled_map.tilewidth if self.tiled_map else 40,
                'height': self.tiled_map.tileheight if self.tiled_map else 40
            }
        
        tw, th = self._tile_cache['width'], self._tile_cache['height']
        
        # Filter only unopened chests
        available_chests = [chest for chest in self.chests if not chest.get("opened")]
        
        for chest in available_chests:
            cx = chest["tx"] * tw + tw / 2
            cy = chest["ty"] * th + th / 2
            d2 = (cx - fx) ** 2 + (cy - fy) ** 2
            
            if d2 < best_d2:
                best, best_d2 = (cx, cy), d2
                
                # If chest is very close, return it immediately
                if d2 < 100:  # 10 tiles squared
                    break
        
        return best
    
    def _process_chest_interactions(self, entity):
        """Process chest interactions (optimized)"""
        if not self.chests or not self.tiled_map or not entity or not hasattr(entity, 'position'):
            return
            
        # Cache tile sizes
        if not hasattr(self, '_tile_cache'):
            self._tile_cache = {
                'width': self.tiled_map.tilewidth,
                'height': self.tiled_map.tileheight
            }
        
        tw, th = self._tile_cache['width'], self._tile_cache['height']
        ex, ey = entity.position
        etx, ety = int(ex // tw), int(ey // th)
        
        # Check only unopened chests
        for chest in self.chests:
            if chest.get("opened"):
                continue
                
            if chest["tx"] == etx and chest["ty"] == ety:
                # Restore health
                if hasattr(entity, 'health') and hasattr(entity, 'max_health'):
                    entity.health = min(entity.max_health, entity.health + 20)
                chest["opened"] = True
                break  # Exit after finding the first chest
    
    def _respawn_player(self):
        """Respawn player (optimized)"""
        if not self.player:
            return
            
        self.reincarnation_count += 1
        
        if hasattr(self.player, 'alive'):
            self.player.alive = True
        if hasattr(self.player, 'health') and hasattr(self.player, 'max_health'):
            self.player.health = self.player.max_health
        if hasattr(self.player, 'learning_rate'):
            self.player.learning_rate = min(2.0, self.player.learning_rate * 1.01)
        
        # Place player in the center of the map
        if self.tiled_map and hasattr(self.tiled_map, 'width') and hasattr(self.tiled_map, 'height'):
            # Cache tile sizes
            if not hasattr(self, '_tile_cache'):
                self._tile_cache = {
                    'width': self.tiled_map.tilewidth,
                    'height': self.tiled_map.tileheight
                }
            
            tw, th = self._tile_cache['width'], self._tile_cache['height']
            map_px_w = self.tiled_map.width * tw
            map_px_h = self.tiled_map.height * th
            self.player.position = [map_px_w // 2, map_px_h // 2]
        else:
            self.player.position = [0, 0]
    
    def _dist2(self, a, b) -> float:
        """Distance between two points squared"""
        if not a or not b or len(a) < 2 or len(b) < 2:
            return float('inf')
        ax, ay = a
        bx, by = b
        return (ax - bx) ** 2 + (ay - by) ** 2
    
    def _use_skill(self, skill_id: str):
        """Use skill"""
        if hasattr(self, 'skill_system') and self.player:
            success = self.skill_system.use_skill(skill_id, self.player)
            if success:
                logger.info(f"Skill {skill_id} used successfully")
            else:
                logger.warning(f"Could not use skill {skill_id}")
    
    def _on_left_click(self):
        """Handle left mouse click"""
        # Add logic for placing obstacles here
        pass
    
    def _on_right_click(self):
        """Handle right mouse click"""
        # Add logic for placing chests here
        pass
    
    def toggle_pause(self):
        """Toggle pause"""
        self.paused = not self.paused
        if self.paused:
            self._show_pause_menu()
        else:
            self._hide_pause_menu()
    
    def _show_pause_menu(self):
        """Show pause menu"""
        # Create pause menu
        pass
    
    def _hide_pause_menu(self):
        """Hide pause menu"""
        # Hide pause menu
        pass
    
    def soft_restart(self):
        """Soft restart"""
        self.victory_shown = False
        self.generation_count += 1
        
        # Respawn player
        if self.player:
            self._respawn_player()
        
        # Respawn enemies
        for e in self.enemies:
            self._respawn_entity(e)
            map_width = self.tiled_map.width * self.tiled_map.tilewidth if self.tiled_map else 800
            map_height = self.tiled_map.height * self.tiled_map.tileheight if self.tiled_map else 600
            
            if map_width <= 200:
                map_width = 800
            if map_height <= 200:
                map_height = 600
            
            e.position = [random.randint(-map_width//2, map_width//2), random.randint(-map_height//2, map_height//2)]
        
        # Respawn boss
        if self.boss:
            self._respawn_entity(self.boss)
            if self.tiled_map:
                map_width = self.tiled_map.width * self.tiled_map.tilewidth
                if map_width <= 200:
                    map_width = 800
                self.boss.position = [map_width//2 - 300, 300]
            else:
                self.boss.position = [300, 300]
    
    @staticmethod
    def _respawn_entity(entity):
        """Respawn entity"""
        entity.alive = True
        entity.health = entity.max_health
    
    def load_game(self):
        """Load saved game"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    save_data = json.load(f)
                
                self.show_menu = False
                self.init_game()
                
                # Restore state
                self.reincarnation_count = save_data.get("reincarnation_count", 0)
                self.generation_count = save_data.get("generation_count", 0)
                self.session_start_time = save_data.get("session_start_time", time.time())
                
                # Restore player
                if "player" in save_data and self.player:
                    player_data = save_data["player"]
                    self.player.health = player_data.get("health", self.player.max_health)
                    self.player.level = player_data.get("level", 1)
                    self.player.learning_rate = player_data.get("learning_rate", 1.0)
                    self.player.position = player_data.get("position", [0, 0])
                
                # Restore obstacles and chests
                self.user_obstacles = set(tuple(obs) for obs in save_data.get("obstacles", []))
                self.chests = save_data.get("chests", [])
                
                logger.info("Game loaded successfully")
            except Exception as e:
                logger.error(f"Error loading: {e}")
                self.show_menu = True
                self.show_main_menu()
        else:
            logger.warning("Save file not found")
            self.show_menu = True
            self.show_main_menu()
    
    def save_game(self):
        """Save game"""
        try:
            save_data = {
                "reincarnation_count": self.reincarnation_count,
                "generation_count": self.generation_count,
                "session_start_time": self.session_start_time,
                "player": {
                    "health": self.player.health if self.player else 100,
                    "level": self.player.level if self.player else 1,
                    "learning_rate": self.player.learning_rate if self.player else 1.0,
                    "position": self.player.position if self.player else [0, 0]
                },
                "obstacles": list(self.user_obstacles),
                "chests": self.chests
            }
            
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)
            
            logger.info("Game saved")
        except Exception as e:
            logger.error(f"Error saving: {e}")
    
    def _update_enemy_ai(self, dt: float):
        """Update enemy AI"""
        if self.player:
            for enemy in self.enemies:
                if enemy.alive and hasattr(enemy, 'update'):
                    enemy.update(dt)
    
    def _update_boss_ai(self, dt: float):
        """Update boss AI"""
        if self.boss and self.boss.alive and hasattr(self.boss, 'update') and self.player:
            self.boss.update(dt)
    
    def _update_coordination(self, dt: float):
        """Update AI coordination"""
        if hasattr(self, 'coordinator') and self.coordinator and self.player:
            self.coordinator.update_group_behavior("enemy_group")
            self.coordinator.update_group_behavior("boss_group")
    
    def _update_patterns(self, dt: float):
        """Update pattern recognition"""
        if hasattr(self, 'pattern_recognizer') and self.pattern_recognizer and self.player:
            entities = [self.player] + self.enemies + ([self.boss] if self.boss else [])
            self.pattern_recognizer.analyze_combat_patterns(entities)
    
    def _update_emotions(self, dt: float):
        """Update emotion synthesis"""
        if hasattr(self, 'emotion_synthesizer') and self.emotion_synthesizer and self.player:
            self.emotion_synthesizer.update_emotions(dt)
    
    def stop(self):
        """Stop game"""
        logger.info("Closing game...")
        self.running = False
        self.userExit()


def main():
    game = Panda3DGame()
    game.run()


if __name__ == "__main__":
    main()

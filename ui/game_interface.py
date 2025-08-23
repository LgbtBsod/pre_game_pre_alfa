#!/usr/bin/env python3
"""
Единый игровой интерфейс для "Эволюционная Адаптация: Генетический Резонанс"
Объединяет все UI компоненты в одну систему на основе Pygame
"""

import pygame
import sys
import time
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import random

# Настройка логирования
logger = logging.getLogger(__name__)

# Импорт основных систем
from core.effect_system import EffectDatabase
from core.genetic_system import AdvancedGeneticSystem
from core.emotion_system import AdvancedEmotionSystem
from core.ai_system import AdaptiveAISystem
from core.content_generator import ContentGenerator
from core.evolution_system import EvolutionCycleSystem
from core.global_event_system import GlobalEventSystem
from core.dynamic_difficulty import DynamicDifficultySystem
from core.advanced_entity import AdvancedGameEntity
from core.isometric_system import IsometricProjection, BeaconNavigationSystem, IsometricRenderer
from ui.camera import Camera
from core.sprite_animation import CharacterSprite, Direction, AnimationState
from core.movement_system import MovementSystem
from core.level_progression import LevelProgressionSystem, StatisticsRenderer, LevelTransitionManager
from core.input_manager import InputManager
from ui.hud import StatusHUD, InventoryHUD, GeneticsHUD, AILearningHUD, DebugHUD
from ui.renderer import GameRenderer
from config.config_manager import config_manager


from core.game_state import GameState
from core.scene_manager import SceneManager
from ui.menu_scene import MenuScene
from ui.pause_scene import PauseScene

# Enhanced Edition системы
try:
    from core.enhanced_game_master import EnhancedGameMaster, GamePhase, DifficultyMode
    from core.curse_blessing_system import CurseBlessingSystem
    from core.risk_reward_system import RiskRewardSystem
    from core.meta_progression_system import MetaProgressionSystem
    from ui.enhanced_event_handler import EnhancedEventHandler
    ENHANCED_EDITION_AVAILABLE = True
except ImportError:
    ENHANCED_EDITION_AVAILABLE = False


@dataclass
class GameSettings:
    """Настройки игры"""
    window_width: int = 1600
    window_height: int = 900
    fps: int = 120
    fullscreen: bool = False
    vsync: bool = True
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    difficulty: str = "normal"
    
    @classmethod
    def from_config(cls) -> 'GameSettings':
        """Создает настройки из конфигурации"""
        try:
            return cls(
                window_width=config_manager.get('game', 'display.window_width', 1280),
                window_height=config_manager.get('game', 'display.window_height', 720),
                fps=config_manager.get('game', 'display.render_fps', 60),
                fullscreen=config_manager.get('game', 'display.fullscreen', False),
                vsync=config_manager.get('game', 'display.vsync', True),
                music_volume=config_manager.get('game', 'audio.music_volume', 0.7),
                sfx_volume=config_manager.get('game', 'audio.sfx_volume', 0.8),
                difficulty=config_manager.get('game', 'gameplay.difficulty', 'normal')
            )
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек из конфигурации: {e}")
            # Возвращаем настройки по умолчанию
            return cls()


class ColorScheme:
    """Цветовая схема интерфейса"""
    # Основные цвета
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    
    # Акцентные цвета
    BLUE = (0, 100, 255)
    GREEN = (0, 200, 0)
    RED = (255, 50, 50)
    YELLOW = (255, 255, 0)
    PURPLE = (150, 50, 255)
    ORANGE = (255, 150, 0)
    
    # Специальные цвета
    HEALTH_COLOR = (255, 50, 50)
    ENERGY_COLOR = (50, 150, 255)
    STAMINA_COLOR = (255, 200, 50)
    EVOLUTION_COLOR = (150, 255, 150)
    EMOTION_COLOR = (255, 100, 255)
    GENETIC_COLOR = (100, 255, 255)


class GameInterface:
    """Главный класс игрового интерфейса"""
    
    def __init__(self, settings: Optional[GameSettings] = None):
        global ENHANCED_EDITION_AVAILABLE
        
        try:
            self.settings = settings or GameSettings.from_config()
        except Exception as e:
            logger.error(f"Ошибка загрузки настроек: {e}")
            # Используем настройки по умолчанию
            self.settings = GameSettings()
        
        self.game_state = GameState.MAIN_MENU
        self.running = False
        
        # Инициализация Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Настройка экрана
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.settings.window_width, self.settings.window_height))
        
        pygame.display.set_caption("Эволюционная Адаптация: Генетический Резонанс")
        
        # Настройка FPS
        self.clock = pygame.time.Clock()
        
        # Шрифты
        self.fonts = self._load_fonts()
        
        # Базовая изометрическая проекция до создания UI/рендерера
        try:
            self.isometric_projection = IsometricProjection(tile_width=64, tile_height=32)
            self.isometric_renderer = IsometricRenderer(self.isometric_projection)
        except Exception as e:
            logger.error(f"Ошибка инициализации изометрии: {e}")
            self.isometric_projection = None
            self.isometric_renderer = None

        # Игровые системы
        self.effect_db = EffectDatabase()
        self.genetic_system = AdvancedGeneticSystem(self.effect_db)
        self.emotion_system = AdvancedEmotionSystem(self.effect_db)
        self.content_generator = ContentGenerator()
        self.evolution_system = EvolutionCycleSystem(self.effect_db)
        self.event_system = GlobalEventSystem(self.effect_db)
        
        # Улучшенные системы (Enhanced Edition)
        self.enhanced_game_master = None
        self.curse_blessing_system = None
        self.risk_reward_system = None
        self.meta_progression_system = None
        
        if ENHANCED_EDITION_AVAILABLE:
            try:
                # Инициализация Enhanced Game Master
                self.enhanced_game_master = EnhancedGameMaster(
                    self.settings.window_width, 
                    self.settings.window_height
                )
                
                # Получаем доступ к подсистемам Enhanced Edition
                self.curse_blessing_system = self.enhanced_game_master.curse_blessing_system
                self.risk_reward_system = self.enhanced_game_master.risk_reward_system
                self.meta_progression_system = self.enhanced_game_master.meta_progression_system
                
                # Инициализируем обработчик событий Enhanced Edition
                self.enhanced_event_handler = EnhancedEventHandler(self)
                
                logger.info("✨ Enhanced Edition активирован!")
                logger.info(f"   - Game Master инициализирован")
                logger.info(f"   - Curse/Blessing система доступна")
                logger.info(f"   - Risk/Reward система доступна")
                logger.info(f"   - Meta Progression система доступна")
                logger.info(f"   - Event Handler инициализирован")
                
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Enhanced Edition: {e}")
                self.enhanced_game_master = None
                ENHANCED_EDITION_AVAILABLE = False
        
        # Остальные улучшенные системы
        try:
            from core.generational_memory_system import GenerationalMemorySystem
            from core.emotional_ai_influence import EmotionalAIInfluenceSystem
            from core.enhanced_combat_learning import EnhancedCombatLearningSystem
            from core.enhanced_content_generator import EnhancedContentGenerator
            from core.enhanced_skill_system import SkillManager, SkillLearningAI
            
            # Инициализация улучшенных систем
            self.memory_system = GenerationalMemorySystem("save")
            self.emotional_ai_system = EmotionalAIInfluenceSystem(self.memory_system)
            self.enhanced_combat_system = EnhancedCombatLearningSystem(self.memory_system, self.emotional_ai_system)
            self.enhanced_content_generator = EnhancedContentGenerator(self.memory_system)
            self.skill_manager = SkillManager(self.memory_system, self.emotional_ai_system)
            self.skill_learning_ai = SkillLearningAI(self.memory_system, self.emotional_ai_system)
            
            logger.info("✅ Enhanced Edition системы инициализированы")
            
        except Exception as e:
            logger.warning(f"Не удалось загрузить Enhanced Edition системы: {e}")
            # Используем None для индикации отсутствия улучшенных систем
            self.memory_system = None
            self.emotional_ai_system = None
            self.enhanced_combat_system = None
            self.enhanced_content_generator = None
            self.skill_manager = None
            self.skill_learning_ai = None
        
        # Система управления вводом
        self.input_manager = InputManager()
        
        # Новые системы
        from core.computer_vision_system import ComputerVisionSystem
        from core.object_creation_system import ObjectCreationSystem
        
        self.computer_vision = ComputerVisionSystem("PLAYER_VISION")
        self.object_creation = ObjectCreationSystem()
        
        # Система управления сессиями
        from core.session_manager import SessionManager
        self.session_manager = SessionManager()
        
        # Инициализация системы сложности с обработкой ошибок
        try:
            self.difficulty_system = DynamicDifficultySystem()
            # Устанавливаем профиль сложности из настроек
            if hasattr(self.settings, 'difficulty'):
                self.difficulty_system.set_difficulty_profile(self.settings.difficulty)
        except Exception as e:
            logger.error(f"Ошибка инициализации системы сложности: {e}")
            # Создаем систему сложности без установки профиля
            self.difficulty_system = DynamicDifficultySystem()
        
        # Игровые данные
        self.player = None
        self.entities = []
        self.current_cycle = 1
        
        # Игровые объекты по умолчанию (безопасная инициализация)
        self.obstacles = []  # Препятствия (ловушки, геобарьеры)
        self.chests = []     # Сундуки с предметами
        self.items = []      # Предметы на карте
        
        # UI элементы
        self.buttons = {}
        self.panels = {}
        self._create_ui_elements()
        
        # Регистрация сцен
        try:
            self.scene_manager = SceneManager()
            self.menu_scene = MenuScene(self.scene_manager, self)
            self.pause_scene = PauseScene(self.scene_manager, self)
            self.scene_manager.register_scene('menu', self.menu_scene)
            self.scene_manager.register_scene('pause', self.pause_scene)
            self.scene_manager.switch_scene('menu')
        except Exception as e:
            logger.error(f"Ошибка регистрации сцен: {e}")
        
        # Статистика
        self.fps_counter = 0
        self.frame_count = 0
        self.last_fps_update = time.time()
    
    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        """Загрузка шрифтов"""
        fonts = {}
        try:
            # Основной шрифт
            font_path = Path("graphics/fonts/PixeloidSans.ttf")
            if font_path.exists():
                fonts["main"] = pygame.font.Font(str(font_path), 24)
                fonts["large"] = pygame.font.Font(str(font_path), 32)
                fonts["small"] = pygame.font.Font(str(font_path), 16)
            else:
                # Fallback на системный шрифт
                fonts["main"] = pygame.font.Font(None, 24)
                fonts["large"] = pygame.font.Font(None, 32)
                fonts["small"] = pygame.font.Font(None, 16)
        except Exception as e:
            print(f"Ошибка загрузки шрифтов: {e}")
            fonts["main"] = pygame.font.Font(None, 24)
            fonts["large"] = pygame.font.Font(None, 32)
            fonts["small"] = pygame.font.Font(None, 16)
        
        return fonts
    
    def _create_ui_elements(self):
        """Создание UI элементов"""
        # Кнопки главного меню
        button_width = 300
        button_height = 50
        start_x = (self.settings.window_width - button_width) // 2
        start_y = 250
        
        self.buttons["start_game"] = pygame.Rect(start_x, start_y, button_width, button_height)
        self.buttons["continue_game"] = pygame.Rect(start_x, start_y + 70, button_width, button_height)
        self.buttons["load_game"] = pygame.Rect(start_x, start_y + 140, button_width, button_height)
        self.buttons["settings"] = pygame.Rect(start_x, start_y + 210, button_width, button_height)
        self.buttons["exit"] = pygame.Rect(start_x, start_y + 280, button_width, button_height)
        
        # Игровые панели
        panel_width = 320
        panel_height = 220
        self.panels["stats"] = pygame.Rect(10, 10, panel_width, panel_height)
        self.panels["inventory"] = pygame.Rect(self.settings.window_width - panel_width - 10, 10, panel_width, panel_height)
        self.panels["genetics"] = pygame.Rect(10, self.settings.window_height - panel_height - 10, panel_width, panel_height)
        self.panels["emotions"] = pygame.Rect(self.settings.window_width - panel_width - 10, self.settings.window_height - panel_height - 10, panel_width, panel_height)
        
        # HUD объекты
        self.status_hud = StatusHUD(self.screen, self.fonts, self.panels["stats"], ColorScheme)
        self.inventory_hud = InventoryHUD(self.screen, self.fonts, self.panels["inventory"], ColorScheme)
        self.genetics_hud = GeneticsHUD(self.screen, self.fonts, self.panels["genetics"], ColorScheme)
        self.ai_hud = AILearningHUD(self.screen, self.fonts, self.panels["emotions"], ColorScheme)
        
        # Камера-хелпер
        self.camera = Camera(self.settings.window_width, self.settings.window_height)
        self.renderer = GameRenderer(self.screen, self.fonts, self.isometric_projection, self.camera, ColorScheme)
    
    def run(self):
        """Главный цикл игры"""
        self.running = True
        
        while self.running:
            # Обработка событий
            self._handle_events()
            
            # Обновление
            self._update()
            
            # Отрисовка
            self._render()
            
            # Ограничение FPS
            self.clock.tick(self.settings.fps)
            
            # Обновление счетчика FPS
            self._update_fps_counter()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
    
    def _handle_keydown(self, key):
        """Обработка нажатий клавиш"""
        if key == pygame.K_ESCAPE:
            if self.game_state == GameState.PLAYING:
                self.game_state = GameState.PAUSED
            elif self.game_state == GameState.PAUSED:
                self.game_state = GameState.PLAYING
            elif self.game_state == GameState.MAIN_MENU:
                self.running = False
            elif self.game_state in [GameState.INVENTORY, GameState.GENETICS, GameState.EMOTIONS, GameState.EVOLUTION]:
                self.game_state = GameState.PLAYING
        
        elif key == pygame.K_c and self.game_state == GameState.PLAYING:
            # Центрировать камеру на персонаже
            if self.player:
                iso_x, iso_y = self.isometric_projection.world_to_iso(
                    self.player.position.x, self.player.position.y, self.player.position.z
                )
                # Центрируем так, чтобы персонаж был в центре экрана
                self.isometric_projection.camera_x = iso_x - self.settings.window_width // 2
                self.isometric_projection.camera_y = iso_y - self.settings.window_height // 2
        
        # Свободная камера (стрелки)
        elif self.game_state == GameState.PLAYING:
            camera_speed = 20
            if key in (pygame.K_LEFT, pygame.K_a):
                self.isometric_projection.camera_x -= camera_speed
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.isometric_projection.camera_x += camera_speed
            elif key in (pygame.K_UP, pygame.K_w):
                self.isometric_projection.camera_y -= camera_speed
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.isometric_projection.camera_y += camera_speed
        
        elif key == pygame.K_i and self.game_state == GameState.PLAYING:
            self.game_state = GameState.INVENTORY
        
        elif key == pygame.K_g and self.game_state == GameState.PLAYING:
            self.game_state = GameState.GENETICS
        
        elif key == pygame.K_e and self.game_state == GameState.PLAYING:
            self.game_state = GameState.EMOTIONS
        
        elif key == pygame.K_v and self.game_state == GameState.PLAYING:
            self.game_state = GameState.EVOLUTION
        
        # Игровое взаимодействие (создание объектов)
        elif self.game_state == GameState.PLAYING and self.player:
            # Создание препятствий
            if key == pygame.K_1:  # Ловушка
                self._create_trap()
            elif key == pygame.K_2:  # Геобарьер
                self._create_geo_barrier()
            elif key == pygame.K_3:  # Сундук с предметами
                self._create_chest()
            elif key == pygame.K_4:  # Добавление врага
                self._add_enemy()
            
            # Активация эмоций
            elif key == pygame.K_5:  # Агрессия
                self._activate_emotion("aggression")
            elif key == pygame.K_6:  # Любопытство
                self._activate_emotion("curiosity")
            elif key == pygame.K_7:  # Осторожность
                self._activate_emotion("caution")
            elif key == pygame.K_8:  # Социальность
                self._activate_emotion("social")
            
            # Навигация к маякам
            elif key == pygame.K_m:  # К любому обнаруженному маяку
                self._navigate_to_any_beacon()
            elif key == pygame.K_x:  # Отменить навигацию
                self._cancel_navigation()
            
            # Управление камерой
            elif key == pygame.K_PLUS or key == pygame.K_EQUALS:  # Приблизить
                self.isometric_projection.set_zoom(self.isometric_projection.zoom * 1.2)
            elif key == pygame.K_MINUS:  # Отдалить
                self.isometric_projection.set_zoom(self.isometric_projection.zoom / 1.2)
            
            # Ручное управление (временное отключение автономности)
            elif key == pygame.K_SPACE:
                self._toggle_autonomous_movement()
        
        # Обработка ввода для прогрессии уровней
        self._handle_level_progression_input(key)
    
    def _create_trap(self):
        """Создает ловушку рядом с игроком"""
        try:
            if not hasattr(self, 'object_creation') or not self.player:
                return
            
            # Позиция рядом с игроком
            player_pos = (self.player.position.x, self.player.position.y, self.player.position.z)
            trap_pos = (player_pos[0] + random.randint(-50, 50), 
                       player_pos[1] + random.randint(-50, 50), 
                       player_pos[2])
            
            # Создаем ловушку
            from core.object_creation_system import ObjectCreationRequest
            request = ObjectCreationRequest(
                template_id="trap_spike",
                position=trap_pos,
                creator_id="PLAYER_001"
            )
            
            created_trap = self.object_creation.create_object(request, time.time())
            if created_trap:
                print(f"Создана ловушка: {created_trap.name} в позиции {trap_pos}")
            
        except Exception as e:
            logger.error(f"Ошибка создания ловушки: {e}")
    
    def _create_geo_barrier(self):
        """Создает геобарьер рядом с игроком"""
        try:
            if not hasattr(self, 'object_creation') or not self.player:
                return
            
            # Позиция рядом с игроком
            player_pos = (self.player.position.x, self.player.position.y, self.player.position.z)
            barrier_pos = (player_pos[0] + random.randint(-30, 30), 
                          player_pos[1] + random.randint(-30, 30), 
                          player_pos[2])
            
            # Создаем препятствие
            from core.object_creation_system import ObjectCreationRequest
            request = ObjectCreationRequest(
                template_id="obstacle_rock",
                position=barrier_pos,
                creator_id="PLAYER_001"
            )
            
            created_barrier = self.object_creation.create_object(request, time.time())
            if created_barrier:
                print(f"Создан геобарьер: {created_barrier.name} в позиции {barrier_pos}")
            
        except Exception as e:
            logger.error(f"Ошибка создания геобарьера: {e}")
    
    def _create_chest(self):
        """Создает сундук рядом с игроком"""
        try:
            if not hasattr(self, 'object_creation') or not self.player:
                return
            
            # Позиция рядом с игроком
            player_pos = (self.player.position.x, self.player.position.y, self.player.position.z)
            chest_pos = (player_pos[0] + random.randint(-40, 40), 
                        player_pos[1] + random.randint(-40, 40), 
                        player_pos[2])
            
            # Создаем сундук
            from core.object_creation_system import ObjectCreationRequest
            request = ObjectCreationRequest(
                template_id="chest_wooden",
                position=chest_pos,
                creator_id="PLAYER_001"
            )
            
            created_chest = self.object_creation.create_object(request, time.time())
            if created_chest:
                print(f"Создан сундук: {created_chest.name} в позиции {chest_pos}")
            
        except Exception as e:
            logger.error(f"Ошибка создания сундука: {e}")
    
    def _add_enemy(self):
        """Создает врага рядом с игроком"""
        try:
            if not self.player:
                return
            
            # Позиция рядом с игроком
            player_pos = (self.player.position.x, self.player.position.y, self.player.position.z)
            enemy_pos = (player_pos[0] + random.randint(-60, 60), 
                        player_pos[1] + random.randint(-60, 60), 
                        player_pos[2])
            
            # Используем Enhanced Content Generator если доступен
            if self.enhanced_content_generator:
                try:
                    from core.enhanced_content_generator import BiomeType
                    # Генерируем врага с помощью улучшенной системы
                    enemy = self.enhanced_content_generator.generate_enemy(
                        BiomeType.FOREST,  # Упрощенно используем лес
                        1,  # Уровень
                        {"level_width": 1000, "level_height": 1000}
                    )
                    
                    # Создаем игровую сущность из сгенерированного врага
                    from core.advanced_entity import AdvancedGameEntity
                    game_enemy = AdvancedGameEntity(
                        entity_id=enemy.guid,
                        entity_type="enemy",
                        name=enemy.name,
                        position=enemy_pos
                    )
                    
                    # Добавляем в список сущностей
                    self.entities.append(game_enemy)
                    logger.info(f"✨ Enhanced враг создан: {enemy.name} [{enemy.enemy_type.value}]")
                    return
                    
                except Exception as e:
                    logger.debug(f"Ошибка Enhanced генератора: {e}, используем fallback")
            
            # Fallback к оригинальной системе
            if hasattr(self, 'object_creation'):
                # Выбираем случайного врага
                enemy_templates = ["enemy_goblin", "enemy_orc", "enemy_skeleton"]
                template_id = random.choice(enemy_templates)
                
                # Создаем врага
                from core.object_creation_system import ObjectCreationRequest
                request = ObjectCreationRequest(
                    template_id=template_id,
                    position=enemy_pos,
                    creator_id="PLAYER_001"
                )
                
                created_enemy = self.object_creation.create_object(request, time.time())
                if created_enemy:
                    logger.info(f"Создан враг: {created_enemy.name} в позиции {enemy_pos}")
            
        except Exception as e:
            logger.error(f"Ошибка создания врага: {e}")
    
    def _handle_mouse_click(self, pos):
        """Обработка кликов мыши"""
        if self.game_state == GameState.MAIN_MENU:
            if self.buttons["start_game"].collidepoint(pos):
                self._start_new_game()
            elif self.buttons["continue_game"].collidepoint(pos):
                self._continue_game()
            elif self.buttons["load_game"].collidepoint(pos):
                self._show_save_slots(mode="load")
            elif self.buttons["settings"].collidepoint(pos):
                self.game_state = GameState.SETTINGS
            elif self.buttons["exit"].collidepoint(pos):
                self.running = False
        
        elif self.game_state == GameState.SETTINGS and hasattr(self, 'settings_buttons'):
            if self.settings_buttons["back"].collidepoint(pos):
                self.game_state = GameState.MAIN_MENU
        
        elif self.game_state == GameState.PAUSED and hasattr(self, 'pause_buttons'):
            if self.pause_buttons["resume"].collidepoint(pos):
                self.game_state = GameState.PLAYING
            elif self.pause_buttons["save"].collidepoint(pos):
                self.save_slots_return_state = GameState.PAUSED
                self._show_save_slots(mode="save")
            elif self.pause_buttons["load"].collidepoint(pos):
                self.save_slots_return_state = GameState.PAUSED
                self._show_save_slots(mode="load")
            elif self.pause_buttons["settings"].collidepoint(pos):
                self.game_state = GameState.SETTINGS
            elif self.pause_buttons["main_menu"].collidepoint(pos):
                self.game_state = GameState.MAIN_MENU
        
        elif self.game_state == GameState.SAVE_MENU and hasattr(self, 'save_slot_buttons'):
            # Обработка кликов по слотам сохранения/загрузки
            for slot_id, button in self.save_slot_buttons.items():
                if button.collidepoint(pos):
                    if slot_id == "back":
                        # Возврат в указанное состояние (по умолчанию главное меню)
                        target_state = getattr(self, 'save_slots_return_state', GameState.MAIN_MENU)
                        self.game_state = target_state
                    else:
                        mode = getattr(self, 'save_slots_mode', 'save')
                        if mode == 'save':
                            self._save_to_slot(slot_id)
                        else:
                            self._load_from_slot(slot_id)
                    break
    
    def _handle_mouse_motion(self, pos):
        """Обработка движения мыши"""
        pass  # Можно добавить hover эффекты
    
    def _start_new_game(self):
        """Начало новой игры"""
        try:
            # Создание новой сессии
            session_data = self.session_manager.create_temporary_session()
            if not session_data:
                raise Exception("Не удалось создать временную сессию")
            
            # Инициализация контента для сессии
            self.content_generator.initialize_session_content(
                session_data.session_uuid,
                level=1
            )
            
            # Создание игрока
            self.player = AdvancedGameEntity(
                entity_id="PLAYER_001",
                entity_type="player",
                name="Игрок",
                position=(0, 0, 0)
            )
            
            # Инициализация систем игрока (уже происходит в конструкторе)
            # self.player.initialize_systems()  # Удалено - инициализация происходит в конструкторе
            
            # Создание ИИ для игрока
            self.player_ai = AdaptiveAISystem("PLAYER_001", self.effect_db)
            # Инициализация происходит в конструкторе, дополнительная инициализация не требуется
            
            # Включение автономного движения
            self.autonomous_movement_enabled = True
            
            # Генерация мира с увеличенным размером (в 100 раз больше)
            world = self.content_generator.generate_world(
                biome="forest",
                size="massive",  # Изменено с "medium" на "massive"
                difficulty=1.0
            )
            
            # Создание врагов из контента сессии
            self.entities = []
            session_enemies = self.session_manager.get_session_content("enemies")
            for i, enemy_data in enumerate(session_enemies):
                enemy = AdvancedGameEntity(
                    entity_id=f"ENEMY_{i:03d}",
                    entity_type="enemy",
                    name=enemy_data.get("name", f"Враг {i+1}"),
                    position=(random.randint(-2000, 2000), random.randint(-2000, 2000), 0)  # Увеличенный диапазон
                )
                self.entities.append(enemy)
            
            # Игровые объекты
            self.obstacles = []
            self.chests = []
            self.items = []
            
            # Создание маяков в увеличенном мире
            self.beacon_system = BeaconNavigationSystem(
                world_width=10000,  # Увеличенный размер мира
                world_height=10000
            )
            
            # Инициализация изометрической проекции с увеличенными границами
            self.isometric_projection = IsometricProjection(
                tile_width=64,  # Размер тайла
                tile_height=32
            )
            
            # Инициализация рендерера
            self.isometric_renderer = IsometricRenderer(self.isometric_projection)
            
            # Создание спрайта игрока
            self.player_sprite = CharacterSprite("graphics/player")
            self.player_sprite.set_position(0, 0)
            
            # Инициализация систем движения
            self.movement_system = MovementSystem()
            
            # Инициализация систем прогрессии
            self.level_progression = LevelProgressionSystem(self.content_generator, self.effect_db)
            self.statistics_renderer = StatisticsRenderer(self.screen, self.fonts["main"])
            self.level_transition_manager = LevelTransitionManager(self.level_progression, self.statistics_renderer)
            
            # Инициализация систем создания объектов
            from core.object_creation_system import ObjectCreationSystem
            self.object_creation = ObjectCreationSystem()
            
            # Инициализация компьютерного зрения
            from core.computer_vision_system import ComputerVisionSystem
            self.computer_vision = ComputerVisionSystem("GAME_VISION")
            
            # Переход к игровому состоянию
            self.game_state = GameState.PLAYING
            
            logger.info("Новая игра успешно создана")
            
        except Exception as e:
            logger.error(f"Ошибка создания новой игры: {e}")
            # В случае ошибки возвращаемся в главное меню
            self.game_state = GameState.MAIN_MENU
    
    def _load_existing_game(self, slot_id: int):
        """Загрузка существующей игры"""
        try:
            # Загружаем сессию
            session_data = self.session_manager.load_session_by_slot(slot_id)
            if not session_data:
                logger.error(f"Не удалось загрузить сессию из слота {slot_id}")
                return False
            
            # Восстанавливаем игровые данные с учетом возможных старых форматов
            player_data = session_data.player_data or {}
            world_data = session_data.world_data or {}
            inventory_data = session_data.inventory_data or {}
            progress_data = session_data.progress_data or {}
            
            # Имя и уровень игрока
            player_name = player_data.get("name", "Игрок") if isinstance(player_data, dict) else "Игрок"
            player_level = 1
            if isinstance(player_data, dict):
                player_level = player_data.get("level", 1)
            if isinstance(progress_data, dict):
                player_level = progress_data.get("player_level", player_level)
            
            # Позиция игрока
            px = py = pz = 0
            if isinstance(player_data, dict):
                pos = player_data.get("position", (0, 0, 0))
                if isinstance(pos, dict):
                    px = pos.get("x", 0); py = pos.get("y", 0); pz = pos.get("z", 0)
                elif isinstance(pos, (list, tuple)) and len(pos) >= 3:
                    px, py, pz = pos[0], pos[1], pos[2]
            
            # Создание игрока
            self.player = AdvancedGameEntity(
                entity_id="PLAYER_001",
                entity_type="player",
                name=player_name,
                position=(px, py, pz)
            )
            # Устанавливаем уровень
            setattr(self.player, 'level', player_level)
            
            # Восстанавливаем характеристики игрока
            if isinstance(player_data, dict):
                stats_block = player_data.get("stats", {}) if isinstance(player_data.get("stats", {}), dict) else {}
                if stats_block:
                    self.player.stats.health = stats_block.get("health", self.player.stats.health)
                    self.player.stats.max_health = stats_block.get("max_health", self.player.stats.max_health)
                    self.player.stats.stamina = stats_block.get("stamina", self.player.stats.stamina)
                    self.player.stats.max_stamina = stats_block.get("max_stamina", self.player.stats.max_stamina)
                    self.player.stats.mana = stats_block.get("mana", self.player.stats.mana)
                    self.player.stats.max_mana = stats_block.get("max_mana", self.player.stats.max_mana)
                # Инвентарь
                inv = player_data.get("inventory", {})
                if isinstance(inv, dict):
                    for item_id, quantity in inv.items():
                        self.player.inventory_system.add_item(item_id, quantity)
            
            # Инициализация ИИ для игрока
            self.player_ai = AdaptiveAISystem("PLAYER_001")
            self.autonomous_movement_enabled = True
            
            # Восстанавливаем врагов из сессионного контента
            self.entities = []
            session_enemies = self.session_manager.get_session_content("enemies")
            for i, enemy_data in enumerate(session_enemies):
                if isinstance(enemy_data, dict) and not enemy_data.get("is_defeated", False):
                    enemy = AdvancedGameEntity(
                        entity_id=f"ENEMY_{i:03d}",
                        entity_type="enemy",
                        name=enemy_data.get("name", f"Враг {i+1}"),
                        position=(random.randint(-200, 200), random.randint(-200, 200), 0)
                    )
                    self.entities.append(enemy)
            
            # Системы
            self.effect_db = EffectDatabase()
            self.genetic_system = AdvancedGeneticSystem(self.effect_db)
            self.emotion_system = AdvancedEmotionSystem(self.effect_db)
            self.content_generator = ContentGenerator(session_data.generation_seed)
            self.evolution_system = EvolutionCycleSystem(self.effect_db)
            self.event_system = GlobalEventSystem(self.effect_db)
            self.difficulty_system = DynamicDifficultySystem()
            
            # Изометрические системы
            self.isometric_projection = IsometricProjection(tile_width=64, tile_height=32)
            self.beacon_system = BeaconNavigationSystem(world_width=1000, world_height=1000)
            self.isometric_renderer = IsometricRenderer(self.isometric_projection)
            self.player_sprite = CharacterSprite("graphics/player")
            self.movement_system = MovementSystem()
            
            # Прогресс: уровень мира
            cur_level = 1
            if isinstance(progress_data, dict):
                cur_level = progress_data.get("current_level", cur_level)
            self.level_progression = LevelProgressionSystem(self.content_generator, self.effect_db)
            self.statistics_renderer = StatisticsRenderer(self.screen, self.fonts["main"])
            self.level_transition_manager = LevelTransitionManager(self.level_progression, self.statistics_renderer)
            self.level_progression.start_level(cur_level)
            
            # Переходим в игровое состояние
            self.game_state = GameState.PLAYING
            logger.info(f"Игра загружена из слота {slot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки игры: {e}")
            self.game_state = GameState.MAIN_MENU
            return False
    
    def _generate_items_for_new_game(self):
        """Генерация предметов для новой игры"""
        if not self.player:
            return
        
        # Очищаем инвентарь игрока
        self.player.inventory_system.clear_inventory()
        
        # Добавляем базовые предметы
        from core.database_manager import database_manager
        
        # Зелье здоровья
        health_potion = database_manager.get_item("health_potion")
        if health_potion:
            self.player.inventory_system.add_item(health_potion["id"], 3)
        
        # Зелье маны
        mana_potion = database_manager.get_item("mana_potion")
        if mana_potion:
            self.player.inventory_system.add_item(mana_potion["id"], 2)
        
        # Базовое оружие
        sword = database_manager.get_weapon("sword_common")
        if sword:
            self.player.inventory_system.add_item(sword["weapon_id"], 1)
    
    def _save_game(self):
        """Сохранение игры"""
        if not self.player or not self.session_manager.active_session:
            return False
        
        try:
            # Обновляем данные активной сессии
            session = self.session_manager.active_session
            
            session.player_data = {
                "entity_id": self.player.id,
                "name": self.player.name,
                "position": (self.player.position.x, self.player.position.y, self.player.position.z),
                "stats": {
                    "health": self.player.stats.health,
                    "max_health": self.player.stats.max_health,
                    "stamina": self.player.stats.stamina,
                    "max_stamina": self.player.stats.max_stamina,
                    "mana": self.player.stats.mana,
                    "max_mana": self.player.stats.max_mana
                },
                "inventory": self.player.inventory_system.get_inventory_data()
            }
            
            session.world_data = {
                "entities": [
                    {
                        "entity_id": entity.id,
                        "name": entity.name,
                        "position": (entity.position.x, entity.position.y, entity.position.z),
                        "stats": {
                            "health": entity.stats.health,
                            "max_health": entity.stats.max_health
                        }
                    }
                    for entity in self.entities
                ],
                "current_cycle": getattr(self, 'current_cycle', 1)
            }
            
            session.inventory_data = session.player_data.get("inventory", {})
            session.progress_data = {
                "world_seed": getattr(self, 'world_seed', 12345),
                "play_time": getattr(self, 'play_time', 0.0),
                "player_level": getattr(self.player, 'level', 1)
            }
            session.generation_seed = getattr(self, 'world_seed', 0)
            session.current_level = getattr(self, 'current_level', 1) if hasattr(self, 'current_level') else 1
            
            # Сохраняем через менеджер сессий
            success = self.session_manager.save_session(session)
            
            if success:
                logger.info("Игра сохранена успешно")
                return True
            else:
                logger.error("Ошибка сохранения через менеджер сессий")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
            return False
    
    def _load_game(self):
        """Загрузка игры"""
        try:
            import json
            with open("save/game_save.json", "r", encoding="utf-8") as f:
                save_data = json.load(f)
            
            # Восстанавливаем игрока
            player_data = save_data["player"]
            self.player = AdvancedGameEntity(
                entity_id=player_data["entity_id"],
                entity_type="player",
                name=player_data["name"],
                position=player_data["position"]
            )
            
            # Восстанавливаем статистику
            self.player.stats.health = player_data["stats"]["health"]
            self.player.stats.max_health = player_data["stats"]["max_health"]
            self.player.stats.stamina = player_data["stats"]["stamina"]
            self.player.stats.max_stamina = player_data["stats"]["max_stamina"]
            self.player.stats.mana = player_data["stats"]["mana"]
            self.player.stats.max_mana = player_data["stats"]["max_mana"]
            
            # Восстанавливаем инвентарь
            for item_id, quantity in player_data["inventory"].items():
                self.player.inventory_system.add_item(item_id, quantity)
            
            # Восстанавливаем врагов
            self.entities = []
            for entity_data in save_data["entities"]:
                entity = AdvancedGameEntity(
                    entity_id=entity_data["entity_id"],
                    entity_type="enemy",
                    name=entity_data["name"],
                    position=entity_data["position"]
                )
                entity.stats.health = entity_data["stats"]["health"]
                entity.stats.max_health = entity_data["stats"]["max_health"]
                self.entities.append(entity)
            
            self.current_cycle = save_data["current_cycle"]
            self.world_seed = save_data.get("world_seed", 12345)
            
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки: {e}")
            return False
    
    def _continue_game(self):
        """Продолжение игры"""
        try:
            # Пытаемся найти последнее сохранение
            save_slots = self.session_manager.get_save_slots()
            if save_slots:
                # Берем самое последнее сохранение
                latest_save = save_slots[0]
                slot_id = latest_save['slot_id']
                
                if self._load_existing_game(slot_id):
                    self.game_state = GameState.PLAYING
                    logger.info(f"Игра продолжена из слота {slot_id}")
                else:
                    # Если загрузка не удалась, создаем новую игру
                    logger.warning("Не удалось загрузить последнее сохранение, создаем новую игру")
                    self._start_new_game()
            else:
                # Если сохранений нет, создаем новую игру
                logger.info("Сохранений не найдено, создаем новую игру")
                self._start_new_game()
                
        except Exception as e:
            logger.error(f"Ошибка продолжения игры: {e}")
            # В случае ошибки создаем новую игру
            self._start_new_game()
    
    def _update(self):
        """Обновление игровой логики"""
        if self.game_state == GameState.PLAYING and self.player:
            # Правильный расчет delta_time
            delta_time = self.clock.get_time() / 1000.0  # Преобразуем мс в секунды
            
            # Непрерывное управление камерой через хелпер
            keys = pygame.key.get_pressed()
            self.camera.update_from_inputs(keys, 300.0, delta_time)
            
            # Ручное движение игрока (WASD/стрелки)
            if hasattr(self, 'movement_system'):
                mdx, mdy = self.movement_system.update_player_from_inputs(self.player, keys, delta_time)
                if hasattr(self, 'player_sprite'):
                    if abs(mdx) > 0.0 or abs(mdy) > 0.0:
                        if abs(mdx) >= abs(mdy):
                            self.player_sprite.set_direction(Direction.RIGHT if mdx > 0 else Direction.LEFT)
                        else:
                            self.player_sprite.set_direction(Direction.DOWN if mdy > 0 else Direction.UP)
                        self.player_sprite.set_state(AnimationState.WALKING)
                    else:
                        self.player_sprite.set_state(AnimationState.IDLE)

            # Автономное движение игрока
            if hasattr(self, 'player_ai') and hasattr(self, 'autonomous_movement_enabled') and self.autonomous_movement_enabled:
                # Обновление ИИ игрока
                self.player_ai.update(self.player, self, delta_time)
                
                # Получение автономного движения
                dx, dy = self.player_ai.get_autonomous_movement(self.player, self)
                
                # Применяем движение только если оно значительное
                if abs(dx) > 0.1 or abs(dy) > 0.1:
                    movement_speed = 50.0  # пикс/сек в мировых координатах
                    self.player.move_pygame(dx * delta_time * movement_speed, dy * delta_time * movement_speed)
                    
                    # Обновляем информацию об окружении для ИИ
                    self.player_ai.update_environment_info(self.player, self)
            
            # Обновление игрока
            self.player.update(delta_time)
            
            # Обновление спрайта игрока
            if hasattr(self, 'player_sprite'):
                # Если активен автономный режим, корректируем направление/состояние
                if hasattr(self, 'player_ai') and hasattr(self, 'autonomous_movement_enabled') and self.autonomous_movement_enabled:
                    dx, dy = self.player_ai.get_autonomous_movement(self.player, self)
                    if abs(dx) > 0.1 or abs(dy) > 0.1:
                        if abs(dx) >= abs(dy):
                            self.player_sprite.set_direction(Direction.RIGHT if dx > 0 else Direction.LEFT)
                        else:
                            self.player_sprite.set_direction(Direction.DOWN if dy > 0 else Direction.UP)
                        self.player_sprite.set_state(AnimationState.WALKING)
                    else:
                        self.player_sprite.set_state(AnimationState.IDLE)

                # Обновляем позицию спрайта в изометрических координатах
                iso_x, iso_y = self.isometric_projection.world_to_iso(
                    self.player.position.x, self.player.position.y, self.player.position.z
                )
                self.player_sprite.set_position(iso_x, iso_y)
                self.player_sprite.update(delta_time)
            
            # Обновление врагов
            for entity in self.entities:
                entity.update(delta_time)
            
            # Обновление препятствий
            for obstacle in self.obstacles:
                if hasattr(obstacle, 'update'):
                    obstacle.update(delta_time)
            
            # Обновление сундуков
            for chest in self.chests:
                if hasattr(chest, 'update'):
                    chest.update(delta_time)
            
            # Обновление предметов на карте
            for item in self.items:
                if hasattr(item, 'update'):
                    item.update(delta_time)
            
            # Обновление компьютерного зрения
            if hasattr(self, 'computer_vision') and self.player:
                # Собираем все объекты в мире для анализа
                world_objects = []
                
                # Добавляем врагов
                world_objects.extend(self.entities)
                
                # Добавляем созданные объекты
                if hasattr(self, 'object_creation'):
                    for obj in self.object_creation.created_objects.values():
                        if obj.is_active:
                            world_objects.append(obj)
                
                # Добавляем препятствия, сундуки, предметы
                world_objects.extend(self.obstacles)
                world_objects.extend(self.chests)
                world_objects.extend(self.items)
                
                # Обновляем поле зрения
                player_pos = (self.player.position.x, self.player.position.y, self.player.position.z)
                self.computer_vision.update_visual_field(player_pos, world_objects, time.time())
                
                # Принимаем визуальное решение
                visual_action = self.computer_vision.make_visual_decision(time.time())
                
                # Очищаем старую память
                self.computer_vision.cleanup_old_memory(time.time())
            
            # Подготовка состояния мира для глобальных событий
            world_state = {
                "mutation_level": getattr(self.player, "mutation_level", 0.0),
                "evolution_cycles": getattr(self, "current_cycle", 1),
                "emotional_instability": 0.5,
                "psychic_energy": 0.4,
                "ai_learning_rate": 0.5,
                "reality_stability": 0.9,
                "radiation_level": 0.1,
                "disease_spread": 0.05,
                "time_distortion": 0.0,
                "reality_coherence": 1.0,
            }
            entities = [self.player] + list(self.entities)
            
            # Проверка обнаружения маяка
            if hasattr(self, 'beacon_system') and self.player:
                discovered_beacon = self.beacon_system.discover_beacon(
                    (self.player.position.x, self.player.position.y, self.player.position.z)
                )
                if discovered_beacon:
                    # Уведомляем систему прогрессии об обнаружении маяка
                    if hasattr(self, 'level_progression'):
                        self.level_progression.on_beacon_found(self.player)
                        self.game_state = GameState.LEVEL_STATISTICS
            
            # Обновление системы прогрессии уровней
            if hasattr(self, 'level_progression'):
                self.level_progression.update(delta_time)
                if hasattr(self, 'level_transition_manager'):
                    self.level_transition_manager.update(delta_time)
            
            # Обновление систем
            try:
                self.event_system.update(delta_time, world_state, entities)
            except TypeError:
                self.event_system.update(delta_time)
            
            # Подготовка данных игрока для DDS
            player_data = {
                "success_rate": 0.5,
                "survival_time": getattr(self, "elapsed_time", 0.0),
                "enemies_defeated": 0,
                "damage_dealt": 0.0,
                "damage_taken": 0.0,
                "genetic_stability": 1.0,
                "emotional_balance": 1.0,
                "ai_adaptation": 0.5,
            }
            try:
                self.difficulty_system.update(delta_time, player_data, world_state)
            except TypeError:
                self.difficulty_system.update(delta_time)
            
            # Обновление Enhanced Edition систем
            try:
                # Обновление Enhanced Game Master
                if self.enhanced_game_master:
                    input_events = []  # В реальной игре здесь были бы события ввода
                    master_update_result = self.enhanced_game_master.update(delta_time, input_events)
                    
                    # Обработка событий от Enhanced Game Master
                    if master_update_result.get("events") and hasattr(self, 'enhanced_event_handler'):
                        for event in master_update_result["events"]:
                            self.enhanced_event_handler.handle_enhanced_event(event)
                
                if self.memory_system:
                    self.memory_system.cleanup_expired_memories()
                
                if self.enhanced_combat_system and self.player:
                    # Симуляция боевого контекста для обучения
                    from core.enhanced_combat_learning import CombatContext, CombatPhase, CombatTactic
                    combat_context = CombatContext(
                        entity_id=self.player.entity_id,
                        target_id="ENVIRONMENT",
                        current_phase=CombatPhase.ADAPT,
                        active_tactic=CombatTactic.ADAPTIVE_EVOLUTION,
                        health_percent=self.player.stats.health / self.player.stats.max_health,
                        stamina_percent=1.0,  # Упрощенно
                        distance_to_target=100.0,
                        target_health_percent=1.0,
                        environmental_hazards=[],
                        available_cover=[],
                        emotional_state="neutral",
                        combat_duration=delta_time,
                        pattern_success_history=[]
                    )
                    
                    # Получаем решение от системы боевого обучения
                    decision = self.enhanced_combat_system.make_combat_decision(
                        self.player.entity_id, 
                        combat_context
                    )
                    
                    # Имитируем результат для обучения
                    result = {"success": True, "experience_gained": 10}
                    self.enhanced_combat_system.learn_from_combat_result(
                        self.player.entity_id, 
                        combat_context, 
                        decision, 
                        result
                    )
                
                if self.skill_learning_ai and self.player:
                    # Обновляем AI обучения навыкам
                    self.skill_learning_ai.analyze_player_performance(
                        self.player.entity_id, 
                        {"combat_effectiveness": 0.8, "adaptation_rate": 0.6},
                        time.time()
                    )
                    
            except Exception as e:
                logger.debug(f"Ошибка обновления Enhanced Edition систем: {e}")
    
    def _render(self):
        """Отрисовка игры"""
        # Очистка экрана
        self.screen.fill(ColorScheme.BLACK)
        
        # Отрисовка в зависимости от состояния
        if self.game_state == GameState.MAIN_MENU:
            self._render_main_menu()
        elif self.game_state == GameState.PLAYING:
            self._render_game()
        elif self.game_state == GameState.PAUSED:
            self._render_pause_menu()
        elif self.game_state == GameState.INVENTORY:
            self._render_inventory()
        elif self.game_state == GameState.GENETICS:
            self._render_genetics()
        elif self.game_state == GameState.EMOTIONS:
            self._render_emotions()
        elif self.game_state == GameState.EVOLUTION:
            self._render_evolution()
        elif self.game_state == GameState.SETTINGS:
            self._render_settings()
        elif self.game_state == GameState.LOADING:
            self._render_loading()
        elif self.game_state == GameState.LEVEL_STATISTICS:
            self._render_level_statistics()
        elif self.game_state == GameState.NEXT_LEVEL:
            self._render_next_level()
        elif self.game_state == GameState.SAVE_MENU:
            self._render_save_slots()
        
        # Обновление экрана
        pygame.display.flip()
    
    def _render_main_menu(self):
        """Отрисовка главного меню"""
        # Заголовок
        title = self.fonts["large"].render("ЭВОЛЮЦИОННАЯ АДАПТАЦИЯ", True, ColorScheme.WHITE)
        subtitle = self.fonts["main"].render("ГЕНЕТИЧЕСКИЙ РЕЗОНАНС", True, ColorScheme.BLUE)
        
        title_rect = title.get_rect(center=(self.settings.window_width // 2, 150))
        subtitle_rect = subtitle.get_rect(center=(self.settings.window_width // 2, 200))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Кнопки
        button_texts = {
            "start_game": "НОВАЯ ИГРА",
            "continue_game": "ПРОДОЛЖИТЬ",
            "load_game": "ЗАГРУЗИТЬ ИГРУ",
            "settings": "НАСТРОЙКИ",
            "exit": "ВЫХОД"
        }
        
        for button_id, text in button_texts.items():
            button = self.buttons[button_id]
            color = ColorScheme.BLUE if button.collidepoint(pygame.mouse.get_pos()) else ColorScheme.GRAY
            
            pygame.draw.rect(self.screen, color, button)
            pygame.draw.rect(self.screen, ColorScheme.WHITE, button, 2)
            
            text_surf = self.fonts["main"].render(text, True, ColorScheme.WHITE)
            text_rect = text_surf.get_rect(center=button.center)
            self.screen.blit(text_surf, text_rect)
        
        # Информация о сохранениях
        self._render_save_slots_info()
    
    def _render_game(self):
        """Отрисовка игровой сцены"""
        # Очистка экрана
        self.screen.fill(ColorScheme.BLACK)
        
        # Отрисовка сетки тайлов (опционально)
        self.renderer.render_grid()
        
        # Отрисовка маяков
        self._render_beacons()
        
        # Отрисовка игрока
        if self.player and hasattr(self, 'player_sprite'):
            # Получаем изометрические координаты игрока
            iso_x, iso_y = self.isometric_projection.world_to_iso(
                self.player.position.x, self.player.position.y, self.player.position.z
            )
            
            # Центрируем позицию на экране
            screen_x = iso_x + self.settings.window_width // 2
            screen_y = iso_y + self.settings.window_height // 2
            
            # Обновляем позицию спрайта
            self.player_sprite.set_position(screen_x, screen_y)
            
            # Отрисовываем спрайт игрока
            self.player_sprite.render(self.screen)
        
        # Отрисовка врагов в изометрии
        for entity in self.entities:
            if hasattr(entity, 'position'):
                # Получаем изометрические координаты врага
                iso_x, iso_y = self.isometric_projection.world_to_iso(
                    entity.position.x, entity.position.y, entity.position.z
                )
                
                # Центрируем позицию на экране
                screen_x = iso_x + self.settings.window_width // 2
                screen_y = iso_y + self.settings.window_height // 2
                
                # Отрисовываем врага как простой круг
                pygame.draw.circle(self.screen, ColorScheme.RED, (int(screen_x), int(screen_y)), 10)
                
                # Отрисовываем имя врага
                if 'small' in self.fonts and hasattr(entity, 'name'):
                    name_text = self.fonts['small'].render(entity.name, True, ColorScheme.WHITE)
                    self.screen.blit(name_text, (int(screen_x) - 20, int(screen_y) - 25))
        
        # Отрисовка созданных объектов
        self._render_created_objects()
        
        # Отрисовка препятствий в изометрии
        for obstacle in self.obstacles:
            if 'position' in obstacle:
                pos = obstacle['position']
                iso_x, iso_y = self.isometric_projection.world_to_iso(pos[0], pos[1], pos[2])
                screen_x = iso_x + self.settings.window_width // 2
                screen_y = iso_y + self.settings.window_height // 2
                
                # Отрисовываем препятствие
                color = ColorScheme.ORANGE if obstacle.get('type') == 'trap' else ColorScheme.GRAY
                pygame.draw.rect(self.screen, color, (int(screen_x) - 5, int(screen_y) - 5, 10, 10))
        
        # Отрисовка сундуков в изометрии
        for chest in self.chests:
            if 'position' in chest:
                pos = chest['position']
                iso_x, iso_y = self.isometric_projection.world_to_iso(pos[0], pos[1], pos[2])
                screen_x = iso_x + self.settings.window_width // 2
                screen_y = iso_y + self.settings.window_height // 2
                
                # Отрисовываем сундук
                pygame.draw.rect(self.screen, ColorScheme.YELLOW, (int(screen_x) - 8, int(screen_y) - 8, 16, 16))
        
        # Отрисовка предметов на карте в изометрии
        for item in self.items:
            if 'position' in item:
                pos = item['position']
                iso_x, iso_y = self.isometric_projection.world_to_iso(pos[0], pos[1], pos[2])
                screen_x = iso_x + self.settings.window_width // 2
                screen_y = iso_y + self.settings.window_height // 2
                
                # Отрисовываем предмет
                pygame.draw.circle(self.screen, ColorScheme.GREEN, (int(screen_x), int(screen_y)), 5)
        
        # Отрисовка HUD: статус, инвентарь и гены (через выделенные классы)
        self.status_hud.render(self.player)
        try:
            from core.database_manager import database_manager
            self.inventory_hud.render(self.player, database_manager)
        except Exception:
            pass
        self.genetics_hud.render(self.player)
        self.ai_hud.render(self.player)
        
        # Отрисовка подсказки управления
        self._render_controls_help()
        
        # Отрисовка информации о маяках
        self._render_beacon_info()
    
    def _render_isometric_grid(self):
        """Отрисовка изометрической сетки"""
        # Увеличенная сетка для большого мира
        grid_size = 10000  # Увеличено с 10 до 100
        for x in range(-grid_size, grid_size + 1):
            for y in range(-grid_size, grid_size + 1):
                if (x + y) % 2 == 0:
                    self.isometric_renderer.render_tile(
                        self.screen, x, y, 'ground', (60, 60, 60)
                    )
                else:
                    self.isometric_renderer.render_tile(
                        self.screen, x, y, 'ground', (50, 50, 50)
                    )
    
    def _render_beacons(self):
        """Отрисовка маяков"""
        for beacon in self.beacon_system.beacons.values():
            # Получаем изометрические координаты маяка
            iso_x, iso_y = self.isometric_projection.world_to_iso(
                beacon.position[0], beacon.position[1], beacon.position[2]
            )
            
            # Центрируем позицию на экране
            screen_x = iso_x + self.settings.window_width // 2
            screen_y = iso_y + self.settings.window_height // 2
            
            # Отрисовываем маяк
            color = ColorScheme.BLUE if beacon.discovered else ColorScheme.GRAY
            pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), 15)
            
            # Отрисовываем ID маяка
            if 'small' in self.fonts:
                beacon_text = self.fonts['small'].render(f"B{beacon.id}", True, ColorScheme.WHITE)
                self.screen.blit(beacon_text, (int(screen_x) - 10, int(screen_y) - 8))
    
    def _render_beacon_info(self):
        """Отрисовка информации о маяках"""
        if 'small' in self.fonts:
            beacon_info = self.beacon_system.get_beacon_info()
            
            # Создаем полупрозрачную панель для информации
            panel_width = 300
            panel_height = 80
            panel = pygame.Surface((panel_width, panel_height))
            panel.set_alpha(180)
            panel.fill(ColorScheme.DARK_GRAY)
            self.screen.blit(panel, (10, self.settings.window_height - panel_height - 10))
            
            y_offset = self.settings.window_height - panel_height + 10
            info_texts = [
                f"Маяков обнаружено: {beacon_info['discovered_beacons']}/{beacon_info['total_beacons']}",
                f"Активная цель: {beacon_info['active_target'] or 'Нет'}"
            ]
            
            for i, text in enumerate(info_texts):
                info_surface = self.fonts['small'].render(text, True, ColorScheme.WHITE)
                self.screen.blit(info_surface, (20, y_offset + i * 20))
    
    def _render_created_objects(self):
        """Отрисовка созданных объектов"""
        try:
            if not hasattr(self, 'object_creation'):
                return
            
            # Получаем все активные объекты
            all_objects = []
            for obj_type in self.object_creation.templates.keys():
                objects = self.object_creation.get_objects_by_type(obj_type)
                all_objects.extend(objects)
            
            # Отрисовываем каждый объект
            for obj in all_objects:
                if not obj.is_visible or not obj.is_active:
                    continue
                
                # Определяем цвет объекта
                color = obj.appearance.get('color', (128, 128, 128))
                size = obj.appearance.get('size', 10.0)
                
                # Отрисовываем в изометрии
                self.isometric_renderer.render_entity(
                    self.screen,
                    obj.position,
                    color,
                    size=int(size)
                )
                
                # Отрисовываем имя объекта
                if 'small' in self.fonts and obj.name:
                    iso_x, iso_y = self.isometric_projection.world_to_iso(*obj.position)
                    iso_x += self.settings.window_width // 2
                    iso_y += self.settings.window_height // 2
                    
                    name_text = self.fonts['small'].render(obj.name, True, ColorScheme.WHITE)
                    self.screen.blit(name_text, (int(iso_x) - 20, int(iso_y) - 40))
                    
        except Exception as e:
            logger.error(f"Ошибка отрисовки созданных объектов: {e}")
    
    def _render_status_panel(self):
        """Отрисовка панели состояния"""
        if not self.player:
            return
        
        # Панель состояния (полупрозрачная)
        panel_surface = pygame.Surface((300, 200))
        panel_surface.set_alpha(180)
        panel_surface.fill(ColorScheme.DARK_GRAY)
        self.screen.blit(panel_surface, (10, 10))
        
        # Заголовок панели
        if 'main' in self.fonts:
            title = self.fonts['main'].render("СТАТУС ИГРОКА", True, ColorScheme.WHITE)
            self.screen.blit(title, (20, 15))
        
        # Статистика игрока
        if 'small' in self.fonts:
            y_offset = 40
            
            # Здоровье
            try:
                health = getattr(self.player.stats, 'health', 100)
                max_health = getattr(self.player.stats, 'max_health', 100)
                health_text = self.fonts['small'].render(f"Здоровье: {health:.0f}/{max_health:.0f}", True, ColorScheme.HEALTH_COLOR)
                self.screen.blit(health_text, (20, y_offset))
                y_offset += 20
            except Exception as e:
                logger.debug(f"Ошибка отображения элемента HUD: {e}")
            
            # Мана
            try:
                mana = getattr(self.player.stats, 'mana', 100)
                max_mana = getattr(self.player.stats, 'max_mana', 100)
                mana_text = self.fonts['small'].render(f"Мана: {mana:.0f}/{max_mana:.0f}", True, ColorScheme.ENERGY_COLOR)
                self.screen.blit(mana_text, (20, y_offset))
                y_offset += 20
            except Exception as e:
                logger.debug(f"Ошибка отображения элемента HUD: {e}")
            
            # Выносливость
            try:
                stamina = getattr(self.player.stats, 'stamina', 100)
                max_stamina = getattr(self.player.stats, 'max_stamina', 100)
                stamina_text = self.fonts['small'].render(f"Выносливость: {stamina:.0f}/{max_stamina:.0f}", True, ColorScheme.STAMINA_COLOR)
                self.screen.blit(stamina_text, (20, y_offset))
                y_offset += 20
            except Exception as e:
                logger.debug(f"Ошибка отображения элемента HUD: {e}")
            
            # Позиция
            pos_text = self.fonts['small'].render(f"Позиция: ({int(self.player.position.x)}, {int(self.player.position.y)})", True, ColorScheme.WHITE)
            self.screen.blit(pos_text, (20, y_offset))
            y_offset += 20
            
            # Статус автономного движения
            auto_status = "ВКЛ" if getattr(self, 'autonomous_movement_enabled', True) else "ВЫКЛ"
            auto_color = ColorScheme.GREEN if getattr(self, 'autonomous_movement_enabled', True) else ColorScheme.RED
            auto_text = self.fonts['small'].render(f"Автономность: {auto_status}", True, auto_color)
            self.screen.blit(auto_text, (20, y_offset))
            y_offset += 20
            
            # Уровень обучения ИИ
            try:
                ai_level = getattr(self.player_ai, 'learning_level', 1)
                ai_text = self.fonts['small'].render(f"Уровень ИИ: {ai_level}", True, ColorScheme.GENETIC_COLOR)
                self.screen.blit(ai_text, (20, y_offset))
                y_offset += 20
            except Exception as e:
                logger.debug(f"Ошибка отображения элемента HUD: {e}")
            
            # Количество врагов
            enemies_text = self.fonts['small'].render(f"Врагов: {len(self.entities)}", True, ColorScheme.RED)
            self.screen.blit(enemies_text, (20, y_offset))
            y_offset += 20
            
            # Количество препятствий
            obstacles_text = self.fonts['small'].render(f"Препятствий: {len(self.obstacles)}", True, ColorScheme.ORANGE)
            self.screen.blit(obstacles_text, (20, y_offset))
            y_offset += 20
            
            # Количество созданных объектов
            if hasattr(self, 'object_creation'):
                created_objects_count = len([obj for obj in self.object_creation.created_objects.values() if obj.is_active])
                created_text = self.fonts['small'].render(f"Созданных объектов: {created_objects_count}", True, ColorScheme.PURPLE)
                self.screen.blit(created_text, (20, y_offset))
                y_offset += 20
            
            # Информация о компьютерном зрении
            if hasattr(self, 'computer_vision'):
                vision_analysis = self.computer_vision.get_visual_analysis()
                detected_objects = vision_analysis.get('detected_objects', 0)
                threat_level = vision_analysis.get('threat_level', 0.0)
                vision_text = self.fonts['small'].render(f"Объектов видно: {detected_objects}, Угроза: {threat_level:.1f}", True, ColorScheme.BLUE)
                self.screen.blit(vision_text, (20, y_offset))
            y_offset += 20
            
            # Количество сундуков
            chests_text = self.fonts['small'].render(f"Сундуков: {len(self.chests)}", True, ColorScheme.YELLOW)
            self.screen.blit(chests_text, (20, y_offset))
    
    def _render_controls_help(self):
        """Отрисовка подсказки управления"""
        if 'small' in self.fonts:
            # Создаем полупрозрачную панель для подсказок
            panel_width = 400
            panel_height = 200
            panel = pygame.Surface((panel_width, panel_height))
            panel.set_alpha(180)
            panel.fill(ColorScheme.DARK_GRAY)
            self.screen.blit(panel, (self.settings.window_width - panel_width - 10, self.settings.window_height - panel_height - 100))
            
            y_offset = self.settings.window_height - panel_height - 80
            controls = [
                "Управление:",
                "WASD/Стрелки - Движение",
                "C - Центрировать камеру",
                "M - Навигация к маяку",
                "1-4 - Создание объектов",
                "5-8 - Эмоции",
                "I - Инвентарь",
                "G - Гены",
                "E - Эмоции",
                "V - Эволюция",
                "Пробел - Автономность"
            ]
            
            for i, control in enumerate(controls):
                color = ColorScheme.YELLOW if i == 0 else ColorScheme.WHITE
                control_surface = self.fonts['small'].render(control, True, color)
                self.screen.blit(control_surface, (self.settings.window_width - panel_width, y_offset + i * 18))
    
    def _render_entity(self, entity, screen_pos):
        """Отрисовка сущности"""
        # Простая отрисовка круга
        color = ColorScheme.GREEN if entity.type == "player" else ColorScheme.RED
        pygame.draw.circle(self.screen, color, (int(screen_pos[0]), int(screen_pos[1])), 20)
        
        # Имя сущности
        name = self.fonts["small"].render(entity.name, True, ColorScheme.WHITE)
        name_rect = name.get_rect(center=(screen_pos[0], screen_pos[1] - 30))
        self.screen.blit(name, name_rect)
    
    def _render_game_ui(self):
        """Отрисовка игрового UI"""
        # Панель статистики
        self._render_stats_panel()
        
        # Панель инвентаря
        self._render_inventory_panel()
        
        # Панель генетики
        self._render_genetics_panel()
        
        # Панель эмоций
        self._render_emotions_panel()
    
    def _render_stats_panel(self):
        """Отрисовка панели статистики"""
        panel = self.panels["stats"]
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 2)
        
        title = self.fonts["main"].render("СТАТИСТИКА", True, ColorScheme.WHITE)
        self.screen.blit(title, (panel.x + 10, panel.y + 10))
        
        if self.player:
            # Здоровье
            health_text = f"Здоровье: {self.player.stats.health:.0f}/{self.player.stats.max_health:.0f}"
            health_surf = self.fonts["small"].render(health_text, True, ColorScheme.HEALTH_COLOR)
            self.screen.blit(health_surf, (panel.x + 10, panel.y + 40))
            
            # Мана
            mana_text = f"Мана: {self.player.stats.mana:.0f}/{self.player.stats.max_mana:.0f}"
            mana_surf = self.fonts["small"].render(mana_text, True, ColorScheme.ENERGY_COLOR)
            self.screen.blit(mana_surf, (panel.x + 10, panel.y + 60))
            
            # Выносливость
            stam_text = f"Выносливость: {self.player.stats.stamina:.0f}/{self.player.stats.max_stamina:.0f}"
            stam_surf = self.fonts["small"].render(stam_text, True, ColorScheme.STAMINA_COLOR)
            self.screen.blit(stam_surf, (panel.x + 10, panel.y + 80))
            
            # Уровень персонажа
            level_value = getattr(self.player, 'level', getattr(self.player.stats, 'level', 1))
            level_text = f"Уровень: {level_value}"
            level_surf = self.fonts["small"].render(level_text, True, ColorScheme.WHITE)
            self.screen.blit(level_surf, (panel.x + 10, panel.y + 100))
            
            # Enhanced Edition информация
            if self.memory_system:
                y_pos = 130
                # Память поколений
                try:
                    memory_stats = self.memory_system.get_memory_statistics()
                    memory_text = f"Поколение: {memory_stats['current_generation']}"
                    memory_surf = self.fonts["small"].render(memory_text, True, ColorScheme.EVOLUTION_COLOR)
                    self.screen.blit(memory_surf, (panel.x + 10, panel.y + y_pos))
                    
                    # Количество воспоминаний
                    total_memories = memory_stats['total_memories']
                    memories_text = f"Воспоминания: {total_memories}"
                    memories_surf = self.fonts["small"].render(memories_text, True, ColorScheme.GENETIC_COLOR)
                    self.screen.blit(memories_surf, (panel.x + 10, panel.y + y_pos + 20))
                    
                except Exception as e:
                    pass
            
            # Информация о навыках
            if self.skill_manager:
                try:
                    learned_skills = len(getattr(self.skill_manager, 'learned_skills', []))
                    skills_text = f"Навыки: {learned_skills}"
                    skills_surf = self.fonts["small"].render(skills_text, True, ColorScheme.BLUE)
                    self.screen.blit(skills_surf, (panel.x + 10, panel.y + 170))
                except Exception as e:
                    pass
    
    def _render_inventory_panel(self):
        """Отрисовка панели инвентаря"""
        panel = self.panels["inventory"]
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 2)
        
        title = self.fonts["main"].render("ИНВЕНТАРЬ", True, ColorScheme.WHITE)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 20))
        self.screen.blit(title, title_rect)
        
        if self.player and hasattr(self.player, 'inventory_system'):
            try:
                inventory = self.player.inventory_system.get_inventory_data()
                y_offset = 50
                
                if inventory:
                    # Координаты для отрисовки и хитбоксов
                    mouse_pos = pygame.mouse.get_pos()
                    self._inventory_item_rects = []
                    for i, (item_id, quantity) in enumerate(list(inventory.items())[:8]):
                        from core.database_manager import database_manager
                        item_info = database_manager.get_item(item_id)
                        weapon_info = database_manager.get_weapon(item_id)
                        item_name = (item_info or weapon_info or {}).get("name", item_id)
                        item_text = f"{item_name} x{quantity}"
                        item_surf = self.fonts["small"].render(item_text, True, ColorScheme.WHITE)
                        draw_y = panel.y + y_offset + i * 22
                        self.screen.blit(item_surf, (panel.x + 10, draw_y))
                        # Сохраняем прямоугольник для наведения
                        rect = item_surf.get_rect(topleft=(panel.x + 10, draw_y))
                        self._inventory_item_rects.append((rect, item_id))
                    
                    # Подсказка при наведении
                    for rect, item_id in self._inventory_item_rects:
                        if rect.collidepoint(mouse_pos):
                            from core.database_manager import database_manager
                            info = database_manager.get_item(item_id) or database_manager.get_weapon(item_id) or {}
                            tooltip_lines = []
                            if "name" in info:
                                tooltip_lines.append(info["name"])
                            if "rarity" in info:
                                tooltip_lines.append(f"Редкость: {info['rarity']}")
                            if "value" in info:
                                tooltip_lines.append(f"Цена: {info['value']}")
                            if "damage" in info:
                                tooltip_lines.append(f"Урон: {info['damage']}")
                            if "effects" in info and info["effects"]:
                                tooltip_lines.append(f"Эффекты: {', '.join(info['effects'])}")
                            self._render_tooltip(mouse_pos, tooltip_lines)
                else:
                    empty_text = self.fonts["small"].render("Инвентарь пуст", True, ColorScheme.GRAY)
                    self.screen.blit(empty_text, (panel.x + 10, panel.y + y_offset))
                
                # Общий вес инвентаря
                try:
                    total_weight = getattr(self.player.inventory_system, 'total_weight', 0)
                    weight_text = f"Вес: {total_weight:.1f}"
                    weight_surf = self.fonts["small"].render(weight_text, True, ColorScheme.LIGHT_GRAY)
                    self.screen.blit(weight_surf, (panel.x + 10, panel.y + 150))
                except Exception as e:
                    logger.debug(f"Ошибка отображения веса инвентаря: {e}")
                    
            except Exception as e:
                error_text = f"Ошибка инвентаря: {str(e)[:20]}"
                error_surf = self.fonts["small"].render(error_text, True, ColorScheme.RED)
                self.screen.blit(error_surf, (panel.x + 10, panel.y + 50))
    
    def _render_genetics_panel(self):
        """Отрисовка панели генетики"""
        panel = self.panels["genetics"]
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 2)
        
        title = self.fonts["main"].render("ГЕНЕТИКА", True, ColorScheme.GENETIC_COLOR)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 20))
        self.screen.blit(title, title_rect)
        
        if self.player:
            y_offset = 50
            
            try:
                # Активные гены
                active_genes = getattr(self.player.genetic_system, 'active_genes', [])
                genes_text = f"Активные гены: {len(active_genes)}"
                genes_surf = self.fonts["small"].render(genes_text, True, ColorScheme.GENETIC_COLOR)
                self.screen.blit(genes_surf, (panel.x + 10, panel.y + y_offset))
                y_offset += 20
                
                # Показываем первые 3 гена
                for i, gene in enumerate(active_genes[:3]):
                    gene_text = f"Ген {i+1}: {gene}"
                    gene_surf = self.fonts["small"].render(gene_text, True, ColorScheme.LIGHT_GRAY)
                    self.screen.blit(gene_surf, (panel.x + 10, panel.y + y_offset))
                    y_offset += 15
                
                y_offset += 5
                
                # Мутационный уровень
                mutation_level = getattr(self.player, 'mutation_level', 0.0)
                mutation_text = f"Мутации: {mutation_level:.2f}"
                mutation_surf = self.fonts["small"].render(mutation_text, True, ColorScheme.GENETIC_COLOR)
                self.screen.blit(mutation_surf, (panel.x + 10, panel.y + y_offset))
                y_offset += 20
                
                # Генетическая стабильность
                genetic_stability = getattr(self.player, 'genetic_stability', 1.0)
                stability_text = f"Стабильность: {genetic_stability:.2f}"
                stability_surf = self.fonts["small"].render(stability_text, True, ColorScheme.GENETIC_COLOR)
                self.screen.blit(stability_surf, (panel.x + 10, panel.y + y_offset))
                
            except Exception as e:
                error_text = f"Ошибка генетики: {str(e)[:20]}"
                error_surf = self.fonts["small"].render(error_text, True, ColorScheme.RED)
                self.screen.blit(error_surf, (panel.x + 10, panel.y + 50))

    def _render_tooltip(self, mouse_pos, lines):
        """Отрисовка всплывающей подсказки возле курсора"""
        if not lines:
            return
        padding = 8
        max_w = 0
        surfaces = []
        for line in lines:
            surf = self.fonts["small"].render(str(line), True, ColorScheme.WHITE)
            surfaces.append(surf)
            max_w = max(max_w, surf.get_width())
        height = sum(s.get_height() for s in surfaces) + padding * 2
        width = max_w + padding * 2
        x, y = mouse_pos
        tooltip_rect = pygame.Rect(x + 16, y + 16, width, height)
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, tooltip_rect)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, tooltip_rect, 1)
        cy = tooltip_rect.y + padding
        for surf in surfaces:
            self.screen.blit(surf, (tooltip_rect.x + padding, cy))
            cy += surf.get_height()
    
    def _render_emotions_panel(self):
        """Отрисовка панели эмоций"""
        panel = self.panels["emotions"]
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 2)
        
        title = self.fonts["main"].render("ЭМОЦИИ", True, ColorScheme.WHITE)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 20))
        self.screen.blit(title, title_rect)
        
        if self.player:
            emotion = self.player.emotion_system.current_state.get_dominant_emotion()
            if emotion:
                emotion_text = f"Доминирующая: {emotion}"
                emotion_surf = self.fonts["small"].render(emotion_text, True, ColorScheme.EMOTION_COLOR)
                self.screen.blit(emotion_surf, (panel.x + 10, panel.y + 50))
            
            # Эмоциональный баланс
            try:
                balance = self.player.emotion_system.current_state.get_emotional_balance()
                balance_text = f"Баланс: {balance:.2f}"
                balance_surf = self.fonts["small"].render(balance_text, True, ColorScheme.EMOTION_COLOR)
                self.screen.blit(balance_surf, (panel.x + 10, panel.y + 70))
            except Exception as e:
                logger.debug(f"Ошибка отображения элемента HUD: {e}")
            
            # Текущие эмоции
            try:
                emotions = self.player.emotion_system.current_state.get_all_emotions()
                y_offset = 90
                for i, (emotion_name, intensity) in enumerate(emotions.items()[:3]):
                    emotion_text = f"{emotion_name}: {intensity:.1f}"
                    emotion_surf = self.fonts["small"].render(emotion_text, True, ColorScheme.LIGHT_GRAY)
                    self.screen.blit(emotion_surf, (panel.x + 10, panel.y + y_offset + i * 20))
            except Exception as e:
                logger.debug(f"Ошибка отображения элемента HUD: {e}")
    
    def _render_pause_menu(self):
        """Отрисовка меню паузы"""
        # Полупрозрачный фон
        overlay = pygame.Surface((self.settings.window_width, self.settings.window_height))
        overlay.set_alpha(128)
        overlay.fill(ColorScheme.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Текст паузы
        pause_text = self.fonts["large"].render("ПАУЗА", True, ColorScheme.WHITE)
        pause_rect = pause_text.get_rect(center=(self.settings.window_width // 2, 200))
        self.screen.blit(pause_text, pause_rect)
        
        # Кнопки меню паузы
        button_width = 300
        button_height = 50
        start_x = (self.settings.window_width - button_width) // 2
        start_y = 300
        
        pause_buttons = {
            "resume": pygame.Rect(start_x, start_y, button_width, button_height),
            "save": pygame.Rect(start_x, start_y + 70, button_width, button_height),
            "load": pygame.Rect(start_x, start_y + 140, button_width, button_height),
            "settings": pygame.Rect(start_x, start_y + 210, button_width, button_height),
            "main_menu": pygame.Rect(start_x, start_y + 280, button_width, button_height)
        }
        
        button_texts = {
            "resume": "ПРОДОЛЖИТЬ",
            "save": "СОХРАНИТЬ ИГРУ",
            "load": "ЗАГРУЗИТЬ ИГРУ",
            "settings": "НАСТРОЙКИ",
            "main_menu": "ГЛАВНОЕ МЕНЮ"
        }
        
        for button_id, button in pause_buttons.items():
            color = ColorScheme.BLUE if button.collidepoint(pygame.mouse.get_pos()) else ColorScheme.GRAY
            
            pygame.draw.rect(self.screen, color, button)
            pygame.draw.rect(self.screen, ColorScheme.WHITE, button, 2)
            
            text_surf = self.fonts["main"].render(button_texts[button_id], True, ColorScheme.WHITE)
            text_rect = text_surf.get_rect(center=button.center)
            self.screen.blit(text_surf, text_rect)
        
        # Сохраняем кнопки для обработки кликов
        self.pause_buttons = pause_buttons
        
        # Информация о текущем состоянии
        if self.player:
            status_text = f"Уровень: {getattr(self, 'current_cycle', 1)} | Позиция: ({int(self.player.position.x)}, {int(self.player.position.y)})"
            status_surf = self.fonts["small"].render(status_text, True, ColorScheme.LIGHT_GRAY)
            status_rect = status_surf.get_rect(center=(self.settings.window_width // 2, 400))
            self.screen.blit(status_surf, status_rect)
    
    def _render_inventory(self):
        """Отрисовка инвентаря"""
        self._render_game()  # Фон игры
        
        # Панель инвентаря
        panel_width = 600
        panel_height = 400
        panel = pygame.Rect((self.settings.window_width - panel_width) // 2, 
                           (self.settings.window_height - panel_height) // 2, 
                           panel_width, panel_height)
        
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 3)
        
        title = self.fonts["large"].render("ИНВЕНТАРЬ", True, ColorScheme.WHITE)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 30))
        self.screen.blit(title, title_rect)
        
        # Отображение предметов в инвентаре
        if self.player and hasattr(self.player, 'inventory_system'):
            inventory = self.player.inventory_system.get_inventory_data()
            y_offset = 80
            
            if inventory:
                for i, (item_id, quantity) in enumerate(inventory.items()):
                    if i >= 10:  # Показываем только первые 10 предметов
                        break
                    
                    # Получаем информацию о предмете
                    from core.database_manager import database_manager
                    item_info = database_manager.get_item(item_id)
                    weapon_info = database_manager.get_weapon(item_id)
                    
                    if item_info:
                        item_name = item_info.get("name", item_id)
                        item_desc = item_info.get("description", "")
                    elif weapon_info:
                        item_name = weapon_info.get("name", item_id)
                        item_desc = "Оружие"
                    else:
                        item_name = item_id
                        item_desc = "Неизвестный предмет"
                    
                    # Отображаем предмет
                    item_text = f"{item_name} x{quantity}"
                    item_surf = self.fonts["main"].render(item_text, True, ColorScheme.WHITE)
                    self.screen.blit(item_surf, (panel.x + 20, panel.y + y_offset + i * 30))
                    
                    # Описание предмета
                    desc_surf = self.fonts["small"].render(item_desc, True, ColorScheme.GRAY)
                    self.screen.blit(desc_surf, (panel.x + 20, panel.y + y_offset + i * 30 + 20))
            else:
                empty_text = self.fonts["main"].render("Инвентарь пуст", True, ColorScheme.GRAY)
                self.screen.blit(empty_text, (panel.x + 20, panel.y + y_offset))
    
    def _render_genetics(self):
        """Отрисовка генетической панели"""
        self._render_game()  # Фон игры
        
        # Панель генетики
        panel_width = 800
        panel_height = 500
        panel = pygame.Rect((self.settings.window_width - panel_width) // 2, 
                           (self.settings.window_height - panel_height) // 2, 
                           panel_width, panel_height)
        
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 3)
        
        title = self.fonts["large"].render("ГЕНЕТИЧЕСКАЯ ИНЖЕНЕРИЯ", True, ColorScheme.GENETIC_COLOR)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 30))
        self.screen.blit(title, title_rect)
        
        if self.player:
            # Активные гены
            genes = self.player.genetic_system.active_genes
            y_offset = 80
            for i, gene in enumerate(genes[:10]):  # Показываем первые 10
                gene_text = f"Ген {i+1}: {gene}"
                gene_surf = self.fonts["small"].render(gene_text, True, ColorScheme.GENETIC_COLOR)
                self.screen.blit(gene_surf, (panel.x + 20, panel.y + y_offset + i * 25))
    
    def _render_emotions(self):
        """Отрисовка эмоциональной панели"""
        self._render_game()  # Фон игры
        
        # Панель эмоций
        panel_width = 700
        panel_height = 450
        panel = pygame.Rect((self.settings.window_width - panel_width) // 2, 
                           (self.settings.window_height - panel_height) // 2, 
                           panel_width, panel_height)
        
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 3)
        
        title = self.fonts["large"].render("ЭМОЦИОНАЛЬНОЕ СОСТОЯНИЕ", True, ColorScheme.EMOTION_COLOR)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 30))
        self.screen.blit(title, title_rect)
        
        if self.player:
            # Текущие эмоции
            state = self.player.emotion_system.current_state
            y_offset = 80
            
            if state.primary_emotion:
                primary_text = f"Основная эмоция: {state.primary_emotion}"
                primary_surf = self.fonts["main"].render(primary_text, True, ColorScheme.EMOTION_COLOR)
                self.screen.blit(primary_surf, (panel.x + 20, panel.y + y_offset))
                y_offset += 40
            
            # Эмоциональный баланс
            balance = state.get_emotional_balance()
            balance_text = f"Эмоциональный баланс: {balance:.2f}"
            balance_surf = self.fonts["main"].render(balance_text, True, ColorScheme.EMOTION_COLOR)
            self.screen.blit(balance_surf, (panel.x + 20, panel.y + y_offset))
    
    def _render_evolution(self):
        """Отрисовка панели эволюции"""
        self._render_game()  # Фон игры
        
        # Панель эволюции
        panel_width = 750
        panel_height = 480
        panel = pygame.Rect((self.settings.window_width - panel_width) // 2, 
                           (self.settings.window_height - panel_height) // 2, 
                           panel_width, panel_height)
        
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 3)
        
        title = self.fonts["large"].render("ЭВОЛЮЦИОННЫЙ ЦИКЛ", True, ColorScheme.EVOLUTION_COLOR)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 30))
        self.screen.blit(title, title_rect)
        
        # Информация о цикле
        cycle_text = f"Текущий цикл: {self.current_cycle}"
        cycle_surf = self.fonts["main"].render(cycle_text, True, ColorScheme.EVOLUTION_COLOR)
        self.screen.blit(cycle_surf, (panel.x + 20, panel.y + 80))
        
        # Прогресс цикла
        progress_text = "Прогресс исследования: 0%"
        progress_surf = self.fonts["main"].render(progress_text, True, ColorScheme.WHITE)
        self.screen.blit(progress_surf, (panel.x + 20, panel.y + 120))
    
    def _render_settings(self):
        """Отрисовка настроек"""
        # Заголовок
        title = self.fonts["large"].render("НАСТРОЙКИ", True, ColorScheme.WHITE)
        title_rect = title.get_rect(center=(self.settings.window_width // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Настройки
        settings_text = [
            "Громкость музыки: 70%",
            "Громкость звуков: 80%",
            "Разрешение: 1280x720",
            "Полноэкранный режим: Выкл",
            "Сложность: Нормальная"
        ]
        
        y_offset = 250
        for i, text in enumerate(settings_text):
            setting_surf = self.fonts["main"].render(text, True, ColorScheme.WHITE)
            setting_rect = setting_surf.get_rect(center=(self.settings.window_width // 2, y_offset + i * 40))
            self.screen.blit(setting_surf, setting_rect)
        
        # Кнопка возврата
        back_button = pygame.Rect((self.settings.window_width - 200) // 2, 500, 200, 50)
        color = ColorScheme.BLUE if back_button.collidepoint(pygame.mouse.get_pos()) else ColorScheme.GRAY
        pygame.draw.rect(self.screen, color, back_button)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, back_button, 2)
        
        back_text = self.fonts["main"].render("НАЗАД", True, ColorScheme.WHITE)
        back_rect = back_text.get_rect(center=back_button.center)
        self.screen.blit(back_text, back_rect)
        
        # Сохраняем кнопку для обработки кликов
        if not hasattr(self, 'settings_buttons'):
            self.settings_buttons = {}
        self.settings_buttons["back"] = back_button
        
        # Инструкция
        instruction_text = self.fonts["small"].render("Настройки пока не изменяемы", True, ColorScheme.LIGHT_GRAY)
        instruction_rect = instruction_text.get_rect(center=(self.settings.window_width // 2, 600))
        self.screen.blit(instruction_text, instruction_rect)
    
    def _render_loading(self):
        """Отрисовка экрана загрузки"""
        # Заголовок
        title = self.fonts["large"].render("ЗАГРУЗКА ИГРЫ", True, ColorScheme.WHITE)
        title_rect = title.get_rect(center=(self.settings.window_width // 2, self.settings.window_height // 2 - 50))
        self.screen.blit(title, title_rect)
        
        # Индикатор загрузки
        loading_text = self.fonts["main"].render("Создание мира...", True, ColorScheme.BLUE)
        loading_rect = loading_text.get_rect(center=(self.settings.window_width // 2, self.settings.window_height // 2))
        self.screen.blit(loading_text, loading_rect)
    
    def _update_fps_counter(self):
        """Обновление счетчика FPS"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_update >= 1.0:
            self.fps_counter = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
        
        # Отображение FPS
        fps_text = self.fonts["small"].render(f"FPS: {self.fps_counter}", True, ColorScheme.GRAY)
        self.screen.blit(fps_text, (10, self.settings.window_height - 30))
    
    def _create_trap(self):
        """Создание ловушки"""
        try:
            if self.player and hasattr(self.player, 'position'):
                # Создание ловушки рядом с игроком
                trap_position = (
                    self.player.position.x + random.randint(-50, 50),
                    self.player.position.y + random.randint(-50, 50),
                    0
                )
                
                trap = {
                    'id': f"TRAP_{len(self.obstacles):03d}",
                    'type': 'trap',
                    'position': trap_position,
                    'damage': 20,
                    'active': True,
                    'triggered': False
                }
                
                self.obstacles.append(trap)
                print(f"Ловушка создана в позиции {trap_position}")
                
                # Обновляем мир для ИИ
                if hasattr(self, 'player_ai'):
                    self.player_ai.update_environment_info(self.player, self)
        except Exception as e:
            print(f"Ошибка создания ловушки: {e}")
    
    def _create_geo_barrier(self):
        """Создание геобарьера"""
        try:
            if self.player and hasattr(self.player, 'position'):
                # Создание геобарьера рядом с игроком
                barrier_position = (
                    self.player.position.x + random.randint(-100, 100),
                    self.player.position.y + random.randint(-100, 100),
                    0
                )
                
                barrier = {
                    'id': f"BARRIER_{len(self.obstacles):03d}",
                    'type': 'geo_barrier',
                    'position': barrier_position,
                    'width': 80,
                    'height': 80,
                    'active': True,
                    'blocking': True
                }
                
                self.obstacles.append(barrier)
                print(f"Геобарьер создан в позиции {barrier_position}")
                
                # Обновляем мир для ИИ
                if hasattr(self, 'player_ai'):
                    self.player_ai.update_environment_info(self.player, self)
        except Exception as e:
            print(f"Ошибка создания геобарьера: {e}")
    
    def _create_chest(self):
        """Создание сундука с предметами"""
        try:
            if self.player and hasattr(self.player, 'position'):
                # Создание сундука рядом с игроком
                chest_position = (
                    self.player.position.x + random.randint(-80, 80),
                    self.player.position.y + random.randint(-80, 80),
                    0
                )
                
                # Генерация случайных предметов для сундука
                chest_items = []
                num_items = random.randint(1, 3)
                for _ in range(num_items):
                    item_id = random.choice(['health_potion', 'mana_potion', 'weapon_sword', 'armor_leather'])
                    chest_items.append({
                        'item_id': item_id,
                        'quantity': random.randint(1, 3)
                    })
                
                chest = {
                    'id': f"CHEST_{len(self.chests):03d}",
                    'type': 'chest',
                    'position': chest_position,
                    'items': chest_items,
                    'opened': False,
                    'locked': random.choice([True, False])
                }
                
                self.chests.append(chest)
                print(f"Сундук создан в позиции {chest_position} с {len(chest_items)} предметами")
                
                # Обновляем мир для ИИ
                if hasattr(self, 'player_ai'):
                    self.player_ai.update_environment_info(self.player, self)
        except Exception as e:
            print(f"Ошибка создания сундука: {e}")
    
    def _add_enemy(self):
        """Добавление врага на карту"""
        try:
            if self.player and hasattr(self.player, 'position'):
                # Создание врага рядом с игроком
                enemy_position = (
                    self.player.position.x + random.randint(-150, 150),
                    self.player.position.y + random.randint(-150, 150),
                    0
                )
                
                enemy = AdvancedGameEntity(
                    entity_id=f"ENEMY_{len(self.entities):03d}",
                    entity_type="enemy",
                    name=f"Враг {len(self.entities)+1}",
                    position=enemy_position
                )
                
                self.entities.append(enemy)
                print(f"Враг добавлен в позиции {enemy_position}")
                
                # Обновляем мир для ИИ
                if hasattr(self, 'player_ai'):
                    self.player_ai.update_environment_info(self.player, self)
        except Exception as e:
            print(f"Ошибка добавления врага: {e}")
    
    def _activate_emotion(self, emotion_type: str):
        """Активация доминирующей эмоции"""
        try:
            if hasattr(self, 'player_ai') and hasattr(self.player_ai, 'personality'):
                # Временное изменение личности ИИ
                if emotion_type == "aggression":
                    self.player_ai.personality.aggression = 0.9
                    self.player_ai.personality.caution = 0.1
                    print("Активирована эмоция: Агрессия")
                elif emotion_type == "curiosity":
                    self.player_ai.personality.curiosity = 0.9
                    self.player_ai.personality.caution = 0.3
                    print("Активирована эмоция: Любопытство")
                elif emotion_type == "caution":
                    self.player_ai.personality.caution = 0.9
                    self.player_ai.personality.aggression = 0.1
                    print("Активирована эмоция: Осторожность")
                elif emotion_type == "social":
                    self.player_ai.personality.social = 0.9
                    self.player_ai.personality.aggression = 0.2
                    print("Активирована эмоция: Социальность")
                
                # Сброс эмоции через некоторое время
                import threading
                import time
                def reset_emotion():
                    time.sleep(10)  # 10 секунд
                    self.player_ai.personality.aggression = 0.5
                    self.player_ai.personality.curiosity = 0.5
                    self.player_ai.personality.caution = 0.5
                    self.player_ai.personality.social = 0.5
                    print("Эмоция сброшена")
                
                thread = threading.Thread(target=reset_emotion)
                thread.daemon = True
                thread.start()
        except Exception as e:
            print(f"Ошибка активации эмоции: {e}")
    
    def _render_minimap(self):
        """Отрисовка мини-карты"""
        if not self.player:
            return
        
        # Размер мини-карты
        minimap_size = 150
        minimap_x = self.settings.window_width - minimap_size - 20
        minimap_y = 230  # Перемещаем ниже панели инвентаря
        
        # Фон мини-карты
        minimap_surface = pygame.Surface((minimap_size, minimap_size))
        minimap_surface.set_alpha(200)
        minimap_surface.fill(ColorScheme.DARK_GRAY)
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))
        
        # Рамка мини-карты
        pygame.draw.rect(self.screen, ColorScheme.WHITE, 
                        (minimap_x, minimap_y, minimap_size, minimap_size), 2)
        
        # Заголовок мини-карты
        if 'small' in self.fonts:
            title = self.fonts['small'].render("МИНИ-КАРТА", True, ColorScheme.WHITE)
            self.screen.blit(title, (minimap_x + 5, minimap_y + 5))
        
        # Масштаб для мини-карты
        scale = minimap_size / 1000  # 1000 - размер мира
        
        # Отрисовка игрока на мини-карте
        player_x = minimap_x + (self.player.position.x + 500) * scale
        player_y = minimap_y + (self.player.position.y + 500) * scale
        pygame.draw.circle(self.screen, ColorScheme.GREEN, (int(player_x), int(player_y)), 4)
        
        # Отрисовка врагов на мини-карте
        for entity in self.entities:
            if hasattr(entity, 'position'):
                enemy_x = minimap_x + (entity.position.x + 500) * scale
                enemy_y = minimap_y + (entity.position.y + 500) * scale
                pygame.draw.circle(self.screen, ColorScheme.RED, (int(enemy_x), int(enemy_y)), 2)
        
        # Отрисовка маяков на мини-карте
        for beacon in self.beacon_system.beacons.values():
            beacon_x = minimap_x + (beacon.position[0] + 500) * scale
            beacon_y = minimap_y + (beacon.position[1] + 500) * scale
            
            # Цвет маяка в зависимости от типа
            colors = {
                "navigation": ColorScheme.GREEN,
                "evolution": ColorScheme.PURPLE,
                "resource": ColorScheme.YELLOW,
                "danger": ColorScheme.RED,
                "mystery": ColorScheme.BLUE
            }
            color = colors.get(beacon.beacon_type.value, ColorScheme.WHITE)
            
            if beacon.discovered:
                pygame.draw.circle(self.screen, color, (int(beacon_x), int(beacon_y)), 3)
            else:
                pygame.draw.circle(self.screen, ColorScheme.GRAY, (int(beacon_x), int(beacon_y)), 2)
    
    def _toggle_autonomous_movement(self):
        """Переключение автономного движения"""
        try:
            if hasattr(self, 'autonomous_movement_enabled'):
                self.autonomous_movement_enabled = not self.autonomous_movement_enabled
            else:
                self.autonomous_movement_enabled = False
            
            status = "включено" if self.autonomous_movement_enabled else "отключено"
            print(f"Автономное движение {status}")
        except Exception as e:
            print(f"Ошибка переключения автономного движения: {e}")
    
    def _navigate_to_beacon(self, beacon_type_str: str):
        """Навигация к маяку определенного типа"""
        try:
            from core.isometric_system import BeaconType
            
            # Преобразование строки в тип маяка
            beacon_type_map = {
                "navigation": BeaconType.NAVIGATION,
                "evolution": BeaconType.EVOLUTION,
                "resource": BeaconType.RESOURCE,
                "danger": BeaconType.DANGER,
                "mystery": BeaconType.MYSTERY
            }
            
            beacon_type = beacon_type_map.get(beacon_type_str)
            if not beacon_type:
                print(f"Неизвестный тип маяка: {beacon_type_str}")
                return
            
            if not self.player:
                return
            
            # Проверяем, есть ли обнаруженные маяки этого типа
            discovered_beacons = [b for b in self.beacon_system.beacons.values() 
                                if b.discovered and b.beacon_type == beacon_type]
            
            if discovered_beacons:
                # Поиск ближайшего обнаруженного маяка указанного типа
                nearest_beacon = self.beacon_system.get_nearest_beacon(
                    (self.player.position.x, self.player.position.y, self.player.position.z),
                    beacon_type
                )
                
                if nearest_beacon:
                    success = self.beacon_system.set_navigation_target(nearest_beacon.id)
                    if success:
                        print(f"Установлена цель навигации: {nearest_beacon.id} ({beacon_type_str})")
                    else:
                        print(f"Не удалось установить цель: {nearest_beacon.id}")
                else:
                    print(f"Ближайший маяк типа '{beacon_type_str}' не найден")
            else:
                print(f"Маяки типа '{beacon_type_str}' еще не обнаружены. Исследуйте мир!")
                
        except Exception as e:
            print(f"Ошибка навигации к маяку: {e}")
    
    def _navigate_to_any_beacon(self):
        """Навигация к любому обнаруженному маяку"""
        try:
            if not self.player:
                return
            
            # Ищем все обнаруженные маяки
            discovered_beacons = [b for b in self.beacon_system.beacons.values() if b.discovered]
            
            if discovered_beacons:
                # Берем ближайший обнаруженный маяк
                nearest_beacon = self.beacon_system.get_nearest_beacon(
                    (self.player.position.x, self.player.position.y, self.player.position.z)
                )
                
                if nearest_beacon:
                    success = self.beacon_system.set_navigation_target(nearest_beacon.id)
                    if success:
                        print(f"Установлена цель навигации: {nearest_beacon.id}")
                    else:
                        print(f"Не удалось установить цель: {nearest_beacon.id}")
                else:
                    print("Обнаруженные маяки недоступны")
            else:
                print("Маяки еще не обнаружены. Исследуйте мир, чтобы найти скрытый маяк!")
                
        except Exception as e:
            print(f"Ошибка навигации к маяку: {e}")
    
    def _cancel_navigation(self):
        """Отмена навигации"""
        try:
            self.beacon_system.active_target = None
            print("Навигация отменена")
        except Exception as e:
            print(f"Ошибка отмены навигации: {e}")
    
    def _render_level_statistics(self):
        """Отрисовка статистики уровня"""
        if hasattr(self, 'level_progression') and hasattr(self, 'statistics_renderer'):
            self.statistics_renderer.render_statistics(self.level_progression.get_statistics())
    
    def _render_next_level(self):
        """Отрисовка экрана перехода к следующему уровню"""
        if hasattr(self, 'level_transition_manager'):
            self.level_transition_manager.render_transition()
    
    def _handle_level_progression_input(self, key):
        """Обработка ввода для прогрессии уровней"""
        if self.game_state == GameState.LEVEL_STATISTICS:
            if key == pygame.K_SPACE:
                # Переход к следующему уровню
                if hasattr(self, 'level_progression') and self.player:
                    next_level_data = self.level_progression.generate_next_level(self.player)
                    self._start_next_level(next_level_data)
            elif key == pygame.K_s:
                # Сохранение игры
                self._save_game()
        elif self.game_state == GameState.NEXT_LEVEL:
            if key == pygame.K_SPACE:
                # Продолжение игры
                self.game_state = GameState.PLAYING
    
    def _start_next_level(self, level_data: dict):
        """Начало следующего уровня"""
        try:
            # Восстанавливаем прогресс игрока
            if 'player_data' in level_data:
                player_data = level_data['player_data']
                
                # Восстанавливаем позицию
                if 'position' in player_data:
                    self.player.position.x = player_data['position']['x']
                    self.player.position.y = player_data['position']['y']
                    self.player.position.z = player_data['position']['z']
                
                # Восстанавливаем характеристики
                if 'stats' in player_data:
                    stats = player_data['stats']
                    self.player.stats.health = stats['health']
                    self.player.stats.max_health = stats['max_health']
                    self.player.stats.mana = stats['mana']
                    self.player.stats.max_mana = stats['max_mana']
                    self.player.stats.stamina = stats['stamina']
                    self.player.stats.max_stamina = stats['max_stamina']
                    self.player.stats.speed = stats['speed']
                    self.player.stats.strength = stats['strength']
                    self.player.stats.intelligence = stats['intelligence']
                    self.player.stats.agility = stats['agility']
                
                # Восстанавливаем инвентарь
                if 'inventory' in player_data:
                    self.player.inventory_system.clear_inventory()
                    for item_id, quantity in player_data['inventory'].items():
                        self.player.inventory_system.add_item(item_id, quantity)
                
                # Восстанавливаем гены
                if 'genes' in player_data and hasattr(self.player, 'genetic_system'):
                    for gene_data in player_data['genes']:
                        self.player.genetic_system.add_gene(gene_data['id'], gene_data['level'])
                
                # Восстанавливаем эмоции
                if 'emotions' in player_data and hasattr(self.player, 'emotion_system'):
                    for emotion, intensity in player_data['emotions'].items():
                        self.player.emotion_system.set_emotion_intensity(emotion, intensity)
                
                # Восстанавливаем прогресс ИИ
                if 'ai_learning' in player_data and hasattr(self.player, 'ai_system'):
                    ai_data = player_data['ai_learning']
                    self.player.ai_system.learning_level = ai_data['level']
                    self.player.ai_system.experience_points = ai_data['experience']
            
            # Генерируем новый мир
            if 'world_config' in level_data:
                world_config = level_data['world_config']
                # Здесь можно добавить генерацию нового мира с новыми врагами и препятствиями
            
            # Начинаем новый уровень
            next_level_number = self.level_progression.current_level + 1
            self.level_progression.start_level(next_level_number)
            
            # Переходим к игре
            self.game_state = GameState.PLAYING
            
            logger.info(f"Начат уровень {next_level_number}")
            
        except Exception as e:
            logger.error(f"Ошибка начала следующего уровня: {e}")
            # В случае ошибки возвращаемся к игре
            self.game_state = GameState.PLAYING
    
    def _render_save_slots_info(self):
        """Отрисовка информации о слотах сохранения в главном меню"""
        try:
            # Получаем информацию о слотах
            slots_info = self.session_manager.get_save_slots()
            
            if slots_info:
                y_offset = 500
                info_text = self.fonts["small"].render("Доступные сохранения:", True, ColorScheme.LIGHT_GRAY)
                self.screen.blit(info_text, (20, y_offset))
                y_offset += 25
                
                for slot_info in slots_info[:3]:  # Показываем первые 3 слота
                    slot_text = f"Слот {slot_info['slot_id']}: {slot_info['save_name']} (Уровень {slot_info.get('current_level', 1)})"
                    slot_surf = self.fonts["small"].render(slot_text, True, ColorScheme.LIGHT_GRAY)
                    self.screen.blit(slot_surf, (20, y_offset))
                    y_offset += 20
        except Exception as e:
            logger.error(f"Ошибка отображения информации о слотах: {e}")
    
    def _show_save_slots(self, mode: str = "save"):
        """Показать экран выбора слотов сохранения/загрузки"""
        self.save_slots_mode = mode  # "save" или "load"
        self.game_state = GameState.SAVE_MENU
        self._create_save_slot_buttons()
    
    def _create_save_slot_buttons(self, mode: str = "save"):
        """Создание кнопок для слотов сохранения"""
        try:
            slots_info = self.session_manager.get_save_slots()
            
            self.save_slot_buttons = {}
            button_width = 400
            button_height = 60
            start_x = (self.settings.window_width - button_width) // 2
            start_y = 200
            
            rendered_count = 0
            for i, slot_info in enumerate(slots_info):
                slot_id = slot_info['slot_id']
                button = pygame.Rect(start_x, start_y + rendered_count * 80, button_width, button_height)
                self.save_slot_buttons[slot_id] = button
                rendered_count += 1
                if rendered_count >= 5:
                    break
            
            # Кнопка назад — ниже последнего слота
            back_y = start_y + rendered_count * 80 + 40
            back_button = pygame.Rect((self.settings.window_width - 200) // 2, back_y, 200, 50)
            self.save_slot_buttons["back"] = back_button
        except Exception as e:
            logger.error(f"Ошибка создания кнопок слотов: {e}")
            self.save_slot_buttons = {}
    
    def _render_save_slots(self):
        """Отрисовка экрана выбора слотов сохранения"""
        # Заголовок
        title_text = "ВЫБОР СЛОТА СОХРАНЕНИЯ" if getattr(self, 'save_slots_mode', 'save') == 'save' else "ВЫБОР СЛОТА ЗАГРУЗКИ"
        title = self.fonts["large"].render(title_text, True, ColorScheme.WHITE)
        title_rect = title.get_rect(center=(self.settings.window_width // 2, 100))
        self.screen.blit(title, title_rect)
        
        try:
            slots_info = self.session_manager.get_save_slots()
            
            if not slots_info:
                no_text_label = "Нет доступных сохранений" if getattr(self, 'save_slots_mode', 'save') == 'load' else "Слоты не созданы"
                no_saves_text = self.fonts["main"].render(no_text_label, True, ColorScheme.GRAY)
                no_saves_rect = no_saves_text.get_rect(center=(self.settings.window_width // 2, 300))
                self.screen.blit(no_saves_text, no_saves_rect)
            
            # Отрисовка слотов
            for slot_id, button in self.save_slot_buttons.items():
                if slot_id == "back":
                    continue
                
                # Находим информацию о слоте
                slot_info = next((s for s in slots_info if s['slot_id'] == slot_id), None)
                if not slot_info:
                    continue
                
                # Цвет кнопки в зависимости от состояния
                color = ColorScheme.GREEN if slot_info.get('is_active', False) else ColorScheme.GRAY
                pygame.draw.rect(self.screen, color, button)
                pygame.draw.rect(self.screen, ColorScheme.WHITE, button, 2)
                
                # Текст слота
                slot_text = f"Слот {slot_id}: {slot_info.get('save_name', 'Без названия')}"
                slot_surf = self.fonts["main"].render(slot_text, True, ColorScheme.WHITE)
                slot_rect = slot_surf.get_rect(center=button.center)
                self.screen.blit(slot_surf, slot_rect)
                
                # Дополнительная информация
                info_text = f"Уровень: {slot_info.get('current_level', 1)} | Время: {slot_info.get('play_time', 0):.0f}с"
                info_surf = self.fonts["small"].render(info_text, True, ColorScheme.LIGHT_GRAY)
                info_rect = info_surf.get_rect(center=(button.centerx, button.centery + 20))
                self.screen.blit(info_surf, info_rect)
            
            # Рендер кнопки назад из заранее созданных кнопок
            if "back" in self.save_slot_buttons:
                back_button = self.save_slot_buttons["back"]
                pygame.draw.rect(self.screen, ColorScheme.BLUE, back_button)
                pygame.draw.rect(self.screen, ColorScheme.WHITE, back_button, 2)
                back_text = self.fonts["main"].render("НАЗАД", True, ColorScheme.WHITE)
                back_rect = back_text.get_rect(center=back_button.center)
                self.screen.blit(back_text, back_rect)
            
        except Exception as e:
            logger.error(f"Ошибка отображения слотов сохранения: {e}")
    
    def _save_to_slot(self, slot_id: int):
        """Сохранение игры в указанный слот (не сбрасывает сессию)"""
        try:
            if slot_id == "back":
                self.game_state = GameState.PAUSED
                return
            
            # Привязываем активную сессию к выбранному слоту (создаст/заменит слот)
            if self.session_manager.bind_active_session_to_slot(slot_id, save_name=f"Save {slot_id}"):
                # Сохраняем данные игры
                if self._save_game():
                    print(f"Игра сохранена в слот {slot_id}!")
                    self.game_state = GameState.PAUSED
                else:
                    print(f"Ошибка сохранения в слот {slot_id}!")
            else:
                print(f"Не удалось привязать сессию к слоту {slot_id}!")
                
        except Exception as e:
            logger.error(f"Ошибка сохранения в слот {slot_id}: {e}")
            print(f"Ошибка сохранения: {e}")
    
    def _load_from_slot(self, slot_id: int):
        """Загрузка игры из указанного слота"""
        try:
            if slot_id == "back":
                # Возврат в паузу/меню
                self.game_state = GameState.PAUSED if hasattr(self, 'pause_buttons') else GameState.MAIN_MENU
                return
            
            # Загружаем игру
            if self._load_existing_game(slot_id):
                print(f"Игра загружена из слота {slot_id}!")
                self.game_state = GameState.PLAYING
            else:
                print(f"Ошибка загрузки из слота {slot_id}!")
                
        except Exception as e:
            logger.error(f"Ошибка загрузки из слота {slot_id}: {e}")
            print(f"Ошибка загрузки: {e}")
    
    def _quick_save(self):
        """Быстрое сохранение активной сессии (без выбора слота)."""
        try:
            if not self.session_manager.active_session:
                return False
            return self.session_manager.save_session(self.session_manager.active_session)
        except Exception as e:
            logger.error(f"Ошибка быстрого сохранения: {e}")
            return False
    
    def _quick_load(self):
        """Быстрая загрузка текущей активной сессии (если есть привязанный слот)."""
        try:
            if self.session_manager.active_slot:
                return self._load_existing_game(self.session_manager.active_slot.slot_id)
            return False
        except Exception as e:
            logger.error(f"Ошибка быстрой загрузки: {e}")
            return False


def main():
    """Главная функция запуска"""
    settings = GameSettings.from_config()
    game = GameInterface(settings)
    game.run()


if __name__ == "__main__":
    main()

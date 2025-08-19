#!/usr/bin/env python3
"""
Единый игровой интерфейс для "Эволюционная Адаптация: Генетический Резонанс"
Объединяет все UI компоненты в одну систему на основе Pygame
"""

import pygame
import sys
import time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import random

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
from config.config_manager import config_manager


class GameState(Enum):
    """Состояния игры"""
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    INVENTORY = "inventory"
    GENETICS = "genetics"
    EMOTIONS = "emotions"
    EVOLUTION = "evolution"
    SETTINGS = "settings"
    LOADING = "loading"


@dataclass
class GameSettings:
    """Настройки игры"""
    window_width: int = 1280
    window_height: int = 720
    fps: int = 60
    fullscreen: bool = False
    vsync: bool = True
    music_volume: float = 0.7
    sfx_volume: float = 0.8
    difficulty: str = "normal"
    
    @classmethod
    def from_config(cls) -> 'GameSettings':
        """Создает настройки из конфигурации"""
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
        self.settings = settings or GameSettings.from_config()
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
        
        # Игровые системы
        self.effect_db = EffectDatabase()
        self.genetic_system = AdvancedGeneticSystem(self.effect_db)
        self.emotion_system = AdvancedEmotionSystem(self.effect_db)
        self.content_generator = ContentGenerator()
        self.evolution_system = EvolutionCycleSystem(self.effect_db)
        self.event_system = GlobalEventSystem(self.effect_db)
        self.difficulty_system = DynamicDifficultySystem()
        
        # Игровые данные
        self.player = None
        self.entities = []
        self.current_cycle = 1
        
        # UI элементы
        self.buttons = {}
        self.panels = {}
        self._create_ui_elements()
        
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
        start_y = 300
        
        self.buttons["start_game"] = pygame.Rect(start_x, start_y, button_width, button_height)
        self.buttons["continue_game"] = pygame.Rect(start_x, start_y + 70, button_width, button_height)
        self.buttons["settings"] = pygame.Rect(start_x, start_y + 140, button_width, button_height)
        self.buttons["exit"] = pygame.Rect(start_x, start_y + 210, button_width, button_height)
        
        # Игровые панели
        panel_width = 300
        panel_height = 200
        
        self.panels["stats"] = pygame.Rect(10, 10, panel_width, panel_height)
        self.panels["inventory"] = pygame.Rect(self.settings.window_width - panel_width - 10, 10, panel_width, panel_height)
        self.panels["genetics"] = pygame.Rect(10, self.settings.window_height - panel_height - 10, panel_width, panel_height)
        self.panels["emotions"] = pygame.Rect(self.settings.window_width - panel_width - 10, self.settings.window_height - panel_height - 10, panel_width, panel_height)
    
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
            
            # Ручное управление (временное отключение автономности)
            elif key == pygame.K_SPACE:
                self._toggle_autonomous_movement()
    
    def _handle_mouse_click(self, pos):
        """Обработка кликов мыши"""
        if self.game_state == GameState.MAIN_MENU:
            if self.buttons["start_game"].collidepoint(pos):
                self._start_new_game()
            elif self.buttons["continue_game"].collidepoint(pos):
                self._continue_game()
            elif self.buttons["settings"].collidepoint(pos):
                self.game_state = GameState.SETTINGS
            elif self.buttons["exit"].collidepoint(pos):
                self.running = False
        
        elif self.game_state == GameState.PAUSED and hasattr(self, 'pause_buttons'):
            if self.pause_buttons["resume"].collidepoint(pos):
                self.game_state = GameState.PLAYING
            elif self.pause_buttons["save"].collidepoint(pos):
                if self._save_game():
                    print("Игра сохранена!")
                else:
                    print("Ошибка сохранения!")
            elif self.pause_buttons["inventory"].collidepoint(pos):
                self.game_state = GameState.INVENTORY
            elif self.pause_buttons["main_menu"].collidepoint(pos):
                self.game_state = GameState.MAIN_MENU
    
    def _handle_mouse_motion(self, pos):
        """Обработка движения мыши"""
        pass  # Можно добавить hover эффекты
    
    def _start_new_game(self):
        """Начало новой игры"""
        self.game_state = GameState.LOADING
        
        # Создание игрока с автономным ИИ
        self.player = AdvancedGameEntity(
            entity_id="PLAYER_001",
            entity_type="player",
            name="Игрок",
            position=(0, 0, 0)
        )
        
        # Инициализация ИИ для игрока (автономное движение)
        self.player_ai = AdaptiveAISystem("PLAYER_001")
        
        # Флаг автономного движения (по умолчанию включен)
        self.autonomous_movement_enabled = True
        
        # Генерация мира
        world = self.content_generator.generate_world(
            biome="forest",
            size="medium",
            difficulty=1.0
        )
        
        # Создание врагов
        self.entities = []
        for i in range(5):
            enemy = AdvancedGameEntity(
                entity_id=f"ENEMY_{i:03d}",
                entity_type="enemy",
                name=f"Враг {i+1}",
                position=(i * 100, 0, 0)
            )
            self.entities.append(enemy)
        
        # Инициализация игровых объектов
        self.obstacles = []  # Препятствия (ловушки, геобарьеры)
        self.chests = []     # Сундуки с предметами
        self.items = []      # Предметы на карте
        
        # Инициализация систем
        self.effect_db = EffectDatabase()
        self.genetic_system = AdvancedGeneticSystem(self.effect_db)
        self.emotion_system = AdvancedEmotionSystem(self.effect_db)
        self.content_generator = ContentGenerator()
        self.evolution_system = EvolutionCycleSystem()
        self.event_system = GlobalEventSystem()
        self.difficulty_system = DynamicDifficultySystem()
        
        # Генерация предметов для новой игры
        self._generate_items_for_new_game()
        
        # Переход к игре
        self.game_state = GameState.PLAYING
    
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
        if not self.player:
            return False
        
        try:
            save_data = {
                "player": {
                    "entity_id": self.player.entity_id,
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
                },
                "entities": [
                    {
                        "entity_id": entity.entity_id,
                        "name": entity.name,
                        "position": (entity.position.x, entity.position.y, entity.position.z),
                        "stats": {
                            "health": entity.stats.health,
                            "max_health": entity.stats.max_health
                        }
                    }
                    for entity in self.entities
                ],
                "current_cycle": self.current_cycle,
                "world_seed": getattr(self, 'world_seed', 12345)
            }
            
            import json
            with open("save/game_save.json", "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
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
        import os
        if os.path.exists("save/game_save.json"):
            if self._load_game():
                self.game_state = GameState.PLAYING
            else:
                # Если загрузка не удалась, создаем новую игру
                self._start_new_game()
        else:
            # Если сохранения нет, создаем новую игру
            self._start_new_game()
    
    def _update(self):
        """Обновление игровой логики"""
        if self.game_state == GameState.PLAYING and self.player:
            delta_time = 0.016
            
            # Автономное движение игрока
            if hasattr(self, 'player_ai') and hasattr(self, 'autonomous_movement_enabled') and self.autonomous_movement_enabled:
                # Обновление ИИ игрока
                self.player_ai.update(self.player, self, delta_time)
                
                # Получение автономного движения
                dx, dy = self.player_ai.get_autonomous_movement(self.player, self)
                if dx != 0 or dy != 0:
                    self.player.move_pygame(dx, dy)
            
            # Обновление игрока
            self.player.update(delta_time)
            
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
    
    def _render_game(self):
        """Отрисовка игрового экрана"""
        # Темно-серый фон
        self.screen.fill((40, 40, 40))
        
        # Отрисовка игрока
        if self.player and hasattr(self.player, 'position'):
            player_x = int(self.player.position[0] + self.settings.window_width // 2)
            player_y = int(self.player.position[1] + self.settings.window_height // 2)
            
            # Игрок (зеленый квадрат)
            pygame.draw.rect(self.screen, ColorScheme.GREEN, (player_x - 10, player_y - 10, 20, 20))
            
            # Имя игрока
            if hasattr(self.fonts, 'small'):
                name_text = self.fonts['small'].render(self.player.name, True, ColorScheme.WHITE)
                self.screen.blit(name_text, (player_x - 20, player_y - 30))
        
        # Отрисовка врагов
        for entity in self.entities:
            if hasattr(entity, 'position'):
                enemy_x = int(entity.position[0] + self.settings.window_width // 2)
                enemy_y = int(entity.position[1] + self.settings.window_height // 2)
                
                # Враг (красный квадрат)
                pygame.draw.rect(self.screen, ColorScheme.RED, (enemy_x - 8, enemy_y - 8, 16, 16))
                
                # Имя врага
                if hasattr(self.fonts, 'small'):
                    name_text = self.fonts['small'].render(entity.name, True, ColorScheme.WHITE)
                    self.screen.blit(name_text, (enemy_x - 15, enemy_y - 25))
        
        # Отрисовка препятствий
        for obstacle in self.obstacles:
            if hasattr(obstacle, 'position'):
                obs_x = int(obstacle['position'][0] + self.settings.window_width // 2)
                obs_y = int(obstacle['position'][1] + self.settings.window_height // 2)
                
                if obstacle['type'] == 'trap':
                    # Ловушка (оранжевый треугольник)
                    points = [(obs_x, obs_y - 10), (obs_x - 8, obs_y + 8), (obs_x + 8, obs_y + 8)]
                    pygame.draw.polygon(self.screen, ColorScheme.ORANGE, points)
                elif obstacle['type'] == 'geo_barrier':
                    # Геобарьер (серый прямоугольник)
                    width = obstacle.get('width', 40)
                    height = obstacle.get('height', 40)
                    pygame.draw.rect(self.screen, ColorScheme.GRAY, 
                                   (obs_x - width//2, obs_y - height//2, width, height))
        
        # Отрисовка сундуков
        for chest in self.chests:
            if hasattr(chest, 'position'):
                chest_x = int(chest['position'][0] + self.settings.window_width // 2)
                chest_y = int(chest['position'][1] + self.settings.window_height // 2)
                
                # Сундук (желтый прямоугольник)
                color = ColorScheme.YELLOW if not chest['opened'] else ColorScheme.GRAY
                pygame.draw.rect(self.screen, color, (chest_x - 12, chest_y - 8, 24, 16))
                
                # Замок (если сундук заблокирован)
                if chest['locked']:
                    pygame.draw.circle(self.screen, ColorScheme.BLACK, (chest_x, chest_y), 3)
        
        # Отрисовка предметов на карте
        for item in self.items:
            if hasattr(item, 'position'):
                item_x = int(item['position'][0] + self.settings.window_width // 2)
                item_y = int(item['position'][1] + self.settings.window_height // 2)
                
                # Предмет (синий круг)
                pygame.draw.circle(self.screen, ColorScheme.BLUE, (item_x, item_y), 6)
        
        # Отрисовка панели состояния
        self._render_status_panel()
        
        # Отрисовка подсказки управления
        self._render_controls_help()
    
    def _render_status_panel(self):
        """Отрисовка панели состояния"""
        if not self.player:
            return
        
        # Панель состояния (полупрозрачная)
        panel_surface = pygame.Surface((300, 170))
        panel_surface.set_alpha(180)
        panel_surface.fill(ColorScheme.DARK_GRAY)
        self.screen.blit(panel_surface, (10, 10))
        
        # Статистика игрока
        if hasattr(self.fonts, 'small'):
            # Здоровье
            health_text = self.fonts['small'].render(f"Здоровье: {getattr(self.player, 'health', 100)}", True, ColorScheme.HEALTH_COLOR)
            self.screen.blit(health_text, (20, 20))
            
            # Выносливость
            stamina_text = self.fonts['small'].render(f"Выносливость: {getattr(self.player, 'stamina', 100)}", True, ColorScheme.STAMINA_COLOR)
            self.screen.blit(stamina_text, (20, 40))
            
            # Позиция
            pos_text = self.fonts['small'].render(f"Позиция: ({int(self.player.position[0])}, {int(self.player.position[1])})", True, ColorScheme.WHITE)
            self.screen.blit(pos_text, (20, 60))
            
            # Статус автономного движения
            auto_status = "ВКЛ" if getattr(self, 'autonomous_movement_enabled', True) else "ВЫКЛ"
            auto_color = ColorScheme.GREEN if getattr(self, 'autonomous_movement_enabled', True) else ColorScheme.RED
            auto_text = self.fonts['small'].render(f"Автономность: {auto_status}", True, auto_color)
            self.screen.blit(auto_text, (20, 80))
            
            # Количество врагов
            enemies_text = self.fonts['small'].render(f"Врагов: {len(self.entities)}", True, ColorScheme.RED)
            self.screen.blit(enemies_text, (20, 100))
            
            # Количество препятствий
            obstacles_text = self.fonts['small'].render(f"Препятствий: {len(self.obstacles)}", True, ColorScheme.ORANGE)
            self.screen.blit(obstacles_text, (20, 120))
            
            # Количество сундуков
            chests_text = self.fonts['small'].render(f"Сундуков: {len(self.chests)}", True, ColorScheme.YELLOW)
            self.screen.blit(chests_text, (20, 140))
    
    def _render_controls_help(self):
        """Отрисовка подсказки управления"""
        if hasattr(self.fonts, 'small'):
            help_texts = [
                "Управление:",
                "1 - Создать ловушку",
                "2 - Создать геобарьер", 
                "3 - Создать сундук",
                "4 - Добавить врага",
                "5-8 - Активировать эмоции",
                "SPACE - Переключить автономность",
                "ESC - Пауза"
            ]
            
            y_offset = self.settings.window_height - 200
            for i, text in enumerate(help_texts):
                color = ColorScheme.WHITE if i == 0 else ColorScheme.LIGHT_GRAY
                help_surface = self.fonts['small'].render(text, True, color)
                self.screen.blit(help_surface, (self.settings.window_width - 250, y_offset + i * 20))
    
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
        
        # Заголовок
        title = self.fonts["main"].render("СТАТИСТИКА", True, ColorScheme.WHITE)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 20))
        self.screen.blit(title, title_rect)
        
        if self.player:
            # Здоровье
            health_text = f"Здоровье: {self.player.stats.health:.0f}/{self.player.stats.max_health:.0f}"
            health_surf = self.fonts["small"].render(health_text, True, ColorScheme.HEALTH_COLOR)
            self.screen.blit(health_surf, (panel.x + 10, panel.y + 50))
            
            # Энергия
            energy_text = f"Энергия: {self.player.stats.stamina:.0f}/{self.player.stats.max_stamina:.0f}"
            energy_surf = self.fonts["small"].render(energy_text, True, ColorScheme.ENERGY_COLOR)
            self.screen.blit(energy_surf, (panel.x + 10, panel.y + 70))
            
            # Цикл
            cycle_text = f"Цикл: {self.current_cycle}"
            cycle_surf = self.fonts["small"].render(cycle_text, True, ColorScheme.EVOLUTION_COLOR)
            self.screen.blit(cycle_surf, (panel.x + 10, panel.y + 90))
    
    def _render_inventory_panel(self):
        """Отрисовка панели инвентаря"""
        panel = self.panels["inventory"]
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 2)
        
        title = self.fonts["main"].render("ИНВЕНТАРЬ", True, ColorScheme.WHITE)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 20))
        self.screen.blit(title, title_rect)
    
    def _render_genetics_panel(self):
        """Отрисовка панели генетики"""
        panel = self.panels["genetics"]
        pygame.draw.rect(self.screen, ColorScheme.DARK_GRAY, panel)
        pygame.draw.rect(self.screen, ColorScheme.WHITE, panel, 2)
        
        title = self.fonts["main"].render("ГЕНЕТИКА", True, ColorScheme.GENETIC_COLOR)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 20))
        self.screen.blit(title, title_rect)
        
        if self.player:
            genes_text = f"Гены: {len(self.player.genetic_system.active_genes)}"
            genes_surf = self.fonts["small"].render(genes_text, True, ColorScheme.GENETIC_COLOR)
            self.screen.blit(genes_surf, (panel.x + 10, panel.y + 50))
    
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
            "inventory": pygame.Rect(start_x, start_y + 140, button_width, button_height),
            "main_menu": pygame.Rect(start_x, start_y + 210, button_width, button_height)
        }
        
        button_texts = {
            "resume": "ПРОДОЛЖИТЬ",
            "save": "СОХРАНИТЬ",
            "inventory": "ИНВЕНТАРЬ",
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
        # TODO: Реализовать панель настроек
        self._render_main_menu()
    
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
                    self.player.position[0] + random.randint(-50, 50),
                    self.player.position[1] + random.randint(-50, 50),
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
        except Exception as e:
            print(f"Ошибка создания ловушки: {e}")
    
    def _create_geo_barrier(self):
        """Создание геобарьера"""
        try:
            if self.player and hasattr(self.player, 'position'):
                # Создание геобарьера рядом с игроком
                barrier_position = (
                    self.player.position[0] + random.randint(-100, 100),
                    self.player.position[1] + random.randint(-100, 100),
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
        except Exception as e:
            print(f"Ошибка создания геобарьера: {e}")
    
    def _create_chest(self):
        """Создание сундука с предметами"""
        try:
            if self.player and hasattr(self.player, 'position'):
                # Создание сундука рядом с игроком
                chest_position = (
                    self.player.position[0] + random.randint(-80, 80),
                    self.player.position[1] + random.randint(-80, 80),
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
        except Exception as e:
            print(f"Ошибка создания сундука: {e}")
    
    def _add_enemy(self):
        """Добавление врага на карту"""
        try:
            if self.player and hasattr(self.player, 'position'):
                # Создание врага рядом с игроком
                enemy_position = (
                    self.player.position[0] + random.randint(-150, 150),
                    self.player.position[1] + random.randint(-150, 150),
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


def main():
    """Главная функция запуска"""
    settings = GameSettings.from_config()
    game = GameInterface(settings)
    game.run()


if __name__ == "__main__":
    main()

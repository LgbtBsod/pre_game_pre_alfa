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
        
        elif key == pygame.K_i and self.game_state == GameState.PLAYING:
            self.game_state = GameState.INVENTORY
        
        elif key == pygame.K_g and self.game_state == GameState.PLAYING:
            self.game_state = GameState.GENETICS
        
        elif key == pygame.K_e and self.game_state == GameState.PLAYING:
            self.game_state = GameState.EMOTIONS
        
        elif key == pygame.K_v and self.game_state == GameState.PLAYING:
            self.game_state = GameState.EVOLUTION
    
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
    
    def _handle_mouse_motion(self, pos):
        """Обработка движения мыши"""
        pass  # Можно добавить hover эффекты
    
    def _start_new_game(self):
        """Начало новой игры"""
        self.game_state = GameState.LOADING
        
        # Создание игрока
        self.player = AdvancedGameEntity(
            entity_id="PLAYER_001",
            entity_type="player",
            name="Игрок",
            position=(0, 0, 0)
        )
        
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
        
        self.current_cycle = 1
        self.game_state = GameState.PLAYING
    
    def _continue_game(self):
        """Продолжение игры"""
        # TODO: Загрузка сохранения
        pass
    
    def _update(self):
        """Обновление игровой логики"""
        if self.game_state == GameState.PLAYING and self.player:
            delta_time = 0.016
            # Обновление игрока
            self.player.update(delta_time)
            
            # Обновление врагов
            for entity in self.entities:
                entity.update(delta_time)
            
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
        """Отрисовка игрового процесса"""
        # Отрисовка игрока
        if self.player:
            self._render_entity(self.player, (self.settings.window_width // 2, self.settings.window_height // 2))
        
        # Отрисовка врагов
        for entity in self.entities:
            pos = (entity.position.x + self.settings.window_width // 2, 
                   entity.position.y + self.settings.window_height // 2)
            self._render_entity(entity, pos)
        
        # Отрисовка UI панелей
        self._render_game_ui()
    
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
        pause_rect = pause_text.get_rect(center=(self.settings.window_width // 2, self.settings.window_height // 2))
        self.screen.blit(pause_text, pause_rect)
        
        # Инструкции
        instructions = self.fonts["small"].render("Нажмите ESC для продолжения", True, ColorScheme.GRAY)
        inst_rect = instructions.get_rect(center=(self.settings.window_width // 2, self.settings.window_height // 2 + 50))
        self.screen.blit(instructions, inst_rect)
    
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
        
        # TODO: Добавить содержимое инвентаря
    
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


def main():
    """Главная функция запуска"""
    settings = GameSettings.from_config()
    game = GameInterface(settings)
    game.run()


if __name__ == "__main__":
    main()

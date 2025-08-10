"""
Главное окно игры с полноценным UI интерфейсом
Версия для Panda3D с улучшенной архитектурой
"""

import sys
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.task import Task
from panda3d.core import Vec4, Point3, OrthographicLens

from .game_menu import GameMenu
from .render_manager import RenderManager
from core.game_state_manager import game_state_manager
from entities.entity_factory import entity_factory
from ai.ai_manager import ai_manager


class GameState(Enum):
    """Состояния игры"""

    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    LOADING = "loading"


@dataclass
class GameSettings:
    """Настройки игры"""

    def __init__(self):
        # Получаем настройки из unified_settings
        from config.unified_settings import UnifiedSettings

        self.player_name = "Player"
        self.difficulty = "normal"
        self.window_width = UnifiedSettings.WINDOW_WIDTH
        self.window_height = UnifiedSettings.WINDOW_HEIGHT
        self.fps = UnifiedSettings.RENDER_FPS
        self.auto_save_interval = 300  # секунды


class UIStyles:
    """Стили UI"""

    COLORS = {
        "bg_dark": Vec4(0.1, 0.1, 0.1, 1.0),
        "bg_medium": Vec4(0.2, 0.2, 0.2, 1.0),
        "bg_light": Vec4(0.3, 0.3, 0.3, 1.0),
        "accent_blue": Vec4(0.3, 0.6, 1.0, 1.0),
        "accent_green": Vec4(0.0, 0.7, 0.0, 1.0),
        "accent_orange": Vec4(1.0, 0.7, 0.0, 1.0),
        "accent_red": Vec4(1.0, 0.3, 0.3, 1.0),
        "text_white": Vec4(1.0, 1.0, 1.0, 1.0),
        "text_gray": Vec4(0.8, 0.8, 0.8, 1.0),
        "text_dark": Vec4(0.4, 0.4, 0.4, 1.0),
        "border": Vec4(0.3, 0.3, 0.3, 1.0),
    }

    BUTTON_STYLE = {
        "relief": "flat",
        "frameColor": COLORS["bg_medium"],
        "frameSize": (-0.1, 0.1, -0.05, 0.05),
        "text_fg": COLORS["text_white"],
        "text_scale": 0.04,
    }


class MainWindow(ShowBase):
    """Главное окно игры с оптимизированной архитектурой"""

    def __init__(self):
        super().__init__()
        self._setup_window()

        # Настройки игры
        self.game_settings = GameSettings()

        # Состояние игры
        self.game_state = GameState.MENU
        self.game_running = False
        self.is_paused = False

        # UI компоненты
        self.render_manager: Optional[RenderManager] = None
        self.game_menu: Optional[GameMenu] = None
        
        # Игровые объекты
        self.player = None
        self.entities = []
        self.current_area = None

        # Время
        self.game_time = 0
        self.delta_time = 0
        self.last_frame_time = 0

        # UI элементы
        self.ui_elements = {}
        
        # Инициализация
        self._init_ui()
        self._bind_events()
        self._create_main_menu()

    def _setup_window(self):
        """Настройка окна"""
        # Устанавливаем размер окна
        self.win.set_size(self.game_settings.window_width, self.game_settings.window_height)
        
        # Центрируем окно
        self.center_window()
        
        # Устанавливаем заголовок
        self.win.set_title("AI EVOLVE - Игра с Искусственным Интеллектом")
        
        # Настройки рендеринга
        self.render.set_antialias(True)
        self.render.set_shader_auto()

    def center_window(self):
        """Центрирует окно на экране"""
        try:
            # Получаем размеры экрана
            props = self.win.get_properties()
            screen_width = props.get_x_size()
            screen_height = props.get_y_size()
            
            # Вычисляем позицию для центрирования
            x = (screen_width - self.game_settings.window_width) // 2
            y = (screen_height - self.game_settings.window_height) // 2
            
            # Устанавливаем позицию окна
            self.win.set_origin(x, y)
        except Exception as e:
            print(f"Ошибка центрирования окна: {e}")

    def _init_ui(self):
        """Инициализация UI"""
        # Создаем основной контейнер
        self.main_frame = DirectFrame(
            frameColor=UIStyles.COLORS["bg_dark"],
            frameSize=(-1, 1, -1, 1),
            parent=self.render2d
        )
        
        # Создаем рендер менеджер
        self.render_manager = RenderManager(self, game_state_manager)

    def _bind_events(self):
        """Привязка событий"""
        # Привязываем клавиши
        self.accept("escape", self._on_escape)
        self.accept("p", self._toggle_pause)
        self.accept("f5", self._save_game)
        self.accept("f1", self._toggle_debug)
        
        # Привязываем мышь
        self.accept("mouse1", self._on_mouse_click)
        self.accept("mouse3", self._on_right_click)

    def _create_main_menu(self):
        """Создание главного меню"""
        # Заголовок игры
        title = OnscreenText(
            text="AI EVOLVE",
            pos=(0, 0.7),
            scale=0.15,
            fg=UIStyles.COLORS["accent_blue"],
            shadow=(0, 0, 0, 1),
            parent=self.main_frame
        )
        self.ui_elements["title"] = title

        # Подзаголовок
        subtitle = OnscreenText(
            text="Игра с Искусственным Интеллектом",
            pos=(0, 0.5),
            scale=0.05,
            fg=UIStyles.COLORS["text_gray"],
            shadow=(0, 0, 0, 1),
            parent=self.main_frame
        )
        self.ui_elements["subtitle"] = subtitle

        # Кнопка "Новая игра"
        new_game_btn = DirectButton(
            text="Новая игра",
            pos=(0, 0.2),
            scale=0.06,
            command=self._start_new_game,
            **UIStyles.BUTTON_STYLE,
            parent=self.main_frame
        )
        self.ui_elements["new_game_btn"] = new_game_btn

        # Кнопка "Загрузить игру"
        load_game_btn = DirectButton(
            text="Загрузить игру",
            pos=(0, 0.1),
            scale=0.06,
            command=self._load_game,
            **UIStyles.BUTTON_STYLE,
            parent=self.main_frame
        )
        self.ui_elements["load_game_btn"] = load_game_btn

        # Кнопка "Настройки"
        settings_btn = DirectButton(
            text="Настройки",
            pos=(0, 0.0),
            scale=0.06,
            command=self._show_settings,
            **UIStyles.BUTTON_STYLE,
            parent=self.main_frame
        )
        self.ui_elements["settings_btn"] = settings_btn

        # Кнопка "Выход"
        exit_btn = DirectButton(
            text="Выход",
            pos=(0, -0.1),
            scale=0.06,
            command=self._exit_game,
            **UIStyles.BUTTON_STYLE,
            parent=self.main_frame
        )
        self.ui_elements["exit_btn"] = exit_btn

    def _start_new_game(self):
        """Начинает новую игру"""
        try:
            # Показываем диалог создания новой игры
            self._show_new_game_dialog()
        except Exception as e:
            print(f"Ошибка создания новой игры: {e}")

    def _show_new_game_dialog(self):
        """Показывает диалог создания новой игры"""
        # Скрываем главное меню
        self._hide_main_menu()
        
        # Создаем диалог
        dialog_frame = DirectFrame(
            frameColor=UIStyles.COLORS["bg_medium"],
            frameSize=(-0.5, 0.5, -0.4, 0.4),
            pos=(0, 0, 0),
            parent=self.render2d
        )
        self.ui_elements["dialog_frame"] = dialog_frame
        
        # Заголовок диалога
        dialog_title = OnscreenText(
            text="Создание новой игры",
            pos=(0, 0.3),
            scale=0.08,
            fg=UIStyles.COLORS["text_white"],
            parent=dialog_frame
        )
        self.ui_elements["dialog_title"] = dialog_title
        
        # Поле ввода имени игрока
        name_label = OnscreenText(
            text="Имя игрока:",
            pos=(-0.3, 0.1),
            scale=0.05,
            fg=UIStyles.COLORS["text_white"],
            parent=dialog_frame
        )
        self.ui_elements["name_label"] = name_label
        
        name_entry = DirectEntry(
            text="Player",
            pos=(0, 0, 0.1),
            scale=0.05,
            width=20,
            parent=dialog_frame
        )
        self.ui_elements["name_entry"] = name_entry
        
        # Выбор сложности
        difficulty_label = OnscreenText(
            text="Сложность:",
            pos=(-0.3, -0.1),
            scale=0.05,
            fg=UIStyles.COLORS["text_white"],
            parent=dialog_frame
        )
        self.ui_elements["difficulty_label"] = difficulty_label
        
        # Кнопки сложности
        easy_btn = DirectButton(
            text="Легкая",
            pos=(-0.2, 0, -0.1),
            scale=0.04,
            command=lambda: self._set_difficulty("easy"),
            **UIStyles.BUTTON_STYLE,
            parent=dialog_frame
        )
        self.ui_elements["easy_btn"] = easy_btn
        
        normal_btn = DirectButton(
            text="Нормальная",
            pos=(0, 0, -0.1),
            scale=0.04,
            command=lambda: self._set_difficulty("normal"),
            **UIStyles.BUTTON_STYLE,
            parent=dialog_frame
        )
        self.ui_elements["normal_btn"] = normal_btn
        
        hard_btn = DirectButton(
            text="Сложная",
            pos=(0.2, 0, -0.1),
            scale=0.04,
            command=lambda: self._set_difficulty("hard"),
            **UIStyles.BUTTON_STYLE,
            parent=dialog_frame
        )
        self.ui_elements["hard_btn"] = hard_btn
        
        # Кнопки диалога
        ok_btn = DirectButton(
            text="Начать игру",
            pos=(-0.15, 0, -0.3),
            scale=0.05,
            command=self._create_game,
            **UIStyles.BUTTON_STYLE,
            parent=dialog_frame
        )
        self.ui_elements["ok_btn"] = ok_btn
        
        cancel_btn = DirectButton(
            text="Отмена",
            pos=(0.15, 0, -0.3),
            scale=0.05,
            command=self._cancel_dialog,
            **UIStyles.BUTTON_STYLE,
            parent=dialog_frame
        )
        self.ui_elements["cancel_btn"] = cancel_btn
        
        # Сохраняем выбранную сложность
        self.selected_difficulty = "normal"

    def _set_difficulty(self, difficulty: str):
        """Устанавливает сложность"""
        self.selected_difficulty = difficulty

    def _create_game(self):
        """Создает новую игру"""
        try:
            # Получаем имя игрока
            name_entry = self.ui_elements.get("name_entry")
            player_name = name_entry.get() if name_entry else "Player"
            
            # Закрываем диалог
            self._cancel_dialog()
            
            # Создаем игру
            self._init_game_systems()
            
            # Создаем игрока
            self.player = entity_factory.create_player(player_name, (0, 0))
            
            # Загружаем начальную область
            self._load_area("starting_area")
            
            # Переключаемся в игровой режим
            self._switch_to_game_mode()
            
            # Запускаем игровой цикл
            self._start_game_loop()
            
        except Exception as e:
            print(f"Ошибка создания игры: {e}")

    def _cancel_dialog(self):
        """Отменяет диалог"""
        # Удаляем элементы диалога
        for key in ["dialog_frame", "dialog_title", "name_label", "name_entry", 
                   "difficulty_label", "easy_btn", "normal_btn", "hard_btn", 
                   "ok_btn", "cancel_btn"]:
            if key in self.ui_elements:
                self.ui_elements[key].destroy()
                del self.ui_elements[key]
        
        # Показываем главное меню
        self._show_main_menu()

    def _hide_main_menu(self):
        """Скрывает главное меню"""
        for key in ["title", "subtitle", "new_game_btn", "load_game_btn", 
                   "settings_btn", "exit_btn"]:
            if key in self.ui_elements:
                self.ui_elements[key].hide()

    def _show_main_menu(self):
        """Показывает главное меню"""
        for key in ["title", "subtitle", "new_game_btn", "load_game_btn", 
                   "settings_btn", "exit_btn"]:
            if key in self.ui_elements:
                self.ui_elements[key].show()

    def _load_game(self):
        """Загружает игру"""
        try:
            # Показываем список сохранений
            saves = game_state_manager.get_save_list()
            if not saves:
                self._show_message("Нет сохранений")
                return
            
            # Создаем диалог выбора сохранения
            self._show_load_dialog(saves)
            
        except Exception as e:
            print(f"Ошибка загрузки игры: {e}")

    def _show_load_dialog(self, saves):
        """Показывает диалог загрузки"""
        # Скрываем главное меню
        self._hide_main_menu()
        
        # Создаем диалог
        dialog_frame = DirectFrame(
            frameColor=UIStyles.COLORS["bg_medium"],
            frameSize=(-0.6, 0.6, -0.5, 0.5),
            pos=(0, 0, 0),
            parent=self.render2d
        )
        self.ui_elements["load_dialog"] = dialog_frame
        
        # Заголовок
        title = OnscreenText(
            text="Выберите сохранение",
            pos=(0, 0.4),
            scale=0.08,
            fg=UIStyles.COLORS["text_white"],
            parent=dialog_frame
        )
        self.ui_elements["load_title"] = title
        
        # Список сохранений
        y_offset = 0.2
        for i, save in enumerate(saves[:5]):  # Показываем первые 5 сохранений
            save_btn = DirectButton(
                text=f"{save['name']} - {save['date']}",
                pos=(0, 0, y_offset - i * 0.1),
                scale=0.04,
                command=lambda s=save: self._load_save(s),
                **UIStyles.BUTTON_STYLE,
                parent=dialog_frame
            )
            self.ui_elements[f"save_btn_{i}"] = save_btn
        
        # Кнопка отмены
        cancel_btn = DirectButton(
            text="Отмена",
            pos=(0, 0, -0.4),
            scale=0.05,
            command=self._cancel_load_dialog,
            **UIStyles.BUTTON_STYLE,
            parent=dialog_frame
        )
        self.ui_elements["load_cancel_btn"] = cancel_btn

    def _load_save(self, save):
        """Загружает сохранение"""
        try:
            # Закрываем диалог
            self._cancel_load_dialog()
            
            # Загружаем игру
            if game_state_manager.load_game(save['id']):
                self._init_game_systems()
                self._switch_to_game_mode()
                self._start_game_loop()
            else:
                self._show_message("Ошибка загрузки сохранения")
                
        except Exception as e:
            print(f"Ошибка загрузки сохранения: {e}")

    def _cancel_load_dialog(self):
        """Отменяет диалог загрузки"""
        # Удаляем элементы диалога
        for key in list(self.ui_elements.keys()):
            if key.startswith("load_"):
                self.ui_elements[key].destroy()
                del self.ui_elements[key]
        
        # Показываем главное меню
        self._show_main_menu()

    def _show_settings(self):
        """Показывает настройки"""
        # Пока просто показываем сообщение
        self._show_message("Настройки будут добавлены позже")

    def _exit_game(self):
        """Выход из игры"""
        self.userExit()

    def _init_game_systems(self):
        """Инициализация игровых систем"""
        # Инициализируем системы
        from config.settings_manager import settings_manager
        from core.data_manager import data_manager
        
        settings_manager.reload_settings()
        data_manager.reload_data()

    def _load_area(self, area_name: str):
        """Загружает игровую область"""
        try:
            self.current_area = area_name
            
            # Очищаем текущие сущности
            self.entities.clear()
            
            # Создаем сущности для области
            self._spawn_area_entities(area_name)
            
        except Exception as e:
            print(f"Ошибка загрузки области: {e}")

    def _spawn_area_entities(self, area_name: str):
        """Создает сущности для области"""
        try:
            if area_name == "starting_area":
                # Создаем несколько слабых врагов
                for i in range(3):
                    enemy = entity_factory.create_enemy(
                        enemy_type="warrior",
                        level=1,
                        position=(2 + i * 2, 2 + i * 2)
                    )
                    self.entities.append(enemy)
                    # Регистрируем в AI системе
                    if hasattr(enemy, 'ai_core'):
                        ai_manager.register_entity(enemy, enemy.ai_core)
            
            elif area_name == "forest":
                # Создаем лесных врагов
                for i in range(5):
                    enemy = entity_factory.create_enemy(
                        enemy_type="archer",
                        level=3,
                        position=(3 + i * 3, 3 + i * 3)
                    )
                    self.entities.append(enemy)
                    if hasattr(enemy, 'ai_core'):
                        ai_manager.register_entity(enemy, enemy.ai_core)
            
            elif area_name == "dungeon":
                # Создаем подземных врагов
                for i in range(8):
                    enemy = entity_factory.create_enemy(
                        enemy_type="mage",
                        level=5,
                        position=(4 + i * 2, 4 + i * 2)
                    )
                    self.entities.append(enemy)
                    if hasattr(enemy, 'ai_core'):
                        ai_manager.register_entity(enemy, enemy.ai_core)
            
        except Exception as e:
            print(f"Ошибка создания сущностей: {e}")

    def _switch_to_game_mode(self):
        """Переключает в игровой режим"""
        # Скрываем главное меню
        self._hide_main_menu()
        
        # Создаем игровое меню
        self.game_menu = GameMenu(self.render2d, self.game_settings.window_width, 
                                 self.game_settings.window_height)
        
        # Создаем игровые UI элементы
        self._create_game_ui()
        
        # Переключаем состояние
        self.game_state = GameState.PLAYING
        self.game_running = True

    def _create_game_ui(self):
        """Создает игровые UI элементы"""
        # Информационная панель
        info_frame = DirectFrame(
            frameColor=UIStyles.COLORS["bg_medium"],
            frameSize=(-0.3, 0.3, 0.8, 1.0),
            pos=(-0.7, 0, 0),
            parent=self.render2d
        )
        self.ui_elements["info_frame"] = info_frame
        
        # Информация об игроке
        player_info = OnscreenText(
            text="Игрок: Неизвестно",
            pos=(-0.7, 0.9),
            scale=0.04,
            fg=UIStyles.COLORS["text_white"],
            parent=self.render2d
        )
        self.ui_elements["player_info"] = player_info
        
        # Информация об области
        area_info = OnscreenText(
            text="Область: Неизвестно",
            pos=(-0.7, 0.85),
            scale=0.04,
            fg=UIStyles.COLORS["text_white"],
            parent=self.render2d
        )
        self.ui_elements["area_info"] = area_info

    def _start_game_loop(self):
        """Запускает игровой цикл"""
        # Добавляем задачу обновления игры
        self.task_mgr.add(self._game_loop, "game_loop")

    def _game_loop(self, task):
        """Игровой цикл"""
        try:
            # Вычисляем delta time
            current_time = time.time()
            self.delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Обновляем время игры
            self.game_time += int(self.delta_time * 1000)
            
            # Обновляем игровую логику
            if not self.is_paused:
                self._update_game()
            
            # Рендерим
            self._render_game()
            
            # Обновляем UI
            self._update_ui()
            
            # Автосохранение
            if self.game_time % (self.game_settings.auto_save_interval * 1000) == 0:
                self._save_game()
            
            return Task.cont
            
        except Exception as e:
            print(f"Ошибка в игровом цикле: {e}")
            return Task.cont

    def _update_game(self):
        """Обновляет игровую логику"""
        try:
            # Обновляем AI систему
            ai_manager.update(self.delta_time)
            
            # Обновляем игрока
            if self.player:
                self.player.update(self.delta_time)
            
            # Обновляем сущности
            for entity in self.entities[:]:
                entity.update(self.delta_time)
                
                # Удаляем мертвых сущностей
                if not entity.alive:
                    self.entities.remove(entity)
                    ai_manager.unregister_entity(entity)
            
            # Проверяем коллизии
            self._check_collisions()
            
        except Exception as e:
            print(f"Ошибка обновления игры: {e}")

    def _render_game(self):
        """Рендерит игру"""
        try:
            if self.render_manager:
                # Рендерим область
                if self.current_area:
                    self.render_manager.render_area(self.current_area)
                
                # Рендерим сущности
                for entity in self.entities:
                    self.render_manager.render_entity(entity)
                
                # Рендерим игрока
                if self.player:
                    self.render_manager.render_entity(self.player)
                
                # Центрируем камеру на игроке
                if self.player:
                    self.render_manager.center_camera_on_player(self.player)
                
                # Рендерим UI
                self.render_manager.render_ui()
                
        except Exception as e:
            print(f"Ошибка рендеринга: {e}")

    def _update_ui(self):
        """Обновляет UI"""
        try:
            # Обновляем информацию об игроке
            if self.player and "player_info" in self.ui_elements:
                player_text = f"Игрок: {self.player.name} (Ур.{self.player.level})"
                self.ui_elements["player_info"].set_text(player_text)
            
            # Обновляем информацию об области
            if "area_info" in self.ui_elements:
                area_text = f"Область: {self.current_area}"
                self.ui_elements["area_info"].set_text(area_text)
                
        except Exception as e:
            print(f"Ошибка обновления UI: {e}")

    def _check_collisions(self):
        """Проверяет коллизии"""
        try:
            if not self.player:
                return
            
            # Проверяем коллизии игрока с врагами
            for entity in self.entities:
                if entity.alive and self.player.alive:
                    distance = self.player.distance_to(entity)
                    if distance < 1.0:  # Радиус коллизии
                        # Игрок атакует врага
                        if self.player.can_attack():
                            self.player.attack(entity)
                        
                        # Враг атакует игрока
                        if entity.can_attack():
                            entity.attack(self.player)
            
        except Exception as e:
            print(f"Ошибка проверки коллизий: {e}")

    def _on_escape(self):
        """Обработка клавиши Escape"""
        if self.game_state == GameState.PLAYING:
            self._toggle_pause()
        elif self.game_state == GameState.PAUSED:
            self._toggle_pause()

    def _toggle_pause(self):
        """Переключает паузу"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.game_state = GameState.PAUSED
            self._show_message("Игра приостановлена")
        else:
            self.game_state = GameState.PLAYING
            self._hide_message()

    def _save_game(self):
        """Сохраняет игру"""
        try:
            if self.player:
                # Создаем состояние игрока
                player_state = {
                    "position": self.player.position,
                    "level": self.player.level,
                    "experience": self.player.experience,
                    "health": self.player.health,
                    "max_health": self.player.max_health,
                }
                
                # Обновляем состояние в менеджере
                game_state_manager.update_player_state(player_state)
                
                # Сохраняем игру
                if game_state_manager.save_game():
                    self._show_message("Игра сохранена")
                else:
                    self._show_message("Ошибка сохранения")
            else:
                self._show_message("Нет игрока для сохранения")
                
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def _toggle_debug(self):
        """Переключает отладочную информацию"""
        if self.render_manager:
            self.render_manager.toggle_debug_info()

    def _on_mouse_click(self):
        """Обработка клика мыши"""
        if self.game_state == GameState.PLAYING and self.player:
            # Получаем позицию мыши в мировых координатах
            mouse_pos = self.mouse_watcher.get_mouse()
            if mouse_pos:
                # Преобразуем в мировые координаты
                world_pos = self.render_manager.get_world_position(mouse_pos.get_x(), mouse_pos.get_y())
                # Перемещаем игрока
                self.player.position = [world_pos[0], world_pos[1]]

    def _on_right_click(self):
        """Обработка правого клика мыши"""
        if self.game_state == GameState.PLAYING:
            # Показываем контекстное меню
            pass

    def _show_message(self, text: str, duration: float = 3.0):
        """Показывает сообщение"""
        try:
            # Удаляем старое сообщение
            if "message" in self.ui_elements:
                self.ui_elements["message"].destroy()
            
            # Создаем новое сообщение
            message = OnscreenText(
                text=text,
                pos=(0, 0),
                scale=0.06,
                fg=UIStyles.COLORS["accent_blue"],
                shadow=(0, 0, 0, 1),
                parent=self.render2d
            )
            self.ui_elements["message"] = message
            
            # Удаляем сообщение через время
            def remove_message(task):
                if "message" in self.ui_elements:
                    self.ui_elements["message"].destroy()
                    del self.ui_elements["message"]
                return Task.done
            
            self.task_mgr.do_method_later(duration, remove_message, "remove_message")
            
        except Exception as e:
            print(f"Ошибка показа сообщения: {e}")

    def _hide_message(self):
        """Скрывает сообщение"""
        if "message" in self.ui_elements:
            self.ui_elements["message"].destroy()
            del self.ui_elements["message"]


def main():
    """Главная функция"""
    try:
        # Создаем и запускаем главное окно
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

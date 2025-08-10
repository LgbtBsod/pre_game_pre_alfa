"""
Главное окно игры с полноценным UI интерфейсом
Оптимизированная версия с улучшенной архитектурой
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

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
    player_name: str = "Player"
    difficulty: str = "normal"
    window_width: int = 1200
    window_height: int = 800
    fps: int = 60
    auto_save_interval: int = 300  # секунды


class UIStyles:
    """Стили UI"""
    COLORS = {
        'bg_dark': '#1a1a1a',
        'bg_medium': '#2a2a2a',
        'bg_light': '#3a3a3a',
        'accent_blue': '#4a9eff',
        'accent_green': '#00aa00',
        'accent_orange': '#ffaa00',
        'accent_red': '#ff4a4a',
        'text_white': '#ffffff',
        'text_gray': '#cccccc',
        'text_dark': '#666666',
        'border': '#555555'
    }
    
    FONTS = {
        'title_large': ('Arial', 24, 'bold'),
        'title_medium': ('Arial', 18, 'bold'),
        'title_small': ('Arial', 14, 'bold'),
        'text_large': ('Arial', 12),
        'text_medium': ('Arial', 10),
        'text_small': ('Arial', 8)
    }
    
    BUTTON_STYLE = {
        'font': FONTS['text_large'],
        'relief': 'flat',
        'bd': 0,
        'padx': 10,
        'pady': 5
    }


class MainWindow:
    """Главное окно игры с оптимизированной архитектурой"""
    
    def __init__(self):
        self.root = tk.Tk()
        self._setup_window()
        
        # Настройки игры
        self.game_settings = GameSettings()
        
        # Состояние игры
        self.game_state = GameState.MENU
        self.game_running = False
        self.game_paused = False
        self.game_thread: Optional[threading.Thread] = None
        
        # UI компоненты
        self.game_canvas: Optional[tk.Canvas] = None
        self.render_manager: Optional[RenderManager] = None
        self.game_menu: Optional[GameMenu] = None
        
        # Игровые объекты
        self.player = None
        self.entities = []
        self.current_area = "starting_area"
        
        # Время и производительность
        self.game_time = 0
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # UI элементы
        self.ui_elements: Dict[str, Any] = {}
        
        # Инициализация
        self._init_ui()
        self._bind_events()
        
    def _setup_window(self):
        """Настройка главного окна"""
        self.root.title("AI EVOLVE - Игра с ИИ")
        self.root.geometry("1200x800")
        self.root.configure(bg=UIStyles.COLORS['bg_dark'])
        self.root.minsize(800, 600)
        
        # Центрируем окно
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self._create_main_menu()
        self._create_game_area()
        self._create_control_panel()
        
    def _create_main_menu(self):
        """Создание главного меню"""
        self.ui_elements['menu_frame'] = tk.Frame(
            self.root, 
            bg=UIStyles.COLORS['bg_medium'], 
            relief='raised', 
            bd=2
        )
        self.ui_elements['menu_frame'].pack(fill='x', padx=5, pady=5)
        
        # Заголовок
        title_label = tk.Label(
            self.ui_elements['menu_frame'],
            text="AI EVOLVE",
            font=UIStyles.FONTS['title_large'],
            fg=UIStyles.COLORS['accent_blue'],
            bg=UIStyles.COLORS['bg_medium']
        )
        title_label.pack(pady=10)
        
        # Подзаголовок
        subtitle_label = tk.Label(
            self.ui_elements['menu_frame'],
            text="Игра с эволюционирующим ИИ",
            font=UIStyles.FONTS['text_large'],
            fg=UIStyles.COLORS['text_gray'],
            bg=UIStyles.COLORS['bg_medium']
        )
        subtitle_label.pack(pady=5)
        
        # Кнопки меню
        button_frame = tk.Frame(self.ui_elements['menu_frame'], bg=UIStyles.COLORS['bg_medium'])
        button_frame.pack(pady=20)
        
        # Создаем кнопки с улучшенным стилем
        self._create_menu_button(button_frame, "Новая игра", self._start_new_game, UIStyles.COLORS['accent_blue'])
        self._create_menu_button(button_frame, "Загрузить игру", self._load_game, UIStyles.COLORS['accent_blue'])
        self._create_menu_button(button_frame, "Настройки", self._show_settings, UIStyles.COLORS['accent_blue'])
        self._create_menu_button(button_frame, "Выход", self._exit_game, UIStyles.COLORS['accent_red'])
        
    def _create_menu_button(self, parent, text: str, command: Callable, bg_color: str):
        """Создание кнопки меню с улучшенным стилем"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=UIStyles.COLORS['text_white'],
            width=20,
            height=2,
            **UIStyles.BUTTON_STYLE
        )
        btn.pack(pady=5)
        
        # Добавляем hover эффект
        btn.bind('<Enter>', lambda e: btn.configure(bg=self._lighten_color(bg_color)))
        btn.bind('<Leave>', lambda e: btn.configure(bg=bg_color))
        
        return btn
        
    def _create_game_area(self):
        """Создание игровой области"""
        self.ui_elements['game_frame'] = tk.Frame(self.root, bg=UIStyles.COLORS['bg_dark'])
        self.ui_elements['game_frame'].pack(fill='both', expand=True, padx=5, pady=5)
        
        # Canvas для игры
        self.game_canvas = tk.Canvas(
            self.ui_elements['game_frame'],
            width=800,
            height=600,
            bg='#000000',
            highlightthickness=0
        )
        self.game_canvas.pack(side='left', fill='both', expand=True)
        
        # Информационная панель
        self._create_info_panel()
        
    def _create_info_panel(self):
        """Создание информационной панели"""
        info_frame = tk.Frame(self.ui_elements['game_frame'], bg=UIStyles.COLORS['bg_medium'], width=300)
        info_frame.pack(side='right', fill='y', padx=(5, 0))
        info_frame.pack_propagate(False)
        
        # Заголовок панели
        info_title = tk.Label(
            info_frame,
            text="ИНФОРМАЦИЯ",
            font=UIStyles.FONTS['title_small'],
            fg=UIStyles.COLORS['accent_blue'],
            bg=UIStyles.COLORS['bg_medium']
        )
        info_title.pack(pady=10)
        
        # Информация об игроке
        self._create_player_info_section(info_frame)
        
        # Информация об области
        self._create_area_info_section(info_frame)
        
        # Кнопки управления
        self._create_control_buttons(info_frame)
        
    def _create_player_info_section(self, parent):
        """Создание секции информации об игроке"""
        self.ui_elements['player_info_frame'] = tk.LabelFrame(
            parent,
            text="Игрок",
            font=UIStyles.FONTS['text_medium'],
            fg=UIStyles.COLORS['text_gray'],
            bg=UIStyles.COLORS['bg_medium'],
            relief='flat'
        )
        self.ui_elements['player_info_frame'].pack(fill='x', padx=10, pady=5)
        
        # Метки информации об игроке
        self.ui_elements['player_name_label'] = self._create_info_label(
            self.ui_elements['player_info_frame'], "Имя: -"
        )
        self.ui_elements['player_level_label'] = self._create_info_label(
            self.ui_elements['player_info_frame'], "Уровень: -"
        )
        self.ui_elements['player_health_label'] = self._create_info_label(
            self.ui_elements['player_info_frame'], "Здоровье: -"
        )
        self.ui_elements['player_fps_label'] = self._create_info_label(
            self.ui_elements['player_info_frame'], "FPS: -"
        )
        
    def _create_area_info_section(self, parent):
        """Создание секции информации об области"""
        self.ui_elements['area_info_frame'] = tk.LabelFrame(
            parent,
            text="Область",
            font=UIStyles.FONTS['text_medium'],
            fg=UIStyles.COLORS['text_gray'],
            bg=UIStyles.COLORS['bg_medium'],
            relief='flat'
        )
        self.ui_elements['area_info_frame'].pack(fill='x', padx=10, pady=5)
        
        self.ui_elements['area_name_label'] = self._create_info_label(
            self.ui_elements['area_info_frame'], "Название: -"
        )
        self.ui_elements['entities_count_label'] = self._create_info_label(
            self.ui_elements['area_info_frame'], "Сущностей: -"
        )
        
    def _create_control_buttons(self, parent):
        """Создание кнопок управления"""
        control_frame = tk.Frame(parent, bg=UIStyles.COLORS['bg_medium'])
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Кнопки с улучшенным стилем
        self.ui_elements['pause_btn'] = self._create_control_button(
            control_frame, "Пауза", self._toggle_pause, UIStyles.COLORS['accent_orange']
        )
        self.ui_elements['save_btn'] = self._create_control_button(
            control_frame, "Сохранить", self._save_game, UIStyles.COLORS['accent_green']
        )
        self.ui_elements['menu_btn'] = self._create_control_button(
            control_frame, "Меню", self._show_game_menu, UIStyles.COLORS['accent_blue']
        )
        
    def _create_control_button(self, parent, text: str, command: Callable, bg_color: str):
        """Создание кнопки управления"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=UIStyles.FONTS['text_medium'],
            bg=bg_color,
            fg=UIStyles.COLORS['text_white'],
            relief='flat',
            width=15,
            **UIStyles.BUTTON_STYLE
        )
        btn.pack(pady=2)
        
        # Hover эффект
        btn.bind('<Enter>', lambda e: btn.configure(bg=self._lighten_color(bg_color)))
        btn.bind('<Leave>', lambda e: btn.configure(bg=bg_color))
        
        return btn
        
    def _create_info_label(self, parent, text: str):
        """Создание информационной метки"""
        label = tk.Label(
            parent,
            text=text,
            font=UIStyles.FONTS['text_medium'],
            fg=UIStyles.COLORS['text_gray'],
            bg=UIStyles.COLORS['bg_medium']
        )
        label.pack(anchor='w', padx=5, pady=2)
        return label
        
    def _create_control_panel(self):
        """Создание панели управления"""
        control_frame = tk.Frame(self.root, bg=UIStyles.COLORS['bg_medium'], height=100)
        control_frame.pack(fill='x', padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        # Статус игры
        self.ui_elements['status_label'] = tk.Label(
            control_frame,
            text="Готов к запуску",
            font=UIStyles.FONTS['text_large'],
            fg=UIStyles.COLORS['accent_green'],
            bg=UIStyles.COLORS['bg_medium']
        )
        self.ui_elements['status_label'].pack(pady=10)
        
        # Прогресс-бар
        self.ui_elements['progress_bar'] = ttk.Progressbar(
            control_frame,
            mode='indeterminate'
        )
        self.ui_elements['progress_bar'].pack(fill='x', padx=10, pady=5)
        
    def _bind_events(self):
        """Привязка событий"""
        # Закрытие окна
        self.root.protocol("WM_DELETE_WINDOW", self._exit_game)
        
        # Клавиши
        self.root.bind('<Key>', self._on_key)
        self.root.bind('<Escape>', lambda e: self._show_game_menu())
        
        # Мышь
        if self.game_canvas:
            self.game_canvas.bind('<Button-1>', self._on_mouse_click)
            self.game_canvas.bind('<Motion>', self._on_mouse_move)
            
    def _lighten_color(self, color: str, factor: float = 1.2) -> str:
        """Осветление цвета для hover эффектов"""
        # Простая реализация осветления цвета
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
        
    def _start_new_game(self):
        """Запуск новой игры"""
        try:
            self.game_state = GameState.LOADING
            self._update_status("Загрузка новой игры...", UIStyles.COLORS['accent_orange'])
            
            # Показываем диалог настроек
            if not self._show_new_game_dialog():
                self.game_state = GameState.MENU
                self._update_status("Готов к запуску", UIStyles.COLORS['accent_green'])
                return
            
            # Скрываем главное меню
            self.ui_elements['menu_frame'].pack_forget()
            
            # Инициализируем игровые системы
            self._init_game_systems()
            
            # Создаем игрока
            self.player = entity_factory.create_player(
                self.game_settings.player_name,
                (400, 300)
            )
            
            # Загружаем начальную область
            self._load_area(self.current_area)
            
            # Запускаем игровой цикл
            self.game_running = True
            self.game_paused = False
            self.game_state = GameState.PLAYING
            self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
            self.game_thread.start()
            
            # Обновляем статус
            self._update_status("Игра запущена", UIStyles.COLORS['accent_green'])
            
        except Exception as e:
            self.game_state = GameState.MENU
            self._update_status("Ошибка запуска", UIStyles.COLORS['accent_red'])
            messagebox.showerror("Ошибка", f"Не удалось запустить игру: {e}")
            
    def _show_new_game_dialog(self):
        """Показывает диалог настроек новой игры"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новая игра")
        dialog.geometry("400x300")
        dialog.configure(bg=UIStyles.COLORS['bg_medium'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрируем диалог
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Имя игрока
        tk.Label(
            dialog,
            text="Имя игрока:",
            font=UIStyles.FONTS['text_large'],
            fg=UIStyles.COLORS['text_gray'],
            bg=UIStyles.COLORS['bg_medium']
        ).pack(pady=10)
        
        name_entry = tk.Entry(
            dialog,
            font=UIStyles.FONTS['text_large'],
            width=20
        )
        name_entry.pack(pady=5)
        name_entry.insert(0, self.game_settings.player_name)
        name_entry.focus()
        
        # Сложность
        tk.Label(
            dialog,
            text="Сложность:",
            font=UIStyles.FONTS['text_large'],
            fg=UIStyles.COLORS['text_gray'],
            bg=UIStyles.COLORS['bg_medium']
        ).pack(pady=10)
        
        difficulty_var = tk.StringVar(value=self.game_settings.difficulty)
        difficulty_combo = ttk.Combobox(
            dialog,
            textvariable=difficulty_var,
            values=["easy", "normal", "hard"],
            state="readonly",
            width=15
        )
        difficulty_combo.pack(pady=5)
        
        # Кнопки
        button_frame = tk.Frame(dialog, bg=UIStyles.COLORS['bg_medium'])
        button_frame.pack(pady=20)
        
        result = [False]
        
        def on_ok():
            self.game_settings.player_name = name_entry.get()
            self.game_settings.difficulty = difficulty_var.get()
            result[0] = True
            dialog.destroy()
            
        def on_cancel():
            dialog.destroy()
        
        tk.Button(
            button_frame,
            text="OK",
            command=on_ok,
            font=UIStyles.FONTS['text_medium'],
            bg=UIStyles.COLORS['accent_blue'],
            fg=UIStyles.COLORS['text_white'],
            width=10,
            **UIStyles.BUTTON_STYLE
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Отмена",
            command=on_cancel,
            font=UIStyles.FONTS['text_medium'],
            bg=UIStyles.COLORS['text_dark'],
            fg=UIStyles.COLORS['text_white'],
            width=10,
            **UIStyles.BUTTON_STYLE
        ).pack(side='left', padx=5)
        
        dialog.wait_window()
        return result[0]
        
    def _load_game(self):
        """Загрузка игры"""
        saves = game_state_manager.get_save_list()
        
        if not saves:
            messagebox.showinfo("Информация", "Нет доступных сохранений")
            return
        
        # Показываем диалог выбора сохранения
        dialog = tk.Toplevel(self.root)
        dialog.title("Загрузить игру")
        dialog.geometry("500x400")
        dialog.configure(bg=UIStyles.COLORS['bg_medium'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Список сохранений
        listbox = tk.Listbox(
            dialog,
            font=UIStyles.FONTS['text_large'],
            bg=UIStyles.COLORS['bg_dark'],
            fg=UIStyles.COLORS['text_gray'],
            selectmode='single'
        )
        listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        for save in saves:
            listbox.insert(tk.END, f"{save['name']} - {save['date']}")
        
        # Кнопки
        button_frame = tk.Frame(dialog, bg=UIStyles.COLORS['bg_medium'])
        button_frame.pack(pady=10)
        
        result = [None]
        
        def on_load():
            selection = listbox.curselection()
            if selection:
                result[0] = saves[selection[0]]['id']
                dialog.destroy()
            else:
                messagebox.showwarning("Предупреждение", "Выберите сохранение")
        
        def on_cancel():
            dialog.destroy()
        
        tk.Button(
            button_frame,
            text="Загрузить",
            command=on_load,
            font=UIStyles.FONTS['text_medium'],
            bg=UIStyles.COLORS['accent_blue'],
            fg=UIStyles.COLORS['text_white'],
            width=10,
            **UIStyles.BUTTON_STYLE
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Отмена",
            command=on_cancel,
            font=UIStyles.FONTS['text_medium'],
            bg=UIStyles.COLORS['text_dark'],
            fg=UIStyles.COLORS['text_white'],
            width=10,
            **UIStyles.BUTTON_STYLE
        ).pack(side='left', padx=5)
        
        dialog.wait_window()
        
        if result[0]:
            try:
                self.game_state = GameState.LOADING
                self._update_status("Загрузка игры...", UIStyles.COLORS['accent_orange'])
                
                if game_state_manager.load_game(result[0]):
                    self._init_game_systems()
                    self.game_running = True
                    self.game_paused = False
                    self.game_state = GameState.PLAYING
                    self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
                    self.game_thread.start()
                    self._update_status("Игра загружена", UIStyles.COLORS['accent_green'])
                else:
                    self.game_state = GameState.MENU
                    self._update_status("Ошибка загрузки", UIStyles.COLORS['accent_red'])
                    messagebox.showerror("Ошибка", "Не удалось загрузить игру")
            except Exception as e:
                self.game_state = GameState.MENU
                self._update_status("Ошибка загрузки", UIStyles.COLORS['accent_red'])
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
                
    def _show_settings(self):
        """Показ настроек"""
        messagebox.showinfo("Настройки", "Настройки игры будут добавлены в следующей версии")
        
    def _init_game_systems(self):
        """Инициализация игровых систем"""
        # Создаем рендер менеджер
        self.render_manager = RenderManager(self.game_canvas, game_state_manager)
        
        # Создаем игровое меню
        self.game_menu = GameMenu(self.game_canvas, 800, 600)
        
        # Инициализируем AI систему
        ai_manager.initialize()
        
    def _load_area(self, area_name: str):
        """Загрузка игровой области"""
        self.current_area = area_name
        self.entities.clear()
        
        # Создаем врагов в зависимости от области
        if area_name == "starting_area":
            for i in range(3):
                enemy = entity_factory.create_enemy(
                    "warrior",
                    1,
                    (100 + i * 50, 100 + i * 50)
                )
                self.entities.append(enemy)
                if hasattr(enemy, 'ai_core'):
                    ai_manager.register_entity(enemy, enemy.ai_core)
        
        # Обновляем информацию об области
        self._update_area_info()
        
    def _game_loop(self):
        """Основной игровой цикл с оптимизацией"""
        try:
            while self.game_running:
                # Вычисляем delta time
                current_time = time.time()
                delta_time = current_time - self.last_frame_time
                self.last_frame_time = current_time
                
                # Обновляем время игры
                self.game_time += int(delta_time * 1000)
                
                # Обновляем FPS счетчик
                self.frame_count += 1
                if current_time - self.last_fps_time >= 1.0:
                    self.fps_counter = self.frame_count
                    self.frame_count = 0
                    self.last_fps_time = current_time
                
                # Обновляем игровую логику только если не на паузе
                if not self.game_paused:
                    self._update_game(delta_time)
                
                # Рендерим
                self._render_game()
                
                # Обновляем UI
                self._update_ui()
                
                # Ограничиваем FPS
                target_frame_time = 1.0 / self.game_settings.fps
                sleep_time = max(0, target_frame_time - delta_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except Exception as e:
            print(f"Ошибка в игровом цикле: {e}")
            self.game_state = GameState.MENU
            
    def _update_game(self, delta_time: float):
        """Обновление игровой логики"""
        # Обновляем AI систему
        ai_manager.update(delta_time)
        
        # Обновляем игрока
        if self.player:
            self.player.update(delta_time)
        
        # Обновляем сущности
        for entity in self.entities[:]:
            entity.update(delta_time)
            if not entity.alive:
                self.entities.remove(entity)
                ai_manager.unregister_entity(entity)
        
        # Проверяем коллизии
        self._check_collisions()
        
    def _render_game(self):
        """Рендеринг игры"""
        if not self.render_manager:
            return
            
        # Очищаем canvas
        self.game_canvas.delete("all")
        
        # Рендерим область
        self.render_manager.render_area(self.current_area)
        
        # Рендерим сущности
        for entity in self.entities:
            self.render_manager.render_entity(entity)
        
        # Рендерим игрока
        if self.player:
            self.render_manager.render_entity(self.player)
        
        # Рендерим UI
        if self.game_menu and self.game_menu.visible:
            self.game_menu.render(self.render_manager)
            
    def _update_ui(self):
        """Обновление UI"""
        if not self.player:
            return
            
        # Обновляем информацию об игроке
        self.ui_elements['player_name_label'].config(text=f"Имя: {self.player.name}")
        self.ui_elements['player_level_label'].config(text=f"Уровень: {getattr(self.player, 'level', 1)}")
        self.ui_elements['player_health_label'].config(text=f"Здоровье: {int(getattr(self.player, 'health', 100))}")
        self.ui_elements['player_fps_label'].config(text=f"FPS: {self.fps_counter}")
        
        # Обновляем информацию об области
        self._update_area_info()
        
    def _update_area_info(self):
        """Обновление информации об области"""
        self.ui_elements['area_name_label'].config(text=f"Название: {self.current_area}")
        self.ui_elements['entities_count_label'].config(text=f"Сущностей: {len(self.entities)}")
        
    def _update_status(self, text: str, color: str):
        """Обновление статуса игры"""
        self.ui_elements['status_label'].config(text=text, fg=color)
        
    def _check_collisions(self):
        """Проверка коллизий"""
        if not self.player:
            return
            
        for entity in self.entities:
            if entity.alive and self.player.alive:
                distance = self.player.distance_to(entity)
                if distance < 50:
                    if self.player.can_attack():
                        self.player.attack(entity)
                    if entity.can_attack():
                        entity.attack(self.player)
                        
    def _toggle_pause(self):
        """Переключение паузы"""
        if self.game_state == GameState.PLAYING:
            self.game_paused = not self.game_paused
            if self.game_paused:
                self.game_state = GameState.PAUSED
                self._update_status("Игра на паузе", UIStyles.COLORS['accent_orange'])
                self.ui_elements['pause_btn'].config(text="Продолжить")
            else:
                self.game_state = GameState.PLAYING
                self._update_status("Игра запущена", UIStyles.COLORS['accent_green'])
                self.ui_elements['pause_btn'].config(text="Пауза")
        
    def _save_game(self):
        """Сохранение игры"""
        try:
            if game_state_manager.save_game():
                messagebox.showinfo("Сохранение", "Игра сохранена успешно")
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить игру")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")
            
    def _show_game_menu(self):
        """Показ игрового меню"""
        if self.game_menu and self.game_state == GameState.PLAYING:
            self.game_menu.toggle()
            
    def _on_key(self, event):
        """Обработка нажатий клавиш"""
        if self.game_state != GameState.PLAYING:
            return
            
        key = event.keysym.lower()
        
        if key == 'escape':
            self._show_game_menu()
        elif key == 'p':
            self._toggle_pause()
        elif key == 'f5':
            self._save_game()
            
    def _on_mouse_click(self, event):
        """Обработка кликов мыши"""
        if self.game_state != GameState.PLAYING or not self.player:
            return
            
        # Перемещение игрока
        self.player.position = (event.x, event.y)
        
    def _on_mouse_move(self, event):
        """Обработка движения мыши"""
        pass
        
    def _exit_game(self):
        """Выход из игры"""
        if self.game_running:
            self.game_running = False
            if self.game_thread:
                self.game_thread.join(timeout=1)
        
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """Запуск главного окна"""
        self.root.mainloop()


def main():
    """Главная функция для запуска UI"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()

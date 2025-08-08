import random
import time
import tkinter as tk
import json
import os
from entities.player import Player
from entities.enemy import Enemy
from entities.boss import Boss
from items.weapon import WeaponGenerator
from ai.cooperation import AICoordinator
from map.tiled_map import TiledMap
import config


def rgb_to_hex(color_tuple):
    r, g, b = color_tuple
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


class TkGame:
    def __init__(self, width: int = 1200, height: int = 800):
        self.show_menu = True
        self.paused = False
        self.save_file = "save_game.json"
        
        self.root = tk.Tk()
        self.root.title("Автономный ИИ-выживач (Tkinter)")
        # Используем значения окна из config по умолчанию
        self.width = width or config.WIDTH
        self.height = height or config.HEIGHT
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg=rgb_to_hex(config.BACKGROUND))
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Загрузка предметов
        self.load_items()
        
        self.running = True
        self.last_time = time.time()
        self.victory_shown = False
        self.reincarnation_count = 0
        self.generation_count = 0
        self.session_start_time = time.time()

        # Карта
        self.map_view_x = 0
        self.map_view_y = 0
        self.tiled_map = None
        
        # Настройки игры (меняются в меню)
        self.settings = {
            "difficulty": "normal",        # easy | normal | hard
            "learning_rate": 1.0,            # скорость обучения игрока
            "window_size": (self.width, self.height),
        }
        
        # Динамические данные для кликов по меню/настройкам
        self.menu_buttons = []  # [{label, action, x0,x1,y0,y1}]
        self.settings_controls = []  # [{key, type, x0,x1,y0,y1, value/index}]
        
        # Инициализация игры
        if self.show_menu:
            self.show_main_menu()
        else:
            self.init_game()
    
    def load_items(self):
        """Загрузка предметов из JSON"""
        try:
            with open("items/items.json", "r", encoding="utf-8") as f:
                self.items_data = json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки предметов: {e}")
            self.items_data = {}
    
    def show_main_menu(self):
        """Показать главное меню"""
        # Снимаем потенциальные старые бинды
        self.root.unbind("<Key>")
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-3>")
        
        self.canvas.delete("all")
        self.menu_buttons = []
        
        # Заголовок
        self.canvas.create_text(
            self.width // 2, 100,
            text="Автономный ИИ-выживач",
            fill=rgb_to_hex((255, 215, 0)),
            font=("Arial", 32, "bold")
        )
        
        # Кнопки
        button_y = 250
        button_spacing = 80
        button_height = 50
        button_half_w = 100
        x0 = self.width // 2 - button_half_w
        x1 = self.width // 2 + button_half_w
        
        def add_button(label, action, fill, outline):
            nonlocal button_y
            y0, y1 = button_y, button_y + button_height
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=rgb_to_hex(fill), outline=rgb_to_hex(outline))
            self.canvas.create_text(self.width // 2, (y0 + y1) // 2, text=label, fill=rgb_to_hex((255, 255, 255)), font=("Arial", 16, "bold"))
            self.menu_buttons.append({"label": label, "action": action, "x0": x0, "x1": x1, "y0": y0, "y1": y1})
            button_y += button_spacing
        
        add_button("Новая игра", "new_game", (50, 150, 50), (100, 200, 100))
        add_button("Загрузить игру", "load_game", (100, 100, 200), (150, 150, 250))
        add_button("Настройки", "settings", (200, 150, 50), (250, 200, 100))
        add_button("Выход", "exit", (200, 50, 50), (250, 100, 100))
        
        # Привязка событий мыши
        self.canvas.bind("<Button-1>", self._on_menu_click)
    
    def _on_menu_click(self, event):
        """Обработка кликов в главном меню"""
        x, y = event.x, event.y
        for btn in self.menu_buttons:
            if btn["x0"] <= x <= btn["x1"] and btn["y0"] <= y <= btn["y1"]:
                action = btn["action"]
                if action == "new_game":
                    self.show_menu = False
                    self.init_game()
                elif action == "load_game":
                    self.load_game()
                elif action == "settings":
                    self.show_settings()
                elif action == "exit":
                    self.stop()
                return
    
    def init_game(self):
        """Инициализация игры"""
        try:
            # Пользовательская карта
            self.tiled_map = TiledMap("map/map.json")
        except Exception:
            self.tiled_map = None

        # Сущности
        self.player = self._create_player()
        self.enemies = self._create_enemies()
        self.boss = self._create_boss()

        # Оружие игроку
        if not self.player.equipment.get("weapon"):
            starter_weapon = WeaponGenerator.generate_weapon(1)
            self.player.equip_item(starter_weapon)

        # AI координатор
        self.coordinator = AICoordinator()
        for enemy in self.enemies:
            self.coordinator.register_entity(enemy, "enemy_group")
        if self.boss:
            self.coordinator.register_entity(self.boss, "boss_group")

        # Пользовательские объекты на карте
        self.user_obstacles = set()  # {(tx, ty)}
        self.chests = []  # [{"tx": int, "ty": int, "opened": bool}]

        # Ввод
        self.root.bind("<Escape>", lambda e: self.stop())
        self.root.bind("<space>", lambda e: self.soft_restart())
        self.root.bind("<p>", lambda e: self.toggle_pause())
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)

        # Камера к центру карты
        self._center_initial_camera()

        # Применяем настройки: скорость обучения игрока
        try:
            lr = float(self.settings.get("learning_rate", 1.0))
            self.player.learning_rate = max(0.01, lr)
        except Exception:
            self.player.learning_rate = 1.0
        
        # Старт цикла
        self.root.after(16, self.game_loop)
    
    def load_game(self):
        """Загрузка сохраненной игры"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    save_data = json.load(f)
                
                self.show_menu = False
                self.init_game()
                
                # Восстановление состояния
                self.reincarnation_count = save_data.get("reincarnation_count", 0)
                self.generation_count = save_data.get("generation_count", 0)
                self.session_start_time = save_data.get("session_start_time", time.time())
                
                # Восстановление игрока
                if "player" in save_data:
                    player_data = save_data["player"]
                    self.player.health = player_data.get("health", self.player.max_health)
                    self.player.level = player_data.get("level", 1)
                    self.player.learning_rate = player_data.get("learning_rate", 1.0)
                    self.player.position = player_data.get("position", [self.width // 2, self.height // 2])
                
                # Восстановление препятствий и сундуков
                self.user_obstacles = set(tuple(obs) for obs in save_data.get("obstacles", []))
                self.chests = save_data.get("chests", [])
                
                print("Игра загружена успешно")
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                self.show_menu = True
                self.show_main_menu()
        else:
            print("Сохранение не найдено")
            self.show_menu = True
            self.show_main_menu()
    
    def save_game(self):
        """Сохранение игры"""
        try:
            save_data = {
                "reincarnation_count": self.reincarnation_count,
                "generation_count": self.generation_count,
                "session_start_time": self.session_start_time,
                "player": {
                    "health": self.player.health,
                    "level": self.player.level,
                    "learning_rate": self.player.learning_rate,
                    "position": self.player.position
                },
                "obstacles": list(self.user_obstacles),
                "chests": self.chests
            }
            
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)
            
            print("Игра сохранена")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    
    def toggle_pause(self):
        """Переключение паузы"""
        self.paused = not self.paused
        if self.paused:
            self.show_pause_menu()
        else:
            self.canvas.delete("pause_menu")
            self.root.after(16, self.game_loop)
    
    def show_pause_menu(self):
        """Показать меню паузы"""
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill=rgb_to_hex((0, 0, 0)), stipple="gray50",
            tags="pause_menu"
        )
        
        # Заголовок паузы
        self.canvas.create_text(
            self.width // 2, 200,
            text="ПАУЗА",
            fill=rgb_to_hex((255, 215, 0)),
            font=("Arial", 36, "bold"),
            tags="pause_menu"
        )
        
        # Кнопки паузы
        button_y = 300
        button_spacing = 60
        
        # Продолжить
        self.canvas.create_rectangle(
            self.width // 2 - 100, button_y,
            self.width // 2 + 100, button_y + 40,
            fill=rgb_to_hex((50, 150, 50)), outline=rgb_to_hex((100, 200, 100)),
            tags="pause_menu"
        )
        self.canvas.create_text(
            self.width // 2, button_y + 20,
            text="Продолжить",
            fill=rgb_to_hex((255, 255, 255)),
            font=("Arial", 14, "bold"),
            tags="pause_menu"
        )
        
        # Сохранить
        button_y += button_spacing
        self.canvas.create_rectangle(
            self.width // 2 - 100, button_y,
            self.width // 2 + 100, button_y + 40,
            fill=rgb_to_hex((100, 100, 200)), outline=rgb_to_hex((150, 150, 250)),
            tags="pause_menu"
        )
        self.canvas.create_text(
            self.width // 2, button_y + 20,
            text="Сохранить",
            fill=rgb_to_hex((255, 255, 255)),
            font=("Arial", 14, "bold"),
            tags="pause_menu"
        )
        
        # Главное меню
        button_y += button_spacing
        self.canvas.create_rectangle(
            self.width // 2 - 100, button_y,
            self.width // 2 + 100, button_y + 40,
            fill=rgb_to_hex((200, 150, 50)), outline=rgb_to_hex((250, 200, 100)),
            tags="pause_menu"
        )
        self.canvas.create_text(
            self.width // 2, button_y + 20,
            text="Главное меню",
            fill=rgb_to_hex((255, 255, 255)),
            font=("Arial", 14, "bold"),
            tags="pause_menu"
        )
        
        # Привязка событий паузы
        self.canvas.bind("<Button-1>", self._on_pause_click)
    
    def _on_pause_click(self, event):
        """Обработка кликов в меню паузы"""
        x, y = event.x, event.y
        
        # Продолжить
        if 300 <= y <= 340:
            self.paused = False
            self.canvas.delete("pause_menu")
            self.canvas.bind("<Button-1>", self._on_left_click)
            self.root.after(16, self.game_loop)
        # Сохранить
        elif 360 <= y <= 400:
            self.save_game()
        # Главное меню
        elif 420 <= y <= 460:
            self.show_menu = True
            self.paused = False
            self.show_main_menu()
    
    def show_settings(self):
        """Показать настройки (сложность, скорость обучения, размер окна)."""
        # Снимаем старые бинды
        self.root.unbind("<Key>")
        self.canvas.unbind("<Button-1>")
        
        self.canvas.delete("all")
        self.settings_controls = []
        
        # Заголовок настроек
        self.canvas.create_text(
            self.width // 2, 100,
            text="Настройки",
            fill=rgb_to_hex((255, 215, 0)),
            font=("Arial", 28, "bold")
        )
        
        left_x = self.width // 2 - 250
        right_x = self.width // 2 + 250
        row_y = 200
        row_step = 90
        
        # Сложность
        self.canvas.create_text(left_x, row_y, text="Сложность:", fill="#ddd", font=("Arial", 16, "bold"), anchor="w")
        difficulties = ["easy", "normal", "hard"]
        current_idx = max(0, difficulties.index(self.settings.get("difficulty", "normal")))
        btn_w, btn_h = 120, 40
        gap = 20
        x_cursor = left_x + 150
        for i, lvl in enumerate(difficulties):
            x0, y0 = x_cursor + i * (btn_w + gap), row_y - btn_h // 2
            x1, y1 = x0 + btn_w, y0 + btn_h
            fill = (90, 110, 150) if i == current_idx else (70, 90, 120)
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=rgb_to_hex(fill), outline="#99a")
            self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=lvl.capitalize(), fill="#eee", font=("Arial", 14, "bold"))
            self.settings_controls.append({"key": "difficulty", "type": "choice", "value": lvl, "x0": x0, "x1": x1, "y0": y0, "y1": y1})
        
        # Скорость обучения
        row_y += row_step
        self.canvas.create_text(left_x, row_y, text="Скорость обучения:", fill="#ddd", font=("Arial", 16, "bold"), anchor="w")
        val = float(self.settings.get("learning_rate", 1.0))
        # Минус
        x0, y0 = left_x + 300, row_y - 20
        x1, y1 = x0 + 40, y0 + 40
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="#566", outline="#99a")
        self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text="-", fill="#eef", font=("Arial", 18, "bold"))
        self.settings_controls.append({"key": "learning_rate", "type": "dec", "x0": x0, "x1": x1, "y0": y0, "y1": y1})
        # Значение
        val_box_x0 = x1 + 10
        val_box_x1 = val_box_x0 + 120
        self.canvas.create_rectangle(val_box_x0, y0, val_box_x1, y1, outline="#99a")
        self.canvas.create_text((val_box_x0 + val_box_x1) // 2, (y0 + y1) // 2, text=f"{val:.2f}", fill="#eef", font=("Arial", 14))
        # Плюс
        x0p = val_box_x1 + 10
        x1p = x0p + 40
        self.canvas.create_rectangle(x0p, y0, x1p, y1, fill="#566", outline="#99a")
        self.canvas.create_text((x0p + x1p) // 2, (y0 + y1) // 2, text="+", fill="#eef", font=("Arial", 18, "bold"))
        self.settings_controls.append({"key": "learning_rate", "type": "inc", "x0": x0p, "x1": x1p, "y0": y0, "y1": y1})
        
        # Размер окна (пресеты)
        row_y += row_step
        self.canvas.create_text(left_x, row_y, text="Размер окна:", fill="#ddd", font=("Arial", 16, "bold"), anchor="w")
        sizes = [(1024, 768), (1200, 800), (1600, 900)]
        cur_w, cur_h = self.settings.get("window_size", (self.width, self.height))
        x_cursor = left_x + 150
        for i, (w, h) in enumerate(sizes):
            x0, y0 = x_cursor + i * (btn_w + gap), row_y - btn_h // 2
            x1, y1 = x0 + btn_w, y0 + btn_h
            is_sel = (w, h) == (cur_w, cur_h)
            fill = (90, 110, 150) if is_sel else (70, 90, 120)
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=rgb_to_hex(fill), outline="#99a")
            self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text=f"{w}x{h}", fill="#eee", font=("Arial", 14))
            self.settings_controls.append({"key": "window_size", "type": "choice", "value": (w, h), "x0": x0, "x1": x1, "y0": y0, "y1": y1})
        
        # Кнопки управления
        row_y += row_step + 30
        ctrl_btn_w, ctrl_btn_h = 160, 48
        cx = self.width // 2
        # Применить
        x0, y0 = cx - ctrl_btn_w - 20, row_y
        x1, y1 = x0 + ctrl_btn_w, y0 + ctrl_btn_h
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=rgb_to_hex((50, 150, 50)), outline="#9c9")
        self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text="Применить", fill="#fff", font=("Arial", 16, "bold"))
        self.settings_controls.append({"key": "apply", "type": "action", "x0": x0, "x1": x1, "y0": y0, "y1": y1})
        # Назад
        x0, y0 = cx + 20, row_y
        x1, y1 = x0 + ctrl_btn_w, y0 + ctrl_btn_h
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=rgb_to_hex((200, 150, 50)), outline="#cc9")
        self.canvas.create_text((x0 + x1) // 2, (y0 + y1) // 2, text="Назад", fill="#fff", font=("Arial", 16, "bold"))
        self.settings_controls.append({"key": "back", "type": "action", "x0": x0, "x1": x1, "y0": y0, "y1": y1})
        
        # Обработчик кликов по настройкам
        self.canvas.bind("<Button-1>", self._on_settings_click)

    def _on_settings_click(self, event):
        x, y = event.x, event.y
        for ctrl in self.settings_controls:
            if ctrl["x0"] <= x <= ctrl["x1"] and ctrl["y0"] <= y <= ctrl["y1"]:
                key = ctrl["key"]
                ctype = ctrl["type"]
                if ctype == "choice":
                    self.settings[key] = ctrl.get("value")
                    # Перерисовать, чтобы подсветить выбранное
                    self.show_settings()
                    return
                if key == "learning_rate":
                    cur = float(self.settings.get("learning_rate", 1.0))
                    if ctype == "inc":
                        cur = min(5.0, cur + 0.1)
                    elif ctype == "dec":
                        cur = max(0.1, cur - 0.1)
                    self.settings["learning_rate"] = round(cur, 2)
                    self.show_settings()
                    return
                if ctype == "action":
                    if key == "apply":
                        self._apply_settings()
                        self.show_main_menu()
                        return
                    if key == "back":
                        self.show_main_menu()
                        return
        
    def _apply_settings(self):
        # Применяем размер окна и фон
        new_w, new_h = self.settings.get("window_size", (self.width, self.height))
        if (new_w, new_h) != (self.width, self.height):
            self.width, self.height = int(new_w), int(new_h)
            try:
                self.root.geometry(f"{self.width}x{self.height}")
            except Exception:
                pass
            self.canvas.config(width=self.width, height=self.height)
        # Обновим config, чтобы сохранить согласованность
        try:
            config.WIDTH, config.HEIGHT = self.width, self.height
        except Exception:
            pass
        # Обновим фон в соответствии с config
        try:
            self.canvas.config(bg=rgb_to_hex(config.BACKGROUND))
        except Exception:
            pass
    
    def _return_to_main_menu(self, event):
        """Возврат в главное меню из настроек"""
        self.root.unbind("<Key>")  # Отвязываем обработчик
        self.show_main_menu()

    # --- Инициализация сущностей ---
    def _create_player(self) -> Player:
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
            map_px_h = self.tiled_map.height * self.tiled_map.tileheight
            start_x = map_px_w // 2
            start_y = map_px_h // 2
        else:
            start_x = self.width // 2
            start_y = self.height // 2
        player = Player("player_ai", (start_x, start_y))
        # Значение будет скорректировано в init_game() из self.settings
        player.learning_rate = float(self.settings.get("learning_rate", 1.0))
        # Убеждаемся, что combat_stats инициализированы правильно
        if "max_health" not in player.combat_stats:
            player.combat_stats["max_health"] = 100
        if "health" not in player.combat_stats:
            player.combat_stats["health"] = 100
        return player

    def _create_enemies(self) -> list:
        enemy_list = []
        enemy_types = ["warrior", "archer", "mage"]
        # Увеличиваем расстояние между врагами
        map_width = self.tiled_map.width * self.tiled_map.tilewidth if self.tiled_map else self.width
        map_height = self.tiled_map.height * self.tiled_map.tileheight if self.tiled_map else self.height
        
        # Убеждаемся, что размеры карты корректны
        if map_width <= 200:
            map_width = self.width
        if map_height <= 200:
            map_height = self.height
        
        # Количество и уровень врагов зависят от сложности
        difficulty = self.settings.get("difficulty", "normal")
        if difficulty == "easy":
            num_enemies, lvl_min, lvl_max = 6, 1, 3
        elif difficulty == "hard":
            num_enemies, lvl_min, lvl_max = 14, 3, 7
        else:
            num_enemies, lvl_min, lvl_max = 10, 1, 5
        for _ in range(num_enemies):
            e = Enemy(random.choice(enemy_types), level=random.randint(lvl_min, lvl_max))
            # Распределяем врагов по всей карте
            x = random.randint(100, max(200, map_width - 100))
            y = random.randint(100, max(200, map_height - 100))
            e.position = [x, y]
            e.player_ref = self.player
            enemy_list.append(e)
        return enemy_list

    def _create_boss(self) -> Boss:
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            bx = self.tiled_map.width * self.tiled_map.tilewidth - 300
            by = 300
        else:
            bx, by = self.width - 300, 300
        difficulty = self.settings.get("difficulty", "normal")
        boss_level = 12 if difficulty == "easy" else (20 if difficulty == "hard" else 15)
        boss = Boss(boss_type="dragon", level=boss_level, position=(bx, by))
        boss.learning_rate = 0.005
        boss.player_ref = self.player
        return boss

    # --- Жизненный цикл ---
    def soft_restart(self) -> None:
        """Перезапуск мира без закрытия окна и без потери знаний."""
        self.victory_shown = False
        self.generation_count += 1
        
        # Возрождаем игрока
        self._respawn_player()
        # Возрождаем врагов и босса
        for e in self.enemies:
            self._respawn_entity(e)
            # Перемещаем врагов на новые позиции
            map_width = self.tiled_map.width * self.tiled_map.tilewidth if self.tiled_map else self.width
            map_height = self.tiled_map.height * self.tiled_map.tileheight if self.tiled_map else self.height
            
            # Убеждаемся, что размеры карты корректны
            if map_width <= 200:
                map_width = self.width
            if map_height <= 200:
                map_height = self.height
            
            e.position = [random.randint(100, max(200, map_width - 100)), random.randint(100, max(200, map_height - 100))]
        if self.boss:
            self._respawn_entity(self.boss)
            # Босс в правом верхнем углу карты
            if self.tiled_map:
                map_width = self.tiled_map.width * self.tiled_map.tilewidth
                if map_width <= 200:
                    map_width = self.width
                self.boss.position = [max(300, map_width - 300), 300]
            else:
                self.boss.position = [self.width - 300, 300]
        # Сохраняем добавленные человеком препятствия/сундуки
        # Камера назад на игрока
        self._center_initial_camera()
        # Продолжаем цикл (если был остановлен)
        if not self.running:
            self.running = True
            self.root.after(16, self.game_loop)

    def stop(self) -> None:
        """Остановка игры и закрытие окна"""
        print("Закрытие игры...")
        self.running = False
        try:
            # Уничтожаем окно
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"Ошибка при закрытии окна: {e}")
            # Принудительное завершение
            import sys
            sys.exit(0)

    def game_loop(self) -> None:
        if not self.running:
            return
        if self.paused:
            self.root.after(16, self.game_loop)
            return
        
        now = time.time()
        delta_time = now - self.last_time
        self.last_time = now

        # Логика ИИ игрока и сущностей
        self._update_player_ai(delta_time)
        self.player.update(delta_time)

        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(delta_time)
                self._move_entity_toward(enemy, self.player.position, enemy.combat_stats.get("movement_speed", 100.0), delta_time)
                self._process_chest_interactions(enemy)

        if self.boss and self.boss.alive:
            self.boss.update(delta_time)
            self._move_entity_toward(self.boss, self.player.position, self.boss.combat_stats.get("movement_speed", 80.0), delta_time)
            self._process_chest_interactions(self.boss)

        # Групповая логика
        self.coordinator.update_group_behavior("enemy_group")
        self.coordinator.update_group_behavior("boss_group")

        # Столкновения и фильтрация
        self.check_collisions()
        self.enemies = [e for e in self.enemies if e.alive]

        # Камера
        if self.tiled_map:
            self._center_camera_on_player()

        # Рендер
        self.draw()

        # Смерть игрока -> перерождение, а не остановка игры
        if not self.player.alive:
            self._respawn_player()

        # Победа: все враги и босс повержены
        if (not self.enemies) and (not self.boss or not self.boss.alive):
            if not self.victory_shown:
                self._draw_banner("Победа! Все повержены.")
                self.victory_shown = True

        self.root.after(16, self.game_loop)

    # --- Игровая логика ---
    def check_collisions(self) -> None:
        px, py = self.player.position
        # Враги
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            ex, ey = enemy.position
            dx = px - ex
            dy = py - ey
            if (dx * dx + dy * dy) <= (20 + 15) * (20 + 15):
                damage = enemy.damage_output * random.uniform(0.8, 1.2)
                self.player.take_damage({
                    "total": damage,
                    "physical": damage,
                    "source": enemy,
                })

        # Босс
        if self.boss and self.boss.alive:
            bx, by = self.boss.position
            dx = px - bx
            dy = py - by
            if (dx * dx + dy * dy) <= (20 + 30) * (20 + 30):
                damage = self.boss.damage_output * random.uniform(0.9, 1.5)
                self.player.take_damage({
                    "total": damage,
                    "boss": damage,
                    "source": self.boss,
                })

    def draw(self) -> None:
        self.canvas.delete("all")
        # Карта
        if self.tiled_map:
            self.tiled_map.draw_to_canvas(
                self.canvas,
                self.map_view_x,
                self.map_view_y,
                self.width,
                self.height,
                tag="map",
            )

        # Игрок
        px, py = self.player.position
        spx, spy = px - self.map_view_x, py - self.map_view_y
        self._draw_circle(spx, spy, 20, fill=rgb_to_hex((0, 100, 255)) if self.player.alive else rgb_to_hex((50, 50, 50)))

        # Враги
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            ex, ey = enemy.position
            sex, sey = ex - self.map_view_x, ey - self.map_view_y
            if enemy.enemy_type == "warrior":
                color = (255, 50, 50)
            elif enemy.enemy_type == "archer":
                color = (200, 50, 150)
            else:
                color = (50, 150, 255)
            self._draw_circle(sex, sey, 15, fill=rgb_to_hex(color))

        # Босс
        if self.boss and self.boss.alive:
            bx, by = self.boss.position
            sbx, sby = bx - self.map_view_x, by - self.map_view_y
            self._draw_circle(sbx, sby, 30, fill=rgb_to_hex((255, 165, 0)))
            self.canvas.create_text(sbx, sby - 40, text=f"Фаза: {self.boss.phase}", fill=rgb_to_hex((255, 255, 0)))

        # UI
        self.canvas.create_text(10, 10, text=f"Уровень: {self.player.level}", fill=rgb_to_hex((255, 255, 255)), anchor="nw")
        self.canvas.create_text(10, 40, text=f"Здоровье: {int(self.player.health)}/{int(self.player.max_health)}", fill=rgb_to_hex((255, 255, 255)), anchor="nw")

        self.canvas.create_text(10, 70, text=f"Реинкарнации: {self.reincarnation_count}", fill=rgb_to_hex((220, 220, 180)), anchor="nw")
        self.canvas.create_text(10, 100, text=f"Поколения: {self.generation_count}", fill=rgb_to_hex((220, 180, 220)), anchor="nw")
        
        # Инфографика обучения
        session_time = time.time() - self.session_start_time
        self.canvas.create_text(10, 130, text=f"Время сессии: {int(session_time // 60)}:{int(session_time % 60):02d}", fill=rgb_to_hex((180, 220, 180)), anchor="nw")
        self.canvas.create_text(10, 160, text=f"Скорость обучения: {self.player.learning_rate:.3f}", fill=rgb_to_hex((220, 180, 180)), anchor="nw")
        
        # Статистика ИИ
        if hasattr(self.player, 'learning_system'):
            learning_stats = getattr(self.player.learning_system, 'stats', {})
            self.canvas.create_text(10, 190, text=f"Опыт: {learning_stats.get('total_experience', 0)}", fill=rgb_to_hex((180, 180, 220)), anchor="nw")
            self.canvas.create_text(10, 220, text=f"Адаптация: {learning_stats.get('adaptation_rate', 0):.2f}", fill=rgb_to_hex((220, 220, 180)), anchor="nw")
        
        if self.tiled_map:
            self.canvas.create_text(10, 250, text=f"Карта: {self.tiled_map.width}x{self.tiled_map.height} (tile {self.tiled_map.tilewidth}x{self.tiled_map.tileheight})", fill=rgb_to_hex((180, 200, 255)), anchor="nw")
        if self.boss and self.boss.alive:
            self.canvas.create_text(self.width - 220, 10, text=f"Босс: {int(self.boss.health)}/{int(self.boss.max_health)}", fill=rgb_to_hex((255, 100, 100)), anchor="nw")

        # Подсказки и пользовательские объекты
        self.canvas.create_text(10, self.height - 24, text="Space: новое поколение | P: пауза | ЛКМ: препятствие | ПКМ: сундук", fill=rgb_to_hex((200, 220, 240)), anchor="sw")
        if self.tiled_map:
            tw, th = self.tiled_map.tilewidth, self.tiled_map.tileheight
            for (tx, ty) in self.user_obstacles:
                x0 = tx * tw - self.map_view_x
                y0 = ty * th - self.map_view_y
                self.canvas.create_rectangle(x0, y0, x0 + tw, y0 + th, outline="#88a", width=2)
            for chest in self.chests:
                tx, ty = chest["tx"], chest["ty"]
                x0 = tx * tw - self.map_view_x + tw * 0.25
                y0 = ty * th - self.map_view_y + th * 0.25
                x1 = x0 + tw * 0.5
                y1 = y0 + th * 0.5
                fill = "#d4a017" if not chest.get("opened") else "#8b7d5b"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#553")

    # --- Вспомогательные методы ---
    def _draw_circle(self, x: float, y: float, radius: float, fill: str = "#ffffff") -> None:
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill, width=0)

    def _draw_banner(self, text: str) -> None:
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#000000", stipple="gray25")
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=text,
            fill=rgb_to_hex((255, 215, 0)),
            font=("Arial", 24, "bold"),
        )

    def _on_left_click(self, event) -> None:
        if not self.tiled_map:
            return
        if self.paused:
            return
        
        world_x = event.x + self.map_view_x
        world_y = event.y + self.map_view_y
        tw, th = self.tiled_map.tilewidth, self.tiled_map.tileheight
        tx, ty = int(world_x // tw), int(world_y // th)
        
        # Проверяем, есть ли уже препятствие в этой точке
        if (tx, ty) in self.user_obstacles:
            # Убираем препятствие при повторном клике
            self.user_obstacles.remove((tx, ty))
        else:
            # Добавляем препятствие
            self.user_obstacles.add((tx, ty))

    def _on_right_click(self, event) -> None:
        if not self.tiled_map:
            return
        if self.paused:
            return
        
        world_x = event.x + self.map_view_x
        world_y = event.y + self.map_view_y
        tw, th = self.tiled_map.tilewidth, self.tiled_map.tileheight
        tx, ty = int(world_x // tw), int(world_y // th)
        
        # Проверяем, есть ли уже сундук в этой точке
        existing_chest = None
        for chest in self.chests:
            if chest["tx"] == tx and chest["ty"] == ty:
                existing_chest = chest
                break
        
        if existing_chest:
            # Убираем сундук при повторном клике
            self.chests.remove(existing_chest)
        else:
            # Добавляем сундук
            self.chests.append({"tx": tx, "ty": ty, "opened": False})

    def _update_player_ai(self, dt: float) -> None:
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
        speed = float(self.player.combat_stats.get("movement_speed", 120.0))
        self._move_entity_toward(self.player, target_pos, speed, dt)
        self._process_chest_interactions(self.player)

    def _move_entity_toward(self, entity, target_pos, speed: float, dt: float) -> None:
        ex, ey = entity.position
        tx, ty = target_pos
        dx = tx - ex
        dy = ty - ey
        dist = max(1e-6, (dx * dx + dy * dy) ** 0.5)
        nx, ny = dx / dist, dy / dist
        step_x = ex + nx * speed * dt
        step_y = ey + ny * speed * dt
        if self._is_blocked_pixel(step_x, step_y):
            ax, ay = ny, -nx
            step1_x = ex + ax * speed * dt
            step1_y = ey + ay * speed * dt
            if not self._is_blocked_pixel(step1_x, step1_y):
                entity.position[0], entity.position[1] = step1_x, step1_y
                return
            bx, by = -ny, nx
            step2_x = ex + bx * speed * dt
            step2_y = ey + by * speed * dt
            if not self._is_blocked_pixel(step2_x, step2_y):
                entity.position[0], entity.position[1] = step2_x, step2_y
                return
            return
        entity.position[0], entity.position[1] = step_x, step_y

    def _is_blocked_pixel(self, x: float, y: float) -> bool:
        if not self.tiled_map:
            return False
        tw, th = self.tiled_map.tilewidth, self.tiled_map.tileheight
        tx, ty = int(x // tw), int(y // th)
        return (tx, ty) in self.user_obstacles

    def _nearest_chest_world_pos(self, from_pos):
        if not self.chests:
            return None
        fx, fy = from_pos
        best, best_d2 = None, None
        tw = self.tiled_map.tilewidth if self.tiled_map else 40
        th = self.tiled_map.tileheight if self.tiled_map else 40
        for chest in self.chests:
            cx = chest["tx"] * tw + tw / 2
            cy = chest["ty"] * th + th / 2
            d2 = (cx - fx) ** 2 + (cy - fy) ** 2
            if best is None or d2 < best_d2:
                best, best_d2 = (cx, cy), d2
        return best

    def _process_chest_interactions(self, entity) -> None:
        if not self.chests or not self.tiled_map:
            return
        tw, th = self.tiled_map.tilewidth, self.tiled_map.tileheight
        ex, ey = entity.position
        etx, ety = int(ex // tw), int(ey // th)
        for chest in list(self.chests):
            if chest.get("opened"):
                continue
            if chest["tx"] == etx and chest["ty"] == ety:
                entity.health = min(entity.max_health, entity.health + 20)
                chest["opened"] = True

    def _center_initial_camera(self) -> None:
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            px, py = self.player.position
            map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
            map_px_h = self.tiled_map.height * self.tiled_map.tileheight
            self.map_view_x = max(0, min(px - self.width // 2, max(0, map_px_w - self.width)))
            self.map_view_y = max(0, min(py - self.height // 2, max(0, map_px_h - self.height)))
        else:
            self.map_view_x = max(0, self.player.position[0] - self.width // 2)
            self.map_view_y = max(0, self.player.position[1] - self.height // 2)

    def _center_camera_on_player(self) -> None:
        px, py = self.player.position
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
            map_px_h = self.tiled_map.height * self.tiled_map.tileheight
            self.map_view_x = max(0, min(px - self.width // 2, max(0, map_px_w - self.width)))
            self.map_view_y = max(0, min(py - self.height // 2, max(0, map_px_h - self.height)))
        else:
            self.map_view_x = max(0, px - self.width // 2)
            self.map_view_y = max(0, py - self.height // 2)

    def _respawn_player(self) -> None:
        self.reincarnation_count += 1
        self.player.alive = True
        self.player.health = self.player.max_health
        # Лёгкое усиление как результат обучения (опционально)
        self.player.learning_rate = min(2.0, self.player.learning_rate * 1.01)
        # Перемещение к центру
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
            map_px_h = self.tiled_map.height * self.tiled_map.tileheight
            self.player.position = [map_px_w // 2, map_px_h // 2]
        else:
            self.player.position = [self.width // 2, self.height // 2]

    @staticmethod
    def _respawn_entity(entity) -> None:
        entity.alive = True
        entity.health = entity.max_health

    @staticmethod
    def _dist2(a, b) -> float:
        ax, ay = a
        bx, by = b
        return (ax - bx) ** 2 + (ay - by) ** 2


def main():
    game = TkGame()
    game.root.mainloop()


if __name__ == "__main__":
    main()
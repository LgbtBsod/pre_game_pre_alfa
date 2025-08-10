#!/usr/bin/env python3
"""
Демонстрационная игра с Panda3D
Показывает основные возможности игрового движка
"""

import sys
import time
import random
from typing import List, Dict

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import (
    Vec3, Vec4, Point3, CardMaker, LineSegs,
    DirectionalLight, AmbientLight, OrthographicLens,
    NodePath
)
from direct.task import Task


class DemoGame(ShowBase):
    """Демонстрационная игра"""
    
    def __init__(self):
        super().__init__()
        
        # Настройка окна
        self.win.set_title("AI EVOLVE - Демо")
        self.win.set_size(1024, 768)
        
        # Настройка камеры для 2D игры
        lens = OrthographicLens()
        lens.set_film_size(20, 15)
        self.cam.node().set_lens(lens)
        self.cam.set_pos(0, -10, 0)
        
        # Настройка освещения
        self._setup_lighting()
        
        # Игровые объекты
        self.player = None
        self.enemies = []
        self.game_time = 0
        self.score = 0
        self.game_running = False
        
        # UI элементы
        self.ui_elements = {}
        
        # Создаем UI
        self._create_ui()
        
        # Привязываем события
        self._bind_events()
        
        # Запускаем игровой цикл
        self.task_mgr.add(self._game_loop, "game_loop")

    def _setup_lighting(self):
        """Настройка освещения"""
        # Основное освещение
        main_light = DirectionalLight("main_light")
        main_light.set_color(Vec4(0.8, 0.8, 0.8, 1.0))
        main_light_np = self.render.attach_new_node(main_light)
        main_light_np.set_hpr(45, -45, 0)
        self.render.set_light(main_light_np)
        
        # Фоновое освещение
        ambient_light = AmbientLight("ambient_light")
        ambient_light.set_color(Vec4(0.3, 0.3, 0.3, 1.0))
        ambient_light_np = self.render.attach_new_node(ambient_light)
        self.render.set_light(ambient_light_np)

    def _create_ui(self):
        """Создание пользовательского интерфейса"""
        # Заголовок
        title = OnscreenText(
            text="AI EVOLVE - Демо",
            pos=(0, 0.8),
            scale=0.08,
            fg=(0.3, 0.6, 1.0, 1.0),
            shadow=(0, 0, 0, 1)
        )
        self.ui_elements["title"] = title
        
        # Информация о счете
        self.score_text = OnscreenText(
            text="Счет: 0",
            pos=(-1.3, 0.6),
            scale=0.05,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        self.ui_elements["score"] = self.score_text
        
        # Информация о времени
        self.time_text = OnscreenText(
            text="Время: 0",
            pos=(-1.3, 0.5),
            scale=0.05,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1)
        )
        self.ui_elements["time"] = self.time_text
        
        # Кнопка старта
        start_btn = DirectButton(
            text="Начать игру",
            pos=(0, 0, 0.2),
            scale=0.06,
            command=self._start_game,
            relief="flat",
            frameColor=(0.2, 0.2, 0.2, 1.0),
            text_fg=(1, 1, 1, 1)
        )
        self.ui_elements["start_btn"] = start_btn
        
        # Инструкции
        instructions = OnscreenText(
            text="Управление:\nWASD - движение\nЛКМ - атака\nESC - выход",
            pos=(-1.3, -0.3),
            scale=0.04,
            fg=(0.8, 0.8, 0.8, 1.0),
            shadow=(0, 0, 0, 1),
            align=0  # Выравнивание по левому краю
        )
        self.ui_elements["instructions"] = instructions

    def _bind_events(self):
        """Привязка событий"""
        self.accept("escape", self.userExit)
        self.accept("w", self._move_up)
        self.accept("s", self._move_down)
        self.accept("a", self._move_left)
        self.accept("d", self._move_right)
        self.accept("mouse1", self._attack)

    def _start_game(self):
        """Начинает игру"""
        if not self.game_running:
            self.game_running = True
            self.score = 0
            self.game_time = 0
            
            # Скрываем кнопку старта
            self.ui_elements["start_btn"].hide()
            
            # Создаем игрока
            self._create_player()
            
            # Создаем врагов
            self._spawn_enemies(5)
            
            # Создаем фон
            self._create_background()

    def _create_player(self):
        """Создает игрока"""
        # Создаем синий круг для игрока
        cm = CardMaker("player")
        cm.set_frame(-0.5, 0.5, -0.5, 0.5)
        self.player = self.render.attach_new_node(cm.generate())
        self.player.set_color(Vec4(0.0, 0.8, 1.0, 1.0))  # Синий цвет
        self.player.set_pos(0, 0, 0)

    def _spawn_enemies(self, count: int):
        """Создает врагов"""
        for i in range(count):
            # Создаем красный круг для врага
            cm = CardMaker(f"enemy_{i}")
            cm.set_frame(-0.3, 0.3, -0.3, 0.3)
            enemy = self.render.attach_new_node(cm.generate())
            enemy.set_color(Vec4(1.0, 0.2, 0.2, 1.0))  # Красный цвет
            
            # Случайная позиция
            x = random.uniform(-8, 8)
            y = random.uniform(-6, 6)
            enemy.set_pos(x, 0, y)
            
            # Добавляем в список врагов
            self.enemies.append(enemy)

    def _create_background(self):
        """Создает фон"""
        # Создаем серую плоскость для фона
        cm = CardMaker("background")
        cm.set_frame(-10, 10, -7.5, 7.5)
        background = self.render.attach_new_node(cm.generate())
        background.set_color(Vec4(0.1, 0.1, 0.1, 1.0))
        background.set_depth_write(False)
        background.set_depth_test(False)
        
        # Создаем сетку
        self._create_grid()

    def _create_grid(self):
        """Создает сетку"""
        ls = LineSegs("grid")
        ls.set_color(Vec4(0.2, 0.2, 0.2, 1.0))
        ls.set_thickness(1.0)
        
        # Вертикальные линии
        for x in range(-10, 11, 2):
            ls.move_to(x, -7.5, 0)
            ls.draw_to(x, 7.5, 0)
        
        # Горизонтальные линии
        for y in range(-7, 8, 2):
            ls.move_to(-10, y, 0)
            ls.draw_to(10, y, 0)
        
        grid_node = ls.create()
        grid_np = self.render.attach_new_node(grid_node)
        grid_np.set_depth_write(False)

    def _move_up(self):
        """Движение вверх"""
        if self.player and self.game_running:
            pos = self.player.get_pos()
            self.player.set_pos(pos.x, pos.y, pos.z + 0.5)

    def _move_down(self):
        """Движение вниз"""
        if self.player and self.game_running:
            pos = self.player.get_pos()
            self.player.set_pos(pos.x, pos.y, pos.z - 0.5)

    def _move_left(self):
        """Движение влево"""
        if self.player and self.game_running:
            pos = self.player.get_pos()
            self.player.set_pos(pos.x - 0.5, pos.y, pos.z)

    def _move_right(self):
        """Движение вправо"""
        if self.player and self.game_running:
            pos = self.player.get_pos()
            self.player.set_pos(pos.x + 0.5, pos.y, pos.z)

    def _attack(self):
        """Атака"""
        if self.player and self.game_running:
            # Проверяем коллизии с врагами
            player_pos = self.player.get_pos()
            
            for enemy in self.enemies[:]:  # Копируем список для безопасного удаления
                enemy_pos = enemy.get_pos()
                distance = (player_pos - enemy_pos).length()
                
                if distance < 1.0:  # Радиус атаки
                    # Удаляем врага
                    enemy.remove_node()
                    self.enemies.remove(enemy)
                    
                    # Увеличиваем счет
                    self.score += 10
                    
                    # Создаем нового врага
                    self._spawn_enemies(1)
                    
                    # Показываем эффект атаки
                    self._show_attack_effect(player_pos)

    def _show_attack_effect(self, pos: Point3):
        """Показывает эффект атаки"""
        # Создаем временный эффект
        cm = CardMaker("attack_effect")
        cm.set_frame(-0.2, 0.2, -0.2, 0.2)
        effect = self.render.attach_new_node(cm.generate())
        effect.set_color(Vec4(1.0, 1.0, 0.0, 1.0))  # Желтый цвет
        effect.set_pos(pos.x, pos.y, pos.z)
        
        # Удаляем эффект через 0.2 секунды
        def remove_effect(task):
            effect.remove_node()
            return Task.done
        
        self.task_mgr.do_method_later(0.2, remove_effect, "remove_attack_effect")

    def _game_loop(self, task):
        """Игровой цикл"""
        if self.game_running:
            # Обновляем время
            self.game_time += 1
            
            # Обновляем UI
            self.score_text.set_text(f"Счет: {self.score}")
            self.time_text.set_text(f"Время: {self.game_time // 60}")
            
            # Движение врагов (простое преследование)
            if self.player:
                player_pos = self.player.get_pos()
                
                for enemy in self.enemies:
                    enemy_pos = enemy.get_pos()
                    direction = player_pos - enemy_pos
                    direction.normalize()
                    
                    # Простое движение к игроку
                    new_pos = enemy_pos + direction * 0.02
                    enemy.set_pos(new_pos)
            
            # Проверяем победу
            if len(self.enemies) == 0:
                self._show_victory()
        
        return Task.cont

    def _show_victory(self):
        """Показывает сообщение о победе"""
        victory_text = OnscreenText(
            text="ПОБЕДА!\nНажмите ESC для выхода",
            pos=(0, 0),
            scale=0.1,
            fg=(0.0, 1.0, 0.0, 1.0),
            shadow=(0, 0, 0, 1)
        )
        self.ui_elements["victory"] = victory_text
        
        self.game_running = False


def main():
    """Главная функция"""
    try:
        # Создаем и запускаем демо игру
        game = DemoGame()
        game.run()
    except Exception as e:
        print(f"Ошибка запуска демо: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

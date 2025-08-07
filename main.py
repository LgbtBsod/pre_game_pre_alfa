import random
import time
import tkinter as tk
from entities.player import Player
from entities.enemy import Enemy
from entities.boss import Boss
from items.weapon import WeaponGenerator
from ai.cooperation import AICoordinator
from map.tiled_map import TiledMap


def rgb_to_hex(color_tuple):
    r, g, b = color_tuple
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


class TkGame:
    def __init__(self, width=1200, height=800):
        self.root = tk.Tk()
        self.root.title("Автономный ИИ-выживач (Tkinter)")
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg=rgb_to_hex((20, 30, 40)))
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Состояние
        self.running = True
        self.last_time = time.time()
        self.ui_items = []

        # Карта Tiled
        self.map_view_x = 0
        self.map_view_y = 0
        self.tiled_map = None
        try:
            self.tiled_map = TiledMap("map/map.json")
        except Exception as e:
            self.tiled_map = None

        # Игровые сущности
        # Позицию игрока задаём по центру карты, если карта загружена
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
            map_px_h = self.tiled_map.height * self.tiled_map.tileheight
            start_x = map_px_w // 2
            start_y = map_px_h // 2
            self.map_view_x = max(0, start_x - self.width // 2)
            self.map_view_y = max(0, start_y - self.height // 2)
            self.player = Player("player_ai", (start_x, start_y))
        else:
            self.player = Player("player_ai", (self.width // 2, self.height // 2))
        self.player.learning_rate = 1.0

        self.enemies = []
        enemy_types = ["warrior", "archer", "mage"]
        for _ in range(10):
            enemy = Enemy(random.choice(enemy_types), level=random.randint(1, 5))
            enemy.position = [random.randint(100, self.width - 100), random.randint(100, self.height - 100)]
            enemy.player_ref = self.player
            self.enemies.append(enemy)

        self.boss = Boss(boss_type="dragon", level=15, position=(self.width - 300, 300))
        self.boss.learning_rate = 0.005
        self.boss.player_ref = self.player

        # Оружие игроку
        starter_weapon = WeaponGenerator.generate_weapon(1)
        self.player.equip_item(starter_weapon)

        # Координатор ИИ
        self.coordinator = AICoordinator()
        for enemy in self.enemies:
            self.coordinator.register_entity(enemy, "enemy_group")
        self.coordinator.register_entity(self.boss, "boss_group")

        # Управление
        self.root.bind("<Escape>", lambda e: self.stop())
        self.root.bind("<space>", lambda e: self.restart())
        # Движение игрока (WASD)
        self._keys = set()
        self.root.bind("<KeyPress>", self._on_key_down)
        self.root.bind("<KeyRelease>", self._on_key_up)

        # Старт цикла
        self.root.after(16, self.game_loop)

    def restart(self):
        if not self.running:
            self.running = True
            self.__init__(self.width, self.height)

    def stop(self):
        self.running = False
        try:
            self.root.destroy()
        except Exception:
            pass

    def game_loop(self):
        if not self.running:
            return
        now = time.time()
        delta_time = now - self.last_time
        self.last_time = now

        # Обновление логики
        self._update_player_movement(delta_time)
        self.player.update(delta_time)
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(delta_time)
                # Простое поведение: двигаться к игроку
                enemy.move_towards(self.player.position, enemy.combat_stats.get("movement_speed", 100.0), delta_time)
        if self.boss.alive:
            self.boss.update(delta_time)
            # Босс тоже понемногу движется к игроку
            self.boss.move_towards(self.player.position, self.boss.combat_stats.get("movement_speed", 80.0), delta_time)

        # Групповая логика
        self.coordinator.update_group_behavior("enemy_group")
        self.coordinator.update_group_behavior("boss_group")

        # Столкновения
        self.check_collisions()
        self.enemies = [e for e in self.enemies if e.alive]

        # Автокамера — центрируем вьюпорт на игроке (если карта есть)
        if self.tiled_map:
            self._center_camera_on_player()

        # Рендер
        self.draw()

        # Проверка конца игры
        if not self.player.alive:
            self.draw_game_over("Поражение! Игрок погиб.")
            self.running = False
            return
        elif not self.boss.alive:
            self.draw_game_over("Победа! Босс повержен!")
            self.running = False
            return

        self.root.after(16, self.game_loop)

    def check_collisions(self):
        px, py = self.player.position

        # Столкновения с врагами (радиусы 20 и 15)
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

        # Столкновение с боссом (радиус 30)
        if self.boss.alive:
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

    def draw(self):
        self.canvas.delete("all")

        # Карта (если загружена)
        if self.tiled_map:
            self.tiled_map.draw_to_canvas(
                self.canvas,
                self.map_view_x,
                self.map_view_y,
                self.width,
                self.height,
                tag="map",
            )

        # Игрок (с учётом камеры)
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
        if self.boss.alive:
            bx, by = self.boss.position
            sbx, sby = bx - self.map_view_x, by - self.map_view_y
            self._draw_circle(sbx, sby, 30, fill=rgb_to_hex((255, 165, 0)))
            self.canvas.create_text(sbx, sby - 40, text=f"Фаза: {self.boss.phase}", fill=rgb_to_hex((255, 255, 0)))

        # UI
        self.canvas.create_text(10, 10, text=f"Уровень: {self.player.level}", fill=rgb_to_hex((255, 255, 255)), anchor="nw")
        self.canvas.create_text(10, 40, text=f"Здоровье: {int(self.player.health)}/{int(self.player.max_health)}", fill=rgb_to_hex((255, 255, 255)), anchor="nw")
        self.canvas.create_text(10, 70, text=f"Известных слабостей: {len(self.player.known_weaknesses)}", fill=rgb_to_hex((255, 255, 255)), anchor="nw")
        self.canvas.create_text(10, 100, text=f"Скорость обучения: {self.player.learning_rate:.2f}", fill=rgb_to_hex((255, 255, 255)), anchor="nw")
        if self.tiled_map:
            self.canvas.create_text(10, 130, text=f"Карта: {self.tiled_map.width}x{self.tiled_map.height} (tile {self.tiled_map.tilewidth}x{self.tiled_map.tileheight})", fill=rgb_to_hex((180, 200, 255)), anchor="nw")
        if self.boss.alive:
            self.canvas.create_text(self.width - 200, 10, text=f"Босс: {int(self.boss.health)}/{int(self.boss.max_health)}", fill=rgb_to_hex((255, 100, 100)), anchor="nw")

    def draw_game_over(self, message):
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#000000", stipple="gray25")
        self.canvas.create_text(self.width // 2, self.height // 2, text=message, fill=rgb_to_hex((255, 50, 50)), font=("Arial", 24, "bold"))
        self.canvas.create_text(self.width // 2, self.height // 2 + 40, text="Нажмите Space для перезапуска или Esc для выхода", fill=rgb_to_hex((255, 255, 255)))

    def _draw_circle(self, x, y, radius, fill="#ffffff"):
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill, width=0)

    def _on_key_down(self, event):
        self._keys.add(event.keysym.lower())

    def _on_key_up(self, event):
        self._keys.discard(event.keysym.lower())

    def _update_player_movement(self, dt: float):
        dx = 0.0
        dy = 0.0
        if "w" in self._keys:
            dy -= 1.0
        if "s" in self._keys:
            dy += 1.0
        if "a" in self._keys:
            dx -= 1.0
        if "d" in self._keys:
            dx += 1.0
        if dx == 0.0 and dy == 0.0:
            return
        length = max(1e-6, (dx * dx + dy * dy) ** 0.5)
        dx /= length
        dy /= length
        speed = float(self.player.combat_stats.get("movement_speed", 120.0))
        self.player.position[0] += dx * speed * dt
        self.player.position[1] += dy * speed * dt

    def _center_camera_on_player(self):
        px, py = self.player.position
        # Размер карты (в пикселях), если известен
        if self.tiled_map.width and self.tiled_map.height:
            map_px_w = self.tiled_map.width * self.tiled_map.tilewidth
            map_px_h = self.tiled_map.height * self.tiled_map.tileheight
            self.map_view_x = max(0, min(px - self.width // 2, max(0, map_px_w - self.width)))
            self.map_view_y = max(0, min(py - self.height // 2, max(0, map_px_h - self.height)))
        else:
            # Неизвестная граница — просто центрируем
            self.map_view_x = max(0, px - self.width // 2)
            self.map_view_y = max(0, py - self.height // 2)


def main():
    game = TkGame()
    game.root.mainloop()


if __name__ == "__main__":
    main()
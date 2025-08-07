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
    def __init__(self, width: int = 1200, height: int = 800):
        self.root = tk.Tk()
        self.root.title("Автономный ИИ-выживач (Tkinter)")
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg=rgb_to_hex((20, 30, 40)))
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.running = True
        self.last_time = time.time()
        self.victory_shown = False
        self.reincarnation_count = 0

        # Карта
        self.map_view_x = 0
        self.map_view_y = 0
        self.tiled_map = None
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
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)

        # Камера к центру карты
        self._center_initial_camera()

        # Старт цикла
        self.root.after(16, self.game_loop)

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
        player.learning_rate = 1.0
        return player

    def _create_enemies(self) -> list:
        enemy_list = []
        enemy_types = ["warrior", "archer", "mage"]
        for _ in range(10):
            e = Enemy(random.choice(enemy_types), level=random.randint(1, 5))
            e.position = [random.randint(200, 1000), random.randint(200, 700)]
            e.player_ref = self.player
            enemy_list.append(e)
        return enemy_list

    def _create_boss(self) -> Boss:
        if self.tiled_map and self.tiled_map.width and self.tiled_map.height:
            bx = self.tiled_map.width * self.tiled_map.tilewidth - 300
            by = 300
        else:
            bx, by = self.width - 300, 300
        boss = Boss(boss_type="dragon", level=15, position=(bx, by))
        boss.learning_rate = 0.005
        boss.player_ref = self.player
        return boss

    # --- Жизненный цикл ---
    def soft_restart(self) -> None:
        """Перезапуск мира без закрытия окна и без потери знаний."""
        self.victory_shown = False
        # Возрождаем игрока
        self._respawn_player()
        # Возрождаем врагов и босса
        for e in self.enemies:
            self._respawn_entity(e)
            e.position = [random.randint(200, 1000), random.randint(200, 700)]
        if self.boss:
            self._respawn_entity(self.boss)
            self.boss.position = [self.width - 300, 300]
        # Сохраняем добавленные человеком препятствия/сундуки
        # Камера назад на игрока
        self._center_initial_camera()
        # Продолжаем цикл (если был остановлен)
        if not self.running:
            self.running = True
            self.root.after(16, self.game_loop)

    def stop(self) -> None:
        self.running = False
        try:
            self.root.destroy()
        except Exception:
            pass

    def game_loop(self) -> None:
        if not self.running:
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
        if self.tiled_map:
            self.canvas.create_text(10, 100, text=f"Карта: {self.tiled_map.width}x{self.tiled_map.height} (tile {self.tiled_map.tilewidth}x{self.tiled_map.tileheight})", fill=rgb_to_hex((180, 200, 255)), anchor="nw")
        if self.boss and self.boss.alive:
            self.canvas.create_text(self.width - 220, 10, text=f"Босс: {int(self.boss.health)}/{int(self.boss.max_health)}", fill=rgb_to_hex((255, 100, 100)), anchor="nw")

        # Подсказки и пользовательские объекты
        self.canvas.create_text(10, self.height - 24, text="Space: перезапуск (знания сохраняются) | ЛКМ: препятствие | ПКМ: сундук", fill=rgb_to_hex((200, 220, 240)), anchor="sw")
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
        world_x = event.x + self.map_view_x
        world_y = event.y + self.map_view_y
        tw, th = self.tiled_map.tilewidth, self.tiled_map.tileheight
        tx, ty = int(world_x // tw), int(world_y // th)
        self.user_obstacles.add((tx, ty))

    def _on_right_click(self, event) -> None:
        if not self.tiled_map:
            return
        world_x = event.x + self.map_view_x
        world_y = event.y + self.map_view_y
        tw, th = self.tiled_map.tilewidth, self.tiled_map.tileheight
        tx, ty = int(world_x // tw), int(world_y // th)
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
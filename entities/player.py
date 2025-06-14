from .entity import Entity
import math
import random
import numpy as np

class Player(Entity):
    def __init__(self, x, y, knowledge=None, inventory=None, level=1, xp=0):
        super().__init__(x, y, learning_rate=1.0)

        # Характеристики игрока
        self.z = 1.0  # высота над землёй (для изометрии)
        self.speed = 0.05
        self.max_health = 90 + level * 10
        self.health = self.max_health
        self.attack_power = 8 + level
        self.level = level
        self.xp = xp
        self.xp_to_level = 100 * level
        self.inventory = inventory if inventory else []

        # Экипировка
        self.equipped_weapon = None
        self.equipped_accessory = None

        # Состояние
        self.state = "exploring"  # exploring, fighting, collecting, resting, avoiding
        self.path = []
        self.target = None
        self.cooldown = 0
        self.poisoned = 0
        self.buffed = 0
        self.vision_range = 6

        # Анимации
        self.attack_anim = 0
        self.damage_anim = 0
        self.level_up_anim = 0

        # Знания
        if knowledge:
            for k in knowledge:
                for entity, value in knowledge[k].items():
                    self.knowledge[k][entity] = value

        # Автоматическая экипировка
        self.equip_best()

    def equip_best(self):
        weapon_types = ["sword", "bow", "axe", "staff"]
        accessory_types = ["shield", "amulet", "ring"]

        for item in self.inventory:
            if item.item_type in weapon_types and (
                not self.equipped_weapon or item.power > self.equipped_weapon.power
            ):
                self.equipped_weapon = item
            elif item.item_type in accessory_types and (
                not self.equipped_accessory or item.defense > self.equipped_accessory.defense
            ):
                self.equipped_accessory = item

    def gain_xp(self, amount):
        """Получение опыта и повышение уровня"""
        self.xp += amount
        while self.xp >= self.xp_to_level:
            self.level_up()

    def level_up(self):
        """Повышение уровня"""
        self.level += 1
        self.xp -= self.xp_to_level
        self.xp_to_level = int(self.xp_to_level * 1.5)
        self.max_health += 20
        self.health = min(self.health + 30, self.max_health)
        self.attack_power += 5
        self.level_up_anim = 60

    def reset(self, x, y):
        """Сброс позиции и здоровья, сохраняя инвентарь и уровень"""
        self.x, self.y = x, y
        self.z = 1
        self.health = self.max_health
        self.path = []
        self.target = None
        self.state = "exploring"
        self.cooldown = 0
        self.attack_anim = 0
        self.damage_anim = 0
        self.level_up_anim = 0
        self.poisoned = 0
        self.buffed = 0

    def update(self, game_map, enemies, items, chests, traps, goal):
        # Ограничение координат персонажа
        self.x = max(0.5, min(self.x, game_map.width - 0.5))
        self.y = max(0.5, min(self.y, game_map.height - 0.5))

        # Таймеры
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.attack_anim > 0:
            self.attack_anim -= 1
        if self.damage_anim > 0:
            self.damage_anim -= 1
        if self.level_up_anim > 0:
            self.level_up_anim -= 1

        # Статусные эффекты
        if self.poisoned > 0:
            self.poisoned -= 1
            if self.poisoned % 20 == 0:
                self.take_damage(3, "poison")
        if self.buffed > 0:
            self.buffed -= 1

        # Проверка победы
        if abs(self.x - goal.x) < 0.5 and abs(self.y - goal.y) < 0.5:
            return True

        # Обновление AI
        state = self._get_state(enemies, items, traps, goal, game_map)
        action = self._apply_ai(state, enemies, items, chests, traps, game_map)
        self._execute_action(action, enemies, game_map)

        # Перемещение по пути
        self._move_along_path(game_map)

        # Проверка ловушек
        self._check_traps(traps)

        return False

    def _get_state(self, enemies, items, traps, goal, game_map):
        enemy_distances = [self.distance_to(e) for e in enemies]
        nearest_enemy_dist = min(enemy_distances) if enemy_distances else 10

        item_distances = [self.distance_to(i) for i in items]
        nearest_item_dist = min(item_distances) if item_distances else 10

        trap_distances = [self.distance_to(t) for t in traps]
        nearest_trap_dist = min(trap_distances) if trap_distances else 10

        return [
            self.health / self.max_health,
            min(1.0, len(enemies) / 10),
            min(1.0, len(items) / 5),
            min(1.0, self.distance_to(goal) / game_map.width),
            nearest_enemy_dist / 10,
            nearest_item_dist / 10,
            nearest_trap_dist / 10,
            self.cooldown / 30,
            int(self.poisoned > 0),
            int(self.buffed > 0),
            self.level / 10,
            self.xp / self.xp_to_level,
            len(self.inventory) / 20,
            (self.equipped_weapon.power if self.equipped_weapon else 0) / 15,
            (self.equipped_accessory.defense if self.equipped_accessory else 0) / 0.5,
            self.knowledge["enemies"]["warrior"],
            self.knowledge["traps"]["spike"],
            self.knowledge["weapon_effect"].get("sword_warrior", 0.5),
            self.knowledge["damage_resist"].get("physical", 0.0),
            self.knowledge["damage_resist"].get("magic", 0.0)
        ]

    def _apply_ai(self, state, enemies, items, chests, traps, game_map):
        # Пример простого AI — заменить на обучение
        if state[0] < 0.3:
            self.state = "resting"
        elif any(item for item in items if self.distance_to(item) < 3):
            self.state = "collecting"
        elif any(enemy for enemy in enemies if self.distance_to(enemy) < self.vision_range):
            self.state = "fighting"
        else:
            self.state = "exploring"

    def _execute_action(self, action, enemies, game_map):
        if self.state == "exploring":
            self.explore(game_map, enemies)
        elif self.state == "collecting":
            self.collect_items(enemies, items, game_map)
        elif self.state == "fighting":
            self.fight_enemies(enemies, game_map)
        elif self.state == "resting":
            self.rest()
        elif self.state == "avoiding":
            self.avoid_danger(game_map, enemies, traps)

    def _move_along_path(self, game_map):
        if self.path:
            next_x, next_y = self.path[0]
            dx, dy = next_x - self.x, next_y - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed:
                self.x, self.y = next_x, next_y
                self.path.pop(0)
            else:
                self.x += dx / dist * self.speed
                self.y += dy / dist * self.speed
            self.x = max(0.5, min(self.x, game_map.width - 0.5))
            self.y = max(0.5, min(self.y, game_map.height - 0.5))

    def _check_traps(self, traps):
        for trap in traps:
            dist = self.distance_to(trap)
            if dist < 3 and random.random() < self.knowledge["traps"][trap.trap_type]:
                trap.visible = True
            if dist < 1 and self.cooldown == 0:
                self.take_damage(trap.damage, trap.trap_type)
                self.learn("traps", trap.trap_type, -1)
                self.cooldown = 20

    def explore(self, game_map, goal):
        if not self.path or random.random() < 0.02:
            if not self.find_path(goal.x, goal.y, game_map):
                self.find_alternative_target(goal.x, goal.y, game_map)

    def collect_items(self, items, game_map):
        nearest_item = None
        min_dist = float('inf')
        for item in items:
            dist = self.distance_to(item)
            if dist < min_dist:
                min_dist = dist
                nearest_item = item
        if nearest_item:
            if min_dist < 0.5:
                self.pick_up_item(nearest_item)
                items.remove(nearest_item)
                game_map.remove_entity(nearest_item)
                self.learn("items", nearest_item.item_type, 1)
            else:
                if not self.find_path(nearest_item.x, nearest_item.y, game_map):
                    items.remove(nearest_item)
                    game_map.remove_entity(nearest_item)

    def fight_enemies(self, enemies, game_map):
        nearest_enemy = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = self.distance_to(enemy)
            if dist < min_dist:
                min_dist = dist
                nearest_enemy = enemy
        if nearest_enemy:
            if min_dist < 1.5 and self.cooldown == 0:
                self.attack(nearest_enemy)
                self.learn("enemies", nearest_enemy.enemy_type, -0.1)
            else:
                if not self.find_path(nearest_enemy.x, nearest_enemy.y, game_map):
                    retreat_x = self.x + (self.x - nearest_enemy.x) * 2
                    retreat_y = self.y + (self.y - nearest_enemy.y) * 2
                    self.find_path(retreat_x, retreat_y, game_map)

    def rest(self):
        self.health = min(self.max_health, self.health + 0.2)
        if self.health > 70:
            self.state = "exploring"

    def attack(self, enemy):
        damage = self.attack_power
        if self.equipped_weapon:
            damage += self.equipped_weapon.power
            weapon_type = self.equipped_weapon.damage_type
        else:
            weapon_type = "physical"

        if enemy.take_damage(damage, weapon_type):
            self.gain_xp(enemy.xp_reward)

        self.cooldown = 20
        self.attack_anim = 8

    def take_damage(self, amount, damage_type="physical"):
        # Защита от урона
        defense = 0
        if self.equipped_accessory:
            defense = self.equipped_accessory.defense
        resistance = self.knowledge["damage_resist"].get(damage_type, 0)
        amount *= (1 - defense) * (1 - resistance)
        self.health -= amount
        self.damage_anim = 10
        return self.health <= 0

    def pick_up_item(self, item):
        self.inventory.append(item)
        if item.effects:
            for effect, value in item.effects.items():
                if effect == "health":
                    self.health = min(self.max_health, self.health + value)
                elif effect == "max_health":
                    self.max_health += value
                    self.health += value
                elif effect == "damage":
                    self.attack_power += value
                elif effect == "speed":
                    self.speed += value
                elif effect == "poison":
                    self.poisoned = 300
                elif effect == "buff":
                    self.buffed = 300
                elif effect == "resistance":
                    for dmg_type, res_value in value.items():
                        current = self.knowledge["damage_resist"].get(dmg_type, 0)
                        self.knowledge["damage_resist"][dmg_type] = min(0.8, current + res_value)

        # Экипировка
        if item.item_type in ["sword", "bow", "axe", "staff"]:
            if not self.equipped_weapon or item.power > self.equipped_weapon.power:
                self.equipped_weapon = item
        elif item.item_type in ["shield", "amulet", "ring"]:
            if not self.equipped_accessory or item.defense > self.equipped_accessory.defense:
                self.equipped_accessory = item

    def find_path(self, target_x, target_y, game_map):
        start = (round(self.x), round(self.y))
        goal = (round(target_x), round(target_y))
        if not self.is_reachable(start, goal, game_map.tiles):
            return False
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}
        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                self.path = self.reconstruct_path(came_from, current)
                return True
            for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if not self.in_bounds(*neighbor, game_map.width, game_map.height):
                    continue
                if game_map.tiles[neighbor[1]][neighbor[0]] == 1:
                    continue
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return False

    def is_reachable(self, start, goal, tiles):
        visited = set([start])
        queue = [start]
        while queue:
            current = queue.pop(0)
            for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if self.in_bounds(*neighbor, len(tiles[0]), len(tiles)) and neighbor not in visited:
                    if tiles[neighbor[1]][neighbor[0]] == 0:
                        if neighbor == goal:
                            return True
                        visited.add(neighbor)
                        queue.append(neighbor)
        return False

    def avoid_danger(self, game_map, enemies, traps):
        nearest_danger = None
        min_dist = float('inf')
        for enemy in enemies:
            dist = self.distance_to(enemy)
            if dist < min_dist:
                min_dist = dist
                nearest_danger = enemy
        for trap in traps:
            dist = self.distance_to(trap)
            if dist < min_dist:
                min_dist = dist
                nearest_danger = trap
        if nearest_danger and min_dist < 5:
            retreat_x = self.x + (self.x - nearest_danger.x) * 3
            retreat_y = self.y + (self.y - nearest_danger.y) * 3
            self.find_path(
                max(0.5, min(game_map.width - 0.5, retreat_x)),
                max(0.5, min(game_map.height - 0.5, retreat_y)),
                game_map
            )

    def distance_to(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return [(x + 0.5, y + 0.5) for x, y in path]

    def in_bounds(self, x, y, width, height):
        return 0 <= x < width and 0 <= y < height

    def draw(self, screen, camera):
        cart_x, cart_y = iso_to_cart(self.x, self.y, self.z)
        screen_x, screen_y = camera.apply(cart_x, cart_y)
        if self.damage_anim > 0:
            pygame.draw.circle(screen, DAMAGE_COLOR, (screen_x, screen_y), 20, 3)
        pygame.draw.circle(screen, PLAYER_COLOR, (screen_x, screen_y), 15)
        if self.equipped_weapon:
            offset_x = 15 if self.equipped_weapon.weapon_type == "melee" else 25
            pygame.draw.line(screen, (150, 150, 150), 
                           (screen_x, screen_y - 5), 
                           (screen_x + offset_x, screen_y - 15), 3)
        if self.attack_anim > 0:
            pygame.draw.circle(screen, ATTACK_COLOR, (screen_x, screen_y), 20 + self.attack_anim, 3)
        # UI
        bar_width = 40
        pygame.draw.rect(screen, (100, 100, 100), (screen_x - bar_width//2, screen_y - 40, bar_width, 5))
        pygame.draw.rect(screen, (50, 200, 50), 
                       (screen_x - bar_width//2, screen_y - 40, 
                        bar_width * (self.health / self.max_health), 5))
        # XP bar
        pygame.draw.rect(screen, (60, 60, 80), (screen_x - bar_width//2, screen_y - 48, bar_width, 4))
        if self.xp_to_level > 0:
            pygame.draw.rect(screen, XP_COLOR, 
                          (screen_x - bar_width//2, screen_y - 48, 
                           bar_width * (self.xp / self.xp_to_level), 4))
        # Level up animation
        if self.level_up_anim > 0:
            size = 30 + self.level_up_anim
            pygame.draw.circle(screen, LEVEL_UP_COLOR, (screen_x, screen_y), size, 3)
        # Poison effect
        if self.poisoned > 0:
            pygame.draw.circle(screen, POISON_COLOR, (screen_x, screen_y), 18, 2)
        # Buff effect
        if self.buffed > 0:
            pygame.draw.circle(screen, (255, 215, 0, 180), (screen_x, screen_y), 18, 2)
        # Path drawing
        for i, (x, y) in enumerate(self.path):
            path_x, path_y = iso_to_cart(x, y)
            px, py = camera.apply(path_x, path_y)
            pygame.draw.circle(screen, PATH_COLOR, (px, py), 3)
            if i > 0:
                prev_x, prev_y = iso_to_cart(self.path[i-1][0], self.path[i-1][1])
                prev_px, prev_py = camera.apply(prev_x, prev_y)
                pygame.draw.line(screen, PATH_COLOR, (prev_px, prev_py), (px, py), 2)

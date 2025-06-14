from .entity import Entity
import math
import random


class Enemy(Entity):
    def __init__(self, x, y, enemy_type="warrior"):
        super().__init__(x, y, z=z, learning_rate=0.01)

        # Базовые параметры
        self.enemy_type = enemy_type
        self.z = 0.5
        self.health = 50
        self.damage = 5
        self.speed = 0.03
        self.attack_cooldown = 0
        self.hit_anim = 0
        self.xp_reward = 25
        self.resistances = {}
        self.weaknesses = {}
        self.phase = 1
        self.learned = False

        # Инициализация характеристик по типу
        if enemy_type == "warrior":
            self.health = 70
            self.damage = 8
            self.resistances["physical"] = 0.3
            self.weaknesses["magic"] = 0.5
            self.xp_reward = 40
        elif enemy_type == "archer":
            self.health = 40
            self.damage = 6
            self.resistances["piercing"] = 0.4
            self.weaknesses["physical"] = 0.3
            self.xp_reward = 30
        elif enemy_type == "mage":
            self.health = 30
            self.damage = 10
            self.resistances["magic"] = 0.6
            self.weaknesses["physical"] = 0.4
            self.xp_reward = 50
        elif enemy_type == "boss":
            self.z = 1.0
            self.health = 200
            self.damage = 15
            self.speed *= 1.5
            self.resistances = {"physical": 0.4, "magic": 0.3}
            self.weaknesses = {"fire": 0.5}
            self.xp_reward = 200
            self.phase = 1
            self.learning_rate = 0.001  # Меньше учимся, чем игрок

    def update(self, player, enemies):
        # Ограничение координат врага
        self.x = max(0.5, min(self.x, 49.5))
        self.y = max(0.5, min(self.y, 49.5))

        # Таймеры
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_anim > 0:
            self.hit_anim -= 1

        # Обучение на основе смерти союзников
        if not self.learned:
            for enemy in enemies:
                if enemy != self and enemy.health <= 0:
                    dist = self.distance_to(enemy)
                    if dist < 10:
                        self.learn_from_death()
                        self.learned = True
                        break

        # Движение к игроку
        dx, dy = player.x - self.x, player.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 8:  # Видимость игрока
            if dist > 1.5:  # Двигаемся, если не рядом
                self.x += dx / dist * self.speed
                self.y += dy / dist * self.speed
            elif self.attack_cooldown == 0:  # Атака
                player.take_damage(self.damage, "physical")
                self.attack_cooldown = 30

    def learn_from_death(self):
        """Обучение при смерти других врагов"""
        self.speed *= 1.1
        self.damage *= 1.1
        # Учимся избегать определённых типов атак
        if "sword" in [item.item_type for item in self.knowledge.get("items", [])]:
            self.learn("damage_resist", "physical", 0.05)
        if "staff" in [item.item_type for item in self.knowledge.get("items", [])]:
            self.learn("damage_resist", "magic", 0.05)

    def take_damage(self, amount, damage_type="physical"):
        resistance = self.resistances.get(damage_type, 0)
        weakness = self.weaknesses.get(damage_type, 0)
        actual_damage = amount * (1 - resistance) * (1 + weakness)
        self.health -= actual_damage
        self.hit_anim = 8
        return self.health <= 0

    def draw(self, screen, camera):
        cart_x, cart_y = iso_to_cart(self.x, self.y, self.z)
        screen_x, screen_y = camera.apply(cart_x, cart_y)

        if self.hit_anim > 0:
            pygame.draw.circle(screen, DAMAGE_COLOR, (screen_x, screen_y), 20, 3)

        if self.enemy_type == "warrior":
            pygame.draw.rect(screen, ENEMY_COLOR, (screen_x - 15, screen_y - 10, 30, 20))
        elif self.enemy_type == "archer":
            pygame.draw.circle(screen, ENEMY_COLOR, (screen_x, screen_y), 12)
        elif self.enemy_type == "mage":
            points = [(screen_x, screen_y - 15), (screen_x - 12, screen_y + 10), (screen_x + 12, screen_y + 10)]
            pygame.draw.polygon(screen, ENEMY_COLOR, points)
        elif self.enemy_type == "boss":
            color = (180, 50, 50) if self.phase == 1 else (200, 50, 50) if self.phase == 2 else (220, 30, 30)
            pygame.draw.rect(screen, color, (screen_x - 20, screen_y - 15, 40, 30))
            pygame.draw.circle(screen, color, (screen_x, screen_y - 20), 10)

        # Health bar
        bar_width = 30
        pygame.draw.rect(screen, (100, 100, 100), (screen_x - bar_width//2, screen_y - 25, bar_width, 4))
        max_health = 70 if self.enemy_type == "warrior" else \
                     200 if self.enemy_type == "boss" else \
                     40 if self.enemy_type == "archer" else 30
        health_ratio = max(0.0, self.health / max_health)
        pygame.draw.rect(screen, (200, 50, 50),
                       (screen_x - bar_width//2, screen_y - 25,
                        bar_width * health_ratio, 4))
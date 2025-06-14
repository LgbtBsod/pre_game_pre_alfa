from .enemy import Enemy
import math
import numpy as np

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, enemy_type="boss")
        self.learning_rate = 0.001  # Очень медленное обучение
        self.phase = 1
        self.attack_pattern = "default"
        self.special_cooldown = 0
        self.boss_music_played = False

        # Уникальные характеристики босса
        self.health = 200
        self.max_health = 200
        self.damage = 15
        self.speed = 0.02
        self.resistances = {"physical": 0.4, "magic": 0.3}
        self.weaknesses = {"fire": 0.5}

    def update(self, player, enemies):
        """Обновление состояния босса"""
        # Ограничение координат
        self.x = max(0.5, min(self.x, 49.5))
        self.y = max(0.5, min(self.y, 49.5))

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_anim > 0:
            self.hit_anim -= 1
        if self.special_cooldown > 0:
            self.special_cooldown -= 1

        # Обучение при смерти других врагов
        if not self.learned:
            for enemy in enemies:
                if enemy != self and enemy.health <= 0:
                    dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
                    if dist < 10:
                        self.learn_from_death(enemy.enemy_type)
                        self.learned = True
                        break

        # Обновление фаз
        self.update_boss_phase(player)

        # Проверка расстояния до игрока
        dx, dy = player.x - self.x, player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 8:
            if dist > 1.5:
                # Движение к игроку
                self.x += dx / dist * self.speed
                self.y += dy / dist * self.speed
            elif self.attack_cooldown == 0:
                # Атака
                player.take_damage(self.damage, "physical")
                self.attack_cooldown = 30
                self.hit_anim = 8

    def update_boss_phase(self, player):
        """Обновляет фазы босса на основе здоровья"""
        if self.health <= 150 and self.phase == 1:
            self.phase = 2
            self.speed *= 1.5
            self.attack_cooldown = 15
            self.resistances["physical"] = min(0.7, self.resistances.get("physical", 0) + 0.3)
        elif self.health <= 75 and self.phase == 2:
            self.phase = 3
            self.damage *= 1.5
            self.speed *= 1.3
            self.resistances = {
                "physical": 0.6,
                "magic": 0.5,
                "fire": 0.3
            }

        # Применение ИИ для выбора действия
        health_ratio = self.health / self.max_health
        player_distance = math.hypot(self.x - player.x, self.y - player.y)
        action = self.ai.decide_action(health_ratio, player_distance, self.phase)

        if action == 0:  # Атака
            pass  # Стандартная атака уже обработана
        elif action == 1:  # Защита
            if self.attack_cooldown == 0:
                # Увеличиваем сопротивления на короткое время
                self.resistances = {k: min(0.8, v + 0.2) for k, v in self.resistances.items()}
                self.attack_cooldown = 45
        elif action == 2:  # Спецспособность
            if self.special_cooldown == 0:
                # Мощная атака или вызов миньонов
                player.take_damage(self.damage * 1.8, "fire")
                self.special_cooldown = 60
                self.hit_anim = 10

    def learn_from_death(self, enemy_type):
        """Обучение на основе смерти других врагов"""
        key = f"enemy_{enemy_type}"
        self.knowledge[key] = min(1.0, self.knowledge[key] + 0.05)
        self.resistances["physical"] = min(0.9, self.resistances.get("physical", 0) + 0.02)
        self.resistances["magic"] = min(0.9, self.resistances.get("magic", 0) + 0.02)

    def take_damage(self, amount, damage_type="physical"):
        resistance = self.resistances.get(damage_type, 0)
        weakness = self.weaknesses.get(damage_type, 0)
        actual_damage = amount * (1 - resistance) * (1 + weakness)
        self.health -= actual_damage
        self.hit_anim = 10
        return self.health <= 0

    def draw(self, screen, camera):
        cart_x, cart_y = iso_to_cart(self.x, self.y, self.z)
        screen_x, screen_y = camera.apply(cart_x, cart_y)

        # Эффект получения урона
        if self.hit_anim > 0:
            pygame.draw.circle(screen, DAMAGE_COLOR, (screen_x, screen_y), 20, 3)

        # Визуализация босса по фазам
        if self.phase == 1:
            color = (180, 50, 50)
        elif self.phase == 2:
            color = (200, 50, 50)
        else:
            color = (220, 30, 30)

        # Рисуем тело босса
        pygame.draw.rect(screen, color, (screen_x - 20, screen_y - 15, 40, 30))
        # Глаза/орнаменты
        pygame.draw.circle(screen, (255, 255, 255), (screen_x - 10, screen_y - 10), 5)
        pygame.draw.circle(screen, (255, 255, 255), (screen_x + 10, screen_y - 10), 5)
        # Health bar
        bar_width = 60
        pygame.draw.rect(screen, (100, 100, 100), (screen_x - bar_width//2, screen_y - 40, bar_width, 6))
        pygame.draw.rect(screen, (200, 50, 50),
                       (screen_x - bar_width//2, screen_y - 40,
                        bar_width * (self.health / self.max_health), 6))

        # Эффект фаз
        if self.phase == 2:
            # Кольцо вокруг босса
            pygame.draw.circle(screen, (255, 100, 100, 100), (screen_x, screen_y), 25, 2)
        elif self.phase == 3:
            # Огненный эффект
            for i in range(6):
                angle = i * math.pi / 3
                pygame.draw.line(screen, (255, 100, 0),
                               (screen_x, screen_y),
                               (screen_x + math.cos(angle)*25, screen_y + math.sin(angle)*25), 3)

    def drop_items(self):
        """Выпадение редких предметов при смерти"""
        drops = [
            Item(self.x, self.y, "legendary_sword", power=20, effects={"buff": 300}),
            Item(self.x, self.y, "ancient_amulet", defense=0.4, effects={"resistance": {"physical": 0.3}})
        ]
        if random.random() < 0.3:
            drops.append(Item(self.x, self.y, "rare_artifact", effects={"xp_gain": 2}))
        return drops

    def distance_to(self, entity):
        return math.hypot(self.x - entity.x, self.y - entity.y)
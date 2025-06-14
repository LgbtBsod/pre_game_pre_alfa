import pygame
from .entity import Entity


class Item(Entity):
    def __init__(self, x, y, item_type):
        super().__init__(x, y)
        self.item_type = item_type
        self.z = 0.5
        self.power = 0
        self.defense = 0
        self.xp_value = 0
        self.damage_type = "physical"
        self.weapon_type = "melee"
        self.effects = {}

        if item_type == "sword":
            self.power = 10
            self.damage_type = "physical"
            self.weapon_type = "melee"
        elif item_type == "bow":
            self.power = 8
            self.damage_type = "piercing"
            self.weapon_type = "ranged"
        elif item_type == "axe":
            self.power = 12
            self.damage_type = "physical"
            self.weapon_type = "melee"
        elif item_type == "staff":
            self.power = 9
            self.damage_type = "magic"
            self.weapon_type = "ranged"
        elif item_type == "shield":
            self.defense = 0.3
        elif item_type == "amulet":
            self.defense = 0.2
        elif item_type == "ring":
            self.defense = 0.1
            self.effects = {"resistance": {"physical": 0.1, "magic": 0.1}}
        elif item_type == "health":
            self.effects = {"health": 30}
        elif item_type == "xp":
            self.xp_value = 50
        elif item_type == "potion_speed":
            self.effects = {"speed": 0.02}
        elif item_type == "potion_damage":
            self.effects = {"damage": 5}
        elif item_type == "potion_poison":
            self.effects = {"poison": True}
        elif item_type == "potion_buff":
            self.effects = {"buff": True}

    def draw(self, screen, camera):
        # Пример отрисовки для теста
        cart_x, cart_y = iso_to_cart(self.x, self.y, self.z)
        screen_x, screen_y = camera.apply(cart_x, cart_y)
        pygame.draw.circle(screen, (50, 200, 150), (int(screen_x), int(screen_y)), 8)
import random
import math
import pygame
from .item import Item


class Chest:
    def __init__(self, x, y):
        self.x, self.y, self.z = x, y, 0
        self.opened = False
        self.items = []
        item_types = ["health", "xp", "potion_speed", "potion_damage"]
        for _ in range(random.randint(1, 3)):
            self.items.append(Item(x, y, random.choice(item_types)))

    def draw(self, screen, camera):
        cart_x, cart_y = iso_to_cart(self.x, self.y, self.z)
        screen_x, screen_y = camera.apply(cart_x, cart_y)
        pygame.draw.rect(screen, (200, 160, 60), (int(screen_x - 15), int(screen_y - 5), 30, 15))
        pygame.draw.rect(screen, (150, 120, 40), (int(screen_x - 15), int(screen_y - 5), 30, 15), 2)
        lid_y = screen_y - 10 if self.opened else screen_y - 5
        pygame.draw.rect(screen, (180, 140, 50), (int(screen_x - 12), int(lid_y), 24, 5))
        pygame.draw.circle(screen, (180, 180, 180), (int(screen_x), int(screen_y - 2)), 4)
import math
import pygame
from .entity import Entity


class Trap(Entity):
    def __init__(self, x, y, trap_type="spike"):
        super().__init__(x, y)
        self.trap_type = trap_type
        self.z = 0
        self.visible = False
        self.damage = {
            "spike": 15,
            "poison": 5,
            "fire": 12
        }.get(trap_type, 10)

    def draw(self, screen, camera):
        if not self.visible:
            return
        cart_x, cart_y = iso_to_cart(self.x, self.y, self.z)
        screen_x, screen_y = camera.apply(cart_x, cart_y)
        if self.trap_type == "spike":
            for i in range(3):
                pygame.draw.line(screen, (220, 180, 60),
                               (screen_x - 10 + i * 10, screen_y + 10),
                               (screen_x - 5 + i * 10, screen_y - 10), 3)
        elif self.trap_type == "poison":
            pygame.draw.circle(screen, (100, 200, 100, 150), (screen_x, screen_y), 15)
        elif self.trap_type == "fire":
            pygame.draw.circle(screen, (255, 100, 0, 150), (screen_x, screen_y), 12)
            for i in range(8):
                angle = i * math.pi / 4
                pygame.draw.line(screen, (255, 200, 0),
                               (screen_x, screen_y),
                               (screen_x + math.cos(angle) * 15, screen_y + math.sin(angle) * 15), 2)
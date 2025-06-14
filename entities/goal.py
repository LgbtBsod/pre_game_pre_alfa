import math
import pygame


class Goal:
    def __init__(self, x, y):
        self.x, self.y, self.z = x, y, 0
        self.pulse = 0

    def update(self):
        self.pulse = math.sin(pygame.time.get_ticks() / 500) * 5

    def draw(self, screen, camera):
        cart_x, cart_y = iso_to_cart(self.x, self.y, self.z)
        screen_x, screen_y = camera.apply(cart_x, cart_y)
        screen_y -= self.pulse
        pygame.draw.rect(screen, (255, 215, 70), (int(screen_x - 15), int(screen_y - 10), 30, 20))
        pygame.draw.circle(screen, (255, 255, 200), (int(screen_x), int(screen_y)), 8)
        for i in range(4):
            angle = i * math.pi / 2
            pygame.draw.line(screen, (255, 255, 200),
                           (int(screen_x), int(screen_y)),
                           (int(screen_x + math.cos(angle)*15), int(screen_y + math.sin(angle)*15)), 3)
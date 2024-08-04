import pygame
import math


class Use_spite(pygame.sprite.Sprite):
	def __init__(self,groups):
		super().__init__(groups)
		
	def get_distance(self,player,sprite):
		spite_vec = pygame.math.Vector2(self.rect.center)
		player_vec = pygame.math.Vector2(player.rect.center)
		distance = (player_vec - spite_vec).magnitude()
		
		if distance > 0:
			direction = (player_vec - spite_vec).normalize()
		else:
			direction = pygame.math.Vector2()
			
		return (distance,direction)
	
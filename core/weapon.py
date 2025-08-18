import pygame 

class Weapon(pygame.sprite.Sprite):
	def __init__(self,player,groups):
		super().__init__(groups)
		self.sprite_type = 'weapon'
		
		# Извлекаем базовое направление из статуса игрока
		status = player.status
		if '_' in status:
			direction = status.split('_')[0]
		else:
			direction = status

		# graphic
		full_path = f'graphics/weapons/{player.weapon}/{direction}.png'
		try:
			self.image = pygame.image.load(full_path).convert_alpha()
		except pygame.error:
			# Если файл не найден, используем fallback
			print(f"Warning: Could not load weapon graphic: {full_path}")
			# Создаем простой прямоугольник как fallback
			self.image = pygame.Surface((32, 32))
			self.image.fill((255, 0, 0))  # Красный цвет для отладки
		
		# placement
		if direction == 'right':
			self.rect = self.image.get_rect(midleft = player.rect.midright + pygame.math.Vector2(0,16))
		elif direction == 'left': 
			self.rect = self.image.get_rect(midright = player.rect.midleft + pygame.math.Vector2(0,16))
		elif direction == 'down':
			self.rect = self.image.get_rect(midtop = player.rect.midbottom + pygame.math.Vector2(-10,0))
		else:
			self.rect = self.image.get_rect(midbottom = player.rect.midtop + pygame.math.Vector2(-10,0))
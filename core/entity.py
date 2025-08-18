import pygame
from math import sin
from typing import List, Optional, Tuple
from core.logger import get_logger

class Entity(pygame.sprite.Sprite):
	"""
	Базовый класс для всех игровых сущностей.
	Отвечает за базовую анимацию, движение и коллизии.
	"""
	
	def __init__(self, groups: List[pygame.sprite.Group]):
		super().__init__(groups)
		self.logger = get_logger()
		
		# Анимация
		self.frame_index: float = 0.0
		self.animation_speed: float = 0.15
		self.direction: pygame.math.Vector2 = pygame.math.Vector2()
		
		# Коллизии
		self.obstacle_sprites: Optional[pygame.sprite.Group] = None
		self.hitbox: Optional[pygame.Rect] = None

	def set_obstacle_sprites(self, obstacle_sprites: pygame.sprite.Group) -> None:
		"""Устанавливает группу спрайтов для коллизий."""
		self.obstacle_sprites = obstacle_sprites

	def set_hitbox(self, hitbox: pygame.Rect) -> None:
		"""Устанавливает хитбокс для коллизий."""
		self.hitbox = hitbox

	def move(self, speed: float) -> None:
		"""
		Перемещает сущность с учетом коллизий.
		
		Args:
			speed: Скорость перемещения
		"""
		if self.hitbox is None:
			self.logger.warning(f"Entity {self.__class__.__name__} has no hitbox set")
			return
			
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		# Горизонтальное движение
		self.hitbox.x += self.direction.x * speed
		self._handle_collision('horizontal')
		
		# Вертикальное движение
		self.hitbox.y += self.direction.y * speed
		self._handle_collision('vertical')
		
		# Обновляем rect на основе hitbox
		if hasattr(self, 'rect'):
			self.rect.center = self.hitbox.center

	def _handle_collision(self, direction: str) -> None:
		"""
		Обрабатывает коллизии в указанном направлении.
		
		Args:
			direction: Направление ('horizontal' или 'vertical')
		"""
		if self.obstacle_sprites is None or self.hitbox is None:
			return
			
		try:
			if direction == 'horizontal':
				for sprite in self.obstacle_sprites:
					if hasattr(sprite, 'hitbox') and sprite.hitbox.colliderect(self.hitbox):
						if self.direction.x > 0:  # Движение вправо
							self.hitbox.right = sprite.hitbox.left
						elif self.direction.x < 0:  # Движение влево
							self.hitbox.left = sprite.hitbox.right

			elif direction == 'vertical':
				for sprite in self.obstacle_sprites:
					if hasattr(sprite, 'hitbox') and sprite.hitbox.colliderect(self.hitbox):
						if self.direction.y > 0:  # Движение вниз
							self.hitbox.bottom = sprite.hitbox.top
						elif self.direction.y < 0:  # Движение вверх
							self.hitbox.top = sprite.hitbox.bottom
		except Exception as e:
			self.logger.error(f"Error handling collision in {direction} direction: {e}")

	def wave_value(self) -> int:
		"""
		Возвращает значение для эффекта мерцания.
		
		Returns:
			Значение альфа-канала (0 или 255)
		"""
		try:
			value = sin(pygame.time.get_ticks())
			return 255 if value >= 0 else 0
		except Exception as e:
			self.logger.error(f"Error calculating wave value: {e}")
			return 255

	def load_animation_frames(self, folder_path: str) -> List[pygame.Surface]:
		"""
		Загружает кадры анимации из папки.
		
		Args:
			folder_path: Путь к папке с кадрами анимации
			
		Returns:
			Список загруженных поверхностей
		"""
		if self.resource_manager is None:
			self.logger.warning("No resource manager available for loading animation frames")
			return []
			
		try:
			frames = self.resource_manager.load_folder(folder_path, ResourceManager.IMAGE)
			if not frames:
				self.logger.warning(f"No animation frames found in {folder_path}")
				return self._create_fallback_frames()
			return frames
		except Exception as e:
			self.logger.error(f"Error loading animation frames from {folder_path}: {e}")
			return self._create_fallback_frames()

	def _create_fallback_frames(self) -> List[pygame.Surface]:
		"""
		Создает резервные кадры анимации при ошибке загрузки.
		
		Returns:
			Список резервных поверхностей
		"""
		fallback_surf = pygame.Surface((64, 64))
		fallback_surf.fill((255, 0, 255))  # Маджента для отладки
		return [fallback_surf]

	def update_animation(self, animation_frames: List[pygame.Surface]) -> None:
		"""
		Обновляет анимацию сущности.
		
		Args:
			animation_frames: Список кадров анимации
		"""
		if not animation_frames:
			return
			
		try:
			# Обновляем индекс кадра
			self.frame_index += self.animation_speed
			if self.frame_index >= len(animation_frames):
				self.frame_index = 0

			# Устанавливаем текущее изображение
			frame_index = int(self.frame_index)
			if 0 <= frame_index < len(animation_frames):
				self.image = animation_frames[frame_index]
			else:
				self.logger.warning(f"Invalid frame index: {frame_index}")
				
		except Exception as e:
			self.logger.error(f"Error updating animation: {e}")

	def get_direction_vector(self) -> pygame.math.Vector2:
		"""
		Возвращает текущий вектор направления.
		
		Returns:
			Вектор направления
		"""
		return self.direction.copy()

	def set_direction(self, direction: pygame.math.Vector2) -> None:
		"""
		Устанавливает направление движения.
		
		Args:
			direction: Новый вектор направления
		"""
		self.direction = direction

	def is_moving(self) -> bool:
		"""
		Проверяет, движется ли сущность.
		
		Returns:
			True, если сущность движется
		"""
		return self.direction.magnitude() > 0
from re import S
import pygame 
from helper.settings import *
from tile import Tile
from player import Player
from debug import debug
from helper.support import *
from random import choice, randint
from weapon import Weapon
from UI.ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from anim_tile import *
from equip.equipment import Equipment
from equip.chance import*
from UI.upgrade import *
from save.save_load import*
from effect import *
from equip.item_base import *

class Level:
	def __init__(self):

		# get the display surface 
		self.display_surface = pygame.display.get_surface()
		self.game_paused = False
		# sprite group setup
		self.visible_sprites = YSortCameraGroup()
		self.obstacle_sprites = pygame.sprite.Group()
		self.interactive_sprites = pygame.sprite.Group()
		
		# attack sprites
		self.current_attack = None
		self.attack_sprites = pygame.sprite.Group()
		self.attackable_sprites = pygame.sprite.Group()

		# sprite setup
		self.create_map()

		# user interface 
		self.ui = UI()
		self.menu = Upgrade(self.player)
		#stats
		self.equip = Equipment(self.current_stats)
		# particles
		self.animation_player = AnimationPlayer()
		self.magic_player = MagicPlayer(self.animation_player)

	def create_map(self):
		layouts = {
			'boundary': import_csv_layout('map/test._block.csv'),
			'tree': import_csv_layout('map/test._tree.csv'),
			'object': import_csv_layout('map/test._lake.csv'),
			'entities': import_csv_layout('map/test._entities.csv'),
			#'chest': import_csv_layout('map/test._chest'),
			#'npc': import_csv_layout('map/test._npc')
		}
		
		graphics = {
			'tree': import_folder('graphics/Tree'),
			'lakes': import_folder('graphics/water/lake')
		}

		for style,layout in layouts.items():
			for row_index,row in enumerate(layout):
				for col_index, col in enumerate(row):
					if col != '-1':
						x = col_index * TILESIZE
						y = row_index * TILESIZE
						if style == 'boundary':
							Tile((x,y),[self.obstacle_sprites],'invisible')
						if style == 'tree':
							random_grass_image = choice(graphics['tree'])
							Tile(
								(x,y),
								[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites],
								'tree',
								random_grass_image)

						if style == 'lake':
							Anim_Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'lake')

						if style == 'entities':
							if col == '164':
								self.player = Player(
									(x,y),
									[self.visible_sprites],
									self.obstacle_sprites,
									self.create_attack,
									self.destroy_attack,
									self.create_magic,
									)
							else:
								if col == '160':
									monster_name = 'warrior'
								elif col == '131': 
									monster_name = 'necromancer'
								# # elif col == '391': monster_name = 'spirit'
								# # elif col == '392': monster_name ='raccoon'
								else: 
									monster_name = 'squid'
								Enemy(
								 	monster_name,
								 	(x,y),
								 	[self.visible_sprites,self.attackable_sprites],
								 	self.obstacle_sprites,
								 	self.damage_player,
								 	self.trigger_death_particles,
								 	self.add_exp,
								 	self.drops)
							

	def create_attack(self):
		
		self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])

	def create_magic(self,style,strength,cost):
		if style == 'heal':
			self.magic_player.heal(self.player,strength,cost,[self.visible_sprites])

		if style == 'flame':
			self.magic_player.flame(self.player,cost,[self.visible_sprites,self.attack_sprites])

	def destroy_attack(self):
		if self.current_attack:
			self.current_attack.kill()
		self.current_attack = None

	def player_attack_logic(self):
		if self.attack_sprites:
			for attack_sprite in self.attack_sprites:
				collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
				if collision_sprites:
					for target_sprite in collision_sprites:
						if target_sprite.sprite_type == 'tree':
							pos = target_sprite.rect.center
							offset = pygame.math.Vector2(0,75)
							for leaf in range(randint(3,6)):
								self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
							target_sprite.kill()
						else:
							target_sprite.get_damage(self.player,attack_sprite.sprite_type)

	def damage_player(self,amount,attack_type):
		if self.player.vulnerable:
			self.player.health -= amount
			if self.player.health <= 0:
				self.player.health = 0
			self.player.vulnerable = False
			self.player.hurt_time = pygame.time.get_ticks()
			self.animation_player.create_particles(attack_type,self.player.rect.center,[self.visible_sprites])

	def trigger_death_particles(self,pos,particle_type):

		self.animation_player.create_particles(particle_type,pos,self.visible_sprites)
	
	def drops(self, item):
		if chance('70%'):
			self.equip.add_to_bag(item)
	
	def check_buff(self,stats):
		print(self.player.status,stats)
		for item in self.equip.equip:
			if artifacts[item]['effect']['name'] == 'brave':
				if brave(self.player.health,self.player.current_stats['health']):
					print('true',self.player.health,self.player.current_stats['health'])
				else:
					print('false',self.player.health,self.player.current_stats['health'])
			else:
				pass
				
	def add_exp(self,amount):
		self.player.exp += amount
	
	def run(self):
		self.visible_sprites.custom_draw(self.player)
		self.ui.display(self.player)
		
		if self.game_paused: 
			self.menu.display()
		else:
			# update and draw the game	
			self.visible_sprites.update()
			self.visible_sprites.enemy_update(self.player)
			#self.equip.update()
			self.player_attack_logic()
			

	def current_stats(self,modify):
		base_stats = self.player.base

		must_be = {}
		for item in modify.keys():
			if item == 'crit_rate' or item == 'crit_chance':
				must_be[item] = modify[item]
			else:
				must_be[item] = modify[item] +1

		for item in must_be.keys():
			if item == 'crit_rate' or item == 'crit_chance':
				self.player.current_stats[item]= must_be[item] + base_stats[item]
			else:	
				self.player.current_stats[item] *= must_be[item]
				
		must_be.clear()
		print(self.player.current_stats)
		self.check_buff(self.player.current_stats)
	def toggle(self):
		self.game_paused = not self.game_paused
	
	def save_load(self):
		pos = list(self.player.rect)
		exp = self.player.exp
		item = self.equip.equip
		save(pos, item, exp)

		
class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):

		# general setup 
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()

		# creating the floor
		self.floor_surf = pygame.image.load('map/test.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def custom_draw(self,player):

		# getting the offset 
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		# drawing the floor
		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf,floor_offset_pos)

		# for sprite in self.sprites():
		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image,offset_pos)

	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)

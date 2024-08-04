import pygame, sys

from helper.settings import *
from level import Level
from debug import *

class Game:
	def __init__(self):

		# general setup
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH,HEIGTH))
		pygame.display.set_caption('Zelda')
		self.clock = pygame.time.Clock()

		self.level = Level()
	
	def run(self):
		while True:
			for event in pygame.event.get(): 
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
	
					if event.key == pygame.K_ESCAPE:
						self.level.toggle()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_F1:
						self.level.save_load()
			self.screen.fill('black')
			self.level.run()
			debug(self.clock.get_fps())
			pygame.display.update()
			self.clock.tick(FPS)

if __name__ == '__main__':
	game = Game()
	game.run()
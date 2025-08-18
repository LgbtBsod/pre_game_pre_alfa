from csv import reader
from os import walk
import pygame
import os

def import_csv_layout(path):
	terrain_map = []
	try:
		with open(path) as level_map:
			layout = reader(level_map,delimiter = ',')
			for row in layout:
				terrain_map.append(list(row))
		return terrain_map
	except FileNotFoundError:
		print(f"Warning: Could not find CSV file: {path}")
		return []
	except Exception as e:
		print(f"Error reading CSV file {path}: {e}")
		return []

def import_folder(path):
	surface_list = []
	
	# Проверяем существование папки
	if not os.path.exists(path):
		print(f"Warning: Folder does not exist: {path}")
		return surface_list

	# Поддерживаемые форматы изображений
	image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tga')
	
	try:
		for _, __, img_files in walk(path):
			for image in img_files:
				# Проверяем расширение файла
				if image.lower().endswith(image_extensions):
					full_path = os.path.join(path, image)
					try:
						image_surf = pygame.image.load(full_path).convert_alpha()
						surface_list.append(image_surf)
					except pygame.error as e:
						print(f"Warning: Could not load image {full_path}: {e}")
						continue
		return surface_list
	except Exception as e:
		print(f"Error reading folder {path}: {e}")
		return surface_list

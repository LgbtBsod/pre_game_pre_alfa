from csv import reader
from os import walk
import pygame

def import_csv_layout(path):
	terrain_map = []
	with open(path) as level_map:
		layout = reader(level_map,delimiter = ',')
		for row in layout:
			terrain_map.append(list(row))
		return terrain_map

def import_folder(path):
	surface_list = []

	for _,__,img_files in walk(path):
		for image in img_files:
			full_path = path + '/' + image
			image_surf = pygame.image.load(full_path).convert_alpha()
			surface_list.append(image_surf)

	return surface_list
	
def convert_to_num(percents)->float:
	if type(percents) == str:
		percents = percents.replace('%', '')
		modify = float(percents)/100
	else:
		modify = float(percents)/100
	
	return modify

def crit_percents(percents):

	percents = str(percents).replace('%','')
	
	modify = int(percents)
	return modify
	
def crit_for_upgrade(percents):

	percents = str(percents).replace('%','')
	
	modify = float(percents)
	return modify
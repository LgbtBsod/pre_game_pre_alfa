import pygame
import sys
import random
import json
import os

from config import screen, clock, WIDTH, HEIGHT, BACKGROUND, TEXT_COLOR, BUTTON_COLOR, BUTTON_HOVER, BUTTON_TEXT
from entities.player import Player
from entities.enemy import Enemy
from entities.boss import Boss
from entities.item import Item
from entities.trap import Trap
from entities.chest import Chest
from entities.goal import Goal
from map.game_map import GameMap
from ui.buttons import Button
from ui.camera import Camera
from utils.file_utils import save_game, load_game


def init_game(saved_knowledge=None, saved_inventory=None, player_level=1, player_xp=0, map_size=50):
    # Случайный спавн игрока
    while True:
        start_x, start_y = random.randint(2, map_size - 3), random.randint(2, map_size - 3)
        break

    game_map = GameMap(map_size, map_size, (start_x, start_y))
    # Случайная цель
    while True:
        goal_x, goal_y = random.randint(map_size - 10, map_size - 3), random.randint(map_size - 10, map_size - 3)
        if game_map.tiles[goal_y][goal_x] == 0:
            break
    goal = Goal(goal_x, goal_y)

    # Создаем врагов
    enemies = []
    for _ in range(15):  # Примерное количество врагов
        x, y = random.randint(5, map_size - 5), random.randint(5, map_size - 5)
        enemy_type = random.choice(["warrior", "archer", "mage"])
        enemy = Enemy(x + 0.5, y + 0.5, enemy_type)
        enemies.append(enemy)
        game_map.add_entity(enemy)

    # Ловушки
    traps = []
    for x in range(game_map.width):
        for y in range(game_map.height):
            if game_map.tiles[y][x] == 0 and random.random() < 0.02:
                trap_type = random.choice(["spike", "poison", "fire"])
                trap = Trap(x + 0.5, y + 0.5, trap_type)
                traps.append(trap)
                game_map.add_entity(trap)

    # Сундуки
    chests = []
    for _ in range(5):
        x, y = random.randint(5, map_size - 5), random.randint(5, map_size - 5)
        chest = Chest(x + 0.5, y + 0.5)
        chests.append(chest)
        game_map.add_entity(chest)

    # Предметы
    items = []
    for enemy in enemies:
        if random.random() < 0.3:
            item_types = ["sword", "bow", "axe", "staff", "shield", "amulet", "ring",
                          "health", "xp", "potion_speed", "potion_damage", "potion_poison", "potion_buff"]
            item = Item(enemy.x, enemy.y, random.choice(item_types))
            items.append(item)
            game_map.add_entity(item)

    # Босс
    boss = Boss(map_size - 5 + 0.5, map_size - 5 + 0.5)
    enemies.append(boss)
    game_map.add_entity(boss)

    # Игрок
    player = Player(start_x + 0.5, start_y + 0.5, saved_knowledge, saved_inventory, player_level, player_xp)
    return game_map, player, goal, enemies, chests, traps, items


def main():
    pygame.init()
    map_size = 50
    saved_data = load_game()
    if saved_data:
        saved_knowledge, saved_inventory, player_level, player_xp = saved_data
    else:
        saved_knowledge, saved_inventory, player_level, player_xp = None, None, 1, 0

    game_map, player, goal, enemies, chests, traps, items = init_game(
        saved_knowledge, saved_inventory, player_level, player_xp, map_size
    )

    font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 48)

    # Камера
    camera = Camera()

    # Кнопки
    new_game_button = Button(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 60, "Новая игра", lambda: "new_game")
    load_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 30, 300, 60, "Загрузить игру", lambda: "load")
    quit_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 110, 300, 60, "Выход", lambda: "quit")

    continue_button = Button(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 60, "Продолжить", lambda: "continue")
    save_button = Button(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 60, "Сохранить игру", lambda: "save")
    menu_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 140, 300, 60, "Выход в меню", lambda: "menu")
    restart_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 60, "Новая игра", lambda: "new_game")
    menu_end_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 130, 300, 60, "Выход в меню", lambda: "menu")

    MENU = 0
    PLAYING = 1
    PAUSED = 2
    GAME_OVER = 3
    GAME_WON = 4
    game_state = MENU

    game_won = False
    game_over = False

    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == MENU:
                new_game_button.check_hover(mouse_pos)
                load_button.check_hover(mouse_pos)
                quit_button.check_hover(mouse_pos)
                action = new_game_button.handle_event(event) or \
                         load_button.handle_event(event) or \
                         quit_button.handle_event(event)
                if action == "new_game":
                    game_map, player, goal, enemies, chests, traps, items = init_game()
                    game_state = PLAYING
                    game_won = False
                    game_over = False
                elif action == "load":
                    saved_data = load_game()
                    if saved_data:
                        saved_knowledge, saved_inventory, player_level, player_xp = saved_data
                        game_map, player, goal, enemies, chests, traps, items = init_game(
                            saved_knowledge, saved_inventory, player_level, player_xp, map_size
                        )
                        game_state = PLAYING
                        game_won = False
                        game_over = False
                elif action == "quit":
                    pygame.quit()
                    sys.exit()

            elif game_state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        game_state = PAUSED
                    elif event.key == pygame.K_r:
                        save_game(player)
                        game_map, player, goal, enemies, chests, traps, items = init_game(
                            player.knowledge, player.inventory, player.level, player.xp, map_size
                        )
                        game_won = False
                        game_over = False
                    elif event.key == pygame.K_s:
                        save_game(player)
                    elif event.key == pygame.K_l:
                        saved_data = load_game()
                        if saved_data:
                            saved_knowledge, saved_inventory, player_level, player_xp = saved_data
                            game_map, player, goal, enemies, chests, traps, items = init_game(
                                saved_knowledge, saved_inventory, player_level, player_xp, map_size
                            )
                            game_won = False
                            game_over = False

            elif game_state == PAUSED:
                continue_button.check_hover(mouse_pos)
                save_button.check_hover(mouse_pos)
                menu_button.check_hover(mouse_pos)
                action = continue_button.handle_event(event) or \
                         save_button.handle_event(event) or \
                         menu_button.handle_event(event)
                if action == "continue":
                    game_state = PLAYING
                elif action == "save":
                    save_game(player)
                elif action == "menu":
                    game_state = MENU

            elif game_state == GAME_OVER or game_state == GAME_WON:
                restart_button.check_hover(mouse_pos)
                menu_end_button.check_hover(mouse_pos)
                action = restart_button.handle_event(event) or \
                         menu_end_button.handle_event(event)
                if action == "new_game":
                    game_map, player, goal, enemies, chests, traps, items = init_game()
                    game_state = PLAYING
                    game_won = False
                    game_over = False
                elif action == "menu":
                    game_state = MENU

        if game_state == PLAYING and not game_won and not game_over:
            goal.update()
            player_cart_x, player_cart_y = iso_to_cart(player.x, player.y, player.z)
            camera.update(player_cart_x, player_cart_y)

            for enemy in enemies[:]:
                enemy.update(player, enemies)
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    game_map.remove_entity(enemy)
                    if random.random() < 0.3:
                        item_types = ["sword", "bow", "axe", "staff", "shield", "amulet", "ring",
                                      "health", "xp", "potion_speed", "potion_damage", "potion_poison", "potion_buff"]
                        new_item = Item(enemy.x, enemy.y, random.choice(item_types))
                        items.append(new_item)
                        game_map.add_entity(new_item)

            for chest in chests:
                if not chest.opened and player.distance_to(chest) < 1:
                    chest.opened = True
                    items.extend(chest.items)
                    for item in chest.items:
                        game_map.add_entity(item)

            game_won = player.update(game_map, enemies, items, chests, traps, goal)
            if game_won:
                game_state = GAME_WON
            elif player.health <= 0:
                game_state = GAME_OVER

        screen.fill(BACKGROUND)

        if game_state in [PLAYING, PAUSED, GAME_OVER, GAME_WON]:
            game_map.draw(screen, camera)
            goal.draw(screen, camera)
            player.draw(screen, camera)

            # UI
            inv_y = HEIGHT - 120
            pygame.draw.rect(screen, (40, 45, 60, 200), (10, inv_y, 300, 110), border_radius=10)
            inv_title = font.render("Инвентарь:", True, TEXT_COLOR)
            screen.blit(inv_title, (20, inv_y + 10))
            for i, item in enumerate(player.inventory[:5]):
                item_text = font.render(f"- {item.item_type}", True, (50, 200, 150))
                screen.blit(item_text, (30, inv_y + 35 + i * 20))

            eq_y = HEIGHT - 200
            pygame.draw.rect(screen, (40, 45, 60, 200), (10, eq_y, 300, 70), border_radius=10)
            eq_title = font.render("Экипировка:", True, TEXT_COLOR)
            screen.blit(eq_title, (20, eq_y + 10))
            weapon = player.equipped_weapon.item_type if player.equipped_weapon else "нет"
            accessory = player.equipped_accessory.item_type if player.equipped_accessory else "нет"
            weapon_text = font.render(f"Оружие: {weapon}", True, (50, 200, 150))
            screen.blit(weapon_text, (30, eq_y + 35))
            accessory_text = font.render(f"Аксессуар: {accessory}", True, (50, 200, 150))
            screen.blit(accessory_text, (160, eq_y + 35))

        if game_state == MENU:
            title = title_font.render("ИЗОМЕТРИЧЕСКИЙ АВТОНОМНЫЙ ПЛАТФОРМЕР", True, (100, 200, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
            new_game_button.draw(screen)
            load_button.draw(screen)
            quit_button.draw(screen)
            hint = font.render("Используйте мышь для взаимодействия с меню", True, (180, 180, 180))
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 100))

        elif game_state == PAUSED:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            title = title_font.render("ПАУЗА", True, (255, 215, 70))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
            continue_button.draw(screen)
            save_button.draw(screen)
            menu_button.draw(screen)

        elif game_state == GAME_OVER:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            title = title_font.render("ИГРА ОКОНЧЕНА", True, (255, 100, 100))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
            stats = font.render(f"Уровень: {player.level} | Опыт: {player.xp}/{player.xp_to_level}", True, TEXT_COLOR)
            screen.blit(stats, (WIDTH // 2 - stats.get_width() // 2, HEIGHT // 3 + 60))
            restart_button.draw(screen)
            menu_end_button.draw(screen)

        elif game_state == GAME_WON:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            title = title_font.render("УРОВЕНЬ ПРОЙДЕН!", True, (100, 255, 150))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
            stats = font.render(f"Уровень: {player.level} | Опыт: {player.xp}/{player.xp_to_level}", True, TEXT_COLOR)
            screen.blit(stats, (WIDTH // 2 - stats.get_width() // 2, HEIGHT // 3 + 60))
            restart_button.draw(screen)
            menu_end_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
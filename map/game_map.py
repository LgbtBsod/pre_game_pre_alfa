import random
import heapq

# Фолбэки для изометрии при отсутствии utils.math_utils
def iso_to_cart(x, y, tile_w=80, tile_h=40):
    cart_x = (x - y) * (tile_w // 2)
    cart_y = (x + y) * (tile_h // 2)
    return cart_x, cart_y


class GameMap:
    def __init__(self, width, height, player_start=None):
        self.width = width
        self.height = height
        self.tiles = [[0 for _ in range(width)] for _ in range(height)]
        self.entities = [[[] for _ in range(width)] for _ in range(height)]
        self.points_of_interest = []

        # Создаем базовый рельеф
        for y in range(height):
            for x in range(width):
                if random.random() < 0.1:
                    self.tiles[y][x] = 1  # Препятствие

        # Создаем естественные препятствия (например, горы)
        for _ in range(5):
            rx, ry = random.randint(5, width - 5), random.randint(5, height - 5)
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    nx, ny = rx + dx, ry + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        if random.random() < 0.7:  # Не все клетки заполняем
                            self.tiles[ny][nx] = 1

        # Точки интереса (для спавна врагов, сундуков и т.п.)
        for _ in range(10):
            while True:
                x, y = random.randint(10, width - 10), random.randint(10, height - 10)
                if self.tiles[y][x] == 0 and (player_start is None or (x, y) != player_start):
                    self.points_of_interest.append((x, y))
                    break

    def add_entity(self, entity):
        """Добавляет сущность на карту"""
        x, y = int(entity.x), int(entity.y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.entities[y][x].append(entity)

    def remove_entity(self, entity):
        """Удаляет сущность с карты"""
        x, y = int(entity.x), int(entity.y)
        if 0 <= x < self.width and 0 <= y < self.height:
            if entity in self.entities[y][x]:
                self.entities[y][x].remove(entity)

    def get_entities_at(self, x, y):
        """Получает список сущностей на указанной позиции"""
        return self.entities[y][x]

    def is_blocked(self, x, y):
        """Проверяет, заблокировано ли место"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return self.tiles[y][x] == 1

    def find_path(self, start_x, start_y, end_x, end_y):
        """
        Находит путь между двумя точками с помощью A*
        
        :param start_x: начальная X
        :param start_y: начальная Y
        :param end_x: конечная X
        :param end_y: конечная Y
        :return: путь как список координат или None
        """
        start = (start_x, start_y)
        goal = (end_x, end_y)

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)

                if not self.in_bounds(*neighbor):
                    continue
                if self.is_blocked(*neighbor):
                    continue

                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None  # Путь не найден

    def heuristic(self, a, b):
        """Эвристика — расстояние Манхэттена"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from, current):
        """Восстанавливает путь"""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def in_bounds(self, x, y):
        """Проверяет, находится ли точка внутри границ карты"""
        return 0 <= x < self.width and 0 <= y < self.height

    def draw(self, surface, camera):
        """Отрисовывает карту с учётом камеры"""
        # Рассчитываем видимую область с запасом
        min_x = max(0, int(camera.x / 80 - 30))
        max_x = min(self.width, int(camera.x / 80 + 30))
        min_y = max(0, int(camera.y / 40 - 30))
        max_y = min(self.height, int(camera.y / 40 + 30))

        # Отрисовка тайлов
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                cart_x, cart_y = iso_to_cart(x, y)
                screen_x, screen_y = camera.apply(cart_x, cart_y)
                color = (80, 90, 110) if self.tiles[y][x] == 0 else (120, 100, 80)
                points = [
                    camera.apply(*iso_to_cart(x, y)),
                    camera.apply(*iso_to_cart(x+1, y)),
                    camera.apply(*iso_to_cart(x+1, y+1)),
                    camera.apply(*iso_to_cart(x, y+1))
                ]
                surface.drawPolygon(points, color)
                surface.drawPolygon(points, (60, 70, 90))

        # Собираем все сущности для отрисовки в правильном порядке
        entities_to_draw = []
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                for entity in self.entities[y][x]:
                    entities_to_draw.append(entity)

        # Сортируем по Y для правильной отрисовки
        entities_to_draw.sort(key=lambda e: e.y + e.x)

        # Отрисовываем сущности
        for entity in entities_to_draw:
            entity.draw(surface, camera)
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import tkinter as tk
import time

def read_field_from_file(filepath):
    """Чтение поля из файла."""
    try:
        with open(filepath, 'r') as file:
            field = [list(map(int, line.strip())) for line in file.readlines()]
            if len(field) != 10 or any(len(row) != 10 for row in field):
                raise ValueError("Некорректный размер поля. Поле должно быть 10x10.")
            return field
    except FileNotFoundError:
        raise FileNotFoundError("Файл не найден.")
    except ValueError as e:
        raise e

def get_neighbors(x, y):
    """Получение соседей клетки с учётом всех направлений."""
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]
    return [(x + dx, y + dy) for dx, dy in directions if 0 <= x + dx < 10 and 0 <= y + dy < 10]

def add_to_priority_queue(queue, element):
    """Добавление элемента в очередь с приоритетом (по возрастанию расстояния)."""
    queue.append(element)
    queue.sort(key=lambda x: x[0])

def shortest_path(field, start, targets):
    """Поиск кратчайшего пути с учётом нескольких целей."""
    visited = set()
    pq = []
    add_to_priority_queue(pq, (0, start))
    print("pq: ", pq)
    distances = {start: 0}
    prev = {start: None}
    print("distances: ", distances)
    while pq:
        dist, current = pq.pop(0)
        if current in visited:
            continue
        visited.add(current)
        print("visited: ", visited)
        if all(target in visited for target in targets):
            break
        
        for neighbor in get_neighbors(*current):
            print("neighbor: ", neighbor)
            nx, ny = neighbor
            if field[nx][ny] == 2:  # Препятствие
                continue
            new_dist = dist + 1
            if neighbor not in distances or new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                print("distances: ", distances)
                prev[neighbor] = current
                add_to_priority_queue(pq, (new_dist, neighbor))
                print("pq: ", pq)
    return distances, prev

def reconstruct_path(prev, start, target):
    """Восстановление пути по предшественникам."""
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = prev.get(current)
    path.reverse()
    return path if path[0] == start else []

def collect_resources(field):
    """Сбор всех ресурсов, начиная с начальной позиции (0, 0)."""
    start = (0, 0)
    resources = [(i, j) for i in range(10) for j in range(10) if field[i][j] == 1]
    
    if not resources:
        print("Нет клеток с ресурсами для сбора.")
        return [], []
    
    visited_order = []
    full_path = []
    current_position = start
    
    while resources:
        distances, prev = shortest_path(field, current_position, resources)
        
        nearest_resource = min(resources, key=lambda pos: distances.get(pos, float('inf')))
        if distances.get(nearest_resource, float('inf')) == float('inf'):
            raise ValueError("Некоторые клетки с ресурсами недостижимы.")
        
        path_to_resource = reconstruct_path(prev, current_position, nearest_resource)
        
        full_path.extend(path_to_resource[1:])
        visited_order.append(nearest_resource)
        resources.remove(nearest_resource)
        current_position = nearest_resource
    
    return visited_order, full_path

def visualize_field(field, start_position=None, resources=[], path=[]):
    """Визуализация поля с использованием Matplotlib."""
    colormap = {
        0: 'white',   # Пустая клетка
        1: 'green',   # Ресурс
        2: 'black',   # Препятствие
    }
    
    visual_field = np.zeros((10, 10, 3))
    for i in range(10):
        for j in range(10):
            color = mcolors.to_rgb(colormap.get(field[i][j], 'white'))
            visual_field[i, j] = color
    
    for x, y in path:
        visual_field[x, y] = mcolors.to_rgb('blue')  # Путь - синий
    
    if start_position:
        cx, cy = start_position
        visual_field[cx, cy] = mcolors.to_rgb('red')  # Начальная позиция - красная
    
    for resource in resources:
        cx, cy = resource
        visual_field[cx, cy] = mcolors.to_rgb('red')  # Ресурсы - красные
    
    plt.imshow(visual_field, extent=[0, 10, 10, 0])
    plt.xticks(range(10))
    plt.yticks(range(10))
    plt.grid(visible=True, which='both', color='gray', linestyle='--', linewidth=0.5)
    plt.title("Визуализация поля")
    plt.show()

def visualize_field_tkinter(field, cell_size=50, resources=[], current_position=None, path=[]):
    """Визуализация поля с использованием Tkinter."""
    rows, cols = len(field), len(field[0])
    window_width = cols * cell_size
    window_height = rows * cell_size

    root = tk.Tk()
    root.title("Визуализация поля")
    canvas = tk.Canvas(root, width=window_width, height=window_height)
    canvas.pack()

    colors = {
        0: "white",  # Пустая клетка
        1: "green",  # Ресурс
        2: "black",  # Препятствие
    }

    for i, row in enumerate(field):
        for j, cell in enumerate(row):
            x0, y0 = j * cell_size, i * cell_size
            x1, y1 = x0 + cell_size, y0 + cell_size
            canvas.create_rectangle(x0, y0, x1, y1, fill=colors[cell], outline="gray")

    if current_position:
        cx, cy = current_position
        x0, y0 = cy * cell_size, cx * cell_size
        x1, y1 = x0 + cell_size, y0 + cell_size
        canvas.create_rectangle(x0, y0, x1, y1, fill="red", outline="gray")
        
    for resource in resources:
        cx, cy = resource
        x0, y0 = cy * cell_size, cx * cell_size
        x1, y1 = x0 + cell_size, y0 + cell_size
        canvas.create_rectangle(x0, y0, x1, y1, fill="red", outline="gray")
            
    for x, y in path:
        x0, y0 = y * cell_size, x * cell_size
        x1, y1 = x0 + cell_size, y0 + cell_size
        canvas.create_rectangle(x0, y0, x1, y1, fill="blue", outline="gray")
        canvas.update()
        time.sleep(0.5)
        
    root.mainloop()

if __name__ == "__main__":
    input_file = "input.txt"
    
    try:
        field = read_field_from_file(input_file)
        resources, full_path = collect_resources(field)
        print("Порядок посещения клеток с ресурсами:", resources)
        print("Порядок посещения клеток:", full_path)
        
        filtered_path = [coord for coord in full_path if coord not in resources]
        
        visualize_field_tkinter(field, cell_size=50, resources=resources, current_position=(0,0), path=filtered_path)

    except Exception as e:
        print(f"Ошибка: {e}")

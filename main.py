import pygame
import random
import math
import heapq
import shapely.geometry as geo
import shapely.ops as ops
from shapely.affinity import translate

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (93, 168, 65)
GRAY = (65, 65, 65)
BLUE = (61, 114, 40)

# Define the axiom and production rules
axiom = "X"

rules_grid = {
    "X": [
        "F[+X]F[-X]FX",
        "F[+X]F[-X]+X",
        "F-[[X]+X]+F[+FX]-X",
        "F[X]F[+X]+F[-X]X",
        "F[+X][-X]F+F[X]+F[+FX]-X",  # New rule for curved paths
        "FF[+X][+X]FF[-X][-X]",  # New rule for intersections
        "F[X]+[X]+F-F",  # New rule for branching paths
        "FX+F+FX-F-F"  # New rule for creating loops
    ],
    "F": [
        "FF",
        "F[+F]F[-F]F",
        "F[+FF][-FF]F"  # New rule for curved paths
    ],
}

rules_hexagonal = {
    "X": [
        "F[++X]F[--X]+X",  # Sharp curves for 60 degrees
        "F[X+F-X]F[+X-]-X",  # Complex branching with 60 degrees
        "F[+F[X]]F[-F[X]]X",  # Nested branching with 60 degrees
        "F[+X]F[-X]FX",  # Common pattern adapted for hexagonal layout
    ],
    "F": [
        "F[+F]F[-F]F",
        "F[+F-F-F]F[-F+F+F]",  # Hexagonal paths
    ],
}

rules_triangular = {
    "X": [
        "F"
        "F[+X]F[-X]FX",
        "F[X]F[+X]+F[-X]X",
        "F[+X][-X]F+F[X]+F[+FX]-X",  # Curved paths
        "F[X+F-X]F[+X-]-X",  # Complex branching with 120 degrees
    ],
    "F": [
        "F[+F]F[-F]F",
        "F[-F+F+F]-[+F-F-F]",  # Triangular paths
    ],
}

#---------------------------------------------------- Functions: Creating Buildings -----------------------------------------------------------
def calculate_polygon_area(polygon):
    """
    Helper function to calculate the area of a polygon.
    Implements the Shoelace formula.
    """
    area = 0
    for i in range(len(polygon)):
        j = (i + 1) % len(polygon)
        area += polygon[i][0] * polygon[j][1]
        area -= polygon[j][0] * polygon[i][1]
    area = abs(area) / 2
    return area

def point_in_polygon(point, polygon):
    """
    Helper function to determine if a point is inside a polygon.
    Implements the ray-casting algorithm.
    """
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def draw_buildings(surface, nodes, edges):
    polygons = []
    current_polygon = []

    for i, edge in enumerate(edges):
        start, end = edge
        current_polygon.append(start)
        if i == len(edges) - 1 or end != edges[(i + 1) % len(edges)][0]:
            current_polygon.append(end)
            if len(current_polygon) >= 3:  # Ensure we have a valid polygon
                polygons.append(current_polygon)
            current_polygon = [end]

    for polygon in polygons:
        area = calculate_polygon_area(polygon)
        if area > 100:  # Only process polygons with a minimum area
            building_size = int(math.sqrt(area) * 0.2)  # Scale down building size to fit within the polygon

            # Compute the bounding box for the polygon and convert to integers
            min_x = int(min(p[0] for p in polygon))
            max_x = int(max(p[0] for p in polygon))
            min_y = int(min(p[1] for p in polygon))
            max_y = int(max(p[1] for p in polygon))

            # Check if the polygon is too thin
            if min_x == max_x or min_y == max_y:
                continue  # Skip this polygon

            # Ensure there's enough space for a building
            if max_x - min_x < building_size or max_y - min_y < building_size:
                continue  # Skip this polygon

            attempts = 0
            while attempts < 100:  # Try up to 100 times to find a valid position
                building_x = random.randint(min_x, max_x - building_size)
                building_y = random.randint(min_y, max_y - building_size)
                building_rect = pygame.Rect(building_x, building_y, building_size, building_size)

                overlaps = False
                for edge in edges:
                    if building_rect.clipline(edge):
                        overlaps = True
                        break

                if not overlaps and point_in_polygon((building_rect.centerx, building_rect.centery), polygon):
                    pygame.draw.rect(surface, BLUE, building_rect)
                    break  # Building successfully placed
                attempts += 1

#---------------------------------------------------- Functions: Connecting Dead End Nodes  -----------------------------------------------------------
def connect_dead_end_nodes_angle(nodes, edges, surface):
    # Create a set of all nodes and existing edges for quick lookup
    all_nodes = set(nodes)
    existing_edges = set(edges)

    # Create a dictionary to store the connected nodes for each node
    connected_nodes = {node: set() for node in all_nodes}

    # Populate the connected_nodes dictionary
    for edge in edges:
        start, end = edge
        if start in all_nodes and end in all_nodes:
            connected_nodes[start].add(end)
            connected_nodes[end].add(start)

    max_iterations = len(nodes) * 2
    iterations = 0

    while iterations < max_iterations:
        iterations += 1
        dead_end_nodes = [node for node, connected in connected_nodes.items() if len(connected) == 1]

        if not dead_end_nodes:
            break

        for dead_end_node in dead_end_nodes:
            closest_node = None
            min_distance = float("inf")
            connected_nodes_for_dead_end = connected_nodes[dead_end_node]

            for node in all_nodes - {dead_end_node} - connected_nodes_for_dead_end:
                if (dead_end_node, node) not in existing_edges and (node, dead_end_node) not in existing_edges:
                    distance = math.sqrt((dead_end_node[0] - node[0]) ** 2 + (dead_end_node[1] - node[1]) ** 2)
                    if distance < min_distance:
                        closest_node = node
                        min_distance = distance

            if closest_node and min_distance < 200:
                step_size = 21
                total_distance = math.sqrt((closest_node[0] - dead_end_node[0])**2 + (closest_node[1] - dead_end_node[1])**2)
                num_steps = max(1, int(total_distance / step_size))
                step_x = (closest_node[0] - dead_end_node[0]) / num_steps
                step_y = (closest_node[1] - dead_end_node[1]) / num_steps

                prev_point = dead_end_node
                for i in range(1, num_steps + 1):
                    current_point = (int(dead_end_node[0] + i * step_x), int(dead_end_node[1] + i * step_y))
                    if (prev_point, current_point) not in existing_edges:
                        pygame.draw.line(surface, GRAY, prev_point, current_point, 7)
                        edges.append((prev_point, current_point))
                        existing_edges.add((prev_point, current_point))
                        existing_edges.add((current_point, prev_point))
                        if current_point not in all_nodes:
                            nodes.append(current_point)
                            all_nodes.add(current_point)
                            connected_nodes[current_point] = set()
                        connected_nodes[prev_point].add(current_point)
                        connected_nodes[current_point].add(prev_point)
                        prev_point = current_point

                connected_nodes[dead_end_node].add(closest_node)
                connected_nodes[closest_node].add(dead_end_node)

        # Break the loop if no new connections were made
        if all(len(connected) > 1 for connected in connected_nodes.values()):
            break

    print(f"Dead-end node connection completed in {iterations} iterations.")


def connect_dead_end_nodes(nodes, edges, surface):
    # Create a set of all nodes for quick lookup and a mapping from nodes to their indices
    all_nodes = set(nodes)
    node_index_map = {node: i for i, node in enumerate(nodes)}

    # Create a dictionary to keep track of connections for each node
    connected_nodes = {node: set() for node in all_nodes}

    # Create a set of existing edges for quick lookup
    existing_edges = set(edges)

    # Populate the connected_nodes dictionary based on the existing edges
    for start, end in edges:
        if start in all_nodes and end in all_nodes:
            connected_nodes[start].add(end)
            connected_nodes[end].add(start)

    # Calculate the maximum possible distance on the surface
    max_distance = math.hypot(surface.get_width(), surface.get_height())
    step_size = 21  # Step size for drawing lines

    # Identify leaf nodes (nodes with only one connection)
    leaf_nodes = [node for node, connected in connected_nodes.items() if len(connected) == 1]

    # Process each leaf node to connect it to other nodes
    for leaf_node in leaf_nodes:
        new_connections = []
        min_total_distance = float('inf')

        # Find the three shortest paths to other nodes
        for node in all_nodes - {leaf_node} - connected_nodes[leaf_node]:
            # Try to find a straight path between the leaf node and the current node
            if (leaf_node[0] == node[0] or leaf_node[1] == node[1]) and \
                    (leaf_node, node) not in existing_edges and (node, leaf_node) not in existing_edges:
                total_distance = math.hypot(node[0] - leaf_node[0], node[1] - leaf_node[1])
                new_connections.append(([leaf_node, node], total_distance))

            # If no straight path is found, try a path with one 90-degree turn
            else:
                turn_point1 = (leaf_node[0], node[1])
                turn_point2 = (node[0], leaf_node[1])
                for turn_point in [turn_point1, turn_point2]:
                    if turn_point not in all_nodes and \
                            (leaf_node, turn_point) not in existing_edges and (turn_point, node) not in existing_edges:
                        dist1 = math.hypot(turn_point[0] - leaf_node[0], turn_point[1] - leaf_node[1])
                        dist2 = math.hypot(node[0] - turn_point[0], node[1] - turn_point[1])
                        total_distance = dist1 + dist2
                        new_connections.append(([leaf_node, turn_point, node], total_distance))

        # Sort the new connections by total distance and take the three shortest paths
        new_connections.sort(key=lambda x: x[1])
        new_connections = new_connections[:3]

        # Check if more than one step is required to connect to three nodes
        if len(new_connections) > 1:
            for best_path, _ in new_connections:
                for i in range(len(best_path) - 1):
                    start_node, end_node = best_path[i], best_path[i + 1]
                    dx, dy = end_node[0] - start_node[0], end_node[1] - start_node[1]
                    distance = math.hypot(dx, dy)
                    num_steps = max(1, int(distance / step_size))
                    step_x, step_y = dx / num_steps, dy / num_steps

                    prev_point = start_node
                    for step in range(1, num_steps + 1):
                        new_point = (int(start_node[0] + step * step_x), int(start_node[1] + step * step_y))
                        pygame.draw.line(surface, GRAY, prev_point, new_point, 7)
                        if (prev_point, new_point) not in existing_edges:
                            edges.append((prev_point, new_point))
                            existing_edges.add((prev_point, new_point))
                            existing_edges.add((new_point, prev_point))

                        if new_point not in all_nodes:
                            nodes.append(new_point)
                            all_nodes.add(new_point)
                            node_index_map[new_point] = len(nodes) - 1
                            connected_nodes[new_point] = set()

                        connected_nodes[prev_point].add(new_point)
                        connected_nodes[new_point].add(prev_point)
                        prev_point = new_point

                # Connect the last two nodes in the path
                connected_nodes[best_path[-2]].add(best_path[-1])
                connected_nodes[best_path[-1]].add(best_path[-2])

        # If only one step is required to connect to three nodes
        else:
            for best_path, _ in new_connections:
                start_node, end_node = best_path[0], best_path[1]
                dx, dy = end_node[0] - start_node[0], end_node[1] - start_node[1]
                distance = math.hypot(dx, dy)
                num_steps = max(1, int(distance / step_size))
                step_x, step_y = dx / num_steps, dy / num_steps

                prev_point = start_node
                for step in range(1, num_steps + 1):
                    new_point = (int(start_node[0] + step * step_x), int(start_node[1] + step * step_y))
                    pygame.draw.line(surface, GRAY, prev_point, new_point, 7)
                    if (prev_point, new_point) not in existing_edges:
                        edges.append((prev_point, new_point))
                        existing_edges.add((prev_point, new_point))
                        existing_edges.add((new_point, prev_point))

                    if new_point not in all_nodes:
                        nodes.append(new_point)
                        all_nodes.add(new_point)
                        node_index_map[new_point] = len(nodes) - 1
                        connected_nodes[new_point] = set()

                    connected_nodes[prev_point].add(new_point)
                    connected_nodes[new_point].add(prev_point)
                    prev_point = new_point

                connected_nodes[best_path[0]].add(best_path[1])
                connected_nodes[best_path[1]].add(best_path[0])

    return nodes, edges
#---------------------------------------------------- Functions: Creating L-System City  -----------------------------------------------------------

# Define the function to draw the l-system
def draw_lsystem(sequence, step_size, surface):
    global angle
    stack = []  # Storage of the current direction and angle of the turtle to remember when backtracking
    nodes = []  # Storage of the nodes (each move forward represents 1 node)
    edges = []
    if angle == 120:
        height = 2
    else: height = 2.3

    x, y = surface.get_width() // 2, surface.get_height() // height
    current_angle = angle

    for char in sequence:

        if char == "F":  # Move forward
            dx = step_size * math.cos(current_angle * math.pi / 180)
            dy = step_size * math.sin(current_angle * math.pi / 180)
            new_x, new_y = x + dx, y + dy

            # Draw a thicker line for the road
            pygame.draw.line(surface, GRAY, (x, y), (new_x, new_y), 7)  # Change the line thickness to 5

            nodes.append((new_x, new_y))  # Add the node to the node list
            edges.append(((x, y), (new_x, new_y)))
            x, y = new_x, new_y

        elif char == "+":  # Rotate turtle 90 degrees right
            current_angle += angle
        elif char == "-":  # Rotate turtle 90 degrees left
            current_angle -= angle
        elif char == "[":  # Push current position and angle onto the stack (start of a new branch)
            stack.append((x, y, current_angle))
        elif char == "]":  # Pop position and angle from the stack (return to the previous branch)
            x, y, current_angle = stack.pop()

    return nodes, edges

# Generate the string of L-system starting with the axiom
def generate_lsystem(axiom, rules, max_segments):
    sequence = axiom  # Start the L-System sequence with the axiom

    while True:
        next_sequence = ""
        for char in sequence:  # Loop through the sequence
            if char in rules:  # Check if the character is a key in the production rules (X or F)
                next_sequence += random.choice(rules[char])
            else:  # If the character is not a key, like ( +, -, [, ], then keep it as it is
                next_sequence += char

        sequence = next_sequence

        # Count the total number of segments (F) in the sequence
        total_segments = sequence.count('F')

        if total_segments < max_segments:  # Continue looping until the total segments are less than max_segments
            continue
        else:
            # Find the index of the max_segments-th occurrence of 'F' in the sequence
            f_index = -1
            segments_found = 0
            for i, char in enumerate(sequence):
                if char == 'F':
                    segments_found += 1
                    if segments_found == max_segments:
                        f_index = i
                        break

            # Cut the sequence from the beginning to the index of the max_segments-th occurrence of 'F'
            sequence = sequence[:f_index + 1]
            break

    print(sequence)
    return sequence
#---------------------------------------------------- Functions: Creating Shortest Path -----------------------------------------------------------

def heuristic(a, b): #returns the euclidean distance between 2 nodes
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def astar(graph, start, end, nodes):

    if not graph or start == end:   # Early exit condition: if the graph is empty or the start node is the same as the end node, return either the start node or None.
        return [start] if start == end else None

    open_set = [] #list of nodes na na-discover (neighboring nodes of current node) na i-evaluate or ika-calculate ang distances para malaman saang neighbor node next na pupunta.
    heapq.heappush(open_set, (0, start))
    #Initialize 3 dictionaries - came_from, g-_score, f-score
    came_from = {}  #stores the parent node (kung saan nanggaling na node or previous node) ng each node, para ma-track kung san nanggaling ang nodes once nakarating na sa end node.
    g_score = {node: float('inf') for node in range(len(nodes))} #Initilizae A dictionary to track the cost of the cheapest path from the start node to each node.
    g_score[start] = 0
    f_score = {node: float('inf') for node in range(len(nodes))} #initilize a dictionary to track the estimated total cost (g_score + heuristic) from the start node to the goal node via each node.
    f_score[start] = heuristic(nodes[start], nodes[end])

    while open_set:
        current = heapq.heappop(open_set)[1] # removes and returns the element with the smallest f_score from the open set.

        if current == end: # If nahanap na ang end node, reconstruct the path
            path = [current]
            while current in came_from: # Traverse back using the came_from dictionary to build the path
                current = came_from[current]
                path.append(current)
            path.reverse() #Reverse the path para makuha ang nodes ng path from start to end.
            return path

        visited = set() #create a set of visited nodes, para di maulit

        # Explore the neighbors of the current node
        for neighbor, cost in graph[current]:
            if neighbor in visited:
                continue  # Skip visited nodes

            tentative_g_score = g_score[current] + cost # Calculate the tentative g_score for the neighbor
            if tentative_g_score < g_score[neighbor]: # If the tentative g_score is better than the current g_score for the neighbor, update the g and f scores and the came_from dictionary
                came_from[neighbor] = current  # Store the parent node
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(nodes[neighbor], nodes[end])
                if neighbor not in [i[1] for i in open_set]: # If the neighbor is not in the open set, add it to the open set
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        visited.add(current)  # Mark the current node as visited

    return None

#----------------------------------------------------Initialize Pygame-----------------------------------------------------------
pygame.init()
screen_width, screen_height = 1500, 700
screen = pygame.display.set_mode((screen_width, screen_height))

button_width, button_height = 250, 50
button_x, button_y = 610, 528

closebutton_width, closebutton_height = 40, 50
closebutton_x, closebutton_y = 1400, 20

button_main_width, button_main_height = 119, 40
button_main_x, button_main_y = 20, 257

button_regenerate_width, button_regenerate_height = 119, 40
button_regenerate_x, button_regenerate_y = 20, 307

button_clear_width, button_clear_height = 119, 40
button_clear_x, button_clear_y = 20, 356

# Load the custom font
pygame.font.init()
font_path = 'assets/RoadRage.ttf'
font_size = 39
font = pygame.font.Font(font_path, font_size)
text_color = (205, 162, 115)

pygame.display.set_caption("City Road Gen")
clock = pygame.time.Clock()

segments = 0
angle = 0

def landing_page():
    try:
        landing_image = pygame.image.load('assets/Landing_page.png')
        landing_image = pygame.transform.scale(landing_image, (screen_width, screen_height))

        button_image = pygame.image.load('assets/Get_started.png')
        button_image = pygame.transform.scale(button_image, (button_width, button_height))

    except pygame.error as e:
        print("Error loading image:", e)
        return

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_x <= mouse_pos[0] <= button_x + button_width and \
                        button_y <= mouse_pos[1] <= button_y + button_height:
                    generate_city_page()
                    return

        screen.blit(landing_image, (0, 0))
        screen.blit(button_image, (button_x, button_y))
        pygame.display.flip()

def generate_city_page():
    global segments
    global angle
    pygame.display.set_caption("City Road Gen")
    input_text = ""
    input_angle = ""
    input_active = None  # Track which input field is active
    cursor_visible = True
    cursor_blink_time = 500
    last_blink_time = pygame.time.get_ticks()

    try:
        image = pygame.image.load('assets/Home.png')
        image = pygame.transform.scale(image, (screen_width, screen_height))

        button = pygame.image.load('assets/Generate.png')
        button = pygame.transform.scale(button, (button_width, button_height))

        close_button = pygame.image.load('assets/Close.png')
        close_button = pygame.transform.scale(close_button, (closebutton_width, closebutton_height))

    except pygame.error as e:
        print("Error loading image:", e)
        return

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_x <= mouse_pos[0] <= button_x + button_width and button_y <= mouse_pos[
                    1] <= button_y + button_height:
                    if len(input_text) < 2 or len(input_angle) < 2:
                        print("Please enter both segments and angle.")
                        continue
                    segments = int(input_text)
                    angle = int(input_angle)
                    # Check if angle is valid (90, 60, or 120)
                    if angle not in (90, 60, 120):
                        print("Invalid angle. Angle must be 90, 60, or 120.")
                        continue
                    main()
                elif closebutton_x <= mouse_pos[0] <= closebutton_x + closebutton_width and \
                        closebutton_y <= mouse_pos[1] <= closebutton_y + closebutton_height:
                    print("Close Button Clicked!")
                    landing_page()
                    return
                else:
                    # Check which input field was clicked
                    input_active = None
                    if 957 <= mouse_pos[0] <= 957 + 150 and 404 <= mouse_pos[1] <= 404 + 40:
                        input_active = "segments"
                    elif 892 <= mouse_pos[0] <= 892 + 150 and 457 <= mouse_pos[1] <= 457 + 40:
                        input_active = "angle"

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_text = ""
                    input_angle = ""
                elif event.key == pygame.K_BACKSPACE:
                    if input_active == "segments":
                        input_text = input_text[:-1]
                    elif input_active == "angle":
                        input_angle = input_angle[:-1]
                else:
                    if input_active == "segments":
                        input_text += event.unicode
                    elif input_active == "angle":
                        input_angle += event.unicode

        screen.blit(image, (0, 0))
        screen.blit(button, (button_x, button_y))
        screen.blit(close_button, (closebutton_x, closebutton_y))

        # Render text input for segments at specified position
        input_surface_segments = font.render(input_text, True, text_color)
        screen.blit(input_surface_segments, (957, 404))

        # Render text input for angle at specified position
        input_surface_angle = font.render(input_angle, True, text_color)
        screen.blit(input_surface_angle, (893, 457))

        # Handle cursor blinking
        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time > cursor_blink_time:
            cursor_visible = not cursor_visible
            last_blink_time = current_time

        # Render cursor if input is active and cursor is visible for segments
        if input_active == "segments" and cursor_visible:
            cursor = font.render("|", True, text_color)
            cursor_x = 956 + input_surface_segments.get_width() + 2
            screen.blit(cursor, (cursor_x, 404))

        # Render cursor if input is active and cursor is visible for angle
        if input_active == "angle" and cursor_visible:
            cursor = font.render("|", True, text_color)
            cursor_x = 892 + input_surface_angle.get_width() + 2
            screen.blit(cursor, (cursor_x, 457))

        pygame.display.flip()



def main():
    global scroll_x, scroll_y

    try:
        generate_btn = pygame.image.load('assets/generate-main.png')
        generate_btn = pygame.transform.scale(generate_btn, (button_main_width, button_main_height))

        regenerate_btn = pygame.image.load('assets/regenerate-main.png')
        regenerate_btn = pygame.transform.scale(regenerate_btn, (button_regenerate_width, button_regenerate_height))

        clear_btn = pygame.image.load('assets/clear-main.png')
        clear_btn = pygame.transform.scale(clear_btn, (button_clear_width, button_clear_height))

    except pygame.error as e:
        print("Error loading image:", e)
        return

    # Create a larger surface for drawing
    surface_width, surface_height = 4000, 4000
    surface = pygame.Surface((surface_width, surface_height))
    surface.fill(GREEN)

    scroll_x, scroll_y = 0, 0
    # Set initial scroll position to center the screen on the surface
    scroll_x = (surface_width - screen_width) // 2
    scroll_y = (surface_height - screen_height) // 2

    if angle == 90:
        rules = rules_grid
    elif angle == 60:
        rules = rules_hexagonal
    elif angle == 120:
        rules = rules_triangular
    else:
        rules = rules_grid

    # Generate the L-system and draw the city on the larger surface
    sequence = generate_lsystem(axiom, rules, segments)
    nodes, edges = draw_lsystem(sequence, step_size=21, surface=surface)

    # Connect the dead-end nodes
    if angle == 60 or angle == 120:
        connect_dead_end_nodes_angle(nodes, edges, surface)
    else: connect_dead_end_nodes(nodes, edges, surface)


    # Add white markers at the nodes' coordinates
    for node in nodes:
        pygame.draw.rect(surface, WHITE, (node[0] - 1, node[1] - 1, 1.8, 1.8))

    # Draw buildings or houses
    draw_buildings(surface, nodes, edges)

    #----------------------------------------------------Initialize Shortest Path-----------------------------------------------------------
    # Create adjacency list - a graph where naka-list lahat ng nodes and its neighboring/adjacent nodes and its euclidean distance to that node.
    n_nodes = len(nodes)
    graph = {i: [] for i in range(n_nodes)} #initialize an empty adjacency list for each node
    for (x1, y1), (x2, y2) in edges: #mag-loop sa every edge/line segment
        if (x1, y1) in nodes and (x2, y2) in nodes: #check if yung start and end nodes ng edge ay nasa nodes list
            i = nodes.index((x1, y1))  # find index of starting node
            j = nodes.index((x2, y2)) # find index of end node
            distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) #Calculate the euclidean distance between two nodes using their coordinates
            graph[i].append((j, distance)) # Add and adjacent node and its distance sa adjacency list
            graph[j].append((i, distance))

    #---------------------------------------------------- Game Loop -----------------------------------------------------------

    # Variables for start and end nodes
    start_node = None
    end_node = None
    running = True
    current_color = None

    while running:
        clock.tick(60)  # Limit the frame rate

        for event in pygame.event.get(): # mag-loop sa event/action ni user (e.g. clicks, close window)
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                # Check for button clicks first
                # Generate city with new parameter
                if button_main_x <= mouse_pos[0] <= button_main_x + button_main_width and \
                        button_main_y <= mouse_pos[1] <= button_main_y + button_main_height:
                    generate_city_page()
                    continue  # Skip the rest of the loop to avoid checking for node clicks

                # Regenerate city with the same parameter
                if button_regenerate_x <= mouse_pos[0] <= button_regenerate_x + button_regenerate_width and \
                        button_regenerate_y <= mouse_pos[1] <= button_regenerate_y + button_regenerate_height:
                    main()
                    continue

                # Create New Slate of the Current City
                if button_clear_x <= mouse_pos[0] <= button_clear_x + button_clear_width and \
                        button_clear_y <= mouse_pos[1] <= button_clear_y + button_clear_height:
                    surface.fill(GREEN)
                    start_node = None
                    end_node = None
                    current_color = None
                    nodes, edges = draw_lsystem(sequence, step_size=21, surface=surface)
                    connect_dead_end_nodes(nodes, edges, surface)
                    for node in nodes:
                        pygame.draw.rect(surface, WHITE, (node[0] - 1, node[1] - 1, 1.8, 1.8))
                    draw_buildings(surface, nodes, edges)
                    continue

                # If no button was clicked, check for node clicks
                mouse_x = event.pos[0] + scroll_x
                mouse_y = event.pos[1] + scroll_y
                for i, (x, y) in enumerate(nodes):  # Loop through all nodes to find the one closest to the mouse click.
                    distance = ((x - mouse_x) ** 2 + (y - mouse_y) ** 2) ** 0.5
                    if distance < 10:  # radius kung gaano dapat kalapit ang click para ma-detect kung saang node siya
                        if start_node is None:
                            start_node = i
                            current_color = (
                            random.randint(128, 255), random.randint(128, 255), random.randint(128, 255))
                            pygame.draw.circle(surface, current_color, (x, y), 5)
                            print("Click the end node")
                        elif end_node is None and i != start_node:  # Check if the clicked node is not the same as the start node
                            end_node = i
                            pygame.draw.circle(surface, current_color, (x, y), 5)
                            print(f"Shortest path from node {start_node} to node {end_node}")

                            # Run A* to find the shortest path
                            shortest_path = astar(graph, start_node, end_node, nodes)
                            if shortest_path:
                                print("Shortest path found:", shortest_path)
                                for node in range(
                                        len(shortest_path) - 1):  # Loop to draw line from current node to next node until all the nodes in shortest path is drawn
                                    node_a = nodes[shortest_path[node]]
                                    node_b = nodes[shortest_path[node + 1]]
                                    pygame.draw.line(surface, current_color, node_a, node_b, 2)
                                print("Number of segments of shortest path: ", (len(shortest_path)-1))

                            # Reset start_node and end_node to None for the next selection
                            start_node = None
                            end_node = None

                        else:
                            print("Start and end nodes cannot be the same. Please click another node for the end node.")
                        break

            elif event.type == pygame.MOUSEWHEEL:
                scroll_x += event.x * 50
                scroll_y += event.y * 50

                # Clamp scroll_x and scroll_y within the bounds of the surface
                scroll_x = max(min(scroll_x, surface_width - screen_width), 0)
                scroll_y = max(min(scroll_y, surface_height - screen_height), 0)

        # Draw the portion of the surface onto the screen
        screen_rect = pygame.Rect(scroll_x, scroll_y, screen_width, screen_height)
        surface_sub = surface.subsurface(screen_rect)
        scaled_surface = pygame.transform.scale(surface_sub, (screen_width, screen_height))
        screen.blit(scaled_surface, (0, 0))
        screen.blit(generate_btn, (button_main_x, button_main_y))
        screen.blit(regenerate_btn, (button_regenerate_x, button_regenerate_y))
        screen.blit(clear_btn, (button_clear_x, button_clear_y))

        pygame.display.flip()

    pygame.quit()

landing_page()
generate_city_page()
main()
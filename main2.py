import pygame
import random
import math
import heapq
import pygame.font

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (1, 50, 32)


# Define the axiom and production rules
axiom = "X"
rules = {
    "X": [
        "F[+X]F[-X]FX",
        "F[+X]F[-X]+X",
        "F-[[X]+X]+F[+FX]-X",
        "F[X]F[+X]+F[-X]X",
        "F[+X][-X]F+F[X]+F[+FX]-X",  # New rule for curved paths
        "FF[+X][+X]FF[-X][-X]",  # New rule for intersections
        "F[X]+[X]+F-F"  # New rule for branching paths
    ],
    "F": [
        "FF",
        "F[+F]F[-F]F",
        "F[+FF][-FF]F"  # New rule for curved paths
    ],
}

# Define the function to draw the l-system
def draw_lsystem(sequence, step_size, surface):
    stack = []
    nodes = []
    edges = []
    x, y = surface.get_width() // 2, surface.get_height() // 2
    angle = 90  # Start facing up

    for char in sequence:
        if char == "F":
            dx = step_size * math.cos(angle * math.pi / 180)
            dy = step_size * math.sin(angle * math.pi / 180)
            new_x, new_y = x + dx, y + dy
            pygame.draw.line(surface, WHITE, (x, y), (new_x, new_y), 2)
            pygame.draw.circle(surface, BLUE, (x, y), 2)
            nodes.append((new_x, new_y))
            edges.append(((x, y), (new_x, new_y)))
            x, y = new_x, new_y
        elif char == "+":
            angle += 90
        elif char == "-":
            angle -= 90
        elif char == "[":
            stack.append((x, y, angle))
        elif char == "]":
            x, y, angle = stack.pop()

    return nodes, edges

# Generate the string of L-system starting with the axiom
def generate_lsystem(axiom, rules, iterations):
    sequence = axiom
    for _ in range(iterations):
        next_sequence = ""
        for char in sequence:
            if char in rules:
                next_sequence += random.choice(rules[char])
            else:
                next_sequence += char
        sequence = next_sequence
        print(sequence)
    return sequence

def heuristic(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def astar(graph, start, end, nodes):

    if not graph or start == end:
        return [start] if start == end else None

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {node: float('inf') for node in range(len(nodes))}
    g_score[start] = 0
    f_score = {node: float('inf') for node in range(len(nodes))}
    f_score[start] = heuristic(nodes[start], nodes[end])

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == end:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        visited = set()

        for neighbor, cost in graph[current]:
            if neighbor in visited:
                continue

            tentative_g_score = g_score[current] + cost
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(nodes[neighbor], nodes[end])
                if neighbor not in [i[1] for i in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        visited.add(current)

    return None

# Set up the screen

screen_width, screen_height = 1500, 700
screen = pygame.display.set_mode((screen_width, screen_height))

button_width, button_height = 250, 50
button_x, button_y = 610, 528

closebutton_width, closebutton_height = 40, 50
closebutton_x, closebutton_y = 1400, 20

# Load the custom font
pygame.font.init()
font_path = 'assets/RoadRage.ttf'
font_size = 39
font = pygame.font.Font(font_path, font_size)
text_color = (205, 162, 115)

def landing_page():
    pygame.display.set_caption("City Road Gen")
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
                    print("Button Clicked!")
                    generate_city()
                    return

        screen.blit(landing_image, (0, 0))
        screen.blit(button_image, (button_x, button_y))
        pygame.display.flip()

def generate_city():
    pygame.display.set_caption("City Road Gen")
    input_text = ""
    input_active = False
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
                if button_x <= mouse_pos[0] <= button_x + button_width and \
                        button_y <= mouse_pos[1] <= button_y + button_height:
                    print("Generate Button Clicked!")
                    iterations = int(input_text)
                    main(iterations)
                    # Remove the `return` statement here
                elif closebutton_x <= mouse_pos[0] <= closebutton_x + closebutton_width and \
                        closebutton_y <= mouse_pos[1] <= closebutton_y + closebutton_height:
                    print("Close Button Clicked!")
                    landing_page()
                    return
                else:
                    input_active = not input_active  # Toggle input activation
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        screen.blit(image, (0, 0))
        screen.blit(button, (button_x, button_y))
        screen.blit(close_button, (closebutton_x, closebutton_y))

        # Render text input at specified position
        input_surface = font.render(input_text, True, text_color)
        screen.blit(input_surface, (925, 440))

        # Handle cursor blinking
        current_time = pygame.time.get_ticks()
        if current_time - last_blink_time > cursor_blink_time:
            cursor_visible = not cursor_visible
            last_blink_time = current_time

        # Render cursor if input is active and cursor is visible
        if input_active and cursor_visible:
            cursor = font.render("|", True, text_color)
            cursor_x = 920 + input_surface.get_width() + 2
            screen.blit(cursor, (cursor_x, 440))

        pygame.display.flip()

def main(iterations):
# Initialize Pygame
    pygame.display.set_caption("L-System City Generator")
    clock = pygame.time.Clock()
# Create a larger surface for drawing
    surface_width, surface_height = 2500, 2500
    surface = pygame.Surface((surface_width, surface_height))
    surface.fill(GREEN)

    scroll_x, scroll_y = 0, 0
    # Set initial scroll position to center the screen on the surface
    scroll_x = (surface_width - screen_width) // 2
    scroll_y = (surface_height - screen_height) // 2

    # Generate the L-system and draw the city on the larger surface
    sequence = generate_lsystem(axiom, rules, iterations)
    nodes, edges = draw_lsystem(sequence, step_size=15, surface=surface)

    # Initialize Shortest Path
    n_nodes = len(nodes)
    graph = {i: [] for i in range(n_nodes)}
    for (x1, y1), (x2, y2) in edges:
        if (x1, y1) in nodes and (x2, y2) in nodes:
            i = nodes.index((x1, y1))
            j = nodes.index((x2, y2))
            distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            graph[i].append((j, distance))
            graph[j].append((i, distance))

    # Variables for start and end nodes
    start_node = None
    end_node = None

    loop_start_node = None
    running = True

    while running:
        clock.tick(60)  # Limit the frame rate

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print("clicked")
                mouse_x = event.pos[0] + scroll_x
                mouse_y = event.pos[1] + scroll_y
                for i, (x, y) in enumerate(nodes):
                    distance = ((x - mouse_x) ** 2 + (y - mouse_y) ** 2) ** 0.5
                    if distance < 10:
                        if start_node is None:
                            start_node = i
                            pygame.draw.circle(surface, RED, (x, y), 5)
                            print("Click the end node")
                        elif end_node is None and i != start_node:
                            end_node = i
                            pygame.draw.circle(surface, RED, (x, y), 5)
                            print(f"Shortest path from node {start_node} to node {end_node}")

                            shortest_path = astar(graph, start_node, end_node, nodes)
                            if shortest_path:
                                print("Shortest path found:", shortest_path)
                                for node in range(len(shortest_path) - 1):
                                    node_a = nodes[shortest_path[node]]
                                    node_b = nodes[shortest_path[node + 1]]
                                    pygame.draw.line(surface, RED, node_a, node_b, 2)

                            start_node = None
                            end_node = None

                        else:
                            print("Start and end nodes cannot be the same. Please click another node for the end node.")
                        break

            elif event.type == pygame.MOUSEWHEEL:
                scroll_x += event.x * 50
                scroll_y += event.y * 50
                scroll_x = max(min(scroll_x, surface_width - screen_width), 0)
                scroll_y = max(min(scroll_y, surface_height - screen_height), 0)

        screen_rect = pygame.Rect(scroll_x, scroll_y, screen_width, screen_height)
        surface_sub = surface.subsurface(screen_rect)
        scaled_surface = pygame.transform.scale(surface_sub, (screen_width, screen_height))
        screen.blit(scaled_surface, (0, 0))

        pygame.display.flip()

    pygame.quit()

pygame.init()
landing_page()
generate_city()
main(iterations)

# Quit Pygame
pygame.quit()
import pygame
import random
import math
import heapq

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (61, 114, 40)
GRAY = (65, 65, 65)  # Define a gray color for buildings

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
        "F[X]+[X]+F-F",  # New rule for branching paths
        "FX+F+FX-F-F"  # New rule for creating loops
    ],
    "F": [
        "FF",
        "F[+F]F[-F]F",
        "F[+FF][-FF]F"  # New rule for curved paths
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
        if area > 0:
            building_size = int(math.sqrt(area) * 0.2)  # Scale down building size to fit within the polygon

            # Compute the bounding box for the polygon
            min_x = min(p[0] for p in polygon)
            max_x = max(p[0] for p in polygon)
            min_y = min(p[1] for p in polygon)
            max_y = max(p[1] for p in polygon)

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
                    pygame.draw.rect(surface, BLACK, building_rect)
                    break  # Building successfully placed
                attempts += 1

#---------------------------------------------------- Functions: Connecting Dead End Nodes  -----------------------------------------------------------
def find_closest_node(node, nodes, edges):
    node_x, node_y = node
    min_distance = float('inf')
    closest_node = None

    for other_node in nodes:
        if other_node != node:
            other_x, other_y = other_node
            distance = math.sqrt((node_x - other_x) ** 2 + (node_y - other_y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_node = other_node

    return closest_node, min_distance

def is_dead_end_node(node, graph):
    connections = graph[node]
    return len(connections) <= 1  # Node with 0 or 1 connection is considered a dead-end

def connect_dead_ends(nodes, edges, surface):
    n_nodes = len(nodes)
    graph = {i: set() for i in range(n_nodes)}  # Use a set to store connected nodes
    for (x1, y1), (x2, y2) in edges:
        if (x1, y1) in nodes and (x2, y2) in nodes:
            i = nodes.index((x1, y1))
            j = nodes.index((x2, y2))
            graph[i].add(j)
            graph[j].add(i)

    dead_end_nodes = [node for node in range(n_nodes) if len(graph[node]) <= 1]

    for dead_end_node in dead_end_nodes:
        unconnected_nodes = [n for n in range(n_nodes) if n not in graph[dead_end_node]]
        if unconnected_nodes:
            closest_node_index, distance = find_closest_node_from_set(nodes[dead_end_node], [nodes[n] for n in unconnected_nodes])
            if closest_node_index is not None and distance <= 5 * 15:  # Check if the distance is less than or equal to 5 steps
                graph[dead_end_node].add(closest_node_index)
                graph[closest_node_index].add(dead_end_node)
                #pygame.draw.line(surface, RED, nodes[dead_end_node], nodes[closest_node_index], 1)

    return graph

def find_closest_node_from_set(node, node_set):
    node_x, node_y = node
    min_distance = float('inf')
    closest_node_index = None

    for i, other_node in enumerate(node_set):
        other_x, other_y = other_node
        distance = math.sqrt((node_x - other_x) ** 2 + (node_y - other_y) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_node_index = i

    return closest_node_index, min_distance

#---------------------------------------------------- Functions: Creating L-System City  -----------------------------------------------------------

# Define the function to draw the l-system
def draw_lsystem(sequence, step_size, surface):
    stack = []  # Storage of the current direction and angle of the turtle to remember when backtracking
    nodes = []  # Storage of the nodes (each move forward represents 1 node)
    edges = []
    x, y = surface.get_width() // 2, surface.get_height() // 2
    angle = 90  # Start facing up

    for char in sequence:
        if char == "F":  # Move forward
            dx = step_size * math.cos(angle * math.pi / 180)
            dy = step_size * math.sin(angle * math.pi / 180)
            new_x, new_y = x + dx, y + dy

            # Draw a thicker line for the road
            pygame.draw.line(surface, GRAY, (x, y), (new_x, new_y), 7)  # Change the line thickness to 5

            nodes.append((new_x, new_y))  # Add the node to the node list
            edges.append(((x, y), (new_x, new_y)))
            x, y = new_x, new_y

        elif char == "+":  # Rotate turtle 90 degrees right
            angle += 90
        elif char == "-":  # Rotate turtle 90 degrees left
            angle -= 90
        elif char == "[":  # Push current position and angle onto the stack (start of a new branch)
            stack.append((x, y, angle))
        elif char == "]":  # Pop position and angle from the stack (return to the previous branch)
            x, y, angle = stack.pop()

    # Add white markers at the nodes' coordinates
    for node in nodes:
        pygame.draw.rect(surface, WHITE, (node[0] - 1, node[1] - 1, 2, 2))

    return nodes, edges

# Generate the string of L-system starting with the axiom
def generate_lsystem(axiom, rules, iterations):
    sequence = axiom # start the L-System sequence with the axiom
    for _ in range(iterations): # loop kung ilan ang iteration
        next_sequence = ""
        for char in sequence: # mag-loop sa sequence
            if char in rules: # if ang character na nasa sequence ay key sa prdouction rule (X or F), then mamili ng random rule sa key na yon.
                next_sequence += random.choice(rules[char])
            else:             # if ang character ay hindi key, like ( +, -, [, ], then skip)
                next_sequence += char
        sequence = next_sequence
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

# Prompt the user for the number of iterations
iterations = int(input("Enter the number of iterations (1-10): "))

#----------------------------------------------------Initialize Pygame-----------------------------------------------------------
pygame.init()
screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("L-System City Generator")
clock = pygame.time.Clock()

# Create a larger surface for drawing
surface_width, surface_height = 3000, 3000
surface = pygame.Surface((surface_width, surface_height))
surface.fill(GREEN)

scroll_x, scroll_y = 0, 0
# Set initial scroll position to center the screen on the surface
scroll_x = (surface_width - screen_width) // 2
scroll_y = (surface_height - screen_height) // 2

def main():
    #----------------------------------------------------Generate City-----------------------------------------------------------
    global scroll_x, scroll_y

    # Generate the L-system and draw the city on the larger surface
    sequence = generate_lsystem(axiom, rules, iterations)
    nodes, edges = draw_lsystem(sequence, step_size=15, surface=surface)

    # Draw buildings or houses
    draw_buildings(surface, nodes, edges)

    # Connect dead-end nodes
    graph = connect_dead_ends(nodes, edges, surface)

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

    loop_start_node = None
    running = True

    while running:
        clock.tick(60)  # Limit the frame rate

        for event in pygame.event.get(): # mag-loop sa event/action ni user (e.g. clicks, close window)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print("clicked")
                mouse_x = event.pos[0] + scroll_x
                mouse_y = event.pos[1] + scroll_y
                for i, (x, y) in enumerate(nodes):  # Loop through all nodes to find the one closest to the mouse click.
                    distance = ((x - mouse_x) ** 2 + (y - mouse_y) ** 2) ** 0.5
                    if distance < 10:  # radius kung gaano dapat kalapit ang click para ma-detect kung saang node siya
                        if start_node is None:
                            start_node = i
                            pygame.draw.circle(surface, RED, (x, y), 5)
                            print("Click the end node")
                        elif end_node is None and i != start_node:  # Check if the clicked node is not the same as the start node
                            end_node = i
                            pygame.draw.circle(surface, RED, (x, y), 5)
                            print(f"Shortest path from node {start_node} to node {end_node}")

                            # Run A* to find the shortest path
                            shortest_path = astar(graph, start_node, end_node, nodes)
                            if shortest_path:
                                print("Shortest path found:", shortest_path)
                                for node in range(len(shortest_path) - 1): #Loop to draw line from current node to next node until all the nodes in shortest path is drawn
                                    node_a = nodes[shortest_path[node]]
                                    node_b = nodes[shortest_path[node + 1]]
                                    pygame.draw.line(surface, RED, node_a, node_b, 2)

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

        pygame.display.flip()

    pygame.quit()

main()
import pygame
import random
import math

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
    stack = [] # storage of the current direction and angle of the turtle para ma-remember kapag babalikan.
    nodes = [] # storage of the nodes (each move forward represents 1 node)
    x, y = surface.get_width() // 2, surface.get_height() // 2
    angle = 90  # Start facing up

    for char in sequence:
        if char == "F": # move forward
            dx = step_size * math.cos(angle * math.pi / 180)
            dy = step_size * math.sin(angle * math.pi / 180)
            new_x, new_y = x + dx, y + dy
            pygame.draw.line(surface, WHITE, (x, y), (new_x, new_y), 2)
            pygame.draw.circle(surface, BLUE, (x, y), 2)
            nodes.append((new_x, new_y)) # add the node to the node list
            x, y = new_x, new_y
        elif char == "+": # Rotate turtle 90 degrees right
            angle += 90
        elif char == "-": # Rotate turtle 90 degrees left
            angle -= 90
        elif char == "[": # Push current position and angle onto the stack ; This means, the turtle will start a new branch (start of a recursion). Ino-note niya para mabalikan
            stack.append((x, y, angle))
        elif char == "]": # Pop position and angle from the stack, para babalik siya sa first position ng branch
            x, y, angle = stack.pop()

    return nodes

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

# Prompt the user for the number of iterations
iterations = int(input("Enter the number of iterations (1-10): "))

# Initialize Pygame
pygame.init()
screen_width, screen_height = 1000, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("L-System City Generator")
clock = pygame.time.Clock()

# Create a larger surface for drawing
surface_width, surface_height = 1500, 1500
surface = pygame.Surface((surface_width, surface_height))
surface.fill(GREEN)

# Generate the L-system and draw the city on the larger surface
sequence = generate_lsystem(axiom, rules, iterations)
nodes = draw_lsystem(sequence, step_size=15, surface=surface)

# Variables for start and end nodes
start_node = None
end_node = None

scroll_x, scroll_y = 0, 0
# Set initial scroll position to center the screen on the surface
scroll_x = (surface_width - screen_width) // 2
scroll_y = (surface_height - screen_height) // 2

# Game loop
running = True
while running:
    clock.tick(60)  # Limit the frame rate

    for event in pygame.event.get(): # mag-loop sa event/action ni user (e.g. clicks, close window)
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("clicked")
            mouse_x, mouse_y = event.pos # get the position of the mouse click
            for i, (x, y) in enumerate(nodes): # Loop through all nodes to find the one closest to the mouse click.
                distance = ((x - mouse_x + scroll_x) ** 2 + (y - mouse_y + scroll_y) ** 2) ** 0.5
                if distance < 10:  # radius kung gaano dapat kalapit ang click para ma-detect kung saang node siya
                    if start_node is None:
                        start_node = i
                        pygame.draw.circle(surface, RED, (x, y), 5)
                        print("Click the end node")
                    elif end_node is None and i != start_node:  # Check if the clicked node is not the same as the start node
                        end_node = i
                        pygame.draw.circle(surface, RED, (x, y), 5)
                        # Implement your shortest path finding algorithm here
                        print(f"Shortest path from node {start_node} to node {end_node}")
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
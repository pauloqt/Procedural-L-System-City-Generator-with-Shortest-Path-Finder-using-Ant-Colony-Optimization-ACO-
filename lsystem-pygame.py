import pygame
import random
import math

# L-system parameters
main_axiom = "[F]--F"
main_rules = {
    'F': "FFF[+FF]FFF|",
}

branching_axiom = "BB"
branching_rules = {
    "B": [
        "BB", "+BB[BB]", "-BB[BB]"
    ],
}

# rules para sa mag co-connect ng 2nd generation
connecting_axiom = "C"
connecting_rules = {
    "C": [
        "CCC", "+CC[CC]", "-CC[CC]", "CC[+CC]C",
        "CC[+A]C[-A]CC",
        "C[+A]C[-A]+C",
        # "C-[[A]+A]+C[+A]-CC",
        # "CC[+A][+A]CC[-A][-A]C",  # New rule for intersections
    ],
}

depth_factor = 0.5
marked_positions = [] # marker para sa branching
marked_branching_positions = [] # marker para sa connecting ng road
#white = (255, 255, 255)
green = (61, 114, 40)
black = (0, 0, 0)


# Function to generate L-system string
def generate_l_system(main_axiom, main_rules, iterations):
    current_string = main_axiom
    for i in range(iterations):
        next_string = ""
        for char in current_string:
            if char in main_rules:
                next_string += main_rules[char]
            else:
                next_string += char
        current_string = next_string
        print(current_string)
    return current_string

# Function to generate branching L-system string
def generate_branching_lsystem(axiom, rules, iterations):
    current_string = axiom
    for i in range(iterations):
        next_string = ""
        for char in current_string:
            if char in rules:
                if isinstance(rules[char], list):
                    next_string += random.choice(rules[char])
                else:
                    next_string += rules[char]
            else:
                next_string += char
        current_string = next_string
        print(current_string)
    return current_string

def generate_connecting_lsystem(connecting_axiom, connecting_rules, iterations):
    current_string = connecting_axiom
    for i in range(iterations):
        next_string = ""
        for char in current_string:
            if char in connecting_rules:
                if isinstance(connecting_rules[char], list):
                    next_string += random.choice(connecting_rules[char])
                else:
                    next_string += connecting_rules[char]
            else:
                next_string += char
        current_string = next_string
        print(current_string)
    return current_string


def draw_l_system(screen, instructions, angle, length, depth_factor, mark=False):
    stack = []
    global marked_positions
    x, y = 800, 600
    heading = 0
    i = 0

    if len(marked_positions) == 0:
        line_width = 2
    else:
        line_width = 1

    while i < len(instructions):
        char = instructions[i]
        if char == 'F':
            new_x = x + length * math.cos(math.radians(heading))
            new_y = y - length * math.sin(math.radians(heading))
            if char == 'F':
                pygame.draw.line(screen, (255, 255, 255), (x, y), (new_x, new_y),
                                 line_width)
            else:
                pygame.draw.line(screen, (255, 255, 255), (x, y), (new_x, new_y), 1)
            x, y = new_x, new_y
        elif char == '+':
            heading -= angle
        elif char == '-':
            heading += angle
        elif char == '[':
            stack.append((x, y, heading))
        elif char == ']':
            x, y, heading = stack.pop()
        elif char == '|': # maglalagay ng line pero naka-depende ang size sa na-compute
            depth_length = length * len(stack) * depth_factor
            new_x = x + depth_length * math.cos(math.radians(heading))
            new_y = y - depth_length * math.sin(math.radians(heading))
            if len(marked_positions) == 0:  # Draw thicker lines only for the first generation
                pygame.draw.line(screen, (255, 255, 255), (x, y), (new_x, new_y), 3)  # Thicker lines for the first generation
            else:
                pygame.draw.line(screen, (255, 255, 255), (x, y), (new_x, new_y), 2)
            x, y = new_x, new_y

        if i + 3 < len(instructions) and instructions[i:i + 9] == '[+FF]FFF|':
            marked_positions.append((x, y, heading))
            i += 3

        i += 1

    if len(marked_positions) == 0:
        pygame.draw.line(screen, (255, 255, 255), (x, y), (x, y), 1)  # Reset line width to default

    return marked_positions

def draw_branching_l_system(screen, instructions, angle, length, depth_factor, x, y, heading):
    stack = []
    i = 0
    global marked_branching_position
    markers = {}

    while i < len(instructions):
        char = instructions[i]
        if char == 'B' or char == 'C':
            new_x = x + length * math.cos(math.radians(heading))
            new_y = y - length * math.sin(math.radians(heading))
            pygame.draw.line(screen, (255, 255, 255), (x, y), (new_x, new_y), 1)
            x, y = new_x, new_y
        elif char == 'A': # mag fo-forward pero hindi maglalagay ng line
            new_x = x + length * math.cos(math.radians(heading))
            new_y = y - length * math.sin(math.radians(heading))
            x, y = new_x, new_y
        elif char == '+':
            heading -= angle
        elif char == '-':
            heading += angle
        elif char == '[':
            stack.append((x, y, heading))
        elif char == ']':
            x, y, heading = stack.pop()
        elif char == '|':
            heading += angle
            depth_length = length * len(stack) * depth_factor
            new_x = x + depth_length * math.cos(math.radians(heading))
            new_y = y - depth_length * math.sin(math.radians(heading))
            pygame.draw.line(screen, (255, 255, 255), (x, y), (new_x, new_y), 1)
            x, y = new_x, new_y

        if i + 2 < len(instructions) and instructions[i:i + 9] == 'BB+BB[BB]':
            marked_branching_positions.append((x, y, heading))
            i += 2
        i += 1

    if len(marked_positions) == 0:
        pygame.draw.line(screen, (255, 255, 255), (x, y), (x, y), 1)  # Reset line width to default

    return marked_branching_positions

# Main function
def main():
    global marked_positions
    global marked_branching_positions

    pygame.init()
    screen = pygame.display.set_mode((1600, 900))
    pygame.display.set_caption("L-System")
    screen.fill(green)

    num_iterations = int(input("Enter the number of iterations (1-10): "))

    # if no. iterations ay equal sa input babawasan niya yung iteration
    if num_iterations == 3:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations)
    elif num_iterations == 4 or num_iterations == 5:
        main_instructions = generate_l_system(main_axiom, main_rules, int(num_iterations - 0.1))
    elif num_iterations == 6 or num_iterations == 7:
        main_instructions = generate_l_system(main_axiom, main_rules, int(num_iterations - 1.3))
    elif num_iterations == 8 or num_iterations == 9:
        main_instructions = generate_l_system(main_axiom, main_rules, int(num_iterations - 2.0))
    elif num_iterations == 10:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations // 5)
    else:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations)

    print(main_instructions)

    # Draw main L-system
    step_size = 10
    random_angle_main = random.uniform(45, 90)
    marked_positions = draw_l_system(screen, main_instructions, random_angle_main, step_size, depth_factor, mark=True)

    # Generate and draw branching using the main road marker
    if marked_positions:
        for marked_position in marked_positions:
            x, y, heading = marked_position
            angle_branching = 90
            rand_number = random.uniform(3.5, 5.5)

            # if no. iterations ay equal sa input babawasan niya yung iteration
            if num_iterations == 3:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 0.1))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 4:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 1.5))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 5:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 2.5))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 6:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 3.5))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 7 or num_iterations == 8 or num_iterations == 9:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - rand_number))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 10:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - rand_number))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            else:
                for i in range(num_iterations):
                    branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, i + 1)
                    draw_branching_l_system(screen, branching_instructions, angle_branching,
                                                     step_size * 2, depth_factor, x, y, heading)

    # Generate and draw another branching using the previous branching marker
    if marked_branching_positions:
        for branching in marked_branching_positions:
            x, y, heading = branching

            angle_branching = 90
            rand_number = random.uniform(3.5, 5.5)

            if num_iterations == 3:
                branching_instructions = generate_connecting_lsystem(connecting_axiom, connecting_rules,
                                                                    int(num_iterations - 0.1))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 4:
                branching_instructions = generate_connecting_lsystem(connecting_axiom, connecting_rules,
                                                                    int(num_iterations - 1.5))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 5:
                branching_instructions = generate_connecting_lsystem(connecting_axiom, connecting_rules,
                                                                    int(num_iterations - 2.5))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 6:
                branching_instructions =generate_connecting_lsystem(connecting_axiom, connecting_rules,
                                                                    int(num_iterations - 4.0))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 7 or num_iterations == 8 or num_iterations == 9:
                branching_instructions = generate_connecting_lsystem(connecting_axiom, connecting_rules,
                                                                    int(num_iterations - rand_number))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            elif num_iterations == 10:
                branching_instructions = generate_connecting_lsystem(connecting_axiom, connecting_rules,
                                                                    int(num_iterations - rand_number))
                draw_branching_l_system(screen, branching_instructions, angle_branching,
                                        step_size * 2, depth_factor, x, y, heading)
            else:
                for i in range(num_iterations):
                    branching_instructions = generate_connecting_lsystem(connecting_axiom, connecting_rules, i + 1)
                    draw_branching_l_system(screen, branching_instructions, angle_branching,
                                            step_size * 2, depth_factor, x, y, heading)

    # Function for the random buildings
    # def draw_random_buildings(screen, positions, num_rectangles):
    #     for pos in positions:
    #         for _ in range(num_rectangles):
    #             # Random size
    #             width = random.uniform(5, 8)
    #             height = random.uniform(5, 8)
    #
    #             # Draw the rectangle at the specified position
    #             x, y = pos
    #             x += 50
    #             y += 50
    #             pygame.draw.rect(screen, black, (x, y, width, height))
    #
    # # Draw buildings at marked_branching_position
    # if marked_positions:
    #     positions = [(pos[0], pos[1]) for pos in marked_positions]
    #     draw_random_buildings(screen, positions, num_iterations - 1)

    # Print marked positions
    # print("Marked Positions:", marked_positions)
    # print("Marked Branching Positions:", marked_branching_positions)

    # Main event loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()

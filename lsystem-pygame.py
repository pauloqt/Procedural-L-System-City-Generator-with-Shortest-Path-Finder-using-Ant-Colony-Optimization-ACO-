import pygame
import random
import math

# L-system parameters
main_axiom = "[F]--F"
main_rules = {
    'F': "FFF[+FF]FFF|",
}

branching_axiom = "A"
branching_rules = {
    "A": [
        "BB[+AA]B[-AB]|BA", "B[+AB]BA[-A]+B+",
        "B-[[AB]+A]+B[+BA]-A",

        "BB[+AB][+A]|BB[-AB][-A]+",  # New rule for intersections
        "BB+AAB+"
    ],
    "B": [
        "BB",
        "B[+B]B[-B]B",
        "B[+BB][-BB]B",  # New rule for curved paths
        "-BA-B"
    ],
}



depth_factor = 0.5
string_placeholder = []
marked_positions = []

# Function to generate L-system string
def generate_l_system(axiom, rules, iterations):
    current_string = axiom
    for i in range(iterations):
        next_string = ""
        for char in current_string:
            if char in rules:
                next_string += rules[char]
            else:
                next_string += char
        current_string = next_string
        string_placeholder.append(current_string)
        print(f"Iteration {i + 1}: {current_string}")
    return current_string

# Function to generate branching L-system string
def generate_branching_lsystem(axiom, branching_rules, iterations):
    current_string = axiom
    for i in range(iterations):
        next_string = ""
        for char in current_string:
            if char in branching_rules:
                if isinstance(branching_rules[char], list):
                    next_string += random.choice(branching_rules[char])
                else:
                    next_string += branching_rules[char]
            else:
                next_string += char
        current_string = next_string
        string_placeholder.append(current_string)
        print(f"Iteration {i + 1}: {current_string}")
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
                pygame.draw.line(screen, (0, 0, 0), (x, y), (new_x, new_y),
                                 line_width)
            else:
                pygame.draw.line(screen, (0, 0, 0), (x, y), (new_x, new_y), 1)
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
            depth_length = length * len(stack) * depth_factor
            new_x = x + depth_length * math.cos(math.radians(heading))
            new_y = y - depth_length * math.sin(math.radians(heading))
            if len(marked_positions) == 0:  # Draw thicker lines only for the first generation
                pygame.draw.line(screen, (0, 0, 0), (x, y), (new_x, new_y), 3)  # Thicker lines for the first generation
            else:
                pygame.draw.line(screen, (0, 0, 0), (x, y), (new_x, new_y), 2)
            x, y = new_x, new_y

        if i + 2 < len(instructions) and instructions[i:i + 9] == '[+FF]FFF|':
            marked_positions.append((x, y, heading))
            i += 2

        i += 1

    if len(marked_positions) == 0:
        pygame.draw.line(screen, (0, 0, 0), (x, y), (x, y), 1)  # Reset line width to default

    return marked_positions

def draw_branching_l_system(screen, instructions, angle, length, depth_factor, x, y, heading):
    stack = []
    i = 0

    while i < len(instructions):
        char = instructions[i]
        if char == 'B':
            new_x = x + length * math.cos(math.radians(heading))
            new_y = y - length * math.sin(math.radians(heading))
            pygame.draw.line(screen, (0, 0, 0), (x, y), (new_x, new_y), 1)
            x, y = new_x, new_y
        elif char == 'A':
            heading -= angle
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
            pygame.draw.line(screen, (0, 0, 0), (x, y), (new_x, new_y), 1)
            x, y = new_x, new_y

        i += 1

# Main function
def main():
    global marked_positions

    pygame.init()
    screen = pygame.display.set_mode((1600, 900))
    pygame.display.set_caption("L-System")
    screen.fill((255, 255, 255))

    num_iterations = int(input("Enter the number of iterations (1-10): "))

    if num_iterations == 3:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations)
    elif num_iterations == 4 or num_iterations == 5:
        main_instructions = generate_l_system(main_axiom, main_rules, int(num_iterations - 0.3))
    elif num_iterations == 6 or num_iterations == 7:
        main_instructions = generate_l_system(main_axiom, main_rules, int(num_iterations - 1.3))
    elif num_iterations == 8 or num_iterations == 9:
        main_instructions = generate_l_system(main_axiom, main_rules, int(num_iterations - 2.4))
    elif num_iterations == 10:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations // 5)
    else:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations)

    print(main_instructions)

    # Draw main L-system
    random_angle_main = random.uniform(45, 90)
    random_length_main = random.uniform(10, 15)
    marked_positions = draw_l_system(screen, main_instructions, random_angle_main, random_length_main, depth_factor, mark=True)

    if marked_positions:
        for marked_position in marked_positions:
            x, y, heading = marked_position
            # x += -30
            # y -= 60
            random_angle_branching = random.uniform(90, 90)
            rand_number = random.uniform(3.5, 7.9)
            concatenated_instructions = ""

            if num_iterations == 3:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 0.3))
                random_length_branching = random.uniform(11, 25)  # Adjust the length range if needed
                draw_branching_l_system(screen, branching_instructions, random_angle_branching,
                                        random_length_branching, depth_factor, x, y, heading)
            elif num_iterations == 4:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 1.9))
                random_length_branching = random.uniform(11, 25)  # Adjust the length range if needed
                draw_branching_l_system(screen, branching_instructions, random_angle_branching,
                                        random_length_branching, depth_factor, x, y, heading)
            elif num_iterations == 5 or num_iterations == 6:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 3.0))
                random_length_branching = random.uniform(11, 25)  # Adjust the length range if needed
                draw_branching_l_system(screen, branching_instructions, random_angle_branching,
                                        random_length_branching, depth_factor, x, y, heading)
            elif num_iterations == 7 or num_iterations == 8 or num_iterations == 9:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - rand_number))
                random_length_branching = random.uniform(11, 25)  # Adjust the length range if needed
                draw_branching_l_system(screen, branching_instructions, random_angle_branching,
                                        random_length_branching, depth_factor, x, y, heading)
            elif num_iterations == 10:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - rand_number))
                random_length_branching = random.uniform(11, 25)  # Adjust the length range if needed
                draw_branching_l_system(screen, branching_instructions, random_angle_branching,
                                        random_length_branching, depth_factor, x, y, heading)
            else:
                for i in range(num_iterations):
                    branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, i + 1)
                    concatenated_instructions += branching_instructions

                    random_angle_branching = random.uniform(90, 90)
                    random_length_branching = random.uniform(11, 25)  # Adjust the length range if needed
                    draw_branching_l_system(screen, concatenated_instructions, random_angle_branching,
                                                     random_length_branching, depth_factor, x, y, heading)


    # Print marked positions
    print("Marked Positions:", marked_positions)

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

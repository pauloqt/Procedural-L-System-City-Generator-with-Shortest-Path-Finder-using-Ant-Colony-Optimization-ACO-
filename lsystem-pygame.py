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
        "BB", "+BB[BB]", "-BB[BB]",
    ],
}

# rules para sa mag co-connect ng 2nd generation
connecting_axiom = "CD"
connecting_rules = {
    "C": [
        "CC", "CC[+CC]", "CC[-CC]",
    ],
    "D": [
        "-FCD"
    ]
}

depth_factor = 0.5
marked_positions = [] # marker para sa branching
marked_branching_positions = [] # marker para sa connecting ng road
road_segments = []
BG_COLOR = (61, 114, 40)
ROAD_COLOR = (255, 255, 255)
BLACK = (0, 0, 0)
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900


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


def draw_l_system(screen, instructions, start_pos, angle, length, depth_factor, mark=False):
    stack = []
    x, y = start_pos
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
                pygame.draw.line(screen, ROAD_COLOR, (x, y), (new_x, new_y),
                                 line_width)
            else:
                pygame.draw.line(screen, ROAD_COLOR, (x, y), (new_x, new_y), 1)
            road_segments.append(((x, y), (new_x, new_y)))
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
                pygame.draw.line(screen, ROAD_COLOR, (x, y), (new_x, new_y), 3)  # Thicker lines for the first generation
            else:
                pygame.draw.line(screen, ROAD_COLOR, (x, y), (new_x, new_y), 2)
            x, y = new_x, new_y

        # dapat ang mangyayari dito, if may na-detect siyang [+FF]FFF| set na siya as marker tas hindi na kasama sa generation
        if i + 3 < len(instructions) and instructions[i:i + 6] == '[+FF]F':
            marked_positions.append((x, y, heading)) # append yung positions ng mga marker
            i += 3

        i += 1

    if len(marked_positions) == 0:
        pygame.draw.line(screen, ROAD_COLOR, (x, y), (x, y), 1)  # Reset line width to default

    return marked_positions

def draw_branching_l_system(screen, instructions, angle, length, depth_factor, x, y, heading):
    # Note: hindi pwede palitan ang x & y kasi yung x,y na gamit neto is yung x,y ng marker sa main lsystem
    stack = []

    i = len(instructions) - 1  # Start from the end of the instructions
    while i >= 0:
        char = instructions[i]

        if char == ']':
            # Move to the beginning of the segment
            while i >= 0 and instructions[i] != '[':
                i -= 1

            if i >= 0 and instructions[i:i + 4] == '[BB]':
                marked_branching_positions.append((x, y, heading)) # mark the pos if the end of instruction is equal to [BB]
                i -= 1
        elif char == 'B' or char == 'C':     # Draw the branching road segment
            new_x = x + length * math.cos(math.radians(heading))
            new_y = y - length * math.sin(math.radians(heading))
            pygame.draw.line(screen, ROAD_COLOR, (x, y), (new_x, new_y), 1)
            road_segments.append(((x, y), (new_x, new_y)))
            x, y = new_x, new_y
        elif char == '+':
            heading -= angle
        elif char == '-':
            heading += angle
        elif char == '[':
            stack.append((x, y, heading))
        elif char == '|':
            depth_length = length * len(stack) * depth_factor
            new_x = x + depth_length * math.cos(math.radians(heading))
            new_y = y - depth_length * math.sin(math.radians(heading))
            pygame.draw.line(screen, ROAD_COLOR, (x, y), (new_x, new_y), 1)
            x, y = new_x, new_y

        i -= 1

    if len(marked_positions) == 0:
        pygame.draw.line(screen, (255, 255, 255), (x, y), (x, y), 1)

    return marked_branching_positions

def does_rect_intersect_line(rect, line_start, line_end):
    rect_x, rect_y, rect_width, rect_height = rect
    lines = [
        ((rect_x, rect_y), (rect_x + rect_width, rect_y)),
        ((rect_x, rect_y), (rect_x, rect_y + rect_height)),
        ((rect_x + rect_width, rect_y), (rect_x + rect_width, rect_y + rect_height)),
        ((rect_x, rect_y + rect_height), (rect_x + rect_width, rect_y + rect_height)),
    ]
    for rect_line_start, rect_line_end in lines:
        if do_lines_intersect(rect_line_start, rect_line_end, line_start, line_end):
            return True
    return False

def do_lines_intersect(a_start, a_end, b_start, b_end):
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    A = a_start
    B = a_end
    C = b_start
    D = b_end
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def draw_random_buildings(screen, positions, num_rectangles=3):
    for pos in positions:
        for _ in range(num_rectangles):
            width = random.uniform(5, 20)
            height = random.uniform(5, 20)
            x, y = pos
            for _ in range(10):  # Attempt up to 10 times to find a non-overlapping position
                offset_x = random.uniform(-50, 50)
                offset_y = random.uniform(-50, 50)
                rect = (x + offset_x, y + offset_y, width, height)
                if not any(does_rect_intersect_line(rect, line_start, line_end) for line_start, line_end in road_segments):
                    pygame.draw.rect(screen, BLACK, rect)  # Fill the rectangle
                    break
# Main function
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("L-System")
    screen.fill(BG_COLOR)

    start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    num_iterations = int(input("Enter the number of iterations (1-10): "))

    # if no. iterations ay equal sa input babawasan niya yung iteration
    if num_iterations == 3:
        main_instructions = generate_l_system(main_axiom, main_rules, int(num_iterations - 0.01))
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
    marked_positions = draw_l_system(screen, main_instructions, start_pos, random_angle_main, step_size, depth_factor, mark=True)

    # Step size na gamit sa branching and connecting ay 20
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
                                                                    int(num_iterations - 0.1))  # pwede i-adjust yung number
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

    num_rectangles = 5
    # Draw buildings at marked_branching_position
    if marked_positions:
        positions = [(pos[0], pos[1]) for pos in marked_positions]
        draw_random_buildings(screen, positions, num_rectangles)


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

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
        "BB[+A]B[-A]|BA",
        "B[+A]B[-A]+B",
        "B-[[A]+A]+B[+BA]-A",
        "BB[+A][+A]BB[-A][-A]",  # New rule for intersections
    ],
    "B": [
        "BB",
        "B[+B]B[-B]B",
        "B[+BB][-BB]B"  # New rule for curved paths
    ],
}

depth_factor = 0.7
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
                    # Randomly select one rule from the list
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
        if char == 'F' or char == 'B':
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

def check_line_intersection(line1, line2):
    x1, y1, x2, y2 = line1[0][0], line1[0][1], line1[1][0], line1[1][1]
    x3, y3, x4, y4 = line2[0][0], line2[0][1], line2[1][0], line2[1][1]

    # Calculate the determinants
    det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    det1 = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
    det2 = (x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)

    # Check if the lines are parallel or coincident
    if det == 0:
        return []  # Parallel or coincident lines don't intersect

    # Check if the intersection point lies on both line segments
    t1 = det1 / det
    t2 = det2 / det

    if 0 <= t1 <= 1 and 0 <= t2 <= 1:
        # Calculate the intersection point
        intersection_x = x1 + t1 * (x2 - x1)
        intersection_y = y1 + t1 * (y2 - y1)
        return [(intersection_x, intersection_y)]  # Return a list containing the intersection point
    else:
        return []  # Lines don't intersect within the line segments

def split_line_segment(line_segment, intersections):
    x1, y1, x2, y2 = line_segment[0][0], line_segment[0][1], line_segment[1][0], line_segment[1][1]
    new_segments = []
    start_point = (x1, y1)

    for intersection in intersections:
        end_point = intersection
        new_segments.append((start_point, end_point))
        start_point = end_point

    new_segments.append((start_point, (x2, y2)))

    return new_segments


def draw_branching_l_system(screen, instructions, angle, length, depth_factor, x, y, heading):
    stack = []
    i = 0
    line_segments = set()  # Set to store line segments

    while i < len(instructions):
        char = instructions[i]
        if char == 'B':
            new_x = x + length * math.cos(math.radians(heading))
            new_y = y - length * math.sin(math.radians(heading))
            new_line_segment = ((x, y), (new_x, new_y))

            # Check for intersections with existing line segments
            intersections = []
            for existing_line in line_segments:
                if isinstance(existing_line, tuple) and len(existing_line) == 2:
                    if isinstance(existing_line[0], tuple) and isinstance(existing_line[1], tuple):
                        intersection = check_line_intersection(new_line_segment, existing_line)
                        if intersection:  # Check if intersection is not empty
                            intersections.extend(intersection)  # Extend instead of append

            if intersections:  # Check if there are any intersections
                # Split the line segment at intersection points
                non_overlapping_segments = split_line_segment(new_line_segment, intersections)

                # Draw the non-overlapping portions
                for segment in non_overlapping_segments:
                    pygame.draw.line(screen, (0, 0, 0), segment[0], segment[1], 1)
            else:
                pygame.draw.line(screen, (0, 0, 0), (x, y), (new_x, new_y), 1)

            x, y = new_x, new_y
            line_segments.add(new_line_segment)

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
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations - 1)
    elif num_iterations == 4 or num_iterations == 5:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations - 2)
    elif num_iterations == 6 or num_iterations == 7:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations - 3)
    elif num_iterations == 8 or num_iterations == 9:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations - 4)
    elif num_iterations == 10:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations // 5)
    else:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations)

    print(main_instructions)

    # Draw main L-system
    random_angle_main = random.uniform(45, 90)
    random_length_main = random.uniform(15, 20)
    marked_positions = draw_l_system(screen, main_instructions, random_angle_main, random_length_main, depth_factor, mark=True)

    if marked_positions:
        for marked_position in marked_positions:
            x, y, heading = marked_position

            random_angle_branching = random.uniform(90, 90)

            if num_iterations == 3:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 0.3))
            elif num_iterations == 4 or num_iterations == 5:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 1.5))
            elif num_iterations == 6 or num_iterations == 7:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 2.9))
            elif num_iterations == 8 or num_iterations == 9:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 4.5))
            elif num_iterations == 10:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, int(num_iterations - 5))
            else:
                branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, num_iterations)

            random_length_branching = random.uniform(10, 15)  # Adjust the length range if needed
            draw_branching_l_system(screen, branching_instructions, random_angle_branching,
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

import turtle
import random
import math

# L-system parameters
main_axiom = "[F]--F"
main_rules = {
    'F': "FFF[+FF]FFF|"
}

branching_axiom = "A"
branching_rules = {
    "A": [
        "BB[+A]B[-A]|BA",
        "B[+A]B[-A|]+B",
        "B-[[A]+A]+B[+BA]-A",
        "BB[+A][+A]BB[-A][-A]|",  # New rule for intersections
    ],
    "B": [
        "BB",
        "B[+B]B[-B]B",
        "B[+BB][-BB]B"  # New rule for curved paths
    ],
}

depth_factor = 0.5
string_placeholder = []
marked_positions = []

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

def draw_l_system(turtle, instructions, angle, length, depth_factor, mark=False):
    stack = []
    global marked_positions
    i = 0
    while i < len(instructions):
        char = instructions[i]
        if char == 'F' or char == 'B':
            turtle.forward(length)
        elif char == '+':
            turtle.right(angle)
        elif char == '-':
            turtle.left(angle)  # Use left for counter-clockwise turns
        elif char == '[':
            stack.append((turtle.position(), turtle.heading()))
        elif char == ']':
            position, heading = stack.pop()
            turtle.penup()
            turtle.setposition(position)
            turtle.setheading(heading)
            turtle.pendown()
        elif char == '|':
            depth_length = length * len(stack) * depth_factor
            turtle.forward(depth_length)

        # Check for specific pattern +FF and mark
        if i + 2 < len(instructions) and instructions[i:i+3] == '+FF':
            marked_positions.append((turtle.position(), turtle.heading()))
            turtle.write('#')
            i += 2  # Skip the pattern characters

        i += 1
    return marked_positions

def generate_branching_l_system(angle):
    iterations = 0
    branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, iterations)
    return branching_instructions, angle

def draw_branching_l_system(turtle, instructions, angle, length, depth_factor, marked_positions):
    # Draw L-system
    draw_l_system(turtle, instructions, angle, length, depth_factor)

    max_distance = 50  # Define the maximum distance to consider markers as neighbors
    for marked_position in marked_positions:
        if distance(turtle.position(), marked_position[0]) <= max_distance:
            # Connect the current position to the nearby marker
            turtle.penup()
            turtle.setposition(turtle.position())
            turtle.pendown()
            turtle.setposition(marked_position[0])

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def find_neighbors(position, positions, max_distance):
    neighbors = []
    for pos in positions:
        if pos != position and distance(position, pos) <= max_distance:
            neighbors.append(pos)
    return neighbors

def main():
    global character_counter
    # Set up the turtle
    screen = turtle.Screen()
    screen.title("L-System")
    l_turtle = turtle.Turtle()
    l_turtle.speed(0)
    l_turtle.width(2)

    num_iterations = int(input("Enter the number of iterations (1-10): "))  # Renamed variable

    if num_iterations == 3:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations - 1)
    elif num_iterations == 4 or num_iterations == 5:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations // 2)
    elif num_iterations == 6 or num_iterations == 7:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations // 3)
    elif num_iterations == 8 or num_iterations == 9:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations // 4)
    elif num_iterations == 10:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations // 5)
    else:
        main_instructions = generate_l_system(main_axiom, main_rules, num_iterations)

    print(main_instructions)

    # Draw main L-system
    random_angle_main = random.uniform(45, 90)
    random_length_main = random.uniform(10, 15)
    l_turtle.penup()
    l_turtle.setposition(-200, 0)
    l_turtle.pendown()
    draw_l_system(l_turtle, main_instructions, random_angle_main, random_length_main, depth_factor, mark=True)

    # Randomly select a position from marked positions
    if marked_positions:
        for marked_position in marked_positions:
            position, heading = marked_position
            x, y = position
            l_turtle.penup()
            l_turtle.setposition(x, y)
            l_turtle.setheading(heading)
            l_turtle.pendown()
            l_turtle.width(0)

            # Generate branching L-system string and set angle
            random_angle_branching = random.uniform(90, 90)
            branching_instructions = generate_branching_lsystem(branching_axiom, branching_rules, num_iterations)

            # Draw branching L-system and connect nearby markers
            random_length_branching = random.uniform(11, 25)
            draw_branching_l_system(l_turtle, branching_instructions, random_angle_branching,
                                     random_length_branching, depth_factor, marked_positions)

    # Print marked positions
    print("Marked Positions:", marked_positions)

    # Finish drawing
    turtle.done()

if __name__ == "__main__":
    main()
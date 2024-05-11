import turtle
import random

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

# Define the turtle drawing function
def draw_lsystem(instructions, order, step_size=10):
    stack = []
    t = turtle.Turtle()
    t.speed(0) # turtle speed to max
    t.penup()
    t.goto(-200, 0) # place turtle on starting position
    t.pendown()

    for char in instructions:
        if char == "F":
            t.forward(step_size)  # Move the turtle forward
            t.dot(4, "red")  # Leave a red dot after moving forward
        elif char == "+":
            t.right(90)  # Turn the turtle right by the specified angle
        elif char == "-":
            t.left(90)  # Turn the turtle left by the specified angle

        elif char == "[":
            stack.append((t.position(), t.heading()))  # Push the current position and heading onto the stack, para mababalikan niya later.
        elif char == "]":
            position, heading = stack.pop()  # Pop the last position and heading from the stack, para babalik siya sa sa position bago ang '[' since wala pa yang laman. Ise-save niya lang, para once magkaroon ng laman, babalikan niya.
            t.penup()
            t.goto(position)  # Move the turtle to the popped position
            t.setheading(heading)  # Set the turtle's heading to the popped heading
            t.pendown()

    turtle.Screen().mainloop()  # Keep the turtle graphics window open

# Generate the L-system
def generate_lsystem(axiom, rules, order):
    instructions = axiom
    for _ in range(order):
        next_instructions = ""
        for char in instructions:
            if char in rules:
                next_instructions += random.choice(rules[char])
            else:
                next_instructions += char
        instructions = next_instructions
        print(instructions)
    return instructions

# Prompt the user for the number of iterations
iterations = int(input("Enter the number of iterations (1-10): "))

# Generate the L-system and draw the city
instructions = generate_lsystem(axiom, rules, iterations)
draw_lsystem(instructions, iterations, step_size=30)
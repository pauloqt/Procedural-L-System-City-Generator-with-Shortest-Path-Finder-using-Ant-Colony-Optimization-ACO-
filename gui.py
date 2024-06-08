import pygame
import pygame.font

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
text_color = (205, 162, 115)  # CDA273 in RGB

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
    cursor_blink_time = 500  # Cursor blink interval in milliseconds
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
                elif closebutton_x <= mouse_pos[0] <= closebutton_x + closebutton_width and \
                        closebutton_y <= mouse_pos[1] <= closebutton_y + closebutton_height:
                    print("Close Button Clicked!")
                    landing_page()
                    return
                else:
                    input_active = not input_active  # Toggle input activation
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    print("User Input:", input_text)
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

# Initialize Pygame
pygame.init()
landing_page()

# Quit Pygame
pygame.quit()

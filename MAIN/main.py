import pygame
import sys
import random
import cv2
import os
import pygame.mask

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
YELLOW = (255, 215, 0)
RED = (255, 0, 0)
FPS = 60

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gabriele's Farm by @aborotto")
clock = pygame.time.Clock()

# Load video file
video_path = 'mainmenubg.mp4'  # Replace with your video file path
if not os.path.isfile(video_path):
    print(f"Error: Video file '{video_path}' not found.")
    pygame.quit()
    exit()

# Set up video playback using OpenCV
cap = cv2.VideoCapture(video_path)
success, img = cap.read()
shape = img.shape[1::-1]

#Define Game State
MAIN_MENU = 0
GAME_PLAY = 1
GAME_OVER = 2
game_state = None
RETURN_TO_GAME = False

#Stop background music
def stop_background_music():
    pygame.mixer.music.stop()

# Create player, hay, and enemy classes
class Player:
    def __init__(self):
        self.image = pygame.image.load("player.png")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.topleft = (WIDTH // 2 - 15, HEIGHT // 2 - 15)
        self.lives = 3
        self.score = 0
        self.invulnerable = False
        self.invulnerability_timer = 0
        self.mask = pygame.mask.from_surface(self.image)

    def move(self, dx, dy):
        # Restrict player movement within the screen boundaries
        new_x = self.rect.x + dx
        new_y = self.rect.y + dy

        if 0 <= new_x <= WIDTH - self.rect.width:
            self.rect.x = new_x

        if 0 <= new_y <= HEIGHT - self.rect.height:
            self.rect.y = new_y

class Hay:
    def __init__(self, x, y):
        # Load the hay image
        self.image = pygame.image.load("hay.png")
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.mask = pygame.mask.from_surface(self.image)

    def check_collision(self, player):
        offset = (self.rect.x - player.rect.x, self.rect.y - player.rect.y)
        return player.mask.overlap(self.mask, offset)

class Enemy:
    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (130, 130))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.dx = random.choice([-2, 2])  # Random horizontal movement
        self.dy = random.choice([-2, 2])  # Random vertical movement


class PowerUp:
    def __init__(self, x, y):
         self.image = pygame.image.load("powerup.png")  # Load the power-up image
         self.image = pygame.transform.scale(self.image, (50, 50))
         self.rect = self.image.get_rect()
         self.rect.topleft = (x, y)
         self.active = False
         self.mask = pygame.mask.from_surface(self.image)  # Create a mask from the image

    def update(self):
        if not self.active:
            self.rect.x += 1  # Move the power-up (you can adjust the movement as needed)

class Button:
    def __init__(self, x, y, image_path, action, scale=1.0, rect=None):
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))

        # Create a rect for collision detection based on the image size
        if rect is None:
            self.rect = self.image.get_rect()
        else:
            self.rect = pygame.Rect(x, y, rect[2], rect[3])

        # Set the position of the button based on the provided (x, y) coordinates
        self.rect.topleft = (x, y)

        self.action = action

    def draw(self):
        screen.blit(self.image, self.rect)

# Create "Start" and "Exit" buttons
start_button = Button(50, 100, "startbutton.png", "start", scale=2.0, rect=(50, 100, 100, 100))
exit_button = Button(50, 180, "exitbutton.png", "exit", scale=2.0, rect=(50, 180, 130, 180))

# Function to generate hay for a given level
def generate_hay(level):
    num_hay = level * 5  # Increase the number of hay with each level
    hays = []
    
    for _ in range(num_hay):
        while True:
            x = random.randint(0, WIDTH - 100)
            y = random.randint(0, HEIGHT - 100)
            new_hay = Hay(x, y)
            
            # Check for collisions with existing hay
            collision = False
            for existing_hay in hays:
                if new_hay.rect.colliderect(existing_hay.rect):
                    collision = True
                    break
            
            if not collision:
                hays.append(new_hay)
                break
    
    return hays


def main_menu():
    global cap, game_state

    game_state = MAIN_MENU
    # Load png Name's Logo
    menu_logo = pygame.image.load("gabriele'sFarm.png")
    game_state = MAIN_MENU
    
    # Load the instructions image
    instructions_image = pygame.image.load("instructions.png")

    # Define the scale factor for the instructions image
    scale_factor = 3  

    # Scale the instructions image
    instructions_image = pygame.transform.scale(instructions_image, (
        int(instructions_image.get_width() * scale_factor),
        int(instructions_image.get_height() * scale_factor)
    ))
        
    if game_state == MAIN_MENU:
        pygame.mixer.music.load("mainmenuMusic.mp3")
        pygame.mixer.music.play(-1)

    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.rect.collidepoint(event.pos):
                    if cap is not None:  # Check if cap is initialized
                        cap.release()  # Release the video capture
                        stop_background_music()
                        return  # Start the game
                elif exit_button.rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

        # Display the video frame using OpenCV
        success, img = cap.read()

        if success:  # Check if the video frame is successfully read
            # Calculate the aspect ratio of the video
            video_width, video_height = img.shape[1], img.shape[0]
            # Calculate scaling factors for width and height
            width_scale = WIDTH / video_width
            height_scale = HEIGHT / video_height
            # Use the smaller of the two scaling factors to fit the entire video within the window
            scale_factor = 0.8
            # Calculate the width and height for resizing to fit the screen width
            new_width = int(video_width * scale_factor)
            new_height = int(video_height * scale_factor)
            # Resize the frame while maintaining the aspect ratio
            img = cv2.resize(img, (new_width, new_height))
            # Flip the frame vertically to correct the orientation
            img = cv2.flip(img, 0)
            # Rotate the frame by 90 degrees (clockwise) to correct the orientation
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            # Calculate the position to center the resized frame on the screen
            x_offset = (WIDTH - new_width) // 2
            y_offset = (HEIGHT - new_height) // 2
            # Convert the image to the RGB format expected by Pygame
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Create a Pygame surface from the image
            pygame_surface = pygame.surfarray.make_surface(img)
            # Blit the Pygame surface onto the screen, considering the offsets
            screen.blit(pygame_surface, (x_offset, y_offset))
        else:  # If the video ends, release and reinitialize the capture
            cap.release()
            cap = cv2.VideoCapture(video_path)

        # Display main menu text and options
        logo_x = (WIDTH - menu_logo.get_width()) // 2
        logo_y = (HEIGHT - menu_logo.get_height()) // 10
        screen.blit(menu_logo, (logo_x, logo_y))

        # Display the instructions image on the main menu
        instructions_x = 50
        instructions_y = (HEIGHT - menu_logo.get_height()) // 1.7
        screen.blit(instructions_image, (instructions_x, instructions_y))

        start_button.draw()
        exit_button.draw()

        pygame.display.flip()
        clock.tick(FPS)

# Game over menu function
def game_over_menu(player_name, player_score):
    retry_pressed = False
    global game_state

    game_state = GAME_OVER
    if game_state == GAME_OVER:
        pygame.mixer.music.load("gameoverMusic.mp3")
        pygame.mixer.music.play(-1)

    # Load the game over background image
    game_over_bg = pygame.image.load("gameover.jpg")  
    game_over_bg = pygame.transform.scale(game_over_bg, (WIDTH, HEIGHT))


    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    retry_pressed = True  # Retry the game
                    pygame.mixer.music.stop()
                elif event.key == pygame.K_ESCAPE:
                    return "exit"  # Exit the game

        # If retry is pressed, return "retry" and exit the loop
        if retry_pressed:
            return "retry"

        # Clear the screen
        screen.fill(WHITE)

        # Blit the game over background image
        screen.blit(game_over_bg, (0, 0))


        # Display game over menu text and options
        font = pygame.font.Font("Farmhouse.otf", 60)
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        retry_text = font.render("Press Enter to Retry", True, (255, 255, 255))
        exit_text = font.render("Press Esc to Exit", True, (255, 255, 255))

        # Calculate text positions for centering
        game_over_x = (WIDTH - game_over_text.get_width()) // 2
        retry_x = (WIDTH - retry_text.get_width()) // 2
        exit_x = (WIDTH - exit_text.get_width()) // 2

        game_over_y = (HEIGHT - game_over_text.get_height()) // 2 - 50
        retry_y = (HEIGHT - retry_text.get_height()) // 2 + 10
        exit_y = (HEIGHT - exit_text.get_height()) // 2 + 70

        screen.blit(game_over_text, (game_over_x, game_over_y))
        screen.blit(retry_text, (retry_x, retry_y))
        screen.blit(exit_text, (exit_x, exit_y))

        # update leaderboard
        update_leaderboard(player_name, player_score)

        # Show leaderboard
        font = pygame.font.Font("Farmhouse.otf", 20)
        leaderboard_text = font.render("Leaderboard", True, (255, 255, 255))
        screen.blit(leaderboard_text, (10, 170))

        for i, (name, score) in enumerate(scores):
            leaderboard_entry = font.render(f"{i + 1}. {name}: {score}", True, (255, 255, 255))
            y_offset = 210 + i * 30
            screen.blit(leaderboard_entry, (10, y_offset))

        pygame.display.flip()
        clock.tick(FPS)

# Read scores from the txt file
def load_scores():
    global scores
    scores = []  # initializing variable with scores
    try:
        with open("scores.txt", "r") as file:
            for line in file:
                name, score = line.strip().split()
                scores.append((name, int(score)))
    except FileNotFoundError:
        pass  # File doesn't exist yet

load_scores()

def update_leaderboard(player_name, player_score):
    global scores  # declaring scores as global variable

    # Search if the player name is already in the txt file
    player_found = False
    for i, (name, score) in enumerate(scores):
        if name == player_name:
            player_found = True
            #Update score only if it's bigger than the previous one
            if player_score > score:
                scores[i] = (player_name, player_score)
            break

    # if the name of the player is not found add a new record
    if not player_found:
        scores.append((player_name, player_score))

    # Limit the leaderboard to 10 scores
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:10]

    # Saving scores in the txt file
    with open("scores.txt", "w") as file:
        for name, score in scores:
            file.write(f"{name} {score}\n")

def get_player_name():
    leaderboard_names = [name for name, _ in scores]  # initialize list of names in the leaderboard

    input_box = pygame.Rect(200, 200, 400, 50)  #Positions and dimensions of the input field
    color_inactive = pygame.Color('white')  
    color_active = pygame.Color('white') 
    color = color_inactive
    active = False
    text = ''
    font = pygame.font.Font("Farmhouse.otf", 32)  

    # Testo sopra la casella
    label_font = pygame.font.Font("Farmhouse.otf", 36)
    label_text = label_font.render("Enter your name:", True, (255, 255, 255))
    label_rect = label_text.get_rect()
    label_rect.center = (WIDTH // 2, 150)  #Centered position
    # Inizializza il messaggio a None
    message = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive

            if active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    elif event.key == pygame.K_RETURN:
                        if text in leaderboard_names:
                            text = ""
                            message = font.render("The selected name is already in use. Please choose another.", True, (255, 0, 0))
                        else:
                            return text  # Return inserted name
                    else:
                        text += event.unicode

        screen.fill((0, 0, 0)) 

        txt_surface = font.render(text, True, color)
        txt_width, txt_height = txt_surface.get_size()
        width = max(400, txt_surface.get_width() + 10)
        input_box.w = width
        # Center input box
        input_box.center = (WIDTH // 2, HEIGHT // 2)

        
        text_x = input_box.x + (input_box.w - txt_width) // 2
        text_y = input_box.y + (input_box.h - txt_height) // 2

        #Drawing centered text
        screen.blit(txt_surface, (text_x, text_y))
        screen.blit(label_text, label_rect) 
        pygame.draw.rect(screen, color, input_box, 2)
        if message:
            message_rect = message.get_rect()
            message_rect.center = (WIDTH // 2, HEIGHT // 2 + 80)
            screen.blit(message, message_rect)
        pygame.display.flip()
        clock.tick(FPS)


# Game loop
def game_loop():
    player = Player()
    level = 1
    hays = generate_hay(level)
    enemies = []
    power_ups = []
    running = True
    power_up_spawn_timer = 0
    last_power_up_score = 0 
    power_up_timer = 0
    power_up_duration = 5 * FPS
    display_power_up_timer = 0
    global game_state, player_name, player_score


    player_name = get_player_name()
    player_score = player.score

    # Load the background image
    gameloop_image = pygame.image.load("GameLoopBG.png")

    # Calculate the scaling factors to fill the window while maintaining aspect ratio
    width_scale = WIDTH / gameloop_image.get_width()
    height_scale = HEIGHT / gameloop_image.get_height()
    scale_factor = max(width_scale, height_scale)

    # Scale the background image to fit the game window
    gameloop_image = pygame.transform.scale(gameloop_image, (int(gameloop_image.get_width() * scale_factor), int(gameloop_image.get_height() * scale_factor)))

    game_state = GAME_PLAY

    
    pygame.mixer.music.load("GameLoopMusic.mp3")
    pygame.mixer.music.play(-1)


    for _ in range(level * 3):
        # Spawn enemies outside the window
        spawn_locations = [
            (-130, random.randint(0, HEIGHT - 20)),  # Left side
            (WIDTH + 10, random.randint(0, HEIGHT - 20)),  # Right side
            (random.randint(0, WIDTH - 20), -130),  # Top
            (random.randint(0, WIDTH - 20), HEIGHT + 10),  # Bottom
        ]
        x, y = random.choice(spawn_locations)
        new_enemy = Enemy(x, y, "pig.png")
        enemies.append(new_enemy)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle player movement
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 5
        player.move(dx, dy)

        # Update hay positions and check for collisions
        for hay in hays[:]:  # Iterate over a copy of the list
            if hay.check_collision(player):
                hays.remove(hay)
                player.score += 10

        # Update enemy positions and check for collisions with player
        for enemy in enemies:
            enemy.rect.x += enemy.dx
            enemy.rect.y += enemy.dy

            # Wrap enemy objects around the screen
            if enemy.rect.left > WIDTH:
                enemy.rect.right = 0
            elif enemy.rect.right < 0:
                enemy.rect.left = WIDTH
            if enemy.rect.top > HEIGHT:
                enemy.rect.bottom = 0
            elif enemy.rect.bottom < 0:
                enemy.rect.top = HEIGHT

            # Check for collisions between player and enemy
            if not player.invulnerable and player.mask.overlap(enemy.mask, (enemy.rect.x- player.rect.x, enemy.rect.y - player.rect.y )):
                player.lives -= 1
                enemies.remove(enemy)

        # Update power-up positions and check for collisions with player
        for power_up in power_ups:
            if not power_up.active and player.mask.overlap(power_up.mask, (power_up.rect.x - player.rect.x, power_up.rect.y - player.rect.y)):  # Check for collisions
                power_up.active = True
                player.invulnerable = True
                player.invulnerability_timer = 5 * FPS  # 5 seconds
                power_ups.remove(power_up)  # Remove the power-up
                power_up_timer = power_up_duration
                display_power_up_timer = power_up_duration  # Start displaying countdown

             # Decrease the power-up timer
            if power_up_timer > 0:
                power_up_timer -= 1

        # If the player is invulnerable, decrease the timer
        if player.invulnerable:
            player.invulnerability_timer -= 1
            if player.invulnerability_timer <= 0:
                player.invulnerable = False

        # Spawn power-ups every 200 points
        if player.score >= last_power_up_score + 200:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
            power_up = PowerUp(x, y)
            power_ups.append(power_up)
            power_up_spawn_timer = 60 * FPS  # 60 seconds
            last_power_up_score = player.score

        # Decrease the power-up spawn timer
        if power_up_spawn_timer > 0:
            power_up_spawn_timer -= 1

        # If all hay are collected, transition to the next level
        if len(hays) == 0:
              level += 1
              hays = generate_hay(level)
    
              # Clear the enemies list before generating new enemies
              enemies.clear()
    
              new_enemies = [Enemy(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), "pig.png") for _ in range(level * 3)]
              enemies.extend(new_enemies)  # Append new enemies to the existing list

        # Clear the screen
        screen.fill(WHITE)

        # Draw the background image
        screen.blit(gameloop_image, (0, 0))

        # Draw the player
        screen.blit(player.image, player.rect)

         # Draw the hay
        for hay in hays:
            screen.blit(hay.image, hay.rect)

        # Draw the enemies
        for enemy in enemies:
            screen.blit(enemy.image, enemy.rect)

        # Draw the power-ups
        for power_up in power_ups:
            if not power_up.active:
                screen.blit(power_up.image, power_up.rect)
        # Display the score, level, and remaining lives
        font = pygame.font.Font("Farmhouse.otf", 20)
        score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
        level_text = font.render(f"Level: {level}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        screen.blit(lives_text, (10, 90))

        # Display the countdown timer
        if display_power_up_timer > 0:
            font = pygame.font.Font("Farmhouse.otf", 20)
            timer_text = font.render(f"Power-Up Timer: {display_power_up_timer // FPS + 1}", True, (0, 0, 0))
            screen.blit(timer_text, (10, 130))
            display_power_up_timer -= 1

        # Update the display
        pygame.display.flip()

        # Check for game over
        if player.lives <= 0:
            result = game_over_menu(player_name, player.score)
            if result == "retry":
                player.lives = 3
                player.score = 0
                level = 1
                hays = generate_hay(level)
                enemies = [Enemy(random.randint(0, WIDTH - 20), random.randint(0, HEIGHT - 20), "pig.png") for _ in range(level * 3)]
                last_power_up_score = 0  # Reset last power-up score
                power_up_spawn_timer = 0  # Reset power-up spawn timer
                pygame.mixer.music.load("GameLoopMusic.mp3")
                pygame.mixer.music.play(-1)
                
                
            elif result == "exit":
                running = False
        
        # Cap the frame rate
        clock.tick(FPS)

# Run the main menu
main_menu()

# Start the game loop after the main menu
game_loop()

# Clean up
pygame.quit()
sys.exit()
import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen setup
screen_size = 600
cell_size = screen_size // 8  # Each cell size for an 8x8 grid
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("CarpCrash")

# Colors
TREE_GREEN = (34, 139, 34)  # Forest green for trees
CARPENTER_COLOR = (139, 69, 19)  # Brown for carpenters
CUT_GROUND_COLOR = (101, 67, 33)  # Dark brown for cut ground
HIGHLIGHT_COLOR = (173, 216, 230)  # Light blue for valid moves
SELECTED_COLOR = (255, 215, 0)  # Yellow for selected carpenter
INVALID_MOVE_COLOR = (255, 0, 0)  # Red for invalid move message

# Board setup
rows, cols = 8, 8
carpenter_count = 5
board = [['T' for _ in range(cols)] for _ in range(rows)]  # 'T' represents a tree

# Place carpenters randomly
carpenters = {}
c_id_counter = 0
while len(carpenters) < carpenter_count:
    x, y = random.randint(0, rows - 1), random.randint(0, cols - 1)
    if board[x][y] == 'T':  # Place carpenter only on tree tiles
        board[x][y] = 'C'
        carpenters[c_id_counter] = (x, y)  # Map ID to position
        c_id_counter += 1

# Function to draw the board
def draw_board(selected_carpenter=None, valid_moves=[], current_turn=None, invalid_move_message=None, stuck_message=None):
    screen.fill((255, 255, 255))  # Clear the screen before drawing

    for row in range(rows):
        for col in range(cols):
            if board[row][col] == 'T':
                color = TREE_GREEN
            elif board[row][col] == 'C':
                color = CARPENTER_COLOR
            elif board[row][col] == 'G':
                color = CUT_GROUND_COLOR
            else:
                color = (255, 255, 255)

            x, y = col * cell_size, row * cell_size
            pygame.draw.rect(screen, color, (x, y, cell_size, cell_size))

            if (row, col) in valid_moves:
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x, y, cell_size, cell_size))

            if selected_carpenter and (row, col) == carpenters[selected_carpenter]:
                pygame.draw.rect(screen, SELECTED_COLOR, (x, y, cell_size, cell_size))

            pygame.draw.rect(screen, (0, 0, 0), (x, y, cell_size, cell_size), 1)

    # Display turn information
    font = pygame.font.Font(None, 36)
    if current_turn is not None:
        turn_text = font.render(f"Turn: {current_turn + 1}", True, (0, 0, 0))
        screen.blit(turn_text, (10, 10))

    # Display labels for carpenters
    font = pygame.font.Font(None, 24)
    for cid, (x, y) in carpenters.items():
        label_text = font.render(f"{cid + 1}", True, (0, 0, 0))  # Display carpenter IDs
        screen.blit(label_text, (y * cell_size + 10, x * cell_size + 10))

    # Display invalid move message if any
    if invalid_move_message:
        invalid_move_text = font.render(invalid_move_message, True, INVALID_MOVE_COLOR)
        screen.blit(invalid_move_text, (screen_size // 2 - invalid_move_text.get_width() // 2, screen_size - 50))

    # Display stuck message if any
    if stuck_message:
        stuck_message_text = font.render(stuck_message, True, INVALID_MOVE_COLOR)
        screen.blit(stuck_message_text, (screen_size // 2 - stuck_message_text.get_width() // 2, screen_size // 2 - 50))

# Function to get valid moves for a carpenter
def get_valid_moves(carpenter_id):
    x, y = carpenters[carpenter_id]
    valid_moves = []
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                if board[nx][ny] == 'T' or (board[nx][ny] == 'C' and (nx, ny) != (x, y)):
                    valid_moves.append((nx, ny))
    return valid_moves

# Function to move a carpenter
def move_carpenter(c_id, new_position):
    global current_turn
    x, y = carpenters[c_id]
    nx, ny = new_position

    # Check if the target contains another carpenter
    for enemy_id, (ex, ey) in list(carpenters.items()):
        if (nx, ny) == (ex, ey) and enemy_id != c_id:
            del carpenters[enemy_id]
            board[ex][ey] = 'G'  # Mark as cut ground
            break

    # Move the carpenter
    board[x][y] = 'G'
    board[nx][ny] = 'C'
    carpenters[c_id] = (nx, ny)

    # Update the turn index to ensure it wraps around the remaining carpenters
    carpenter_ids = list(carpenters.keys())
    current_turn = (carpenter_ids.index(c_id) + 1) % len(carpenters)
    if current_turn >= len(carpenters):
        current_turn = 0

# Function to check if any carpenter is stuck with no valid moves
def check_for_stuck_carpenters():
    global stuck_message_time
    stuck_message = None
    for c_id, pos in list(carpenters.items()):
        valid_moves = get_valid_moves(c_id)
        if len(valid_moves) <= 1:  # Check if the carpenter has 1 or fewer valid moves
            stuck_message = f"Carpenter {c_id + 1} is stuck and is eliminated!"  # Display a stuck message
            stuck_message_time = pygame.time.get_ticks()  # Record the time when the message is shown
            del carpenters[c_id]  # Delete the carpenter
            board[pos[0]][pos[1]] = 'G'  # Mark the cell as cut ground
            break  # After deleting a carpenter, check if only 1 is left
    return stuck_message

# Function to check for winner
def check_winner():
    if len(carpenters) == 1:
        font = pygame.font.Font(None, 48)  # Use a larger font for emphasis
        winner_message = f"Game Over! Carpenter {list(carpenters.keys())[0] + 1} wins!"
        winner_text = font.render(winner_message, True, (0, 0, 255))  # Blue color

        # Calculate position to center the text
        text_x = (screen_size - winner_text.get_width()) // 2
        text_y = (screen_size - winner_text.get_height()) // 2

        # Draw the message on the screen
        screen.blit(winner_text, (text_x, text_y))
        pygame.display.flip()

        # Wait for 1 second before quitting
        pygame.time.delay(1000)
        pygame.quit()
        sys.exit()

# Initial draw
current_turn = 0
selected_carpenter = None
valid_moves = []
invalid_move_message = None
stuck_message = None

# Timer for stuck message display
stuck_message_time = 0

draw_board(current_turn=list(carpenters.keys())[current_turn], stuck_message=stuck_message)
pygame.display.flip()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            clicked_cell = (my // cell_size, mx // cell_size)

            if selected_carpenter is not None and clicked_cell in valid_moves:
                move_carpenter(selected_carpenter, clicked_cell)
                stuck_message = check_for_stuck_carpenters()  # Check and remove stuck carpenters
                check_winner()  # Check if the game is over

                selected_carpenter = None
                valid_moves = []
                invalid_move_message = None

            elif clicked_cell in carpenters.values():
                for cid, pos in carpenters.items():
                    if pos == clicked_cell and cid == list(carpenters.keys())[current_turn]:
                        selected_carpenter = cid
                        valid_moves = get_valid_moves(cid)
                        break

            else:
                invalid_move_message = "Invalid Move!"

            # If enough time has passed, clear the stuck message
            if pygame.time.get_ticks() - stuck_message_time > 1000:
                stuck_message = None

            draw_board(selected_carpenter, valid_moves, current_turn=list(carpenters.keys())[current_turn], invalid_move_message=invalid_move_message, stuck_message=stuck_message)
            pygame.display.flip()

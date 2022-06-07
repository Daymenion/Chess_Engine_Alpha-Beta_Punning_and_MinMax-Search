#
# Created by: Daymenion 16/05/2022
#
# this program under the GNU General Public License v3.0 license.

import pygame
import Engine
import AI
import tkinter as tk
from tkinter import simpledialog, messagebox

pygame.init()  # Initialize pygame

WIDTH = HEIGHT = 500  # Set the width and height of the screen
DIMENSION = 8  # 8x8 board
SQ_SIZE = HEIGHT // DIMENSION  # Size of each square
MAX_FPS = 5  # only from animation
IMAGES = {}  # Dictionary of Sources


def load_images():  # Loads all Sources into a dictionary of Sources for later use in the game loop
    pieces = ["bR", "bN", "bB", "bQ", "bK", "wR", "wN", "wB", "wQ", "wK", "bP", "wP"]  # List of all pieces
    for piece in pieces:  # For each piece
        IMAGES[piece] = pygame.image.load("Sources/" + piece + ".png")  # Load the image
        IMAGES[piece] = pygame.transform.scale(IMAGES[piece], (SQ_SIZE, SQ_SIZE))  # Scale the image to the correct size


# Main menu function that displays the main menu and allows the user to select a game mode
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game by Daymenion")  # Set the title of the window
    clock = pygame.time.Clock()  # Create a clock object to control the frame rate
    screen.fill(pygame.Color("white"))  # Fill the screen with white
    gs = Engine.GameState()
    valid_moves = gs.getValidMoves()  # Get the valid moves for the current game state (for AI)
    move_made = False  # used to chk whether to regenerate valid_moves function again or not based on the move performed
    load_images()  # load Sources before starting game

    # Run until the user asks to quit
    running = True  # Set running to true to start the game loop
    do_animate = False  # Set do_animate whether to animate the piece or not
    sqselected = ()  # Set sqselected to selected square to be blank
    player_clicks = []  # List of player clicks
    game_over = False  # Used to check if the game is over or not

    root = tk.Tk()
    root.withdraw()  # Hide the root window so that the user can't see it while playing the game

    while True:  # get the user input
        choice = simpledialog.askstring("Game Mode:", "Please select a game mode: \n1) Player vs AI \n2) AI vs AI "
                                                      "\n3)Player vs Player \n4. Exit", parent=root, initialvalue="2")
        print(choice)
        if choice == '1':  # Player vs AI
            player1 = True
            player2 = False
            break
        elif choice == '2':  # AI vs AI
            player1 = False
            player2 = False
            break
        elif choice == '3':  # Player vs Player
            player1 = True
            player2 = True
            break
        elif choice == '4':  # Exit
            running = False
            break
        # if the user click cancel or presses escape, then exit the game
        elif choice is None or choice == '\x1b':
            running = False
            break
        else:
            # show message box to select a valid option
            messagebox.showinfo("Invalid Option", "Please select a valid option")

    print("\nPlayer White Turn")
    # Main game loop - runs until the user quits the game or the game is over (checkmate or stalemate)
    # or the game is a draw (50 move rule)
    while running:
        userTurn = (gs.whiteToMove and player1) or (not gs.whiteToMove and player2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # If the user clicked the window close button
                running = False

            # mouse click to select a piece
            elif event.type == pygame.MOUSEBUTTONDOWN:  # If the user clicked the mouse button down
                if not game_over and userTurn:  # If the game is not over and it is the user's turn to play
                    location = pygame.mouse.get_pos()  # Get the mouse position on the screen
                    col = location[0] // SQ_SIZE  # Get the column of the mouse click
                    row = location[1] // SQ_SIZE  # Get the row of the mouse click
                    if sqselected == (row, col):  # If the user clicked the same square again, then unselect it
                        sqselected = ()
                        player_clicks = []
                    else:
                        sqselected = (row, col)  # If the user clicked a new square, then select it
                        player_clicks.append(sqselected)  # Add the square to the list of player clicks
                    if len(player_clicks) == 2:  # If the user has selected two squares, then check if the move is valid
                        move = Engine.Move(player_clicks[0], player_clicks[1], gs.board, player1,
                                                player2)  # Create a move object from the player clicks
                        print(move.getChessNotation())  # Print the move in chess notation (e.g. e2e4)
                        print(
                            "Possible moves: ")  # Print the possible moves for the selected piece
                        # (e.g. e2e4, e2e5, e2e6, e2e7, e2e8, e2e1, e2e3, e2f1, e2d1, e2c1, e2b1, e2a1)
                        for temp in valid_moves:  # Print the possible moves for the selected piece
                            print(temp.getChessNotation(), end=", ")

                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:  # If the move is valid, then execute the move
                                gs.makeMove(valid_moves[i])  # Make the move on the game state object
                                move_made = True
                                do_animate = True
                                sqselected = ()
                                player_clicks = []

                        if not move_made:  # If the move is not valid, then unselect the piece
                            player_clicks = [sqselected]  # Reset the player clicks

            # using key 'Z' to undo a move and 'R' to reset Game
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:  # If the user pressed the 'Z' key (undo)
                    gs.undoMove()  # Undo the last move
                    print("\nUndoing Move\n")
                    move_made = True
                    do_animate = False
                    game_over = False

                if event.key == pygame.K_r:  # If the user pressed the 'R' key (reset)
                    gs = Engine.GameState()  # Reset the game state
                    valid_moves = gs.getValidMoves()  # Get the valid moves for the current game state
                    sqselected = ()
                    player_clicks = []
                    move_made = False
                    do_animate = False
                    game_over = False

        # AI
        if not game_over and not userTurn:  # If the game is not over and it is the AI's turn to move
            AIMove = AI.findBestMove(gs, valid_moves)  # Find the best move for the AI
            if AIMove is None:
                AIMove = AI.findRandomMove(valid_moves)  # If the AI cannot find a valid move, then find a random move
            gs.makeMove(AIMove)  # Make the move on the game state object
            print("Ai Moved: ", AIMove.getChessNotation())
            move_made = True
            do_animate = True

        # Generating new possible moves after a move
        if move_made:  # If a move has been made
            if do_animate:  # If the move has not animated yet
                animateMove(gs.moveLog[-1], screen, gs.board, clock)  # Animate the move on the screen
            valid_moves = gs.getValidMoves()  # Get the valid moves for the current game state

            if len(gs.getValidMoves()) == 0:  # If there are no valid moves for the current game state
                if gs.inCheck:
                    gs.checkMate = True  # Set the game state to checkmate (if the AI is in check)
                else:
                    gs.staleMate = True  # Set the game state to stalemate (if the AI is not in check)

            if gs.whiteToMove:
                print("\n\nPlayer White Turn")
            else:
                print("\n\nPlayer Black Turn")

            move_made = False  # Reset the move made flag
            print("checkMate:", gs.checkMate)
            print("staleMate:", gs.staleMate)
            print("Available Moves: ", len(valid_moves))

        # Draw Game State
        draw_game_state(screen, gs, valid_moves, sqselected)  # Draw the game state on the screen

        if gs.checkMate:  # If the game state is checkmate
            game_over = True
            if gs.whiteToMove:
                if not messagebox.askyesno("Check Mate",
                                           "Black Wins. Play again?"):  # Ask the user if they want to play again
                    exit()  # If not, exit the program
                else:
                    main()  # If so, restart the game
            else:
                if not messagebox.askyesno("Check Mate", "White Wins. Play again?"):
                    exit()
                else:
                    main()
        elif gs.staleMate:  # If the game state is stalemate
            game_over = True
            if not messagebox.askyesno("Stale Mate", "Draw. Play again?"):
                exit()
            else:
                main()

        clock.tick(MAX_FPS)  # Limit the frame rate to 15 frames per second

        # Flip the display

        pygame.display.flip()  # Update the display

    # Done! Time to quit.

    pygame.quit()  # Quit the pygame module


def highlightSquares(screen, gs, validMoves, sqSelected):  # Highlight the valid moves for the selected piece
    if sqSelected != ():  # If a square has been selected
        row, col = sqSelected  # Get the row and column of the selected square
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):  # If the selected piece is white or black
            title = pygame.Surface((SQ_SIZE, SQ_SIZE))  # Create a surface for the title
            title.set_alpha(100)  # range 0 -255
            title.fill(pygame.Color('blue'))  # Fill the surface with blue
            screen.blit(title, (col * SQ_SIZE, row * SQ_SIZE))  # Blit the title to the screen
            title.fill(pygame.Color('Yellow'))  # Fill the surface with yellow
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(title, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def animateMove(move, screen, board,
                clock):  # Animate the move of a piece on the board and update the display every frame
    global colors
    deltaR = move.endRow - move.startRow  # Get the difference in row between the start and end of the move
    deltaC = move.endCol - move.startCol  # Get the difference in column between the start and end of the move
    fps = 6
    frameCount = (abs(deltaR) + abs(deltaC)) * fps  # Get the number of frames needed to animate the move

    for frame in range(frameCount + 1):
        frameRatio = frame / frameCount  # Get the ratio of the current frame to the total number of frames
        row, col = (move.startRow + deltaR * frameRatio,
                    move.startCol + deltaC * frameRatio)  # Get the row and column of the current frame
        draw_board(screen)  # Draw the board on the screen
        draw_pieces(screen, board)  # Draw the pieces on the screen
        color = colors[(move.endRow + move.endCol) % 2]  # Get the color of the current frame
        endSqr = pygame.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE,
                             SQ_SIZE)  # Get the rectangle of the end square of the move
        pygame.draw.rect(screen, color,
                         endSqr)  # Draw the end square of the move on the screen with the color of the current frame

        if move.pieceCaptured != '--':  # If the move captured a piece on the board
            screen.blit(IMAGES[move.pieceCaptured],
                        endSqr)  # Draw the captured piece on the end square of the move on the screen

        screen.blit(IMAGES[move.pieceMoved],
                    pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))  # Draw the moved piece on the screen
        pygame.display.flip()  # Update the display
        clock.tick(60)  # Limit the frame rate to 60 frames per second


def draw_game_state(screen, gs, validMoves, sqSelected):
    # drawing simple squares
    draw_board(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)

    # draw pieces on top of board
    draw_pieces(screen, gs.board)

    # TOD: draw highlighting ang available moves


def draw_board(screen):
    global colors
    colors = [pygame.Color("#eeeed2"), pygame.Color("#769656")]  # Set the colors of the board
    # colors = [pygame.Color("white"), pygame.Color("grey")]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]  # Get the color of the current square on the board
            pygame.draw.rect(screen, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE,
                                                        SQ_SIZE))  # Draw the current square on the screen


def draw_pieces(screen, board):  # Draw the pieces on the board on the screen with the correct color
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]  # Get the piece on the board at the current row and column
            if piece != "--":
                screen.blit(IMAGES[piece], pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE,
                                                       SQ_SIZE))  # Draw the piece on the screen with the correct color


if __name__ == '__main__':
    main()  # Call the main function

# Sanket Mundra - IIT2018189
import pygame                      # pygame is used to make the gui
from copy import deepcopy

pygame.font.init()

# constants
INF = 1000000000
width = height = 720
ROWS = COLS = 8
edge_len = height // ROWS
brown = (180, 114, 30)
white = (255, 255, 255)
black = (0, 0, 0)
cyan = (0, 255, 255)
# to display the king differently
king = pygame.transform.scale(pygame.image.load('king.png'), (50, 33))

'''
Checkers class handles the complete game:
    * whose turn is it
    * what piece is selected
    * where all can we move the piece
'''
class Checkers:
    def __init__(self):
        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Checkers Game')
        self.selected = None
        self.board = Board()
        self.turn = white        # first move of white piece
        self.all_moves = {}      # stores the current valid moves for a player currently playing

    # updates the game state
    def update(self):
        self.board.draw(self.window)
        pygame.display.update()

    # declares winner of the game
    def winner(self):
        if (self.board.brown <= 0):
            self.window.fill(white)
            f = pygame.font.SysFont('Comic Sans MS', 32)
            self.window.blit(f.render("White Won!!", False, brown), (width // 2, height // 2))
            pygame.display.update()
            pygame.time.delay(5000)
            return "White won!!"
        elif (self.board.white <= 0):
            self.window.fill(brown)
            f = pygame.font.SysFont('Comic Sans MS', 32)
            self.window.blit(f.render("Brown Won!!", False, white), (width // 2, height // 2))
            pygame.display.update()
            pygame.time.delay(5000)
            return "Brown won!!"
        else:
            return None

    # on first call, it finds all the moves and then on second call moves to that position
    def select(self, row, col):
        piece = self.board.get_piece(row, col)
        if (self.selected):
            self.move(piece, row, col)

        if (piece != 0 and piece.color == self.turn):
            self.selected = piece
            self.all_moves = self.board.get_all_moves(piece)
            return True

        return False

    # moves the previously selected piece to the given row and col
    def move(self, piece, row, col):
        if (piece == 0 and (row, col) in self.all_moves):
            self.board.move(self.selected, row, col)
            self.board.remove(self.all_moves[(row, col)])
            self.all_moves = {}
            if (self.turn == brown):
                self.turn = white
            else:
                self.turn = brown

    def computer(self, board):
        self.board = board
        self.all_moves = {}
        if (self.turn == brown):
            self.turn = white
        else:
            self.turn = brown

    def get_board(self):
        return self.board


'''
Piece class represents a checkers piece on the board:
    * drawing a piece on the board
    * moving specific piece
'''
class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.x = edge_len * self.col + (edge_len // 2)  # x-coordinate of center of the piece on the board
        self.y = edge_len * self.row + (edge_len // 2)  # y-coordinate of center of the piece on the board
        self.color = color
        self.is_king = False

    # draws a piece on the screen on respective positions
    def draw(self, window):
        rad = edge_len // 2 - 10
        pygame.draw.circle(window, self.color, (self.x, self.y), rad)
        # placing the is_king.png at that location
        if (self.is_king):
            window.blit(king, (self.x - king.get_width() // 2, self.y - king.get_height() // 2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.x = edge_len * self.col + (edge_len // 2)
        self.y = edge_len * self.row + (edge_len // 2)


'''
Board class represents a checkers board:
    * drawing the checkers board
    * drawing all the pieces on the board
    * hadles all the pieces moving
    * moving specific pieces
    * deleting (capturing) different pieces
'''
class Board:
    def __init__(self):
        self.board = []                            # 2D board of checker
        self.brown = self.white = 12               # #normal pieces of each type remaining on the bard
        self.brown_kings = self.white_kings = 0    # #kings of each type remaining on the board

        # initialise the self.board with correct pieces at correct positions
        for i in range(ROWS):
            temp = []
            for j in range(COLS):
                if (j % 2 == (i + 1) % 2):
                    # top three rows for brown pieces
                    if (i <= 2):
                        temp.append(Piece(i, j, brown))
                    # bottom three rows for white pieces
                    elif (i >= 5):
                        temp.append(Piece(i, j, white))
                    # middle 2 rows initially empty
                    else:
                        temp.append(0)
                # rest all positions are empty
                else:
                    temp.append(0)
            self.board.append(temp)

    # function to draw all the edge_lens on the window
    def draw_squares(self, window):
        window.fill(white)
        for i in range(ROWS):
            for j in range((i + 1) % 2, COLS, 2):
                pygame.draw.rect(window, black, (i * edge_len, j * edge_len, edge_len, edge_len))

    # to draw all the pieces on the board
    def draw(self, window):
        self.draw_squares(window)
        for i in range(ROWS):
            for j in range(COLS):
                if (self.board[i][j] != 0):
                    self.board[i][j].draw(window)

    # function to calculate the utility value at cut-off
    # giving priority to killing rather than making king was performing better
    def get_score(self):
        return (self.brown - self.white) + ((self.brown_kings - self.white_kings) / 2)

    # return all the pieces of a given color
    def get_all_pieces(self, color):
        pieces = []
        for i in range(ROWS):
            for j in range(COLS):
                if(self.board[i][j] != 0 and self.board[i][j].color == color):
                    pieces.append(self.board[i][j])
        return pieces

    # moves a piece on the new position on the board and updates board and piece accordingly
    def move(self, piece, new_row, new_col):
        # swapping the initial and final position values
        self.board[new_row][new_col] = self.board[piece.row][piece.col]
        self.board[piece.row][piece.col] = 0
        piece.move(new_row, new_col)

        if (new_row == 0 or new_row == ROWS - 1):
            piece.is_king = True
            if (piece.color == brown):
                self.brown_kings += 1
            else:
                self.white_kings += 1

    # removes list of pieces from the board
    def remove(self, pieces):
        for i in range(len(pieces)):
            self.board[pieces[i].row][pieces[i].col] = 0
            if (pieces[i] != 0):
                if (pieces[i].color == brown):
                    self.brown -= 1
                else:
                    self.white -= 1

    # returns all the moves possible as a dictionary
    # key = final position, values = list of pieces that can reach there
    def get_all_moves(self, piece):
        all_moves = {}

        # checking the feasible moves in downward direction
        if (piece.color == brown or piece.is_king):
            all_moves.update(self.move_left(piece.row + 1, min(piece.row + 3, ROWS), 1, piece.color, piece.col - 1))
            all_moves.update(self.move_right(piece.row + 1, min(piece.row + 3, ROWS), 1, piece.color, piece.col + 1))

        # checking the feasible moves in upward direction
        if (piece.color == white or piece.is_king):
            all_moves.update(self.move_left(piece.row - 1, max(piece.row - 3, -1), -1, piece.color, piece.col - 1))
            all_moves.update(self.move_right(piece.row - 1, max(piece.row - 3, -1), -1, piece.color, piece.col + 1))

        return all_moves

    # move in left diagonal
    def move_left(self, beg, end, inc, color, l, removed = []):
        moves = {}
        last_piece = []
        for i in range(beg, end, inc):
            if (l < 0):
                break

            if (self.board[i][l] == 0):
                if (len(removed) > 0 and len(last_piece) == 0):
                    break
                else:
                    moves[(i, l)] = last_piece + removed

                # next recursive call
                if (len(last_piece) > 0):
                    if (inc == -1):
                        row = max(i - 3, -1)
                    else:
                        row = min(i + 3, ROWS)
                    moves.update(self.move_left(i + inc, row, inc, color, l - 1, last_piece))
                    moves.update(self.move_right(i + inc, row, inc, color, l + 1, last_piece))
                break
            elif (self.board[i][l].color != color):
                last_piece.append(self.board[i][l])
            else:
                break
            l -= 1
        return moves

    # move in right diagonal
    def move_right(self, beg, end, inc, color, r, removed = []):
        moves = {}
        last_piece = []
        for i in range(beg, end, inc):
            if (r >= COLS):
                break

            if (self.board[i][r] == 0):
                if (len(removed) > 0 and len(last_piece) == 0):
                    break
                else:
                    moves[(i, r)] = last_piece + removed

                # next recursive call
                if (len(last_piece) > 0):
                    if (inc == -1):
                        row = max(i - 3, -1)
                    else:
                        row = min(i + 3, ROWS)
                    moves.update(self.move_left(i + inc, row, inc, color, r - 1, last_piece))
                    moves.update(self.move_right(i + inc, row, inc, color, r + 1, last_piece))
                break
            elif (self.board[i][r].color != color):
                last_piece.append(self.board[i][r])
            else:
                break
            r += 1
        return moves

    def get_piece(self, row, col):
        return self.board[row][col]

    def print_board(self):
        for i in range(ROWS):
            for j in range(COLS):
                if (self.board[i][j] != 0):
                    if(self.board[i][j].color == white):
                        print("W ", end = "")
                    else:
                        print("B ", end = "")
                else:
                    print("0 ", end = "")
            print("")

# mini-max function
def mini_max(current_board, depth, turn, checkers):
    # 3 = cut-off limit for the mini-max
    if (depth == 3 or checkers.winner() != None):
        return current_board.get_score(), current_board

    # MAX player turn
    if (turn == 1):
        moved_boards = get_moved_boards(current_board, brown, checkers)
        MAX = -INF
        best_moved_board = None
        for i in range(len(moved_boards)):
            val, temp = mini_max(moved_boards[i], depth + 1, 0, checkers)
            if (MAX < val):
                best_moved_board = moved_boards[i]
                MAX = val
        return MAX, best_moved_board

    # MIN player turn
    else:
        moved_boards = get_moved_boards(current_board, white, checkers)
        MIN = INF
        best_moved_board = None
        for i in range(len(moved_boards)):
            val, temp = mini_max(moved_boards[i], depth + 1, 1, checkers)
            if (MIN > val):
                best_moved_board = moved_boards[i]
                MIN = val
        return MIN, best_moved_board

# function to find all the next state boards
def get_moved_boards(board, color, checkers):
    new_boards = []
    all_pieces = board.get_all_pieces(color)
    for i in range(len(all_pieces)):
        all_moves = board.get_all_moves(all_pieces[i])
        '''
        print(all_moves)
        for i in all_moves:
            print(i, end = " ")
            if len(all_moves[i]) > 0:
                print(all_moves[i][0].row, all_moves[i][0].col)
        '''
        for move, remove in all_moves.items():
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(all_pieces[i].row, all_pieces[i].col)

            # applying changes
            temp_board.move(temp_piece, move[0], move[1])
            if (len(remove) > 0):
                temp_board.remove(remove)
            new_boards.append(temp_board)

    return new_boards

def main():
    run = True
    # setting up pygame display
    checkers = Checkers()

    while run:

        '''
        comment this if condition: if (checkers.turn == brown):
        as well as the below one: if (checkers.turn == white):
        to play human vs human
        '''
        if (checkers.turn == brown):
            value, new_board = mini_max(checkers.get_board(), 0, 1, checkers)
            checkers.computer(new_board)

        # uncomment this part for computer vs computer
        '''
        if (checkers.turn == white):
            value, new_board = mini_max(checkers.get_board(), 0, 0, checkers)
            checkers.computer(new_board)
        '''

        # destination point or goal reached
        if (checkers.winner() != None):
            run = False

        # run through all the events happening at the moment
        for i in pygame.event.get():
            if (i.type == pygame.QUIT):
                print("Terminated!!")
                run = False

            if (i.type == pygame.MOUSEBUTTONDOWN):
                pos_xy = pygame.mouse.get_pos()
                row = pos_xy[1] // edge_len
                col = pos_xy[0] // edge_len
                checkers.select(row, col)
        checkers.update()
    pygame.quit()

main()
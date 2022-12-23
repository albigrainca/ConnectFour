import math
import tkinter as tk
from tkinter import ttk
import numpy as np
import random as rnd
from threading import Thread
from queue import Queue

disk_color = ['white', 'red', 'orange']
disks = list()

player_type = ['human']
for i in range(42):
    player_type.append('AI: alpha-beta level ' + str(i + 1))

def player_playing(turn):
    return 2 - (turn % 2)

def alpha_beta_decision(board, turn, ai_level, queue, max_player):
    possible_moves = board.get_possible_moves()
    best_move = possible_moves[0]
    best_value = -math.inf
    nodes_explored = 0
    alpha = -math.inf
    beta = math.inf
    print("AI PLAYS : ALPHA BETA")
    print("TURN : {}".format(turn))
    for move in possible_moves:
        nodes_explored += 1
        update_board = board.copy()
        update_board.add_disk(move, player_playing(turn), update_display=False)
        value, nodes_explored = min_value(update_board, turn + 1, alpha, beta, nodes_explored, ai_level, max_player, 0)
        if value > best_value:
            best_value = value
            best_move = move
        alpha = max(alpha, best_value)
    print("NODES EXPLORED : {}".format(nodes_explored))
    print("BEST VALUE : {}".format(best_value))
    print("BEST MOVE : {}".format(best_move))
    print("score =" + str(board.eval(player_playing(turn))))
    print("player : " + str(player_playing(turn)))
    print()
    queue.put(best_move)

def min_value(board, turn, alpha, beta, nodes_explored, ai_level, max_player, depth_explored):
    if board.check_victory():
        return 1, nodes_explored
    elif depth_explored >= ai_level:
        return 0, nodes_explored
    possible_moves = board.get_possible_moves()
    value = math.inf
    for move in possible_moves:
        nodes_explored += 1
        update_board = board.copy()
        update_board.add_disk(move, player_playing(turn), update_display=False)
        max_val, nodes_explored = max_value(update_board, turn + 1, alpha, beta, nodes_explored, ai_level, max_player,
                                            depth_explored + 1)
        value = min(value, max_val)
        if value <= alpha:
            return value, nodes_explored
        beta = min(beta, value)
    return value, nodes_explored

def max_value(board, turn, alpha, beta, nodes_explored, ai_level, max_player, depth_explored):
    if board.check_victory():
        return -1, nodes_explored
    elif depth_explored >= ai_level:
        return 0, nodes_explored
    possible_moves = board.get_possible_moves()
    value = -math.inf
    for move in possible_moves:
        nodes_explored += 1
        update_board = board.copy()
        update_board.add_disk(move, player_playing(turn), update_display=False)
        min_val, nodes_explored = min_value(update_board, turn + 1, alpha, beta, nodes_explored, ai_level, max_player,
                                            depth_explored + 1)
        value = max(value, min_val)
        if value >= beta:
            return value, nodes_explored
        alpha = max(alpha, value)
    return value, nodes_explored

def eval_sequence(seq, player):
    # Count the number of disks of each player in the sequence
    count = [np.sum(seq == i) for i in range(1, 3)]

    # If the current player has 3 disks in a row, return a high score
    if count[player - 1] == 3:
        return 100
    # If the other player has 3 disks in a row, return a low score
    elif count[player % 2] == 3:
        return -100
    # If the current player has 2 disks in a row and an empty space, return a medium score
    elif count[player - 1] == 2 and 0 in count:
        return 10
    # If the other player has 2 disks in a row and an empty space, return a medium negative score
    elif count[player % 2] == 2 and 0 in count:
        return -10
    # Otherwise, return 0
    else:
        return 0

class Board:
    grid = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])

    def eval(self, player):
        score = 0
        # Iterate over the rows and columns of the grid
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                # Check for horizontal sequences of 3 or 4 disks
                if j <= self.grid.shape[1] - 3:
                    seq = self.grid[i, j:j + 3]
                    score += eval_sequence(seq, player)
                    if j <= self.grid.shape[1] - 4:
                        seq = self.grid[i, j:j + 4]
                        score += eval_sequence(seq, player)
                # Check for vertical sequences of 3 or 4 disks
                if i <= self.grid.shape[0] - 3:
                    seq = self.grid[i:i + 3, j]
                    score += eval_sequence(seq, player)
                    if i <= self.grid.shape[0] - 4:
                        seq = self.grid[i:i + 4, j]
                        score += eval_sequence(seq, player)
                # Check for diagonal sequences of 3 or 4 disks
                if i <= self.grid.shape[0] - 3 and j <= self.grid.shape[1] - 3:
                    seq = self.grid[i:i + 3, j:j + 3]
                    score += eval_sequence(seq, player)
                    if i <= self.grid.shape[0] - 4 and j <= self.grid.shape[1] - 4:
                        seq = self.grid[i:i + 4, j:j + 4]
                        score += eval_sequence(seq, player)
        # Return the score
        return score

    def copy(self):
        new_board = Board()
        new_board.grid = np.array(self.grid, copy=True)
        return new_board

    def reinit(self):
        self.grid.fill(0)
        for i in range(7):
            for j in range(6):
                canvas1.itemconfig(disks[i][j], fill=disk_color[0])

    def get_possible_moves(self):
        possible_moves = list()
        if self.grid[3][5] == 0:
            possible_moves.append(3)
        for shift_from_center in range(1, 4):
            if self.grid[3 + shift_from_center][5] == 0:
                possible_moves.append(3 + shift_from_center)
            if self.grid[3 - shift_from_center][5] == 0:
                possible_moves.append(3 - shift_from_center)
        return possible_moves

    def add_disk(self, column, player, update_display=True):
        for j in range(6):
            if self.grid[column][j] == 0:
                break
        self.grid[column][j] = player
        if update_display:
            canvas1.itemconfig(disks[column][j], fill=disk_color[player])

    def column_filled(self, column):
        return self.grid[column][5] != 0

    def check_victory(self):
        # Horizontal alignment check
        for line in range(6):
            for horizontal_shift in range(4):
                if self.grid[horizontal_shift][line] == self.grid[horizontal_shift + 1][line] == \
                        self.grid[horizontal_shift + 2][line] == self.grid[horizontal_shift + 3][line] != 0:
                    return True
        # Vertical alignment check
        for column in range(7):
            for vertical_shift in range(3):
                if self.grid[column][vertical_shift] == self.grid[column][vertical_shift + 1] == \
                        self.grid[column][vertical_shift + 2] == self.grid[column][vertical_shift + 3] != 0:
                    return True
        # Diagonal alignment check
        for horizontal_shift in range(4):
            for vertical_shift in range(3):
                if self.grid[horizontal_shift][vertical_shift] == self.grid[horizontal_shift + 1][vertical_shift + 1] == \
                        self.grid[horizontal_shift + 2][vertical_shift + 2] == self.grid[horizontal_shift + 3][vertical_shift + 3] != 0:
                    return True
                elif self.grid[horizontal_shift][5 - vertical_shift] == self.grid[horizontal_shift + 1][4 - vertical_shift] == \
                        self.grid[horizontal_shift + 2][3 - vertical_shift] == self.grid[horizontal_shift + 3][2 - vertical_shift] != 0:
                    return True
        return False


class Connect4:

    def __init__(self):
        self.board = Board()
        self.human_turn = False
        self.turn = 1
        self.players = (0, 0)
        self.ai_move = Queue()

    def current_player(self):
        return 2 - (self.turn % 2)

    def launch(self):
        self.board.reinit()
        self.turn = 0
        information['fg'] = 'black'
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        self.human_turn = False
        self.players = (combobox_player1.current(), combobox_player2.current())
        self.handle_turn()

    def move(self, column):
        if not self.board.column_filled(column):
            self.board.add_disk(column, self.current_player())
            self.handle_turn()

    def click(self, event):
        if self.human_turn:
            column = event.x // row_width
            self.move(column)

    def ai_turn(self, ai_level):
        Thread(target=alpha_beta_decision,
               args=(self.board, self.turn, ai_level, self.ai_move, self.current_player(),)).start()
        self.ai_wait_for_move()

    def ai_wait_for_move(self):
        if not self.ai_move.empty():
            self.move(self.ai_move.get())
        else:
            window.after(100, self.ai_wait_for_move)

    def handle_turn(self):
        self.human_turn = False
        if self.board.check_victory():
            information['fg'] = 'red'
            information['text'] = "Player " + str(self.current_player()) + " wins !"
            return
        elif self.turn >= 42:
            information['fg'] = 'red'
            information['text'] = "This a draw !"
            return
        self.turn = self.turn + 1
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        if self.players[self.current_player() - 1] != 0:
            self.human_turn = False
            self.ai_turn(self.players[self.current_player() - 1])
        else:
            self.human_turn = True


game = Connect4()

# Graphical settings
width = 700
row_width = width // 7
row_height = row_width
height = row_width * 6
row_margin = row_height // 10

window = tk.Tk()
window.title("Connect 4")
canvas1 = tk.Canvas(window, bg="blue", width=width, height=height)

# Drawing the grid
for i in range(7):
    disks.append(list())
    for j in range(5, -1, -1):
        disks[i].append(canvas1.create_oval(row_margin + i * row_width, row_margin + j * row_height,
                                            (i + 1) * row_width - row_margin,
                                            (j + 1) * row_height - row_margin, fill='white'))

canvas1.grid(row=0, column=0, columnspan=2)

information = tk.Label(window, text="")
information.grid(row=1, column=0, columnspan=2)

label_player1 = tk.Label(window, text="Player 1: ")
label_player1.grid(row=2, column=0)
combobox_player1 = ttk.Combobox(window, state='readonly')
combobox_player1.grid(row=2, column=1)

label_player2 = tk.Label(window, text="Player 2: ")
label_player2.grid(row=3, column=0)
combobox_player2 = ttk.Combobox(window, state='readonly')
combobox_player2.grid(row=3, column=1)

combobox_player1['values'] = player_type
combobox_player1.current(0)
combobox_player2['values'] = player_type
combobox_player2.current(6)

button2 = tk.Button(window, text='New game', command=game.launch)
button2.grid(row=4, column=0)

button = tk.Button(window, text='Quit', command=window.destroy)
button.grid(row=4, column=1)

# Mouse handling
canvas1.bind('<Button-1>', game.click)

window.mainloop()
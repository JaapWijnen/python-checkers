import curses
from curses import wrapper
import tkinter.messagebox
from board import Board
from consts import *


def initCurses():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(4, 43, 43)  # Dark cyan
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(7, curses.COLOR_WHITE, 22)  # Dark green
    curses.init_pair(8, curses.COLOR_BLACK, 22)
    curses.init_pair(9, curses.COLOR_CYAN, curses.COLOR_CYAN)
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.curs_set(0)


def main(stdscr):
    stdscr.clear()
    initCurses()
    stdscr.attron(curses.A_BOLD)

    board = Board((10, 10))
    board.setupGame(20)

    board.checkCaptures(WHITE)
    board.draw(stdscr)

    while(True):
        key = stdscr.getch()

        if key == curses.KEY_UP:
            if board.cursor[1] > 0:
                board.cursor[1] -= 1
        elif key == curses.KEY_DOWN:
            if board.cursor[1] < board.size[1] - 1:
                board.cursor[1] += 1
        elif key == curses.KEY_RIGHT:
            if board.cursor[0] < board.size[0] - 1:
                board.cursor[0] += 1
        elif key == curses.KEY_LEFT:
            if board.cursor[0] > 0:
                board.cursor[0] -= 1
        elif key == 10:  # Enter key
            board.select()
        elif key == 127:  # Backspace key
            board.tSelect = []
        elif key == 97:  # A key for debug purposes
            tkinter.messagebox.showinfo("info", board.tSelect)

        board.draw(stdscr)


wrapper(main)

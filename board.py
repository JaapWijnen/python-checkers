from consts import *
import curses
import tkinter.messagebox


def setColor(scr, group, hgroup, cgroup, highlight):
    if highlight == HIGHLIGHT:
        scr.attron(curses.color_pair(hgroup))
    elif highlight == CURSOR:
        scr.attron(curses.color_pair(cgroup))
    elif highlight == MOVE:
        scr.attron(curses.color_pair(9))
    elif highlight == SELECT_MOVE:
        scr.attron(curses.color_pair(4))
    else:
        scr.attron(curses.color_pair(group))


class Board:
    def __init__(self, size):
        self.size = size
        self.tiles = []
        self.currentPlayer = WHITE
        self.win = 0

        self.cursor = [0, size[1] - 1]
        self.tSelect = []
        self.captures = []

        # Init tiles with all zeros
        for j in range(size[1]):
            row = []
            for i in range(size[0]):
                row.append(0)
            self.tiles.append(row)

    def getTile(self, pos):
        return self.tiles[pos[1]][pos[0]]

    def setTile(self, pos, tile):
        self.tiles[pos[1]][pos[0]] = tile

    def draw(self, scr):
        # Draw grid with stones
        for j in range(self.size[1]):
            for i in range(self.size[0]):
                self.drawSquare(scr, (i, j), NO_HIGHLIGHT)

        if self.win == WHITE:
            scr.attron(curses.color_pair(10))
            scr.addstr(14, 25, 'WHITE WINS')
        elif self.win == BLACK:
            scr.attron(curses.color_pair(10))
            scr.addstr(14, 25, 'BLACK WINS')

        if not self.tSelect:  # Draw capture overlay if no capture is selected
            cOverlay = [t[0] for t in self.captures]

            for pos in cOverlay:
                self.drawSquare(scr, (pos[0], pos[1]), HIGHLIGHT)

        self.drawCursor(scr)

        # Draw possible moves of selected tile
        if not self.captures:  # normal moves
            if self.tSelect:  # Check if a tile is selected
                t = self.tSelect
                self.drawSquare(scr, t[0], HIGHLIGHT)
                self.drawCursor(scr)
                for sq in t[1]:
                    if sq == tuple(self.cursor):
                        self.drawSquare(scr, sq, SELECT_MOVE)
                    else:
                        self.drawSquare(scr, sq, MOVE)
            else:  # Check moves at current cursor position if no tile is selected
                pos = (self.cursor[0], self.cursor[1])
                p = self.currentPlayer
                moves = self.checkMove(pos, p)
                if moves:
                    for move in moves:  # Draw all moves
                        self.drawSquare(scr, move, MOVE)

        else:  # Must capture stone of opponent
            if not self.tSelect:  # No capture selected yet
                for cap in self.captures:
                    if cap[0] == tuple(self.cursor):
                        for item in cap[2]:
                            for pos in item:
                                self.drawSquare(scr, pos, MOVE)
            else:  # Specific capture selected
                spos = self.tSelect[0]
                self.drawSquare(scr, spos, HIGHLIGHT)
                self.drawCursor(scr)
                for item in self.tSelect[2]:
                    for move in item:
                        if move == tuple(self.cursor):
                            self.drawSquare(scr, move, SELECT_MOVE)
                        else:
                            self.drawSquare(scr, move, MOVE)

        scr.refresh()

    def nextPlayer(self): # Switch players
        if self.currentPlayer == WHITE:
            self.currentPlayer = BLACK
        else:
            self.currentPlayer = WHITE

    def drawCursor(self, scr):
        cx = self.cursor[0]
        cy = self.cursor[1]
        self.drawSquare(scr, (cx, cy), CURSOR)

    def drawSquare(self, scr, pos, highlight):
        ttype = self.getTile(pos)
        x = pos[0] * 6
        y = pos[1] * 3
        if ttype == EMPTY:
            if (pos[0] + pos[1]) % 2 == 0:
                setColor(scr, 1, 7, 5, highlight)
            else:
                setColor(scr, 2, 7, 5, highlight)
            scr.addstr(y,     x, '      ')
            scr.addstr(y + 1, x, '      ')
            scr.addstr(y + 2, x, '      ')
        if ttype == BLACK:
            setColor(scr, 3, 8, 6, highlight)
            scr.addstr(y,   x, '      ')
            scr.addstr(y + 1, x, '  ()  ')
            scr.addstr(y + 2, x, '      ')
        if ttype == BLACK_KING:
            setColor(scr, 3, 8, 6, highlight)
            scr.addstr(y,     x, '      ')
            scr.addstr(y + 1, x, ' (()) ')
            scr.addstr(y + 2, x, '      ')
        if ttype == WHITE:
            setColor(scr, 1, 7, 5, highlight)
            scr.addstr(y,     x, '      ')
            scr.addstr(y + 1, x, '  ()  ')
            scr.addstr(y + 2, x, '      ')
        if ttype == WHITE_KING:
            setColor(scr, 1, 7, 5, highlight)
            scr.addstr(y,     x, '      ')
            scr.addstr(y + 1, x, ' (()) ')
            scr.addstr(y + 2, x, '      ')

    def setupGame(self, stonesPerPlayer):
        width = self.size[0]
        height = self.size[1]

        for i in range(stonesPerPlayer):
            # setup black stones
            bx = (2 * i) % width + int(2 * i / width) % 2
            by = int((2 * i) / width)
            self.setTile((bx, by), BLACK)

            # setup white stones
            wx = (2 * i) % width + 1 - int(2 * i / width) % 2
            wy = height - 1 - int((2 * i) / width)
            self.setTile((wx, wy), WHITE)

    def withinBounds(self, pos):
        if pos[0] < 0 or pos[0] > self.size[0] - 1:
            return False
        if pos[1] < 0 or pos[1] > self.size[1] - 1:
            return False
        return True

    def checkCaptures(self, player):
        captures = []
        playerK = player + 1

        for j in range(self.size[1]):
            for i in range(self.size[0]):
                pos = (i, j)
                t = self.getTile(pos)
                # Check if stone belongs to player
                if t == player:
                    cap = self.checkNormalCapture(pos, player)
                    if cap is not None:
                        captures.append(cap)

                # Check if stone belongs to player and is king
                elif t == player + 1:
                    cap = self.checkKingCapture(pos, player)
                    if cap is not None:
                        captures.append(cap)
                # Current Tile contains no stone or stone which doesn't belong to player
        self.captures = captures

    def checkKingCapture(self, pos, player):
        opp = (player + 2) % 4
        oppK = opp + 1

        capPosses = []
        newPossesses = []

        newPosses = []

        ul = tuple(map(sum, zip(pos, UP_LEFT)))
        foundStone = False
        oppStone = None
        while ul[0] >= 0 and ul[1] >= 0:
            if self.withinBounds(ul):
                t = self.getTile(ul)
                if foundStone:
                    if t == EMPTY:
                        newPosses.append(ul)
                    else:
                        break
                else:
                    if t == opp or t == oppK:
                        foundStone = True
                        oppStone = ul

                ul = tuple(map(sum, zip(ul, UP_LEFT)))
        if newPosses:
            newPossesses.append(newPosses)
            capPosses.append(oppStone)
        newPosses = []

        ur = tuple(map(sum, zip(pos, UP_RIGHT)))
        foundStone = False
        oppStone = None
        while ur[0] < self.size[0] and ur[1] >= 0:
            if self.withinBounds(ur):
                t = self.getTile(ur)
                if foundStone:
                    if t == EMPTY:
                        newPosses.append(ur)
                    else:
                        break
                else:
                    if t == opp or t == oppK:
                        foundStone = True
                        oppStone = ur

                ur = tuple(map(sum, zip(ur, UP_RIGHT)))
        if newPosses:
            newPossesses.append(newPosses)
            capPosses.append(oppStone)
        newPosses = []

        dl = tuple(map(sum, zip(pos, DOWN_LEFT)))
        foundStone = False
        oppStone = None
        while dl[0] >= 0 and dl[1] < self.size[1]:
            if self.withinBounds(dl):
                t = self.getTile(dl)
                if foundStone:
                    if t == EMPTY:
                        newPosses.append(dl)
                    else:
                        break
                else:
                    if t == opp or t == oppK:
                        foundStone = True
                        oppStone = dl

                dl = tuple(map(sum, zip(dl, DOWN_LEFT)))
        if newPosses:
            newPossesses.append(newPosses)
            capPosses.append(oppStone)
        newPosses = []

        dr = tuple(map(sum, zip(pos, DOWN_RIGHT)))
        foundStone = False
        oppStone = None
        while dr[0] < self.size[0] and dr[1] < self.size[1]:
            if self.withinBounds(dr):
                t = self.getTile(dr)
                if foundStone:
                    if t == EMPTY:
                        newPosses.append(dr)
                    else:
                        break
                else:
                    if t == opp or t == oppK:
                        foundStone = True
                        oppStone = dr

                dr = tuple(map(sum, zip(dr, DOWN_RIGHT)))
        if newPosses:
            newPossesses.append(newPosses)
            capPosses.append(oppStone)

        if capPosses:
            return (pos, capPosses, newPossesses)

    def checkNormalCapture(self, pos, player):
        opp = (player + 2) % 4
        oppK = opp + 1
        ul = tuple(map(sum, zip(pos, UP_LEFT)))
        ur = tuple(map(sum, zip(pos, UP_RIGHT)))
        dl = tuple(map(sum, zip(pos, DOWN_LEFT)))
        dr = tuple(map(sum, zip(pos, DOWN_RIGHT)))
        surrounds = [ul, ur, dl, dr]
        capPosses = []
        newPosses = []
        for capPos in surrounds:
            if self.withinBounds(capPos):
                cap = self.getTile(capPos)
                if cap == opp or cap == oppK:
                    dx = capPos[0] - pos[0]
                    dy = capPos[1] - pos[1]
                    newPos = (capPos[0] + dx, capPos[1] + dy)
                    if self.withinBounds(newPos):
                        if self.getTile(newPos) == EMPTY:
                            capPosses.append(capPos)
                            newPosses.append(newPos)
        if capPosses and newPosses:
            return (pos, capPosses, [newPosses])

    def checkMove(self, pos, player):
        playerKing = player + 1
        t = self.getTile(pos)
        result = []

        ul = tuple(map(sum, zip(pos, UP_LEFT)))
        ur = tuple(map(sum, zip(pos, UP_RIGHT)))
        dl = tuple(map(sum, zip(pos, DOWN_LEFT)))
        dr = tuple(map(sum, zip(pos, DOWN_RIGHT)))

        if t == player:
            if player == WHITE:
                options = [ul, ur]
                for op in options:
                    if self.withinBounds(op):
                        opt = self.getTile(op)
                        if opt == EMPTY:
                            result.append(op)

            else:
                options = [dl, dr]
                for op in options:
                    if self.withinBounds(op):
                        opt = self.getTile(op)
                        if opt == EMPTY:
                            result.append(op)

        elif t == playerKing:
            options = [ul, ur, dl, dr]
            for op in options:
                dx = op[0] - pos[0]
                dy = op[1] - pos[1]
                tmp = [op[0], op[1]]
                while self.withinBounds(tuple(tmp)):
                    if self.getTile(tmp) != EMPTY:
                        break
                    else:
                        result.append(tuple(tmp))
                        tmp[0] += dx
                        tmp[1] += dy

        return result

    def select(self):
        if not self.captures:  # Normal select
            if self.tSelect:
                for t in self.tSelect[1]:
                    if t == tuple(self.cursor):
                        oldPos = self.tSelect[0]
                        temp = self.getTile(oldPos)
                        self.setTile(oldPos, EMPTY)
                        self.setTile(t, temp)
                        self.endTurn()
            else:
                x = self.cursor[0]
                y = self.cursor[1]
                moves = self.checkMove((x, y), self.currentPlayer)
                if moves:
                    self.tSelect = ((x, y), moves)

        else:  # Can only select stones that can capture
            if self.tSelect:
                pos = self.tSelect[0]
                t = self.getTile(pos)
                captures = self.tSelect[1]
                newPosses = self.tSelect[2]
                for idx, cap in enumerate(captures):
                    for newPos in newPosses[idx]:
                        if newPos == tuple(self.cursor):
                            self.setTile(newPos, t)
                            self.setTile(cap, EMPTY)
                            self.setTile(pos, EMPTY)

                            newCap = self.checkNormalCapture(
                                (newPos[0], newPos[1]), self.currentPlayer)

                            if newCap is not None:
                                self.captures = [newCap]
                                self.tSelect = newCap
                            else:
                                self.endTurn()

            else:
                for cap in self.captures:
                    if cap[0] == tuple(self.cursor):
                        self.tSelect = cap

    def endTurn(self):
        self.tSelect = []
        self.captures = []
        for i in range(5):
            xb = 2 * i + 1
            yb = self.size[1] - 1
            tb = self.getTile((xb, yb))
            if tb == BLACK:
                self.setTile((xb, xy), BLACK_KING)
            xw = 2 * i
            yw = 0
            tw = self.getTile((xw, yw))
            if tw == WHITE:
                self.setTile((xw, yw), WHITE_KING)
        self.checkWin()
        self.nextPlayer()
        self.checkCaptures(self.currentPlayer)

    def checkWin(self):
        black = 0
        white = 0
        for j in range(self.size[1]):
            for i in range(self.size[0]):
                t = self.getTile((i, j))
                if t == BLACK or t == BLACK_KING:
                    black += 1
                elif t == WHITE or t == WHITE_KING:
                    white += 1

        if black == 0:
            self.win = WHITE
        elif white == 0:
            self.win = BLACK

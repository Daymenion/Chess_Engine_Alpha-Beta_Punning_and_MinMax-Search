#
# Created by: Daymenion 16/05/2022
#
# this program under the GNU General Public License v3.0 license.

import tkinter as tk
from tkinter import simpledialog


class GameState:
    def __init__(self):

        # board setup (8x8 board with empty squares)
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.whiteToMove = True  # white to move first
        self.moveLog = []  # list of moves made
        self.whiteKingLocation = (7, 4)  # white king location (row, col)
        self.blackKingLocation = (0, 4)  # black king location (row, col)
        self.possibleMoveFunctions = {'P': self.getPawnMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves,
                                      'R': self.getRookMoves, 'Q': self.getQueenMoves,
                                      'K': self.getKingMoves}  # dictionary of possible move functions for each piece
        self.enpassantPossible = ()  # the square for enpassant possible
        self.checkMate = False  # checkmate flag
        self.staleMate = False  # stalemate flag

        self.inCheck = False  # check flag
        self.pins = []  # list of pins for each piece
        self.checks = []  # list of checks for each piece (for AI)

        self.currentCastlingRights = CastleRights(True, True, True, True)  # wks, wqs, bks, bqs (True = can castle)
        # Deep Copy Rights object
        self.castleRightsLog = [
            CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs,
                         self.currentCastlingRights.bqs)]  # wks, wqs, bks, bqs (True can castle) list of rights objects

    # Simple Chess Moves: Pawns, Knights, Bishops, Rooks, Queens, Kings (no castling)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"  # remove piece from start square

        self.board[move.endRow][move.endCol] = move.pieceMoved  # add piece to end square

        self.moveLog.append(move)  # add move to move log
        self.whiteToMove = not self.whiteToMove  # switch turn to next player

        if move.pieceMoved == 'wK':  # if white king moved
            self.whiteKingLocation = (move.endRow, move.endCol)  # update white king location
        elif move.pieceMoved == 'bK':  # if black king moved
            self.blackKingLocation = (move.endRow, move.endCol)  # update black king location

        # For Pawn Promotion:
        if move.isPawnPromotion:
            if move.AIPlaying:
                self.board[move.endRow][move.endCol] = move.pieceMoved[
                                                           0] + move.AIPromotionKey  # add piece to end square
            else:
                ROOT = tk.Tk()

                ROOT.withdraw()
                # the input dialog

                while True:
                    promotedPiece = simpledialog.askstring("Game Mode:", "Please select a game mode: \nQ)Queen(Q) "
                                                                         "\nR)Rook(R) \nB)Bishop(B) \nN)Knight(N)",
                                                           initialvalue="Q")  # ask for promotion piece

                    print(promotedPiece)
                    promotion = ['Q', 'R', 'B', 'N']
                    if promotedPiece in promotion:
                        self.board[move.endRow][move.endCol] = move.pieceMoved[
                                                                   0] + promotedPiece  # add piece to end square
                        break
                    else:
                        print("invalid Promotion")

        # Update Enpassant Variable only if Pawn Moves Two Squares:
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:  # if pawn moved two squares
            self.enpassantPossible = ((move.startRow + move.endRow) // 2,
                                      move.startCol)  # update enpassant variable
        else:
            self.enpassantPossible = ()  # reset enpassant variable

        # For Enpassant Move:
        if move.isEnpassantMove:  # if enpassant move is true
            self.board[move.startRow][move.endCol] = '--'  # remove captured pawn from board

        # For Castle Move:
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # King side Castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                    move.endCol + 1]  # move rook to new square
                self.board[move.endRow][move.endCol + 1] = '--'
            else:  # Queen Side Castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                    move.endCol - 2]  # move rook to new square
                self.board[move.endRow][move.endCol - 2] = '--'

        # Updating Castle Rights on Each Move:
        self.updateCastleRights(move)
        self.castleRightsLog.append(
            CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks, self.currentCastlingRights.wqs,
                         self.currentCastlingRights.bqs))  # add castle rights to log

    def undoMove(self):  # undo move function

        if len(self.moveLog) != 0:

            move = self.moveLog.pop()  # pop last move from log  (undo last move)

            self.board[move.startRow][move.startCol] = move.pieceMoved  # move piece back to start square
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # move piece back to end square
            self.whiteToMove = not self.whiteToMove  # switching the turn
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)  # update white king location
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)  # update black king location

            # Undo Enpassant Move
            if move.isEnpassantMove:
                self.board[move.endRow][
                    move.endCol] = '--'  # Making The Ending square blank as the pawn captured was not in that square
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # move pawn back to start square
                self.enpassantPossible = (move.endRow, move.endCol)  # update enpassant variable

            # Undo the captured
            if move.pieceMoved[1] == 'P' and abs(
                    move.startRow - move.endRow) == 2:  # if pawn moved two squares and captured
                self.enpassantPossible = ()  # reset enpassant variable

            # undo Castle Rights
            self.castleRightsLog.pop()  # pop last castle rights from log
            newRights = self.castleRightsLog[-1]  # get last castle rights from log
            self.currentCastlingRights = CastleRights(newRights.wks, newRights.bks, newRights.wqs,
                                                      newRights.bqs)  # update current castle rights

            # undo Castle Move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # King side Castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                        move.endCol - 1]  # move rook back to new square
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # Queen Side Castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][
                        move.endCol + 1]  # move rook back to new square
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkMate = False  # reset checkmate variable
            self.staleMate = False  # reset stalemate variable

    def updateCastleRights(self, move):  # update castle rights function
        if move.pieceMoved == 'wK':  # if white king moved
            self.currentCastlingRights.wks = False  # set white king side castle to false
            self.currentCastlingRights.wqs = False  # set white queen side castle to false
        elif move.pieceMoved == 'bK':  # if black king moved
            self.currentCastlingRights.bks = False  # set black king side castle to false
            self.currentCastlingRights.bqs = False  # set black queen side castle to false
        elif move.pieceMoved == 'wR':  # if white rook moved
            if move.startRow == 7:  # if white rook moved from row 7
                if move.startCol == 0:  # if white rook moved from col 0
                    self.currentCastlingRights.wqs = False  # set white queen side castle to false
                elif move.startCol == 7:  # if white rook moved from col 7
                    self.currentCastlingRights.wks = False  # set white king side castle to false
        elif move.pieceMoved == 'bR':  # if black rook moved
            if move.startRow == 0:  # if black rook moved from row 0
                if move.startCol == 0:  # if black rook moved from col 0
                    self.currentCastlingRights.bqs = False  # set black queen side castle to false
                elif move.startCol == 7:  # if black rook moved from col 7
                    self.currentCastlingRights.bks = False  # set black king side castle to false
        if move.pieceCaptured == 'wR':  # if white rook captured
            if move.startRow == 7:  # if white rook moved from row 7
                if move.startCol == 0:  # if white rook moved from col 0
                    self.currentCastlingRights.wqs = False  # set white queen side castle to false
                elif move.startCol == 7:  # if white rook moved from col 7
                    self.currentCastlingRights.wks = False  # set white king side castle to false
        elif move.pieceCaptured == 'bR':  # if black rook captured
            if move.startRow == 0:  # if black rook moved from row 0
                if move.startCol == 0:  # if black rook moved from col 0
                    self.currentCastlingRights.bqs = False  # set black queen side castle to false
                elif move.startCol == 7:  # if black rook moved from col 7
                    self.currentCastlingRights.bks = False  # set black king side castle to false

    # every possible move that a piece can make without the concern of other pieces
    def getAllPossibleMoves(self):  # get all possible moves function

        possibleMoves = []  # list of possible moves

        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]  # get the first character of the piece
                if (turn == 'w' and self.whiteToMove) or (
                        turn == 'b' and not self.whiteToMove):  # if it's correct turn and the piece is white or black
                    piece = self.board[row][col][1]  # get the second character of the piece
                    self.possibleMoveFunctions[piece](row, col,
                                                      possibleMoves)  # call the function that corresponds to the piece

        return possibleMoves  # return the list of possible moves

    def getValidMoves(self):  # get valid moves function  (returns a list of valid moves)

        moves = []  # list of valid moves
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()  # check for pins and checks

        if self.whiteToMove:  # if it is white's turn
            kingRow = self.whiteKingLocation[0]  # get the row of the white king
            kingCol = self.whiteKingLocation[1]  # get the col of the white king
            allyColor = 'w'  # set the color of the pieces to white
        else:  # if it is black's turn
            kingRow = self.blackKingLocation[0]  # get the row of the black king
            kingCol = self.blackKingLocation[1]  # get the col of the black king
            allyColor = 'b'  # set the color of the pieces to black

        if self.inCheck:  # if the king is in check  (if the king is in check, then the king can't move)
            if len(self.checks) == 1:  # if there is only one check
                moves = self.getAllPossibleMoves()  # get all possible moves
                check = self.checks[0]  # get the check
                checkRow = check[0]  # get the row of the check
                checkCol = check[1]  # get the col of the check
                pieceChecking = self.board[checkRow][checkCol]  # get the piece that is checking the king
                validSquares = []  # list of valid squares
                if pieceChecking[0] == 'N':  # if the piece checking the king is a knight
                    validSquares = [(checkRow, checkCol)]  # add the check square to the list of valid squares
                else:
                    for i in range(1, 8):  # for each direction
                        validSquare = (kingRow + check[2] * i, kingCol + check[
                            3] * i)  # get the valid square based on the direction of the check
                        validSquares.append(validSquare)  # add the valid square to the list of valid squares
                        if validSquare[0] == checkRow and validSquare[
                            1] == checkCol:  # if the valid square is the check square
                            break  # break out of the loop
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':  # if the piece moved is not a king
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:  # if the end square
                            # is not a valid square for the piece to move to
                            moves.remove(moves[i])  # remove the move from the list of valid moves
            else:
                self.getKingMoves(kingRow, kingCol, moves)  # get the king moves
        else:
            moves = self.getAllPossibleMoves()  # get possible moves (if the king isn't in check, then king can move)
            self.getCastleMoves(kingRow, kingCol, moves,
                                allyColor)  # get the castle moves (if the king is not in check, then the king can move)

        return moves  # return the list of valid moves

    def squareUnderAttack(self, row, col):  # square under attack function (returns true if the square is under attack)

        self.whiteToMove = not self.whiteToMove  # switch to opponent
        oppMoves = self.getAllPossibleMoves()  # get all possible moves for the opponent

        self.whiteToMove = not self.whiteToMove  # switch back to the original color

        for move in oppMoves:  # for each move
            if move.endRow == row and move.endCol == col:  # if the move ends at the square under attack
                return True  # return true

        return False

    def getPawnMoves(self, row, col, possibleMoves):  # get pawn moves function
        piecePinned = False  # if the piece is pinned
        pinDirection = ()  # direction of the pin
        for i in range(len(self.pins) - 1, -1, -1):  # for each pin in the list of pins
            if self.pins[i][0] == row and self.pins[i][1] == col:  # if the pin is at the square under attack
                piecePinned = True  # set piecePinned to true
                pinDirection = (self.pins[i][2], self.pins[i][3])  # get the direction of the pin
                self.pins.remove(self.pins[i])  # remove the pin from the list of pins
                break

        # for white pieces
        if self.whiteToMove:

            # move up 1 or 2 squres
            if self.board[row - 1][col] == "--":  # if the square above is empty
                if not piecePinned or pinDirection == (-1, 0):  # if the piece isn't pinned or the pin direction is up
                    possibleMoves.append(
                        Move((row, col), (row - 1, col), self.board))  # add the move to the list of possible moves
                    if row == 6 and self.board[row - 2][
                        col] == "--":  # if the pawn is on its starting square and the square above it is empty
                        possibleMoves.append(
                            Move((row, col), (row - 2, col), self.board))  # add the move to the list of possible moves

            # move diagonals
            if col - 1 >= 0:  # if the square to the left is on the board
                if self.board[row - 1][col - 1][0] == 'b':  # if the square to the left is black
                    if not piecePinned or pinDirection == (
                    -1, -1):  # if the piece isn't pinned or the pin direction is up left
                        possibleMoves.append(Move((row, col), (row - 1, col - 1),
                                                  self.board))  # add the move to the list of possible moves
                if (row - 1, col - 1) == self.enpassantPossible:  # if the square to the left is the enpassant square
                    possibleMoves.append(Move((row, col), (row - 1, col - 1), self.board,
                                              isEnpassantMove=True))  # add the move to the list of possible moves

            if col + 1 <= 7:  # if the square to the right is on the board
                if self.board[row - 1][col + 1][0] == 'b':  # if the square to the right is black
                    if not piecePinned or pinDirection == (
                    -1, 1):  # if the piece isn't pinned or the pin direction is up right
                        possibleMoves.append(Move((row, col), (row - 1, col + 1),
                                                  self.board))  # add the move to the list of possible moves
                if (row - 1, col + 1) == self.enpassantPossible:  # if the square to the right is the enpassant square
                    possibleMoves.append(Move((row, col), (row - 1, col + 1), self.board,
                                              isEnpassantMove=True))  # add the move to the list of possible moves

        # for black pieces

        else:

            # move up 1 or 2 squres
            if self.board[row + 1][col] == "--":  # if the square below is empty
                if not piecePinned or pinDirection == (1, 0):  # if the piece isn't pinned or the pin direction is down
                    possibleMoves.append(
                        Move((row, col), (row + 1, col), self.board))  # add the move to the list of possible moves
                    if row == 1 and self.board[row + 2][
                        col] == "--":  # if the pawn is on its starting square and the square below it is empty
                        possibleMoves.append(
                            Move((row, col), (row + 2, col), self.board))  # add the move to the list of possible moves

            # move diagonals
            if col - 1 >= 0:  # if the square to the left is on the board
                if self.board[row + 1][col - 1][0] == 'w':  # if the square to the left is white
                    if not piecePinned or pinDirection == (
                    1, 1):  # if the piece isn't pinned or the pin direction is down left
                        possibleMoves.append(Move((row, col), (row + 1, col - 1),
                                                  self.board))  # add the move to the list of possible moves
                if (row + 1, col - 1) == self.enpassantPossible:  # if the square to the left is the enpassant square
                    possibleMoves.append(Move((row, col), (row + 1, col - 1), self.board,
                                              isEnpassantMove=True))  # add the move to the list of possible moves

            if col + 1 <= 7:  # if the square to the right is on the board
                if self.board[row + 1][col + 1][0] == 'w':  # if the square to the right is white
                    if not piecePinned or pinDirection == (
                    1, -1):  # if the piece isn't pinned or the pin direction is down right
                        possibleMoves.append(Move((row, col), (row + 1, col + 1),
                                                  self.board))  # add the move to the list of possible moves
                if (row + 1, col + 1) == self.enpassantPossible:  # if the square to the right is the enpassant square
                    possibleMoves.append(Move((row, col), (row + 1, col + 1), self.board,
                                              isEnpassantMove=True))  # add the move to the list of possible moves

    def getKnightMoves(self, row, col, possibleMoves):  # get knight moves function
        piecePinned = False  # if the piece is pinned
        for i in range(len(self.pins) - 1, -1, -1):  # for each pin in the list of pins
            if self.pins[i][0] == row and self.pins[i][1] == col:  # if the pin is at the square under attack
                piecePinned = True  # set piecePinned to true
                self.pins.remove(self.pins[i])  # remove the pin from the list of pins
                break

        knightMoves = ((-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1))
        # L shapes as in left_down2, left_up2, right_down2, right_up2, left2_down, left2_up, right2_down, right2_up
        if self.whiteToMove:  # if white to move
            allyColor = "w"
        else:
            allyColor = "b"

        for n_move in knightMoves:  # for each move in the list of knight moves
            endRow = row + n_move[0]  # get the row of the end square
            endCol = col + n_move[1]  # get the column of the end square

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # if the end square is on the board
                if not piecePinned:  # if the piece isn't pinned
                    endPiece = self.board[endRow][endCol]  # get the piece at the end square
                    if endPiece[0] != allyColor:  # if the end square is not the same color as the piece
                        possibleMoves.append(Move((row, col), (endRow, endCol),
                                                  self.board))  # add the move to the list of possible moves

    def getBishopMoves(self, row, col, possibleMoves):  # get bishop moves function
        piecePinned = False  # if the piece is pinned
        pinDirection = ()  # the pin direction
        for i in range(len(self.pins) - 1, -1, -1):  # for each pin in the list of pins
            if self.pins[i][0] == row and self.pins[i][1] == col:  # if the pin is at the square under attack
                piecePinned = True  # set piecePinned to true
                pinDirection = (self.pins[i][2], self.pins[i][3])  # set pinDirection to the pin direction
                self.pins.remove(self.pins[i])  # remove the pin from the list of pins
                break

        bishopMoves = ((-1, -1), (1, -1), (-1, 1), (1, 1))  # left_down, right_down, left_up, right_up
        if self.whiteToMove:
            enemyColor = "b"
        else:
            enemyColor = "w"

        for b_moves in bishopMoves:  # for each move in the list of bishop moves
            for i in range(1, 8):  # for each square in the row
                endRow = row + b_moves[0] * i  # get the row of the end square
                endCol = col + b_moves[1] * i  # get the column of the end square
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # if the end square is on the board
                    if not piecePinned or pinDirection == b_moves or pinDirection == (-b_moves[0], -b_moves[
                        1]):  # if the piece isn't pinned or the pin direction is the same as the bishop move
                        endPiece = self.board[endRow][endCol]  # get the piece at the end square
                        if endPiece == "--":
                            possibleMoves.append(Move((row, col), (endRow, endCol),
                                                      self.board))  # add the move to the list of possible moves
                        elif endPiece[0] == enemyColor:  # if the end square is the enemy color
                            possibleMoves.append(Move((row, col), (endRow, endCol),
                                                      self.board))  # add the move to the list of possible moves
                            break
                        else:
                            break
                else:
                    break

    def getRookMoves(self, row, col, possibleMoves):  # get rook moves function
        piecePinned = False  # if the piece is pinned
        pinDirection = ()  # the pin direction
        for i in range(len(self.pins) - 1, -1, -1):  # for each pin in the list of pins
            if self.pins[i][0] == row and self.pins[i][1] == col:  # if the pin is at the square under attack
                piecePinned = True  # set piecePinned to true
                pinDirection = (self.pins[i][2], self.pins[i][3])  # set pinDirection to the pin direction
                if self.board[row][col][1] != 'Q':  # if the piece isn't a queen
                    self.pins.remove(self.pins[i])  # remove the pin from the list of pins
                break

        rookMoves = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        if self.whiteToMove:
            enemyColor = "b"
        else:
            enemyColor = "w"

        for r_move in rookMoves:  # for each move in the list of rook moves
            for i in range(1, 8):  # for each square in the row
                endRow = row + r_move[0] * i  # get the row of the end square
                endCol = col + r_move[1] * i  # get the column of the end square
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # if the end square is on the board
                    if not piecePinned or pinDirection == r_move or pinDirection == (-r_move[0], -r_move[
                        1]):  # if the piece isn't pinned or the pin direction is the same as the rook move
                        endPiece = self.board[endRow][endCol]  # get the piece at the end square
                        if endPiece == "--":  # if the end square is empty
                            possibleMoves.append(Move((row, col), (endRow, endCol),
                                                      self.board))  # add the move to the list of possible moves
                        elif endPiece[0] == enemyColor:  # if the end square is the enemy color
                            possibleMoves.append(Move((row, col), (endRow, endCol),
                                                      self.board))  # add the move to the list of possible moves
                            break
                        else:
                            break
                else:
                    break

    def getQueenMoves(self, row, col, possibleMoves):  # get queen moves function
        self.getBishopMoves(row, col, possibleMoves)  # get bishop moves
        self.getRookMoves(row, col, possibleMoves)  # get rook moves

    def getKingMoves(self, row, col, possibleMoves):  # get king moves function
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)  # up, left, down, right
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)  # up, left, down, right

        if self.whiteToMove:  # if the player is white
            allyColor = "w"
        else:
            allyColor = "b"

        for k_move in range(8):  # for each move in the list of king moves
            endRow = row + rowMoves[k_move]  # get the row of the end square
            endCol = col + colMoves[k_move]  # get the column of the end square

            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # if the end square is on the board
                endPiece = self.board[endRow][endCol]  # get the piece at the end square
                if endPiece[0] != allyColor:  # if the end square is the enemy color

                    if allyColor == 'w':  # if the player is white
                        self.whiteKingLocation = (endRow, endCol)  # set the white king location to the end square
                    else:
                        self.blackKingLocation = (endRow, endCol)  # set the black king location to the end square

                    inCheck, pins, checks = self.checkForPinsAndChecks()  # check for pins and checks

                    if not inCheck:  # if the king isn't in check
                        possibleMoves.append(Move((row, col), (endRow, endCol),
                                                  self.board))  # add the move to the list of possible moves

                    if allyColor == 'w':  # if the player is white
                        self.whiteKingLocation = (row, col)  # set the white king location to the start square
                    else:
                        self.blackKingLocation = (row, col)  # set the black king location to the start square

    def getCastleMoves(self, row, col, moves, allyColor):  # get castle moves function
        if self.squareUnderAttack(row, col):  # if the square is under attack
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):  # if the player can castle kingside
            self.getKingCastleMoves(row, col, moves, allyColor)  # get the king castle moves

        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):  # if the player can castle queenside
            self.getQeenCastleMoves(row, col, moves, allyColor)  # get the queen castle moves

    def getKingCastleMoves(self, row, col, moves, allyColor):  # get king castle moves function
        if self.board[row][col + 1] == '--' and self.board[row][
            col + 2] == '--':  # if the squares in between the king and the rook are empty
            if (not self.squareUnderAttack(row, col + 1)) and (
            not self.squareUnderAttack(row, col + 2)):  # if the squares are not under attack
                moves.append(Move((row, col), (row, col + 2), self.board,
                                  isCastleMove=True))  # add the move to the list of possible moves

    def getQeenCastleMoves(self, row, col, moves, allyColor):  # get queen castle moves function
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][
            col - 3] == '--':  # if the squares in between the king and the rook are empty
            if (not self.squareUnderAttack(row, col - 1)) and (
            not self.squareUnderAttack(row, col - 2)):  # if the squares are not under attack
                moves.append(Move((row, col), (row, col - 2), self.board,
                                  isCastleMove=True))  # add the move to the list of possible moves

    def checkForPinsAndChecks(self):  # check for pins and checks function
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:  # if the player is white
            allyColor = 'w'
            enemyColor = 'b'
            startRow = self.whiteKingLocation[0]  # get the white king's row
            startCol = self.whiteKingLocation[1]  # get the white king's column
        else:  # if the player is black
            allyColor = 'b'
            enemyColor = 'w'
            startRow = self.blackKingLocation[0]  # get the black king's row
            startCol = self.blackKingLocation[1]  # get the black king's column

        # directions = ((-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1), (0, -1), (0, 1))
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):  # for each direction
            d = directions[j]  # get the direction
            possiblePin = ()  # set the possible pin to an empty tuple
            for i in range(1, 8):  # for each square in the direction
                endRow = startRow + d[0] * i  # get the row of the end square
                endCol = startCol + d[1] * i  # get the column of the end square

                if 0 <= endRow < 8 and 0 <= endCol < 8:  # if the end square is on the board
                    endPiece = self.board[endRow][endCol]  # get the piece at the end square
                    if endPiece[0] == allyColor and endPiece[
                        1] != 'K':  # if the end square is the ally color and is not a king
                        if possiblePin == ():  # if the possible pin is empty
                            possiblePin = (
                            endRow, endCol, d[0], d[1])  # set the possible pin to the end square and the direction
                        else:
                            break
                    elif endPiece[0] == enemyColor:  # if the end square is the enemy color
                        type = endPiece[1]
                        # print("Black King location", self.blackKingLocation)
                        # print(startRow, startCol," enemy found in direction ", d[0], d[1], enemyColor, type, endRow, endCol, i, j)
                        # print((i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))))
                        # if enemy piece found near King
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or \
                                (i == 1 and type == 'K'):  # if the enemy piece is a rook, bishop, queen, or king
                            if possiblePin == ():  # if the possible pin is empty
                                inCheck = True  # if enemy directly in range of King
                                # print("king in check by: ", enemyColor, type, endRow, endCol)
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)  # if ally piece in between king and enemy
                                break
                        else:
                            break  # if no enemy found the respective direction that poses threat
                else:
                    break

        #  Special Case for Knight Moves
        knightMoves = ((-1, -2), (-1, 2), (1, -2), (1, 2), (-2, -1), (-2, 1), (2, -1), (2, 1))
        for m in knightMoves:  # for each knight move
            endRow = startRow + m[0]  # get the row of the end square
            endCol = startCol + m[1]  # get the column of the end square
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # if the end square is on the board
                endPiece = self.board[endRow][endCol]  # get the piece at the end square
                if endPiece[0] == enemyColor and endPiece[
                    1] == 'N':  # if the end square is the enemy color and is a knight
                    inCheck = True  # if enemy directly in range of King
                    checks.append((endRow, endCol, m[0], m[1]))  # add the check to the list of checks
        return inCheck, pins, checks


class CastleRights():  # class for castle rights
    def __init__(self, wks, bks, wqs, bqs):  # constructor
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {"1": 7,
                   "2": 6,
                   "3": 5,
                   "4": 4,
                   "5": 3,
                   "6": 2,
                   "7": 1,
                   "8": 0}  # dictionary for converting ranks to rows
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6,
                   "h": 7}  # dictionary for converting files to columns
    colsToFiles = {v: k for k, v in filesToCols.items()}  # constructor

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False, AIPromotionKey='Q',
                 AIPlaying=False):  # constructor
        self.startRow = startSq[0]  # get the start row
        self.startCol = startSq[1]  # get the start column
        self.endRow = endSq[0]  # get the end row
        self.endCol = endSq[1]  # get the end column
        self.pieceMoved = board[self.startRow][self.startCol]  # get the piece that was moved
        self.pieceCaptured = board[self.endRow][self.endCol]  # get the piece that was captured

        # For AI:
        self.AIPromotionKey = AIPromotionKey  # get the promotion key
        self.AIPlaying = AIPlaying  # get the AI playing boolean

        # For Pawn Promotion:
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (
                self.pieceMoved == 'bP' and self.endRow == 7):  # if the pawn is at the end of the board
            self.isPawnPromotion = True  # set the pawn promotion boolean to true

        # For Enpassant Move:
        self.isEnpassantMove = isEnpassantMove  # get the enpassant move boolean
        if self.isEnpassantMove:  # if the move is an enpassant move
            if self.pieceMoved == 'wP':
                self.pieceCaptured = 'bP'
            else:
                self.pieceCaptured = 'wP'

        self.isCastleMove = isCastleMove  # get the castle move boolean
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  # get the move ID

    def __eq__(self, other):  # overloaded equality operator
        if isinstance(other, Move):  # if the other object is a move
            return self.moveID == other.moveID  # return the move ID of the move

    def getChessNotation(self):  # get the chess notation of the move
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow,
                                                                                 self.endCol)  # return the chess notation of the move

    def getRankFile(self, row, col):  # get the rank and file of the square
        return self.colsToFiles[col] + self.rowsToRanks[row]  # return the rank and file of the square

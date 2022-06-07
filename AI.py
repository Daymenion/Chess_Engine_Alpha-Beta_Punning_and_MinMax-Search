#
# Created by: Daymenion 16/05/2022
#
# this program under the GNU General Public License v3.0 license.

import random

pieceScore = {"K": 100, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3  # depth of the search

Promotions = ['Q', 'B', 'R', 'N']  # the promotions for the AI to choose from


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)] if len(
        validMoves) > 0 else None  # return a random move if there are any


def findBestMove(gs, validMoves):  # find the best move for the AI to make
    global nextMove, counter  # global variables
    nextMove = None  # reset the next move
    counter = 0  # reset the counter
    random.shuffle(validMoves)  # shuffle the valid moves
    if gs.whiteToMove:  # if the AI is white to move
        bestAlphaBetaMinMaxMove(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1)  # find the best move
    else:  # if the AI is black to move
        bestAlphaBetaMinMaxMove(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, -1)  # find the best move
    print("Number of Moves checked: ", counter)  # print the number of moves checked
    return nextMove  # return the best move


def bestAlphaBetaMinMaxMove(gs, validMoves, depth, alpha, beta,
                            turn):  # find the best move for the AI to make using alpha beta pruning and minimax search
    global nextMove, counter  # global variables
    if depth == 0:  # if the depth is 0
        return turn * scoreBoard(gs)  # return the score of the board

    maxScore = -CHECKMATE  # set the max score to -1000
    for move in validMoves:  # for each move in the valid moves
        if move.isPawnPromotion:  # if the move is a pawn promotion
            move.AIPlaying = True  # set the move to be played by the AI
            move.AIPromotionKey = Promotions[0]  # set the promotion key to the first promotion "queen"
        gs.makeMove(move)  # make the move
        nextMoves = gs.getValidMoves()  # get the next moves
        counter += len(nextMoves)  # add the number of moves to the counter
        score = -bestAlphaBetaMinMaxMove(gs, nextMoves, depth - 1, -beta, -alpha,
                                         -turn)  # find the score of the next move
        if score > maxScore:  # if the score is greater than the max score
            maxScore = score  # set the max score to the score
            if depth == DEPTH:  # if the depth is the same as the depth
                nextMove = move  # set the next move to the move
        gs.undoMove()  # undo the move

        if maxScore > alpha:  # if the max score is greater than the alpha
            alpha = maxScore  # set the alpha to the max score
        if alpha >= beta:  # if the alpha is greater than or equal to the beta
            break  # break the loop
    return maxScore  # return the max score


def scoreBoard(gs):  # score the board
    if gs.checkMate:  # if the game is over
        if gs.whiteToMove:  # if the AI is white to move
            return -CHECKMATE  # return a score of -1000
        else:
            return CHECKMATE  # return a score of 1000
    elif gs.staleMate:
        return STALEMATE  # return a score of 0
    score = 0
    for row in gs.board:  # for each row in the board
        for square in row:  # for each square in the row
            if square[0] == 'w':  # if the square is white
                score += pieceScore[square[1]]  # add the score of the piece to the score
            if square[0] == 'b':  # if the square is black
                score -= pieceScore[square[1]]  # subtract the score of the piece from the score
    return score

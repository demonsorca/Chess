"""
This is main driver file. It will be responsible for handling user input and displaying current game state object.
"""

import pygame as p
from Chess import ChessEngine

WIDTH = HEIGHT = 720
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ["wQ", "wK", "wB", "wN", "wR","wP","bP","bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+piece+".png"), (SQ_SIZE,SQ_SIZE))


def main():
    p.init()
    clock = p.time.Clock()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for a move is made
    loadImages()
    running = True
    sqSelected = () #keep track of the last click of the user
    playerClicks = [] #keep track of player clicks
    gameOver = False
    while running:
        for e in p.event.get():
            # mouse press
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # Get x,y of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col): #deselect the current selected sq
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks)==2: #Valid 2nd move need to change postions
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        # print(gs.checkMate,gs.staleMate)
                        for i in range(len(validMoves)):
                            if validMoves[i]==move:
                                # print(move.getChessNotation())
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # Undo the last Move
                    log = gs.castleRightsLog[-1]
                    print(len(gs.castleRightsLog))
                    print(log.wks, log.wqs, log.bks, log.bqs)
                    gs.undoMove()
                    log = gs.castleRightsLog[-1]
                    print(log.wks, log.wqs, log.bks, log.bqs)
                    moveMade = True
                    sqSelected = ()
                    playerClicks = []
                if e.key == p.K_r: # Reset the game
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []

        if moveMade:
            # print(validMoves)
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs,validMoves,sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen,"Black wins by Checkmate")
            else:
                drawText(screen,"White wins by Checkmate")
        elif gs.staleMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen,"Black wins by Checkmate")
            else:
                drawText(screen,"White wins by Checkmate")
        clock.tick(MAX_FPS)
        p.display.flip()

"""
This fun. responsible for all the graphics within a current game state.
"""
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) #draw squares on the board
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen, gs.board) #draw pieceson those squares and move suggestion later

#This fun draw squares on boards
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece!="--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected !=():
        r,c = sqSelected
        if gs.board[r][c][0]==("w" if gs.whiteToMove else "b"):
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))

            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow ==r and move.startCol==c:
                    screen.blit(s,(SQ_SIZE*move.endCol,move.endRow*SQ_SIZE))

def animateMoves(move,screen,board,clock):
    global colors
    coords = []

def drawText(screen,text):
    font = p.font.SysFont('Helvitca',46,True,False)
    textObject = font.render(text,0,p.Color('Blue'))
    textLocation = p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2-textObject.get_width()/2,HEIGHT/2-textObject.get_height()/2)
    screen.blit(textObject,textLocation)

if __name__ == "__main__":
    main()
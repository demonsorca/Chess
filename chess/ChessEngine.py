"""
This class is responsible for storing all the info about the current state of a chess game. It will also be responsible
for determining the valid moves at the current state. It will also keep a move log.
"""
class GameState():
    def __init__(self):
        # Here we have 8x8 grid,1st letter tells about color "black" or "white" and 2nd tells about type.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.moveFunction = {"P":self.getPawnMoves,"R":self.getRockMoves,"N":self.getKnightMoves,"B":self.getBishopMoves,"K":self.getKingMoves,"Q":self.getQueenMoves}
        self.whiteToMove = True
        self.movelog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.currentCastlingRight = CastleRights(True,True,True,True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)]


    def makeMove(self,move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movelog.append(move) #log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove #swap players
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        # Pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0]+"Q"
        # enpassant move
        if move.isEnPassantMove:
             self.board[move.startRow][move.endCol] = "--"  # capturing the pawn

        # update enpassant_possible variable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:  # only on 2 square pawn advance
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastling:
            if move.endCol - move.startCol==2: #King side castling
                self.board[move.endRow][move.endCol-1] = move.pieceMoved[0]+"R"
                self.board[move.endRow][move.endCol+1] = "--"
            else: #Queen side castling
                self.board[move.endRow][move.endCol + 1] = move.pieceMoved[0] + "R"
                self.board[move.endRow][move.endCol - 2] = "--"

        #update castling rights whenever it is rock or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,self.currentCastlingRight.wqs,self.currentCastlingRight.bqs))

    def undoMove(self):
        if self.movelog:
            move = self.movelog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #swap players
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow,move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow,move.startCol)
            #enpassant undo move
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow,move.endCol)

            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]

            # undo castle move
            if move.isCastling:
                if move.endCol - move.startCol == 2:  # King side castling
                    self.board[move.endRow][move.endCol - 1] = "--"
                    self.board[move.endRow][move.endCol + 1] = move.pieceMoved[0] + "R"
                else:  # Queen side castling
                    self.board[move.endRow][move.endCol + 1] = "--"
                    self.board[move.endRow][move.endCol - 2] = move.pieceMoved[0] + "R"

    def updateCastleRights(self,move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: #left rock
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #right rock
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: #left rock
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: #right rock
                    self.currentCastlingRight.bks = False

    """
    All moves considering checks
    """
    def getValidMoves(self):
        # print(len(self.castleRightsLog))
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks,self.currentCastlingRight.bks,self.currentCastlingRight.wqs,self.currentCastlingRight.bqs)
        print("In:",tempCastleRights.wqs)
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)
        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.pop(i)
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        print("Out:",self.currentCastlingRight.wqs)
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareInCheck(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareInCheck(self.blackKingLocation[0],self.blackKingLocation[1])

    def squareInCheck(self,r,c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    """
    All possible moves of selected sq
    """
    def getAllPossibleMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                turn = self.board[r][c][0]
                if (turn=="w" and self.whiteToMove) or (turn=="b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r,c,moves)
        return moves

    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:#White chance to move
            if self.board[r-1][c]=="--":
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c]=="--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c>0 and self.board[r-1][c-1][0]=="b": #Enemy
                moves.append(Move((r, c),(r-1,c-1), self.board))
            elif c>0 and (r-1,c-1) == self.enpassantPossible:
                # print(self.enpassantPossible,r,c,r-1,c-1)
                moves.append(Move((r, c), (r - 1, c - 1), self.board,isEnPassantMove=True))
            if c<7 and self.board[r-1][c+1][0]=="b": #Enemy
                moves.append(Move((r, c),(r-1,c+1), self.board))
            elif c<7 and (r-1,c+1) == self.enpassantPossible:
                # print(self.enpassantPossible,r,c,r-1,c+1)
                moves.append(Move((r, c), (r - 1, c + 1), self.board,isEnPassantMove=True))
        else: #Black move
            if self.board[r+1][c]=="--":
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c]=="--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c<7 and self.board[r+1][c+1][0]=="w": #Enemy
                moves.append(Move((r, c),(r+1,c+1), self.board))
            elif c<7 and (r+1,c+1) == self.enpassantPossible:
                # print(self.enpassantPossible,r,c,r+1,c+1)
                moves.append(Move((r, c), (r + 1, c + 1), self.board,isEnPassantMove=True))
            if c>0 and self.board[r+1][c-1][0]=="w": #Enemy
                moves.append(Move((r, c),(r+1,c-1), self.board))
            elif c>0 and (r+1,c-1) == self.enpassantPossible:
                # print(self.enpassantPossible,r,c,r+1,c-1)
                moves.append(Move((r, c), (r + 1, c - 1), self.board,isEnPassantMove=True))

    def getRockMoves(self,r,c,moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0<= endRow < 8 and 0<= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self,r,c,moves):
        arr = [[r + 2, c - 1], [r + 2, c+1], [r - 2, c + 1], [r-2, c - 1], [r + 1, c + 2], [r - 1, c+2], [r + 1, c - 2],
               [r-1, c - 2]]
        for P in arr:
            if 0<=P[0]<8 and 0<=P[1]<8:
                if self.board[P[0]][P[1]]=="--":
                    moves.append(Move((r, c), (P[0], P[1]), self.board))
                elif self.whiteToMove and self.board[P[0]][P[1]][0]=="b":
                    moves.append(Move((r, c), (P[0], P[1]), self.board))
                elif not self.whiteToMove and self.board[P[0]][P[1]][0]=="w":
                    moves.append(Move((r, c), (P[0], P[1]), self.board))

    def getKingMoves(self,r,c,moves):
        arr = [[r-1,c-1],[r-1,c],[r-1,c+1],[r,c+1],[r+1,c+1],[r+1,c],[r+1,c-1],[r,c-1]]
        for P in arr:
            if 0<=P[0]<8 and 0<=P[1]<8:
                if self.board[P[0]][P[1]]=="--":
                    moves.append(Move((r, c), (P[0], P[1]), self.board))
                elif self.whiteToMove and self.board[P[0]][P[1]][0]=="b":
                    moves.append(Move((r, c), (P[0], P[1]), self.board))
                elif not self.whiteToMove and self.board[P[0]][P[1]][0]=="w":
                    moves.append(Move((r, c), (P[0], P[1]), self.board))

    def getCastleMoves(self,r,c,moves):
        if self.squareInCheck(r,c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r,c,moves)

    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1]=="--" and self.board[r][c+2]=="--":
            if not self.squareInCheck(r,c+1) and not self.squareInCheck(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastling = True))

    def getQueensideCastleMoves(self,r,c,moves):
        if self.board[r][c-1]=="--" and self.board[r][c-2]=="--" and self.board[r][c-3]=="--":
            if not self.squareInCheck(r,c-1) and not self.squareInCheck(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastling = True))

    def getQueenMoves(self,r,c,moves):
        self.getRockMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)

    def getBishopMoves(self,r,c,moves):
        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break



class CastleRights():
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs



class Move():
    # maps keys to values
    ranksToRows = {"1":7,"2":6,"3":5,"4":4,
                   "5":3,"6":2,"7":1,"8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}
    filesToCols = {"h": 7, "g": 6, "f": 5, "e": 4,
                   "d": 3, "c": 2, "b": 1, "a": 0}
    colsToFiles = {v:k for k,v in filesToCols.items()}
    def __init__(self,startSq,endSq,board,isEnPassantMove=False,isCastling=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved=="wP" and self.endRow==0) or (self.pieceMoved=="bP" and self.endRow==7)
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved=="bP" else "bP"
        self.isCastling = isCastling
        self.moveId = 1000*self.startRow + 100*self.startCol + 10*self.endRow + self.endCol

    """
    overriding the equals while comparing moves in main fun
    """
    def __eq__(self, other):
        if isinstance(other,Move):
            return self.moveId == other.moveId
        return False


    def getChessNotation(self):
        # real chess Notation
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c]+self.rowsToRanks[r]





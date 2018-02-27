import sys
import random
import signal
import time
import copy
import traceback
from simulator import Random_Player
from team12idfsnew import Team12

TIME = 16
MAX_PTS = 68

class TimedOutExc(Exception):
    pass

def handler(signum, frame):
    raise TimedOutExc()


class Swagalicious():
    def __init__(self):
        self.bs_score_matrix = [[0 for i in range(4)] for j in range(4)]
        self.opp_bs_score_matrix = [[0 for i in range(4)] for j in range(4)]
        self.winners = [(8,9,10,11), (12,13,14,15), (0,1,2,3), (4,5,6,7), (0,4,8,12), (1,5,9,13), (2,6,10,14), (3,7,11,15), (1,4,6,9), (5,8,10,13), (2, 5, 7, 10), (6, 9, 11, 14) ]

    def move(self, board, old_move, flag):
        #You have to implement the move function with the same signature as this
        #Find the list of valid cells allowed
        maxval = -1000000000000000000
        bm = []
        alpha = -1000000000000000000
        beta = 1000000000000000000
        cells = board.find_valid_move_cells(old_move)
        start_time = time.time()
        # print self.bs_score_matrix
        # print self.opp_bs_score_matrix
        for cell in cells:
            if flag == 'x':
                fl = 'o'
            else:
                fl = 'x'
            board.update(old_move, cell, flag)
            val = self.minimax(board, 1, cell, alpha, beta, fl, 0, start_time)
            self.revert(board, cell, '-')
            if val > maxval:
                maxval = val
                bm = cell
        return bm

    def minimax(self, board, depth, old_move, a, b, flag, isMax, start_time):
        # First checking if terminal state has been reached
        term_state = board.find_terminal_state()
        if term_state[1] == 'WON' and term_state[0] == 'x' and isMax and flag == 'x' or term_state[1] == 'WON' and term_state[0] == 'o' and isMax and flag == 'o':
            return 1000000000000000000
        elif term_state[1] == 'WON' and term_state[0] == 'x' and not isMax and flag == 'x' or term_state[1] == 'WON' and term_state[0] == 'o' and not isMax and flag == 'o':
            return -1000000000000000000
        elif term_state[0] == 'NONE' and term_state[1] == 'DRAW':
            return 0

        if depth >= 6:
            return self.heuristic1(board, depth, isMax, flag, old_move)

        cells = board.find_valid_move_cells(old_move)
        if flag=='x':
            fl = 'o'
        else:
            fl = 'x'
        if isMax:
            best = -1000000000000000000
        else:
            best = 1000000000000000000
        for cell in cells:
            if board.board_status[cell[0]][cell[1]]=='-':
                    board.update(old_move,cell,flag)
                    if isMax:
                        best = max(best,self.minimax(board, depth+1, cell, a, b, fl, (isMax+1)%2, start_time))
                    else:
                        best = min(best,self.minimax(board, depth+1, cell, a, b, fl, (isMax+1)%2, start_time))
                    self.revert(board, cell, '-')
                    if isMax:
                        a = max(best, a)
                    else:
                        b = min(best, b)
                    if time.time() - start_time > 15:
                        # print "Timed out!"
                        return best
                    if b <= a:
                        break
        return best

    def heuristic1(self, board, depth, isMax, flag, old_move):
        alt_flag = 'o'
        if flag == 'o' and isMax == 1:
            alt_flag = 'x'
        elif flag == 'o' and isMax == 0:
            flag = 'x'
            alt_flag = 'o'
        elif flag == 'x' and isMax == 0:
            flag = 'o'
            alt_flag = 'x'

        bs = board.block_status
        bds = board.board_status

        can_win = 0
        temp_flag = 0
        while True:
            for i in range(4):
                for j in range(4):
                    if bs[i][j] == 'd' or bs[i][j] == alt_flag:
                        temp_flag = 1
                    if bs[j][i] == 'd' or bs[j][i] == alt_flag:
                        temp_flag = 1
                if temp_flag == 0:
                    can_win = 1
                    break
            if temp_flag == 0:
                break

            if (bs[0][1] != 'd' and bs[1][0] != 'd' and bs[1][2] != 'd' and bs[0][2] != 'd') and (bs[0][1] != alt_flag and bs[1][0] != alt_flag and bs[1][2] != alt_flag and bs[0][2] != alt_flag):
                can_win = 1
                break
            if (bs[0][2] != 'd' and bs[1][1] != 'd' and bs[1][3] != 'd' and bs[0][3] != 'd') and (bs[0][2] != alt_flag and bs[1][1] != alt_flag and bs[1][3] != alt_flag and bs[0][3] != alt_flag):
                can_win = 1
                break
            if (bs[1][1] != 'd' and bs[2][0] != 'd' and bs[2][2] != 'd' and bs[1][2] != 'd') and (bs[1][1] != alt_flag and bs[2][0] != alt_flag and bs[2][2] != alt_flag and bs[1][2] != alt_flag):
                can_win = 1
                break
            if (bs[1][2] != 'd' and bs[2][1] != 'd' and bs[2][3] != 'd' and bs[1][3] != 'd') and (bs[1][2] != alt_flag and bs[2][1] != alt_flag and bs[2][3] != alt_flag and bs[1][3] != alt_flag):
                can_win = 1
                break
            break

        self.bs_score_matrix = [[0 for i in range(4)] for j in range(4)]
        self.opp_bs_score_matrix = [[0 for i in range(4)] for j in range(4)]
        for i in range(4):
            for j in range(4):
                temp_matrix = [[2, 3, 3, 2], [3, 4, 4, 3], [3, 4, 4, 3], [2, 3, 3, 2]]
                opp_temp_matrix = [[2, 3, 3, 2], [3, 4, 4, 3], [3, 4, 4, 3], [2, 3, 3, 2]]
                for k in range(4):
                    for l in range(4):
                        if bds[4*i+k][4*j+l] == flag:
                            # temp_matrix[k][l] *= 1
                            opp_temp_matrix[k][l] = 0
                        elif bds[4*i+k][4*j+l] == alt_flag:
                            temp_matrix[k][l] = 0
                            # opp_temp_matrix[k][l] *= 1
                        elif bds[4*i+k][4*j+l] == '-':
                            temp_matrix[k][l] *= 0.5
                            opp_temp_matrix[k][l] *= 0.5
                # print temp_matrix
                # print opp_temp_matrix
                for k in range(4):
                    row_product = 1
                    opp_row_product = 1
                    for l in range(4):
                        row_product *= temp_matrix[k][l]
                        opp_row_product *= opp_temp_matrix[k][l]
                        self.bs_score_matrix[i][j] += row_product
                        self.opp_bs_score_matrix[i][j] += opp_row_product
                for l in range(4):
                    column_product = 1
                    opp_column_product = 1
                    for k in range(4):
                        column_product *= temp_matrix[k][l]
                        opp_column_product *= opp_temp_matrix[k][l]
                        self.bs_score_matrix[i][j] += column_product
                        self.opp_bs_score_matrix[i][j] += opp_column_product
                # print self.bs_score_matrix
                # print self.opp_bs_score_matrix
                # print i, j
                self.bs_score_matrix[i][j] += temp_matrix[1][0]*temp_matrix[0][1]*temp_matrix[1][2]*temp_matrix[2][1]
                self.bs_score_matrix[i][j] += temp_matrix[1][1]*temp_matrix[0][2]*temp_matrix[1][3]*temp_matrix[2][2]
                self.bs_score_matrix[i][j] += temp_matrix[2][0]*temp_matrix[1][1]*temp_matrix[2][2]*temp_matrix[3][1]
                self.bs_score_matrix[i][j] += temp_matrix[2][1]*temp_matrix[1][2]*temp_matrix[2][3]*temp_matrix[3][2]

                self.opp_bs_score_matrix[i][j] += opp_temp_matrix[1][0]*opp_temp_matrix[0][1]*opp_temp_matrix[1][2]*opp_temp_matrix[2][1]
                self.opp_bs_score_matrix[i][j] += opp_temp_matrix[1][1]*opp_temp_matrix[0][2]*opp_temp_matrix[1][3]*opp_temp_matrix[2][2]
                self.opp_bs_score_matrix[i][j] += opp_temp_matrix[2][0]*opp_temp_matrix[1][1]*opp_temp_matrix[2][2]*opp_temp_matrix[3][1]
                self.opp_bs_score_matrix[i][j] += opp_temp_matrix[2][1]*opp_temp_matrix[1][2]*opp_temp_matrix[2][3]*opp_temp_matrix[3][2]

                if can_win == 1:
                    if is_centre(i, j):
                        self.bs_score_matrix[i][j] *= 4
                        self.opp_bs_score_matrix[i][j] *= 4
                    elif is_corner(i, j):
                        self.bs_score_matrix[i][j] *= 2
                        self.opp_bs_score_matrix[i][j] *= 2
                    else:
                        self.bs_score_matrix[i][j] *= 3
                        self.opp_bs_score_matrix[i][j] *= 3
                else:
                    if is_centre(i, j):
                        self.bs_score_matrix[i][j] *= 3
                        self.opp_bs_score_matrix[i][j] *= 3
                    elif is_corner(i, j):
                        self.bs_score_matrix[i][j] *= 6
                        self.opp_bs_score_matrix[i][j] *= 6
                    else:
                        self.bs_score_matrix[i][j] *= 4
                        self.opp_bs_score_matrix[i][j] *= 4

                # ffflag = 0
                # if isMax == 1:
                #     if self.is_row(bds, i, j, flag):
                #         self.bs_score_matrix[i][j] *= 3
                #         ffflag = 1
                #     if self.is_column(bds, i, j, flag):
                #         self.bs_score_matrix[i][j] *= 3
                #         ffflag = 1
                #     if self.is_diamond(bds, i, j, flag):
                #         self.bs_score_matrix[i][j] *= 3
                #         ffflag = 1
                #     if ffflag == 1:
                #         return 99999999999999
                # else:
                #     if self.is_row(bds, i, j, flag):
                #         self.bs_score_matrix[i][j] /= 3
                #         ffflag = 1
                #     if self.is_column(bds, i, j, flag):
                #         self.bs_score_matrix[i][j] /= 3
                #         ffflag = 1
                #     if self.is_diamond(bds, i, j, flag):
                #         self.bs_score_matrix[i][j] /= 3
                #         ffflag = 1
                #     if ffflag == 1:
                #         return -99999999999999
                # ffflag = 0
                #
                # if self.is_row(bds, i, j, alt_flag):
                #     self.opp_bs_score_matrix[i][j] *= 3
                # if self.is_column(bds, i, j, alt_flag):
                #     self.opp_bs_score_matrix[i][j] *= 3
                # if self.is_diamond(bds, i, j, alt_flag):
                #     self.opp_bs_score_matrix[i][j] *= 3

        # print self.bs_score_matrix
        # print self.opp_bs_score_matrix
        # sys.exit()
        final_score = 0
        for i in range(4):
            row_product = 1
            opp_row_product = 1
            for j in range(4):
                row_product *= self.bs_score_matrix[i][j]
                opp_row_product *= self.opp_bs_score_matrix[i][j]
            final_score += row_product - opp_row_product

        for j in range(4):
            column_product = 1
            opp_column_product = 1
            for i in range(4):
                column_product *= self.bs_score_matrix[i][j]
                opp_column_product *= self.opp_bs_score_matrix[i][j]
            final_score += column_product - opp_column_product

        final_score += self.bs_score_matrix[1][0]*self.bs_score_matrix[0][1]*self.bs_score_matrix[1][2]*self.bs_score_matrix[2][1]
        final_score += self.bs_score_matrix[1][1]*self.bs_score_matrix[0][2]*self.bs_score_matrix[1][3]*self.bs_score_matrix[2][2]
        final_score += self.bs_score_matrix[2][0]*self.bs_score_matrix[1][1]*self.bs_score_matrix[2][2]*self.bs_score_matrix[3][1]
        final_score += self.bs_score_matrix[2][1]*self.bs_score_matrix[1][2]*self.bs_score_matrix[2][3]*self.bs_score_matrix[3][2]

        final_score -= self.opp_bs_score_matrix[1][0]*self.opp_bs_score_matrix[0][1]*self.opp_bs_score_matrix[1][2]*self.opp_bs_score_matrix[2][1]
        final_score -= self.opp_bs_score_matrix[1][1]*self.opp_bs_score_matrix[0][2]*self.opp_bs_score_matrix[1][3]*self.opp_bs_score_matrix[2][2]
        final_score -= self.opp_bs_score_matrix[2][0]*self.opp_bs_score_matrix[1][1]*self.opp_bs_score_matrix[2][2]*self.opp_bs_score_matrix[3][1]
        final_score -= self.opp_bs_score_matrix[2][1]*self.opp_bs_score_matrix[1][2]*self.opp_bs_score_matrix[2][3]*self.opp_bs_score_matrix[3][2]
        # print final_score
        return final_score


    def revert(self, board, new_move, ply):
        #updating the game board and block status as per the move that has been passed in the arguments
        board.board_status[new_move[0]][new_move[1]] = ply
        x = new_move[0]/4
        y = new_move[1]/4
        fl = 0
        board.block_status[x][y]=ply

    def is_row(self, bds, x, y, flag):
        count = 0
        alt_flag = 'o'
        if flag == 'o':
            alt_flag = 'x'

        for i in range(4*x, (4*x)+4):
            for j in range(4*y, (4*y)+4):
                if bds[i][j] == flag:
                    # print bds[i][j]
                    count += 1
                if bds[i][j] == alt_flag:
                    count = 0
                    break
                if count == 3:
                    return 1
        return 0

    def is_column(self, bds, x, y, flag):
        count = 0
        alt_flag = 'o'
        if flag == 'o':
            alt_flag = 'x'

        for j in range(4*x, 4*x+4):
            for i in range(4*y, 4*y+4):
                if bds[i][j] == flag:
                    count += 1
                if bds[i][j] == alt_flag:
                    count = 0
                    break
            if count == 3:
                return 1
        return 0

    def is_diamond(self, bs, x, y, flag):
        count = 0
        alt_flag = 'o'
        if flag == 'o':
            alt_flag = 'x'

        if bs[4*x+1][4*y+0] == flag and bs[4*x+1][4*y+0] == bs[4*x+0][4*y+1] and bs[4*x+1][4*y+0] == bs[4*x+1][4*y+2] and bs[4*x+2][4*y+1] != alt_flag:
            return 1
        if bs[4*x+1][4*y+0] == flag and bs[4*x+1][4*y+0] == bs[4*x+0][4*y+1] and bs[4*x+1][4*y+0] == bs[4*x+2][4*y+1] and bs[4*x+1][4*y+2] != alt_flag:
            return 1
        if bs[4*x+1][4*y+0] == flag and bs[4*x+1][4*y+0] == bs[4*x+2][4*y+1] and bs[4*x+1][4*y+0] == bs[4*x+1][4*y+2] and bs[4*x+0][4*y+1] != alt_flag:
            return 1
        if bs[4*x+2][4*y+1] == flag and bs[4*x+2][4*y+1] == bs[4*x+0][4*y+1] and bs[4*x+2][4*y+1] == bs[4*x+1][4*y+2] and bs[4*x+1][4*y+0] != alt_flag:
            return 1

        if bs[4*x+1][4*y+1] == flag and bs[4*x+1][4*y+1] == bs[4*x+0][4*y+2] and bs[4*x+1][4*y+1] == bs[4*x+1][4*y+3] and bs[4*x+2][4*y+2] != alt_flag:
            return 1
        if bs[4*x+1][4*y+1] == flag and bs[4*x+1][4*y+1] == bs[4*x+0][4*y+2] and bs[4*x+1][4*y+1] == bs[4*x+2][4*y+2] and bs[4*x+1][4*y+3] != alt_flag:
            return 1
        if bs[4*x+1][4*y+1] == flag and bs[4*x+1][4*y+1] == bs[4*x+2][4*y+2] and bs[4*x+1][4*y+1] == bs[4*x+1][4*y+3] and bs[4*x+0][4*y+2] != alt_flag:
            return 1
        if bs[4*x+2][4*y+2] == flag and bs[4*x+2][4*y+2] == bs[4*x+0][4*y+2] and bs[4*x+2][4*y+2] == bs[4*x+1][4*y+3] and bs[4*x+1][4*y+1] != alt_flag:
            return 1

        if bs[4*x+2][4*y+0] == flag and bs[4*x+2][4*y+0] == bs[4*x+1][4*y+1] and bs[4*x+2][4*y+0] == bs[4*x+2][4*y+2] and bs[4*x+3][4*y+1] != alt_flag:
            return 1
        if bs[4*x+2][4*y+0] == flag and bs[4*x+2][4*y+0] == bs[4*x+1][4*y+1] and bs[4*x+2][4*y+0] == bs[4*x+3][4*y+1] and bs[4*x+2][4*y+2] != alt_flag:
            return 1
        if bs[4*x+2][4*y+0] == flag and bs[4*x+2][4*y+0] == bs[4*x+3][4*y+1] and bs[4*x+2][4*y+0] == bs[4*x+2][4*y+2] and bs[4*x+1][4*y+1] != alt_flag:
            return 1
        if bs[4*x+3][4*y+1] == flag and bs[4*x+3][4*y+1] == bs[4*x+1][4*y+1] and bs[4*x+3][4*y+1] == bs[4*x+2][4*y+2] and bs[4*x+2][4*y+0] != alt_flag:
            return 1

        if bs[4*x+2][4*y+1] == flag and bs[4*x+2][4*y+1] == bs[4*x+1][4*y+2] and bs[4*x+2][4*y+1] == bs[4*x+2][4*y+3] and bs[4*x+3][4*y+2] != alt_flag:
            return 1
        if bs[4*x+2][4*y+1] == flag and bs[4*x+2][4*y+1] == bs[4*x+1][4*y+2] and bs[4*x+2][4*y+1] == bs[4*x+3][4*y+2] and bs[4*x+2][4*y+3] != alt_flag:
            return 1
        if bs[4*x+2][4*y+1] == flag and bs[4*x+2][4*y+1] == bs[4*x+3][4*y+2] and bs[4*x+2][4*y+1] == bs[4*x+2][4*y+3] and bs[4*x+1][4*y+2] != alt_flag:
            return 1
        if bs[4*x+3][4*y+2] == flag and bs[4*x+3][4*y+2] == bs[4*x+1][4*y+2] and bs[4*x+3][4*y+2] == bs[4*x+2][4*y+3] and bs[4*x+2][4*y+1] != alt_flag:
            return 1

        return 0


class Manual_Player:
    def __init__(self):
        pass
    def move(self, board, old_move, flag):
        print 'Enter your move: <format:row column> (you\'re playing with', flag + ")"
        mvp = raw_input()
        mvp = mvp.split()
        return (int(mvp[0]), int(mvp[1]))

class Board:
    def __init__(self):
        self.board_status = [['-' for i in range(16)] for j in range(16)]
        self.block_status = [['-' for i in range(4)] for j in range(4)]

    def print_board(self):

        print '==============Board State============== '
        for i in range(16):
            if i%4 == 0:
                print
            for j in range(16):
                if j%4 == 0:
                    print "",
                print self.board_status[i][j],
            print
        print

        print '==============Block State============== '
        for i in range(4):
            for j in range(4):
                print self.block_status[i][j],
            print
        print '======================================= '
        print
        print
        # sys.exit()

    def find_valid_move_cells(self, old_move):

        allowed_cells = []
        allowed_block = [old_move[0] % 4, old_move[1] % 4]

        if old_move != (-1, -1) and self.block_status[allowed_block[0]][allowed_block[1]] == '-':
            for i in range(4*allowed_block[0], 4*allowed_block[0]+4):
                for j in range(4*allowed_block[1], 4*allowed_block[1]+4):
                    if self.board_status[i][j] == '-':
                        allowed_cells.append((i, j))
        else:
            for i in range(16):
                for j in range(16):
                    if self.board_status[i][j] == '-' and self.block_status[i/4][j/4] == '-':
                        allowed_cells.append((i,j))
        return allowed_cells

    def find_terminal_state(self):

        bs = self.block_status

        cntx = 0
        cnto = 0
        cntd = 0

        for i in range(4):
            for j in range(4):
                if bs[i][j] == 'x':
                    cntx += 1
                if bs[i][j] == 'o':
                    cnto += 1
                if bs[i][j] == 'd':
                    cntd += 1

        for i in range(4):
            row = bs[i]
            col = [x[i] for x in bs]

            if (row[0] == 'x' or row[0] == 'o') and (row.count(row[0]) == 4):
                return (row[0], 'WON')
            if (col[0] == 'x' or col[0] == 'o') and (col.count(col[0]) == 4):
                return (col[0], 'WON')

        if (bs[1][0] == bs[0][1] == bs[2][1] == bs[1][2]) and (bs[1][0] == 'x' or bs[1][0] == 'o'):
            return (bs[1][0], 'WON')
        if (bs[1][1] == bs[0][2] == bs[2][2] == bs[1][3]) and (bs[1][1] == 'x' or bs[1][1] == 'o'):
            return (bs[1][1], 'WON')
        if (bs[2][0] == bs[1][1] == bs[3][1] == bs[2][2]) and (bs[2][0] == 'x' or bs[2][0] == 'o'):
            return (bs[2][0], 'WON')
        if (bs[2][1] == bs[1][2] == bs[3][2] == bs[2][3]) and (bs[2][1] == 'x' or bs[2][1] == 'o'):
            return (bs[2][1], 'WON')

        if cntx+cnto+cntd < 16:
            return ('CONTINUE', '-')
        elif cntx+cnto+cntd == 16:
            return ('NONE', 'DRAW')

    def check_valid_move(self, old_move, new_move):
        if (len(old_move) != 2) or (len(new_move) != 2):
            return False
        if (type(old_move[0]) is not int) or (type(old_move[1]) is not int) or (type(new_move[0]) is not int) or (type(new_move[1]) is not int):
            return False
        if (old_move != (-1, -1)) and (old_move[0] < 0 or old_move[0] > 16 or old_move[1] < 0 or old_move[1] > 16):
            return False
        cells = self.find_valid_move_cells(old_move)
        return new_move in cells

    def update(self, old_move, new_move, ply):

        if(self.check_valid_move(old_move, new_move)) == False:
            return 'UNSUCCESSFUL', False
        self.board_status[new_move[0]][new_move[1]] = ply

        x = new_move[0]/4
        y = new_move[1]/4
        fl = 0
        bs = self.board_status

        for i in range(4):
            if (bs[4*x+i][4*y] == bs[4*x+i][4*y+1] == bs[4*x+i][4*y+2] == bs[4*x+i][4*y+3]) and (bs[4*x+i][4*y] == ply):
                self.block_status[x][y] = ply
                return 'SUCCESSFUL', True

            if (bs[4*x][4*y+i] == bs[4*x+1][4*y+i] == bs[4*x+2][4*y+i] == bs[4*x+3][4*y+i]) and (bs[4*x][4*y+i] == ply):
                self.block_status[x][y] = ply
                return 'SUCCESSFUL', True

        if (bs[4*x+1][4*y] == bs[4*x][4*y+1] == bs[4*x+2][4*y+1] == bs[4*x+1][4*y+2]) and (bs[4*x+1][4*y] == ply):
            self.block_status[x][y] = ply
            return 'SUCCESSFUL', True

        if (bs[4*x+1][4*y+1] == bs[4*x][4*y+2] == bs[4*x+2][4*y+2] == bs[4*x+1][4*y+3]) and (bs[4*x+1][4*y+1] == ply):
            self.block_status[x][y] = ply
            return 'SUCCESSFUL', True

        if (bs[4*x+2][4*y] == bs[4*x+1][4*y+1] == bs[4*x+3][4*y+1] == bs[4*x+2][4*y+2]) and (bs[4*x+2][4*y] == ply):
            self.block_status[x][y] = ply
            return 'SUCCESSFUL', True

        if (bs[4*x+2][4*y+1] == bs[4*x+1][4*y+2] == bs[4*x+3][4*y+2] == bs[4*x+2][4*y+3]) and (bs[4*x+2][4*y+1] == ply):
            self.block_status[x][y] = ply
            return 'SUCCESSFUL', True

        for i in range(4):
            for j in range(4):
                if bs[4*x+i][4*y+j] == '-':
                    return 'SUCCESSFUL', False
        self.block_status[x][y] = 'd'
        return 'SUCCESSFUL', False

def player_turn(game_board, old_move, obj, ply, opp, flg):
        temp_board_status = copy.deepcopy(game_board.board_status)
        temp_block_status = copy.deepcopy(game_board.block_status)
        signal.alarm(TIME)
        WINNER = ''
        MESSAGE = ''
        pts = {"P1": 0, "P2": 0}
        to_break = False
        p_move = ''

        try:
            p_move = obj.move(game_board, old_move, flg)
        except TimedOutExc:

            WINNER = opp
            MESSAGE = 'TIME OUT'
            pts[opp] = MAX_PTS
            return p_move, WINNER, MESSAGE, pts["P1"], pts["P2"], True, False
        except Exception as e:
            WINNER = opp
            MESSAGE = "THREW AN EXCEPTION"
            traceback.print_exc()
            pts[opp] = MAX_PTS
            return p_move, WINNER, MESSAGE, pts["P1"], pts["P2"], True, False
        signal.alarm(0)

        if (game_board.block_status != temp_block_status) or (game_board.board_status != temp_board_status):
            WINNER = opp
            MESSAGE = 'MODIFIED THE BOARD'
            pts[opp] = MAX_PTS
            return p_move, WINNER, MESSAGE, pts["P1"], pts["P2"], True, False

        update_status, block_won = game_board.update(old_move, p_move, flg)
        if update_status == 'UNSUCCESSFUL':
            WINNER = opp
            MESSAGE = 'INVALID MOVE'
            pts[opp] = MAX_PTS
            return p_move, WINNER, MESSAGE, pts["P1"], pts["P2"], True, False

        status = game_board.find_terminal_state()
        print status
        if status[1] == 'WON':
            pts[ply] = MAX_PTS
            WINNER = ply
            MESSAGE = 'WON'
            return p_move, WINNER, MESSAGE, pts["P1"], pts["P2"], True, False
        elif status[1] == 'DRAW':
            WINNER = 'NONE'
            MESSAGE = 'DRAW'
            return p_move, WINNER, MESSAGE, pts["P1"], pts["P2"], True, False

        return p_move, WINNER, MESSAGE, pts["P1"], pts["P2"], False, block_won


def gameplay(obj1, obj2):

    game_board = Board()
    fl1 = 'x'
    fl2 = 'o'
    old_move = (-1, -1)
    WINNER = ''
    MESSAGE = ''
    pts1 = 0
    pts2 = 0

    game_board.print_board()
    signal.signal(signal.SIGALRM, handler)
    while(1):

        p1_move, WINNER, MESSAGE, pts1, pts2, to_break, block_won = player_turn(game_board, old_move, obj1, "P1", "P2", fl1)

        if to_break:
            break

        old_move = p1_move
        game_board.print_board()

        if block_won:
            p1_move, WINNER, MESSAGE, pts1, pts2, to_break, block_won = player_turn(game_board, old_move, obj1, "P1", "P2", fl1)

            if to_break:
                break

            old_move = p1_move
            game_board.print_board()


        p2_move, WINNER, MESSAGE, pts1, pts2, to_break, block_won = player_turn(game_board, old_move, obj2, "P2", "P1", fl2)

        if to_break:
            break

        game_board.print_board()
        old_move = p2_move

        if block_won:
            p2_move, WINNER, MESSAGE, pts1, pts2, to_break, block_won = player_turn(game_board, old_move, obj2, "P2", "P1", fl2)

            if to_break:
                break

            old_move = p2_move
            game_board.print_board()

    game_board.print_board()

    print "Winner:", WINNER
    print "Message", MESSAGE

    x = 0
    d = 0
    o = 0
    for i in range(4):
        for j in range(4):
            if game_board.block_status[i][j] == 'x':
                x += 1
            if game_board.block_status[i][j] == 'o':
                o += 1
            if game_board.block_status[i][j] == 'd':
                d += 1
    print 'x:', x, ' o:', o, ' d:', d
    if MESSAGE == 'DRAW':

        for i in range(4):
            for j in range(4):
                val = 4
                if is_corner(i,j):
                    val = 6
                elif is_centre(i,j):
                    val = 3
                if game_board.block_status[i][j] == 'x':
                    pts1 += val
                if game_board.block_status[i][j] == 'o':
                    pts2 += val
    return (pts1,pts2)

def is_centre(row, col):
    if row == 1 and col == 1:
        return 1
    if row == 1 and col == 2:
        return 1
    if row == 2 and col == 1:
        return 1
    if row == 2 and col == 2:
        return 1
    return 0

def is_corner(row, col):
    if row == 0 and col == 0:
        return 1
    if row == 0 and col == 3:
        return 1
    if row == 3 and col == 0:
        return 1
    if row == 3 and col == 3:
        return 1
    return 0

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'Usage: python simulator.py <option>'
        print '<option> can be 1 => Random player vs. Random player'
        print '                2 => Human vs. Random Player'
        print '                3 => Human vs. Human'
        sys.exit(1)

    obj1 = ''
    obj2 = ''
    option = sys.argv[1]
    if option == '1':
        obj1 = Swagalicious()
        obj2 = Swagalicious()

    elif option == '2':
        obj1 = Swagalicious()
        obj2 = Random_Player()
    elif option == '3':
        obj1 = Swagalicious()
        obj2 = Team12()
    else:
        print 'Invalid option'
        sys.exit(1)

    x = gameplay(obj1, obj2)
    print "Player 1 points:", x[0]
    print "Player 2 points:", x[1]

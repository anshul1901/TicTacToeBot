import sys
import random
import signal
import time
import copy
import traceback

class Team16():
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

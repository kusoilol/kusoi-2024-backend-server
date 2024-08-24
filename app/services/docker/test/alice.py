def read(board):
    if board:
        n, m = map(int, input().split())
        for _ in range(n):
            input()
    else:
        my_x, my_y, dir = input().split()
        my_x, my_y, dir = input().split()
        for i in range(int(input())):
            input()

board = True
while True:
    read(board)
    board = False
    print('sh')

for _ in range(10):
    field = [[i for i in input().split()] for _ in range(3)]
    for i in range(3):
        stop = False
        for j in range(3):
            if field[i][j] == '.':
                print(1)
                print(i + 1, j + 1)
                stop = True
                break
        if stop:
            break

def in_bounds(i, j):
    return 0 <= i <= 2 and 0 <= j <= 2


def is_complete(field_):
    deltas = [[1, 0], [1, 1], [0, 1], [-1, 1]]
    for i in range(3):
        for j in range(3):
            for di, dj in deltas:
                if in_bounds(i + di, j + dj) and in_bounds(i + 2 * di, j + 2 * dj):
                    if field_[i][j] != '.' and field_[i][j] == field_[i + di][j + dj] == field_[i + di * 2][j + dj * 2]:
                        return True
    return False


print('SETUP 3')
field = [['.'] * 3 for _ in range(3)]
for l in field:
    print(*l)
turn = 0
while turn <= 8:
    i, j = map(int, input().split())
    i -= 1
    j -= 1
    if in_bounds(i, j) and field[i][j] == '.':
        field[i][j] = ['x', 'o'][turn % 2]
        if is_complete(field):
            print(f'WIN {1 + turn % 2}')
            exit(0)
        elif turn == 8 and not is_complete(field):
            print('DRAW -1')
            exit(0)
        else:
            print(f"KEEP 3")
            for l in field:
                print(*l)
    else:
        print(f'LOSE {1 + turn % 2}')
        exit(0)
    turn += 1

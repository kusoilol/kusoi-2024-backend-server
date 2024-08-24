import sys
from copy import deepcopy

DIRECTION_DELTAS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
READABLE_DIRS = ['up', 'right', 'down', 'left']


class Pos:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)

    def __add__(self, other):
        if isinstance(other, Pos):
            return Pos(self.x + other.x, self.y + other.y)
        else:
            return Pos(self.x + other[0], self.y + other[1])

    def __sub__(self, other):
        if isinstance(other, Pos):
            return Pos(self.x - other.x, self.y - other.y)
        else:
            return Pos(self.x - other[0], self.y - other[1])

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class GameObject:
    def __init__(self, pos, dir):
        self.pos = pos
        self.dir = dir


def print_field():
    f = deepcopy(field)
    tank_dir_render = '↑→↓←'
    for t in tanks:
        if not t:
            continue
        f[t.pos.y][t.pos.x] = tank_dir_render[t.dir]
    for b in bullets:
        f[b.pos.y][b.pos.x] = '*'
    for line in f:
        print(''.join(line))


def in_bounds(pos):
    return FIELD_WIDTH > pos.x >= 0 and FIELD_HEIGHT > pos.y >= 0 and field[pos.y][pos.x] == '.'


map_filename = sys.argv[1] if len(sys.argv) > 1 else 'default.txt'
tanks = []
bullets = set()
field = []

with open(map_filename) as f:
    tanks_amount = int(f.readline())
    for _ in range(tanks_amount):
        a, b, c = map(int, f.readline().split())
        tanks.append(GameObject(Pos(a, b), c))
    for s in f.readlines():
        field.append(list(s.strip()))
FIELD_WIDTH = len(field[0])
FIELD_HEIGHT = len(field)

print_data = False
# fw, bw, rr, rl, sh, ff - вперед, назад, поворот вправо, поворот влево, выстрел, похуй проебали
for i in range(100):
    for team in range(tanks_amount):
        if tanks[team] is None:
            continue
        if len(tanks) - tanks.count(None) == 1:
            for i in range(tanks_amount):
                if tanks[i] is not None:
                    print('win', i + 1)
                    exit()
        if i == 0:
            print('setup', FIELD_HEIGHT + 1 + tanks_amount + 1 + len(bullets))
            print(FIELD_HEIGHT, FIELD_WIDTH)
            for line in field:
                print(''.join(line))
        else:
            print('data', tanks_amount + 1 + len(bullets))
        print(tanks[team].pos.x, tanks[team].pos.y, READABLE_DIRS[tanks[team].dir])
        for team2 in range(tanks_amount):
            if team != team2:
                print(tanks[team2].pos.x, tanks[team2].pos.y, READABLE_DIRS[tanks[team2].dir])
        print(len(bullets))
        for bullet in bullets:
            print(bullet.pos.x, bullet.pos.y, READABLE_DIRS[bullet.dir])
        command = input()
        if command == 'fw':
            tanks[team].pos += DIRECTION_DELTAS[tanks[team].dir]
            if not in_bounds(tanks[team].pos):
                tanks[team].pos -= DIRECTION_DELTAS[tanks[team].dir]
        elif command == 'bw':
            tanks[team].pos += DIRECTION_DELTAS[(tanks[team].dir + 2) % 4]
            if not in_bounds(tanks[team].pos):
                tanks[team].pos -= DIRECTION_DELTAS[(tanks[team].dir + 2) % 4]
        elif command == 'rr':
            tanks[team].dir += 1
            tanks[team].dir %= 4
        elif command == 'rl':
            tanks[team].dir -= 1
            tanks[team].dir %= 4
        elif command == 'sh':
            bullets.add(GameObject(tanks[team].pos, tanks[team].dir))
        else:
            tanks[team] = None

    new_bullets = set()
    for b in bullets:
        b.pos += DIRECTION_DELTAS[b.dir]
        if in_bounds(b.pos):
            for team in range(tanks_amount):
                if tanks[team] is None:
                    continue
                if tanks[team].pos == b.pos:
                    tanks[team] = None
                    break
            else:
                new_bullets.add(b)
    bullets = new_bullets

print('draw -1')

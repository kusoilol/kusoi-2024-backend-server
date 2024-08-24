import os

_up = os.path.dirname

ROOT_PATH = _up(_up(_up(_up(os.path.abspath(__file__)))))

DATA_PATH = os.path.join(ROOT_PATH, 'data')
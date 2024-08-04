import os

_up = os.path.dirname

ROOT_PATH = _up(_up(_up(_up(os.path.abspath(__file__)))))

TEAMS_PATH = os.path.join(ROOT_PATH, 'teams')

HISTORY_NAME = "solutions_history"

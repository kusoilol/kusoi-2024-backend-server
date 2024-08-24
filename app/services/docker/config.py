import os

_up = os.path.dirname

ROOT_PATH = _up(_up(_up(_up(os.path.abspath(__file__)))))

MAIN_TESTER = "main_test.py"
DOCKERPATH = os.path.join(ROOT_PATH, 'app', 'services', 'docker', 'dockerhome')
TESTFOLDER = "app/"

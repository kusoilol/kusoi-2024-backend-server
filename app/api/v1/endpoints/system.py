import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix='/system')


class Item(BaseModel):
    code: str


TESTER_PATH = "app/services/docker/dockerhome/"


@router.post('/tester')
def change_tester(tester: Item) -> None:
    os.rename(os.path.join(TESTER_PATH, 'tester.py'), os.path.join(TESTER_PATH, 'old_tester.py'))
    try:
        with open(os.path.join(TESTER_PATH, 'tester.py'), 'w') as file:
            file.write(tester.code)
    except (IOError, OSError, FileNotFoundError, RuntimeError) as e:
        os.remove(os.path.join(TESTER_PATH, 'tester.py'))
        os.rename(os.path.join(TESTER_PATH, 'old_tester.py'), os.path.join(TESTER_PATH, 'tester.py'))
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/old_tester')
def fuck_go_back() -> None:
    try:
        if os.path.exists(os.path.join(TESTER_PATH, 'old_tester.py')):
            os.remove(os.path.join(TESTER_PATH, 'tester.py'))
            os.rename(os.path.join(TESTER_PATH, 'old_tester.py'), os.path.join(TESTER_PATH, 'tester.py'))
    except (IOError, OSError, FileNotFoundError, RuntimeError) as e:
        raise HTTPException(status_code=500, detail=str(e))

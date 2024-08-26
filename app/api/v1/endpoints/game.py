import io
import os
import shutil
import random
import time
import uuid
from uuid import UUID

import docker.errors
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import TeamManager
from app.schemas import Language
from app.db import db
from app.dm import dm

router = APIRouter(prefix="/game")


def get_data_of_team(team_id: UUID) -> tuple[str, Language]:
    tm = TeamManager(team_id)
    filepath = tm.get_main_solution()
    language = tm.get_language_of_main()
    return filepath, language


def get_result_from_logs(logs: list[str]):
    data = logs[0].split('\n')
    for x in data[::-1]:
        if 'win' in x or 'draw' in x:
            return x
    return "draw -1"

@router.get("/run")
async def play(first_team: UUID, second_team: UUID) -> tuple[str, str, UUID]:
    first_path, first_lang = get_data_of_team(first_team)
    second_path, second_lang = get_data_of_team(second_team)
    if random.choice([False, True]):
        first_team, second_team = second_team, first_team
        first_path, second_path = second_path, first_path
        first_lang, second_lang = second_lang, first_lang
    out = []
    print(f'Playing {str(first_team)} and {str(second_team)}')
    for i in range(3):
        try:
            out.append(dm.run_game(first_path, first_lang, second_path, second_lang))
            break
        except docker.errors.DockerException as e:
            if i == 2:
                raise HTTPException(status_code=500, detail=str(e))

    winner, code = get_result_from_logs(out).split()
    if winner != 'draw':
        winner = str(first_team) if code == '1' else str(second_team)
    print(winner, code)
    winner = str(winner)
    log = '\n'.join(out)
    game_id = db.add_game(first_team, second_team, winner, log)
    return log, winner, game_id


class PlayResponse(BaseModel):
    timestamp: str
    game_id: UUID
    winner: str
    opponent: UUID


@router.get('/list')
async def get_games_by_team_id(team_id: UUID) -> list[PlayResponse] | None:
    data = db.get_games(team_id)
    if data is None:
        return None
    out = []
    for a, b, c, d in data:
        out.append(PlayResponse(timestamp=a,
                                game_id=b,
                                winner=str(c),
                                opponent=d))
    return out


@router.get('/')
async def get_game_by_game_id(game_id: UUID) -> str | None:
    return db.get_log(game_id)


class Submission(BaseModel):
    code: str
    team_id: UUID
    language: Language


def remove_directory(path: str):
    shutil.rmtree(path)
    os.rmdir(path)


@router.post('/local')
async def local_play(item: Submission) -> tuple[str, str, UUID]:
    dummy_team = uuid.uuid4()
    tm = TeamManager(dummy_team)
    with io.BytesIO(item.code.encode()) as file:
        tm.create_solution(file, item.language)
    result = await play(item.team_id, dummy_team)
    try:
        remove_directory(tm._team_path)
    except (OSError, IOError, FileExistsError, FileNotFoundError) as e:
        print(str(e))
    except PermissionError as e:
        time.sleep(0.1)
        try:
            remove_directory(tm._team_path)
        except Exception as a:
            print(str(e), 'then', str(a))
    out = list(result)
    if out[1] == dummy_team:
        out[1] = 'bot'
    out[1] = str(out[1])
    return tuple(out)

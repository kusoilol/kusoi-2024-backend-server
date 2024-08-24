import random
from uuid import UUID

import docker.errors
from fastapi import APIRouter, HTTPException
from app.services import TeamManager, DockerManager, DBManager
from app.schemas import Language

router = APIRouter(prefix="/game")


def get_data_of_team(team_id: UUID) -> tuple[str, Language]:
    tm = TeamManager(team_id)
    filepath = tm.get_main_solution()
    language = tm.get_language_of_main()
    return filepath, language


def get_result_from_logs(logs: list[str]):
    return logs[1].split('\n')[-2]


@router.get("/run")
async def play(first_team: UUID, second_team: UUID) -> tuple[str, UUID, UUID]:
    first_path, first_lang = get_data_of_team(first_team)
    second_path, second_lang = get_data_of_team(second_team)
    if random.choice([False, True]):
        first_team, second_team = second_team, first_team
        first_path, second_path = second_path, first_path
        first_lang, second_lang = second_lang, first_lang
    out = [str(first_team)]
    for i in range(3):
        try:
            dm = DockerManager()
            out.append(dm.run_game(first_path, first_lang, second_path, second_lang))
            break
        except docker.errors.DockerException as e:
            if i == 2:
                raise HTTPException(status_code=500, detail=str(e))

    winner = get_result_from_logs(out)
    winner = first_team if winner == '1' else second_team
    log = '\n'.join(out)
    db = DBManager()
    game_id = db.add_game(first_team, second_team, winner, log)
    db.close()
    return log, winner, game_id


@router.get('/list')
async def get_game_ids_by_team_id(team_id: UUID) -> list[tuple] | None:
    return DBManager().game_id_by_team_id(team_id)


@router.get('/')
async def get_game_by_game_id(game_id: UUID) -> str | None:
    return DBManager().log_by_game_id(game_id)

import random
from uuid import UUID

import docker.errors
from fastapi import APIRouter, HTTPException
from app.services import TeamManager, DockerManager
from app.schemas import Language

router = APIRouter(prefix="/game")


def get_data_of_team(team_id: UUID) -> tuple[str, Language]:
    tm = TeamManager(team_id)
    filepath = tm.get_main_solution()
    language = tm.get_language_of_main()
    return filepath, language


@router.get("/")
def play(first_team: UUID, second_team: UUID) -> str:
    first_path, first_lang = get_data_of_team(first_team)
    second_path, second_lang = get_data_of_team(second_team)
    if random.choice([False, True]):
        first_team, second_team = second_team, first_team
        first_path, second_path = second_path, first_path
        first_lang, second_lang = second_lang, first_lang
    out = [first_team]
    for i in range(3):
        try:
            dm = DockerManager()
            result = dm.run_game(first_path, first_lang, second_path, second_lang)
            out.append(result)
            break
        except docker.errors.DockerException as e:
            if i == 2:
                raise HTTPException(status_code=500, detail=str(e))
    return '\n'.join(out)

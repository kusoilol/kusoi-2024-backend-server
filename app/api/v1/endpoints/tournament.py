from uuid import UUID
from typing import List

from fastapi import APIRouter
from .game import play
from app.db import db
from app.services.team_manager import TeamManager

router = APIRouter(prefix="/tournament")


@router.post('/')
async def run_tournament(teams: List[UUID]) -> dict:
    """
    :param teams: participating teams

    :return: dictionary: key is team_id, value is a list of three items:

        1. score before tournament

        2. change of score during tournament

        3. score after tournament

    """

    data = db.dump_scoreboard(teams)
    new_data = data
    for key, val in data.items():
        new_data[key] = [val, 0, 0]
    for team in teams:
        if team not in new_data:
            new_data[team] = [0, 0, 0]
    data = new_data

    managers = [TeamManager(team) for team in teams]

    for i in range(len(teams)):
        print(f'{teams[i]} team playing')
        if not managers[i].has_solutions():
            continue
        for j in range(i + 1, len(teams)):
            if managers[j].has_solutions():
                log, winner, game_id = await play(teams[i], teams[j])
                if winner != 'draw':
                    if winner not in data:
                        data[winner] = [0, 0, 0]
                    data[winner][1] += 1

    for team, lst in data.items():
        if lst[1] != 0:
            db.inc_score(team, lst[1])
        lst[2] = lst[1] + lst[0]

    return data


@router.get('/score')
async def get_score(team_id: UUID) -> int:
    return db.get_score(team_id)


@router.get('/scoreboard')
async def get_scoreboard() -> dict:
    return db.dump_scoreboard()

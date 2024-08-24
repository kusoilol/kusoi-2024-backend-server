from uuid import UUID
from typing import List

from fastapi import APIRouter
from .game import play
from app.db import db

router = APIRouter(prefix="/tournament")


@router.post('/')
async def run_tournament(teams: List[UUID]) -> dict:
    """
    :param teams: participating teams
    :return: dictionary: key - team_id, value = list[previous_score, delta]
    """
    data = db.dump_scoreboard(teams)
    new_data = data
    for key, val in data.items():
        new_data[key] = [val, 0]
    data = new_data

    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            log, winner, game_id = await play(teams[i], teams[j])
            if winner not in data:
                data[winner] = [0, 0]

            data[winner][1] += 1

    for team, lst in data.items():
        if lst[1] != 0:
            db.inc_score(team, lst[1])

    return data


@router.get('/score')
async def get_score(team_id: UUID) -> int:
    return db.get_score(team_id)

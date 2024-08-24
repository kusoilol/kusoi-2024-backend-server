from uuid import UUID
from typing import List

from collections import defaultdict
from fastapi import APIRouter
from app.services import DBManager
from .game import play

router = APIRouter(prefix="/tournament")


@router.post('/')
async def run_tournament(teams: List[UUID]) -> dict:
    db = DBManager()
    result = defaultdict(lambda: [0, 0])
    for team in teams:
        result[team][0] = db.score_by_team_id(team)
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            log, winner, game_id = await play(teams[i], teams[j])
            result[winner][1] += 1
    return result

from uuid import UUID
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services import TeamManager

router = APIRouter()


@router.get("/get_solution", response_class=FileResponse)
async def get_solution(team_id: UUID, solution_id: int | None = None) -> str:
    team_manager = TeamManager(team_id)
    if solution_id is None:
        return team_manager.get_main_solution()
    try:
        return team_manager.get_solution(solution_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404,
                            detail=str(e))


@router.get("/last_solution")
async def last_solution(team_id: UUID) -> tuple[int, int]:
    team_manager = TeamManager(team_id)
    if team_manager.max_id == 0:
        raise HTTPException(status_code=404,
                            detail=f"Team {team_id} doesn't have any solutions yet")
    return team_manager.max_id, int(team_manager.get_main_filename()[0].split('.')[0])

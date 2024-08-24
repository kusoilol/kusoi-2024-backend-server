import io
from uuid import UUID
from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.services import TeamManager
from app.schemas import Language

router = APIRouter(prefix="/solutions")


@router.get("/", response_class=FileResponse)
async def get_solution(team_id: UUID, solution_id: int) -> FileResponse:
    team_manager = TeamManager(team_id)
    if solution_id is None:
        return team_manager.get_main_solution()
    try:
        return team_manager.get_solution(solution_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


def check_any_solutions(team_manager: TeamManager):
    """
    HTTPException with 404 code if team doesn't have any solution
    """
    if team_manager.max_id == 0:
        raise HTTPException(status_code=404,
                            detail=f"Team {team_manager.team_id} doesn't have any solutions yet")


@router.get("/last")
async def last_solution(team_id: UUID) -> tuple[int, int]:
    """
    :return: int tuple of max_id and id of main solution
    """
    team_manager = TeamManager(team_id)
    check_any_solutions(team_manager)
    return team_manager.max_id, int(team_manager.get_main_filename()[0].split('.')[0])


@router.get("/main", response_class=FileResponse)
async def get_main_solution(team_id: UUID) -> FileResponse:
    team_manager = TeamManager(team_id)
    check_any_solutions(team_manager)
    return team_manager.get_main_solution()


@router.put("/main")
async def select_main(team_id: UUID, solution_id: int):
    team_manager = TeamManager(team_id)
    check_any_solutions(team_manager)
    try:
        team_manager.select_main(solution_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IOError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def upload_solution(code: str, team_id: UUID, language: Language) \
        -> int:
    team_manager = TeamManager(team_id)
    try:
        return team_manager.create_solution(io.BytesIO(code.encode()), language)
    except IOError as e:
        raise HTTPException(status_code=500, detail=str(e))

from uuid import UUID
from fastapi import APIRouter, UploadFile, HTTPException
from app.schemas import Language
from app.services import TeamManager

router = APIRouter()


@router.post("/upload_solution")
async def upload_solution(code: UploadFile, team_id: UUID, language: Language) \
        -> int:
    team_manager = TeamManager(team_id)
    try:
        return team_manager.create_solution(code.file, language)
    except IOError as e:
        raise HTTPException(status_code=500, detail=str(e))

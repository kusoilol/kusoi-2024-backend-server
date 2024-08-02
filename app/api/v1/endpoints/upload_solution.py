from fastapi import APIRouter, UploadFile, File, Depends, Form
from app.schemas import UploadSolutionRequest, UploadSolutionResponse, Language

router = APIRouter()


def get_user_request(user_id: int = Form(...), language: Language = Form(...)) -> UploadSolutionRequest:
    return UploadSolutionRequest(user_id=user_id, language=language)


@router.post("/upload_solution")
async def upload_solution(code: UploadFile = File(...),
                            user_data: UploadSolutionRequest = Depends(get_user_request)) \
        -> UploadSolutionResponse:
    ...
    """
    try:
        Docker.get_user(user_data.user_id).upload_new_solution(code)
    except Exception:
        return Amogus
    return Docker.get_user(user_data.user_id).current_solution().id
    """

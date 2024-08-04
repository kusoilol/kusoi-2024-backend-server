from pydantic import BaseModel
from .solution_language import Language


class UploadSolutionRequest(BaseModel):
    """
    Data that is expected from front-side when acquiring a solution uploading request
        passed along with code file
    """
    user_id: int
    language: Language

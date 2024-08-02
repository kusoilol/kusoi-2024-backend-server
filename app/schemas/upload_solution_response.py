from pydantic import BaseModel


class UploadSolutionResponse(BaseModel):
    submission_id: int

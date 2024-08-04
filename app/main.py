from fastapi import FastAPI
from app.api.v1.endpoints import get_solution_router, upload_solution_router

app = FastAPI()
app.include_router(get_solution_router)
app.include_router(upload_solution_router)

from fastapi import FastAPI
from app.api.v1.endpoints import solutions_router

app = FastAPI()
app.include_router(solutions_router)

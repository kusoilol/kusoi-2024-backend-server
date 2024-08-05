from fastapi import FastAPI
from app.api import v1_router

app = FastAPI()
app.include_router(v1_router)

from fastapi import APIRouter
from .endpoints import solutions_router, game_router, tournament_router, system_router

version_router = APIRouter(prefix="/v1")
version_router.include_router(solutions_router)
version_router.include_router(game_router)
version_router.include_router(tournament_router)
version_router.include_router(system_router)

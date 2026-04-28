from fastapi import APIRouter

from backend.routes.carreira_routes import router as carreira_router
from backend.routes.health_routes import router as health_router
from backend.routes.usuario_routes import router as usuario_router

router = APIRouter(prefix="/api")
router.include_router(health_router)
router.include_router(carreira_router)
router.include_router(usuario_router)

__all__ = ["router"]

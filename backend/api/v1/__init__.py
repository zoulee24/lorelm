from fastapi import APIRouter

from ...response import SuccessResponse
from .admin import admin_router
from .character import role_router, world_router

v1_router = APIRouter(prefix="/v1", default_response_class=SuccessResponse)
v1_router.include_router(admin_router)
v1_router.include_router(role_router)
v1_router.include_router(world_router)

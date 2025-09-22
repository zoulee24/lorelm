from fastapi import APIRouter

from .user import user_router

admin_router = APIRouter(prefix="/admin", tags=["admin"])
admin_router.include_router(user_router)

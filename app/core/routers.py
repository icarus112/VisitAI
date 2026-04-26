from aiogram import Router

from app.handlers.record import router as record_router
from app.handlers.admin import router as admin_router

router = Router()

router.include_router(record_router)
router.include_router(admin_router)
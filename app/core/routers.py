from aiogram import Router

from app.handlers.record import router as record_router
from app.handlers.admin import router as admin_router
from app.handlers.dev import dev_router as dev_router


router = Router()

router.include_router(record_router)
router.include_router(admin_router)
router.include_router(dev_router)
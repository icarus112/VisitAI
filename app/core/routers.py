from aiogram import Router

from app.handlers.record import router as record_router
from app.handlers.admin import router as admin_router
from app.handlers.dev import dev_router as dev_router
from app.handlers.start import router as start_router
from app.handlers.user import router as user_router
from app.handlers.ai_user import router as ai_user_router
from app.handlers.ai_admin import router as ai_admin_router


router = Router()

router.include_router(admin_router)
router.include_router(start_router)
router.include_router(record_router)
router.include_router(dev_router)
router.include_router(user_router)
router.include_router(ai_admin_router)
router.include_router(ai_user_router)
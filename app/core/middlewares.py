from typing import Dict, Any, Callable
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware
from fastapi import FastAPI

from app.repository.admin import AdminRepos
from app.repository.booking import BookingRepos
from app.repository.catalog import CatalogRepos
from app.repository.user import UserRepos
from app.service.admin import AdminService
from app.service.booking import BookingService
from app.service.catalog import CatalogService
from app.service.user import UserService
from database.async_engine import async_session

# создание сессии, и дать доступ к нему классам которые написаны ниже
class AppMiddleware(BaseMiddleware):
    def __init__(self, async_session):
        self.async_session = async_session

    async def __call__(self, handler: Callable,
                       event: TelegramObject,
                       data: Dict[str, Any]):
        async with self.async_session() as session:
            try:
                #session
                data["session"] = session

                #repos
                us_rp = UserRepos(session)
                ad_rp = AdminRepos(session)
                ct_rp = CatalogRepos(session)
                bk_rp = BookingRepos(session)

                # service
                data["us_sv"] = UserService(us_rp)
                data["ad_sv"] = AdminService(ad_rp)
                data["ct_sv"] = CatalogService(ct_rp)
                data["bk_sv"] = BookingService(bk_rp)

                result = await handler(event, data)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise

# class RepoMiddleware(BaseMiddleware):
#     def __init__(self, session_pool):
#         self.session_pool = session_pool
#
#     async def __call__(self, handler: Callable,
#                        event: TelegramObject,
#                        data: Dict[str, Any]):
#         async with self.session_pool() as session:
#             data["session"] = session
#             data["ad_rp"] = AdminRepos(session)
#             return await handler(event, data)
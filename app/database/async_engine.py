import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.conf import settings

async_engine = create_async_engine(settings.database_url,
                                   json_serializer= lambda obj: json.dumps(obj, ensure_ascii=False),
                                   echo=False)

async_session = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

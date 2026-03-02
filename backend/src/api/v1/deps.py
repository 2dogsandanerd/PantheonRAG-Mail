from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.database import get_db
from src.database.models import User
from src.core.auth import get_current_active_user


async def get_db_session() -> AsyncSession:
    async for session in get_db():
        yield session


CurrentUser = Annotated[User, Depends(get_current_active_user)]
DBSession = Annotated[AsyncSession, Depends(get_db_session)]

import asyncio
from jose import jwt
from src.database.database import async_session_maker
from src.database.models import User
from sqlalchemy import select

SECRET_KEY = "dev-secret-key-change-in-production"

async def test():
    async with async_session_maker() as db:
        result = await db.execute(select(User).where(User.username == "endboss_tester"))
        user = result.scalar_one_or_none()
        if user:
            print(f"User in DB: {user.id}, {user.username}")
            from src.core.auth import create_access_token, decode_token
            token = create_access_token({"sub": str(user.id)})
            print("Token:", token)
            payload = decode_token(token)
            print("Decoded Payload:", payload)
        else:
            print("User nicht in DB")

asyncio.run(test())

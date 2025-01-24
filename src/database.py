from src.config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASS
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.models import Keys
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def check_api_key(api_key: str):
    async with engine.begin() as conn:
        stmt = select(Keys).where(Keys.api_key == api_key)
        result = await conn.execute(stmt)
        return result.all()

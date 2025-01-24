from typing import Annotated

from fastapi import Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Keys
from src.database import get_session


async def verify_key(api_key: Annotated[str, Header()], session: AsyncSession = Depends(get_session)):
    stmt = select(Keys).where(Keys.api_key == api_key)
    key_exists = await session.execute(stmt)
    if len(key_exists.all()) < 1:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Api-Key header invalid")
    return JSONResponse(status_code=200, content='Success')

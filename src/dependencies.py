from fastapi import Depends
from typing import Annotated
from src.database import AsyncSession, get_session
from pydantic import BaseModel, Field


class PaginationParamsSchema(BaseModel):
	limit: int = Field(50, ge=0, le=50)
	offset: int = Field(0, ge=0)

SessionDep = Annotated[AsyncSession, Depends(get_session)]
PaginationDep = Annotated[PaginationParamsSchema, Depends(PaginationParamsSchema)]

from typing import Type, List, Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

async def search_data(
    session: AsyncSession,
    model: Type,
    search_fields: List[str],
    query_text: str,
    limit: int = 10,
    offset: int = 0,
    extra_filters: Optional[dict] = None,
    join_relations: Optional[List[str]] = None
):
    """
    Универсальная функция поиска по модели SQLAlchemy.
    
    :param session: асинхронная сессия SQLAlchemy
    :param model: модель для поиска
    :param search_fields: поля модели, в которых искать текст
    :param query_text: текст поиска
    :param limit: лимит результатов
    :param offset: смещение для пагинации
    :param extra_filters: дополнительные фильтры, например {"is_deleted": False}
    :param join_relations: связи, которые нужно сразу подгрузить через joinedload
    """
    
    # Формируем условия поиска по тексту
    search_conditions = [getattr(model, field).ilike(f"%{query_text}%") for field in search_fields]

    # Основной запрос
    stmt = select(model)
    
    # Подгружаем отношения
    if join_relations:
        for rel in join_relations:
            stmt = stmt.options(joinedload(getattr(model, rel)))

    # Добавляем поиск
    stmt = stmt.where(or_(*search_conditions))

    # Добавляем дополнительные фильтры
    if extra_filters:
        for key, value in extra_filters.items():
            stmt = stmt.where(getattr(model, key) == value)

    # Пагинация
    stmt = stmt.limit(limit).offset(offset)
    
    # Выполняем
    result = await session.execute(stmt)
    return result.scalars().all()
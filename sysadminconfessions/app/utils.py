# app/utils.py
from sqlmodel import Session, SQLModel, select
from sqlalchemy import func
from typing import Type


def paginate(
    session: Session,
    model: Type[SQLModel],
    page: int,
    page_size: int = 3,
    sort: str = "recent",
):
    # total count
    total = session.exec(select(func.count()).select_from(model)).one()

    # build base select
    stmt = select(model)

    # apply sort
    if sort == "top":
        stmt = stmt.order_by(model.score.desc())
    elif sort == "random":
        stmt = stmt.order_by(func.random())
    else:  # recent
        stmt = stmt.order_by(model.id.desc())

    # apply pagination (for random, offset+limit still works)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    results = session.exec(stmt).all()

    return {
        "results": results,
        "page": page,
        "page_size": page_size,
        "total": total,
        "has_next": page * page_size < total,
        "has_prev": page > 1,
    }


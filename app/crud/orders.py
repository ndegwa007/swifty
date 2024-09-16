from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.orders import Order, OrderCreate, OrderUpdate
import app.models as models
from typing import Sequence
from sqlalchemy import select
from fastapi import HTTPException
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError


async def create_order(db_session: AsyncSession, params: OrderCreate) -> Order:
    order = models.Order(**params.model_dump())
    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order

async def get_orders(db_session: AsyncSession) -> Sequence[Order]:
    res = await db_session.execute(select(models.Order))
    orders = res.scalars().all()
    return orders

async def get_order(order_id: UUID, db_session: AsyncSession) -> Order:
    order = (
        await db_session.scalars(select(models.Order).where(models.Order.order_id == str(order_id)))
    ).first()
    if not order:
        raise HTTPException(status_code=404, message="order not found!")
    return order

async def update_order(order_id:UUID, params: OrderUpdate, db_session: AsyncSession) -> Order:
    order = await get_order(order_id, db_session)
    
    for attr, value in params.model_dump(exclude_unset=True).items():
        setattr(order, attr, value)

    db_session.add(order)
    await db_session.commit()
    await db_session.refresh(order)
    return order

async def delete_order(order_id:UUID, db_session: AsyncSession) -> Order:
    order = await get_order(order_id, db_session)

    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    
    try:
        await db_session.delete(order)
        await db_session.commit()
    except SQLAlchemyError as e:
        await db_session.rollback()
        raise HTTPException(status_code=500, detail="an error occured while deleting order")
    return order
    
    
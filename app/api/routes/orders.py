from fastapi import APIRouter, Depends
from app.schemas import Order, OrderCreate, OrderUpdate
from typing import Sequence
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db_session
import app.crud.orders as orders
from sqlalchemy import select
import app.models as models
from uuid import UUID


router = APIRouter()

@router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db_session)) -> Order:
    logger.info(f"creating order:  {order}")
    order_params = OrderCreate(**order.model_dump())
    created_order = await orders.create_order(db, order_params)
    logger.info(f"created order: {created_order}")
    return created_order

@router.get("/orders", response_model=list[Order])
async def get_orders(db:AsyncSession = Depends(get_db_session)) -> Sequence[Order]:
    logger.info("fetching orders")
    orders_list = await orders.get_orders(db)
    logger.info(f"fetched orders: {orders_list}")
    return orders_list

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: UUID, db: AsyncSession = Depends(get_db_session)) -> Order:
    logger.info(f"get order with id {order_id}")
    order = await orders.get_order(order_id, db)
    logger.info(f"found order: {order}")
    return order

@router.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: UUID, params: OrderUpdate, db: AsyncSession = Depends(get_db_session)) -> Order:
    logger.info(f"update order with id: {order_id}")
    order = await orders.update_order(order_id, params, db)
    logger.info(f"updated order: {order}")
    return order

@router.delete("/orders/{order_id}", response_model=Order)
async def delete_order(order_id: UUID, db: AsyncSession = Depends(get_db_session)) -> Order:
    logger.info(f"deleting order with id: {order_id}")
    order = await orders.delete_order(order_id, db)
    logger.info(f"deleted order: {order}")
    return order

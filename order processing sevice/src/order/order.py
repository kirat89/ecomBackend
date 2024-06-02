
import asyncpg
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from order.order_data_access import Order as sql
from utilities.database_connection import get_pool
from utilities.query_excutor import AsyncExecutor
from utilities import services

from models.order import Order
from db.connection import get_db_connection
from services.shipping_service import assign_carrier, generate_shipping_label

router = APIRouter()

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int,  db_pool: asyncpg.pool.Pool=Depends(get_pool)):

    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)
        order = await executor.execute_query(sql.get_order_detail(), (order_id,))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

@router.post("/orders/{order_id}/fulfill")
async def fulfill_order(order_id: int, db_pool: asyncpg.pool.Pool=Depends(get_pool)):
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)

        await services.assign_carrier(executor,order_id)
        await services.generate_shipping_label(executor,order_id)
        await executor.execute_query(sql.update_order_status(), (order_id,))
        return {"message": "Order fulfilled"}
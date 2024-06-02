
import asyncpg
import requests
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from typing import List
from order.order_data_access import Order as sql
from utilities.database_connection import get_pool
from utilities.query_excutor import AsyncExecutor
from utilities import services

router = APIRouter()

def validate_user(request):

    token = None
    if "x-access-token" in request.headers:
        token = request.headers.get("x-access-token")

    if not token:
        return False

    payload = {"token":token}
    r = requests.post('http://localhost/auth/validateToken', payload)

    if r.status_code != 200:
        return False  
    result = r.json()
    return result.get('login')

@router.get("/orders/{order_id}")
async def get_order(request:Request,order_id: int,  db_pool: asyncpg.pool.Pool=Depends(get_pool)):
    valid_user = validate_user(request)
    if not valid_user:
        return JSONResponse(content={"msg": "Invalid User"}, status_code=401)
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)
        order = await executor.execute_query(sql.get_order_detail(), (order_id,))
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
    return JSONResponse(content={"order":order }, status_code=200) 

@router.post("/orders/{order_id}/fulfill")
async def fulfill_order(request:Request,order_id: int, db_pool: asyncpg.pool.Pool=Depends(get_pool)):
    valid_user = validate_user(request)
    if not valid_user:
        return JSONResponse(content={"msg": "Invalid User"}, status_code=401)
    
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)

        await services.assign_carrier(executor,order_id)
        await services.generate_shipping_label(executor,order_id)
        await executor.execute_query(sql.update_order_status(), (order_id,))
    return JSONResponse(content={"message": "Order fulfilled" }, status_code=200) 
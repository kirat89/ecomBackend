import asyncpg
import requests
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from typing import List
from cart.val import OrderCreate, OrderItem
from cart.cart_data_access import Cart as sql
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

@router.post("/cart/validate")
async def validate_cart(request:Request,items: List[OrderItem], db_pool: asyncpg.pool.Pool=Depends(get_pool)):
    valid_user = validate_user(request)
    if not valid_user:
        return JSONResponse(content={"msg": "Invalid User"}, status_code=401)
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)

        for item in items:
            product = services.get_inventory(product_id=item.product_id)
            if not product or product.data.get("stock_available") < item.quantity:
                raise HTTPException(status_code=400, detail=f"Product {item.product_id} is out of stock")
    return {"message": "Cart is valid"}

@router.post("/cart/checkout")
async def checkout(request:Request,order: OrderCreate, db_pool: asyncpg.pool.Pool=Depends(get_pool)):
    valid_user = validate_user(request)
    if not valid_user:
        return JSONResponse(content={"msg": "Invalid User"}, status_code=401)
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)
    # Validate stock again as a safety measure
        for item in order.items:
            product = services.get_inventory(product_id=item.product_id)
            if product.data.get("stock_available") < item.quantity:
                raise HTTPException(status_code=400, detail=f"Product {item.product_id} is out of stock")

        # Process payment (this would be a call to a payment service)
        payment_status = await services.process_payment(order.total_amount)
        if not payment_status:
            raise HTTPException(status_code=400, detail="Payment failed")

    # Insert order
        order_id = await executor.execute_query(sql.insert_order(), order.customer_id, order.total_amount, datetime.now(), "Processing")

        # Insert order items
        for item in order.items:
            await executor.execute_query(sql.insert_order_item(), order_id, item.product_id, item.quantity)

        # Update stock
        for item in order.items:
            services.update_inventory( item.quantity, item.product_id,request.headers.get("x-access-token"))

        # Send order confirmation email (this would be a call to an email service)
        await services.send_order_confirmation_email(order_id, order.customer_id)

        return {"order_id": order_id}

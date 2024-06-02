import asyncpg
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from utilities.database_connection import get_pool
from utilities.query_excutor import AsyncExecutor
from inventory_management.inventory_management_data_access import Inventory_management as sql
import inventory_management.validators as val
import requests

router = APIRouter(
    prefix='/inventory',
    tags=['inventory']
)

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
    


@router.get("/")
async def get_all_items_in_inventory(db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)
        inventory_items = await executor.execute_query(sql.get_all_product_detials())
    return JSONResponse(content={"data": inventory_items}, status_code=200)

@router.get("/{id}")
async def get_item_in_inventory_by_id(id: int, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)
        inventory_item = await executor.execute_query(sql.get_product_detials(), (id,))
    return JSONResponse(content={"data": inventory_item}, status_code=200)

@router.post("/")
async def create_item_in_inventory(inventory_data: val.CreateProduct, request:Request,db_pool: asyncpg.pool.Pool = Depends(get_pool)):

    
    valid_user = validate_user(request)
    if not valid_user:
        return JSONResponse(content={"msg": "Invalid User"}, status_code=401)
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)
        advisory_lock_key = hash(inventory_data.name)
          # Generate a unique lock key based on product name
        
        await executor.acquire_advisory_lock(advisory_lock_key)  # Acquire the advisory lock

        try:
            category_name = inventory_data.category

            # Check for category in database, if exists
            get_category_id = await executor.execute_query(sql.get_category_id(), (category_name,))
            if get_category_id:
                category_id = get_category_id[0]['id']
            else:
                get_category_id = await executor.execute_query(sql.insert_category(), (category_name,))
                category_id = get_category_id[0]['id']

            insert_data = (
                inventory_data.name,
                inventory_data.description,
                inventory_data.specifications,
                category_id,
                inventory_data.no_of_stock,
                inventory_data.price_per_stock,
            )

            product = await executor.execute_query(sql.insert_product(), insert_data)
            if not product:
                return JSONResponse(content={"msg": "unable to insert product"}, status_code=400)

            product_id = product[0]['id']
            if inventory_data.images:
                for image_url in inventory_data.images:
                    await executor.execute_query(sql.insert_product_image(), (product_id, image_url))
        finally:
            await executor.release_advisory_lock(advisory_lock_key)  # Release the advisory lock

    return JSONResponse(content={"msg": "Product inserted"}, status_code=201)

@router.put("/quant/{id}")
async def update_item_quantity_in_inventory(id: int, inventory_data: val.UpdateProductQuantity,request:Request, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    valid_user = validate_user(request)
    if not valid_user:
        return JSONResponse(content={"msg": "Invalid User"}, status_code=401)
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)
        executor.begin_trans()
        # Implementing pessimistic lock
        await executor.execute_query(sql.get_product_detials(), (id,),use_pessimistic_lock=True)
        product = await executor.execute_query(sql.update_product_quantity(), (inventory_data.quantity,id)
        )
        executor.commit()

    return JSONResponse(content={"msg": "Product Quantity updated"}, status_code=204)
@router.put("/{id}")
async def update_item_in_inventory(id: int, inventory_data: val.UpdateProduct,request:Request, db_pool: asyncpg.pool.Pool = Depends(get_pool)):
    
    valid_user = validate_user(request)
    if not valid_user:
        return JSONResponse(content={"msg": "Invalid User"}, status_code=401)
    async with db_pool.acquire() as conn:
        executor = AsyncExecutor(conn)
        executor.begin_trans()
        # Implementing pessimistic lock
        await executor.execute_query(sql.get_product_detials(), (id,),use_pessimistic_lock=True)

        category_name = inventory_data.category

        # Check for category in database, if exists
        if category_name:
            get_category_id = await executor.execute_query(sql.get_category_id(), (category_name,))
            if get_category_id:
                category_id = get_category_id[0]['id']
            else:
                get_category_id = await executor.execute_query(sql.insert_category(), (category_name,))
                category_id = get_category_id[0]['id']
        else:
            category_id = None

        update_data = (
            inventory_data.name,
            inventory_data.description,
            inventory_data.specifications,
            category_id,
            inventory_data.no_of_stock,
            inventory_data.price_per_stock,
            1 if inventory_data.soft_delete else 0,
            1 if inventory_data.archived else 0,
            id
        )

        product = await executor.execute_query(sql.update_product(), update_data)
        executor.commit()

    return JSONResponse(content={"msg": "Product updated"}, status_code=204)

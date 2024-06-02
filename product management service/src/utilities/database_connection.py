import asyncpg

POOL = None

async def create_db_pool():
    global POOL

    POOL = await asyncpg.create_pool(host = '127.0.0.1',
                                     port = '5432',
                                     user= 'postgres',
                                     password='password',
                                     database='product_db',)



async def get_pool():

    global POOL
    if POOL is None:
        print(POOL) 
        return Exception ("DB Connection Not Initiated")
    return POOL
    

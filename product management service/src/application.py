from fastapi import FastAPI
from inventory_management.inventory_management import router as product_router

app = FastAPI()


app.include_router(product_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
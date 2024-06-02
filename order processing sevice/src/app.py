from fastapi import FastAPI
from cart.cart import router as cart_router
from order.order import router as order_router

app = FastAPI()


app.include_router(cart_router)
app.include_router(order_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
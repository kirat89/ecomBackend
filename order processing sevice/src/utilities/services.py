##inventory
import requests
from utilities.service_data_access import Service as sql

async def update_inventory(product_id: int, quantity: int,token):
    
    payload = {"quantity":quantity}
    headers = {'x-access-token':token}
    r = requests.post(f'http://localhost/inventory/quant/{product_id}', payload,headers)

    if r.status_code != 200:
        return False  
    result = r.json()
    return result.get('login')

async def get_inventory(product_id: int,):
    
    
    r = requests.get(f'http://localhost/inventory/{product_id}', )

    if r.status_code != 200:
        return False  
    result = r.json()
    return result.get('login')


#shipping

async def assign_carrier(executor,order_id: int):

    carrier = "Carrier X"  # Logic to assign carrier
    await executor.execute_query(sql.update_order_carrier(), (carrier, order_id))

async def generate_shipping_label(executor,order_id: int):
    
    # Logic to generate shipping label
    label = "Shipping Label"
    await executor.execute_query(sql.update_shipping_label(), (label, order_id))


#payment
async def process_payment(amount: float) -> bool:
    # Logic to process payment
    return True

async def send_order_confirmation_email(order_id: int, customer_id: int):
    # Logic to send order confirmation email
    pass

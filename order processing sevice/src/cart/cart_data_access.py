

class Cart:

    
    @staticmethod
    def insert_order():
        sql = """
            INSERT INTO orders (customer_id, total_amount, order_date, status)
            VALUES ($1, $2, $3, $4) RETURNING id
        """
        return sql
    @staticmethod
    def insert_order_item():
        sql = """
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES ($1, $2, $3)
            """
        return sql
    
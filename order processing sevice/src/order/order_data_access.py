

class Order:

    @staticmethod
    def get_order_detail():
        sql = "SELECT * FROM orders WHERE id=$1"
        return sql
    @staticmethod
    def update_order_status():
        sql = """
            UPDATE orders SET status = 'Fulfilled' WHERE id = $1
        """
        return sql
class Service:

    @staticmethod
    def update_order_carrier():
        sql = """
        UPDATE orders SET carrier = $1 WHERE id = $2
    """
        return sql
    @staticmethod
    def update_shipping_label():
        sql = """
        UPDATE orders SET shipping_label = $1 WHERE id = $2
    """
        return sql
        

class Inventory_management:

    @staticmethod
    def get_all_product_detials():
        sql = """select p.id,p.name,p.description,c.category_name ,p.specifications,p.proce, p.stock_avaliable,  pp.image_url from product join category c
         on c.id = p.category_id
         join product_images pp
           on pp.product_id = p.id  """
        return sql
    
    @staticmethod
    def get_product_detials():
        sql = """select p.id,p.name,p.description,c.category_name ,p.specifications,p.proce, p.stock_avaliable, 
          pp.image_url from product p 
          join category c
         on c.id = p.category_id
         join product_images pp
           on pp.product_id = p.id 
        where   p.id = $1   """
        return sql
    
    @staticmethod
    def get_category_id():
        sql = """ select id from category where name = $1"""
        return sql
    
    @staticmethod
    def insert_category():
        sql = """ insert into category (name) values ($1) returing id as category_id """
        return sql
    
    @staticmethod
    def insert_product():
        sql = """ insert into product (name,description,specifications, category_id, stock_available,price) values($1,$2,$3,$4,$5,$6) returning product_id"""
        return sql
    
    @staticmethod
    def update_product():
        sql = """ update product 
        set name =$1 ,description =$2,specifications=$3, 
        category_id=$4, stock_available=$5 ,price =$6, soft_delete=$7,archived =$8 where id = &7"""
        return sql
    
    @staticmethod
    def update_product_quantity():
        sql = """ UPDATE products SET stock_available = stock_available - $1 WHERE id = $2"""
        return sql
    
    @staticmethod
    def insert_product_image():
        sql = """ insert into product_images (product_id,image_url) values($1,$2) """
        return sql
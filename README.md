# ecomBackend
Backend Repository for ecom website.

In this application we have three services:

1. Auth service
 --used for registration
    user can have roles(either Admin, user)
 --login
 --validateToken

 2. Product management

 this service is used for product management on the main site,i.e., viewing all the products available, checking single product


 3. order management

 this service has two modules
 1. cart
 --used for validating cart by calling product management service
 --checkout
    --update product count
    --process payment
    --send confirmation mail

 2. order
 --check all orders
 --update a order to be fulfilled.  

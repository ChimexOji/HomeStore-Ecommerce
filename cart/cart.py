from django.conf import settings
from product.models import Product

class Cart(object):
    # sets a session for cart object
    def __init__(self, request):

        # this becomes available for other methods in cart
        self.session = request.session

        # actual cart object using session_id created in setings.py for cart
        cart = self.session.get(settings.CART_SESSION_ID)

        # if cart is empty or not created new instance of cart variable becomes empty by default
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}

        self.cart = cart

    # loops through all cart items using keys as id for products. The loop also makes the products a string using the primary key.
    # Therefore, the products can be easily recovered from the database.
    def __iter__(self):
        for key in self.cart.keys():
            self.cart[str(key)]['product'] = Product.objects.get(pk=key)

        for item in self.cart.values():
            item['total_price'] = int(item['product'].price * item['quantity']) / 100

            yield item

    # checks the amount of items available in the cart then sums it up to get only 1 variable.
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    # notifies the server of any changes or modification made to the cart by saving session activity.
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
    
    # method to add things to cart by product_id and quantity. Method also updates cart automatically.
    def add(self, product_id, quantity=1, update_quantity=False):
        product_id = str(product_id)

        # checks to see if item has been added by product_id. 
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 1, 'id': product_id}
        
        # increases or decreases the quantity of items in cart. Also, makes quantity type integer
        if update_quantity:
            self.cart[product_id]['quantity'] += int(quantity)

            # if quantity is 0 removes it from cart.
            if self.cart[product_id]['quantity'] == 0:
                self.remove(product_id)
        
        self.save()
    
    # method to remove or delete item from cart using product_id an del function.
    def remove(self, product_id):
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    # method to clear cart session after making purchase
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
    
    def get_total_cost(self):
        for key in self.cart.keys():
            self.cart[str(key)]['product'] = Product.objects.get(pk=key)

        return int(sum(item['product'].price * item['quantity'] for item in self.cart.values())) / 100
    
    def get_item(self, product_id):
        if str(product_id) in self.cart:
            return self.cart[str(product_id)]
        else:
            return None
        
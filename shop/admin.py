from django.contrib import admin
from .models import (
    User, Category, Product, ProductColor, ProductColorImage,
    Cart, CartItem, Order, OrderItem
)

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductColor)
admin.site.register(ProductColorImage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
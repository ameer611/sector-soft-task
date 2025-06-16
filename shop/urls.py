from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CategoryViewSet, ProductViewSet, ProductColorViewSet,
    ProductColorImageViewSet, CartViewSet, CartItemViewSet, OrderViewSet, OrderItemViewSet
)
from django.urls import path, include

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-colors', ProductColorViewSet)
router.register(r'product-color-images', ProductColorImageViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
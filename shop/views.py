from rest_framework import viewsets, permissions
from .models import (
    User, Category, Product, ProductColor, ProductColorImage,
    Cart, CartItem, Order, OrderItem
)
from .serializers import (
    UserSerializer, CategorySerializer, ProductSerializer, ProductColorSerializer,
    ProductColorImageSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductColorViewSet(viewsets.ModelViewSet):
    queryset = ProductColor.objects.all()
    serializer_class = ProductColorSerializer

class ProductColorImageViewSet(viewsets.ModelViewSet):
    queryset = ProductColorImage.objects.all()
    serializer_class = ProductColorImageSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
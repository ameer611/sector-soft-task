from rest_framework import serializers
from .models import (
    User, Category, Product, ProductColor, ProductColorImage,
    Cart, CartItem, Order, OrderItem
)

class ProductColorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColorImage
        fields = ["id", "image"]

class ProductColorSerializer(serializers.ModelSerializer):
    images = ProductColorImageSerializer(many=True, read_only=True)
    image_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProductColorImage.objects.all(), many=True, write_only=True, source='images'
    )

    class Meta:
        model = ProductColor
        fields = ["id", "product", "name_uz", "name_ru", "price", "images", "image_ids"]

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name_uz", "name_ru", "parent", "children"]

    def get_children(self, obj):
        return CategorySerializer(obj.children.all(), many=True).data

class ProductSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    colors = ProductColorSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name_uz", "name_ru", "categories", "main_image", "description_uz", "description_ru", "colors"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "telegram_id", "name", "phone", "language", "is_active", "is_blocked", "created_at"]

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    color = ProductColorSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "cart", "product", "color", "quantity", "added_at"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "created_at", "items"]

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    color = ProductColorSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "order", "product", "color", "quantity", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "created_at", "status", "items"]
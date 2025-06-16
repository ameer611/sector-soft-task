from django.db import models
from django.contrib.auth.models import AbstractUser

# User model for Telegram users
class User(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    language = models.CharField(max_length=2, choices=(('uz', 'Uzbek'), ('ru', 'Russian')))
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.telegram_id})"

class Category(models.Model):
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return self.name_uz

class Product(models.Model):
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category, related_name='products')
    main_image = models.ImageField(upload_to='products/main/')
    description_uz = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)

    def __str__(self):
        return self.name_uz

class ProductColor(models.Model):
    product = models.ForeignKey(Product, related_name='colors', on_delete=models.CASCADE)
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    # Each color can have multiple images
    images = models.ManyToManyField('ProductColorImage', related_name='colors')

    def __str__(self):
        return f"{self.product.name_uz} - {self.name_uz}"

class ProductColorImage(models.Model):
    image = models.ImageField(upload_to='products/colors/')

class Cart(models.Model):
    user = models.OneToOneField(User, related_name='cart', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    STATUS_CHOICES = (
        ('created', 'Created'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
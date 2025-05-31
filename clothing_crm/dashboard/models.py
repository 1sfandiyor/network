from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Product(models.Model):
    """Product model for clothing items"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        """Return image URL or placeholder if no image exists"""
        try:
            url = self.image.url
        except:
            url = '/static/images/placeholder.png'
        return url


class Customer(models.Model):
    """Customer model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=200)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    """Order model"""
    STATUS_CHOICES = (
        ('new', 'New'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'Order {self.id}'

    @property
    def get_cart_total(self):
        """Calculate total price of all items in the order"""
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        """Calculate total number of items in the order"""
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    """Order item model (products in an order)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    @property
    def get_total(self):
        """Calculate total price for this item"""
        total = self.product.price * self.quantity
        return total
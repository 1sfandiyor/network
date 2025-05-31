from django.contrib import admin
from .models import Category, Product, Customer, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'date_ordered', 'status']
    list_filter = ['status', 'date_ordered']
    search_fields = ['customer__name', 'id']
    inlines = [OrderItemInline]

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    search_fields = ['name', 'email', 'phone']

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
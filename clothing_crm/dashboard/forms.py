from django import forms
from django.forms import inlineformset_factory
from .models import Product, Customer, Order, OrderItem, Category


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories"""
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    """Form for creating and updating products"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
        }


class CustomerForm(forms.ModelForm):
    """Form for creating and updating customers"""
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    """Form for creating and updating orders"""
    class Meta:
        model = Order
        fields = ['customer', 'status']


class OrderItemForm(forms.ModelForm):
    """Form for creating and updating order items"""
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': '1'}),
        }


# Create a formset for OrderItems
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True
)
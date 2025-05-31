from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, F, Q, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import timedelta
import time

from .models import Product, Category, Customer, Order, OrderItem
from .forms import ProductForm, CategoryForm, CustomerForm, OrderForm, OrderItemFormSet


# Dashboard view
@login_required
def dashboard(request):
    """
    Dashboard view showing sales statistics, product count, customer count,
    daily revenue, and best-selling products
    """
    # Get counts
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()

    # Get orders from the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_orders = Order.objects.filter(date_ordered__gte=thirty_days_ago)

    # Calculate daily revenue for the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)

    # Create a list of all days in the last 7 days
    days = []
    for i in range(7):
        day = timezone.now().date() - timedelta(days=i)
        days.append(day)
    days.reverse()  # Oldest to newest

    # Get revenue data for each day
    daily_revenue_data = Order.objects.filter(
        date_ordered__gte=seven_days_ago,
        status__in=['paid', 'delivered']  # Only count paid or delivered orders
    ).annotate(
        day=TruncDate('date_ordered')
    ).values('day').annotate(
        revenue=Sum(
            ExpressionWrapper(
                F('orderitem__product__price') * F('orderitem__quantity'),
                output_field=DecimalField()
            )
        )
    ).order_by('day')

    # Convert to dictionary for easier lookup
    daily_revenue_dict = {item['day']: item['revenue'] for item in daily_revenue_data}

    # Create the final daily revenue list with all days
    daily_revenue = []
    for day in days:
        daily_revenue.append({
            'day': day,
            'revenue': daily_revenue_dict.get(day, 0)
        })

    # Get best-selling products
    best_selling = OrderItem.objects.values(
        'product__name', 'product__id'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    # Get recent orders
    recent_orders = Order.objects.order_by('-date_ordered')[:5]

    # Calculate total revenue
    total_revenue = OrderItem.objects.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('product__price') * F('quantity'),
                output_field=DecimalField()
            )
        )
    )['total'] or 0

    # Get order status counts
    status_counts = Order.objects.values('status').annotate(count=Count('id'))

    # Get low stock products (less than 10 items)
    low_stock_products = Product.objects.filter(stock__lt=10).order_by('stock')

    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'best_selling': best_selling,
        'recent_orders': recent_orders,
        'daily_revenue': daily_revenue,
        'status_counts': status_counts,
        'low_stock_products': low_stock_products,
    }

    return render(request, 'dashboard/dashboard.html', context)


# List views
@login_required
def product_list(request):
    """View for listing all products with search and filter functionality"""
    # Get all products
    products_list = Product.objects.all()

    # Get all categories for filter dropdown
    all_categories = Category.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        products_list = products_list.filter(category__id=category_id)

    # Sorting
    sort_by = request.GET.get('sort', 'name')
    products_list = products_list.order_by(sort_by)

    # Pagination
    paginator = Paginator(products_list, 10)  # Show 10 products per page
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'all_categories': all_categories,
        'search_query': search_query,
        'category_id': category_id,
        'sort_by': sort_by,
    }

    return render(request, 'dashboard/product_list.html', context)


@login_required
def category_list(request):
    """View for listing all categories"""
    # Get all categories
    categories_list = Category.objects.all().order_by('name')

    # Pagination
    paginator = Paginator(categories_list, 10)  # Show 10 categories per page
    page = request.GET.get('page')

    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        categories = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        categories = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
    }

    return render(request, 'dashboard/category_list.html', context)


@login_required
def customer_list(request):
    """View for listing all customers with search and filter functionality"""
    # Get all customers
    customers_list = Customer.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        customers_list = customers_list.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # Sorting
    sort_by = request.GET.get('sort', 'name')
    customers_list = customers_list.order_by(sort_by)

    # Pagination
    paginator = Paginator(customers_list, 10)  # Show 10 customers per page
    page = request.GET.get('page')

    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        customers = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        customers = paginator.page(paginator.num_pages)

    context = {
        'customers': customers,
        'search_query': search_query,
        'sort_by': sort_by,
    }

    return render(request, 'dashboard/customer_list.html', context)


@login_required
def order_list(request):
    """View for listing all orders with search and filter functionality"""
    # Get all orders
    orders_list = Order.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders_list = orders_list.filter(
            Q(customer__name__icontains=search_query) |
            Q(transaction_id__icontains=search_query)
        )

    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders_list = orders_list.filter(status=status_filter)

    # Sorting
    sort_by = request.GET.get('sort', '-date_ordered')
    orders_list = orders_list.order_by(sort_by)

    # Pagination
    paginator = Paginator(orders_list, 10)  # Show 10 orders per page
    page = request.GET.get('page')

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        orders = paginator.page(paginator.num_pages)

    context = {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }

    return render(request, 'dashboard/order_list.html', context)


# Product CRUD views
@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm()

    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Create Product'})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'dashboard/product_detail.html', {'product': product})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('dashboard:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'dashboard/product_form.html', {'form': form, 'product': product, 'title': 'Update Product'})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('dashboard:product_list')

    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


# Category CRUD views
@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()

    return render(request, 'dashboard/category_form.html', {'form': form, 'title': 'Create Category'})


@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    products = Product.objects.filter(category=category)
    return render(request, 'dashboard/category_detail.html', {'category': category, 'products': products})


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('dashboard:category_detail', pk=category.pk)
    else:
        form = CategoryForm(instance=category)

    return render(request, 'dashboard/category_form.html',
                  {'form': form, 'category': category, 'title': 'Update Category'})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('dashboard:category_list')

    return render(request, 'dashboard/category_confirm_delete.html', {'category': category})


# Customer CRUD views
@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('dashboard:customer_list')
    else:
        form = CustomerForm()

    return render(request, 'dashboard/customer_form.html', {'form': form, 'title': 'Create Customer'})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = Order.objects.filter(customer=customer).order_by('-date_ordered')
    return render(request, 'dashboard/customer_detail.html', {'customer': customer, 'orders': orders})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('dashboard:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'dashboard/customer_form.html',
                  {'form': form, 'customer': customer, 'title': 'Update Customer'})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('dashboard:customer_list')

    return render(request, 'dashboard/customer_confirm_delete.html', {'customer': customer})


# Order CRUD views
@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST, prefix='items')

        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.transaction_id = f'TRX{int(time.time())}'
            order.save()

            for form in formset:
                if form.cleaned_data.get('product'):
                    order_item = form.save(commit=False)
                    order_item.order = order
                    order_item.save()

            messages.success(request, 'Order created successfully!')
            return redirect('dashboard:order_detail', pk=order.pk)
    else:
        form = OrderForm()
        formset = OrderItemFormSet(prefix='items')

    return render(request, 'dashboard/order_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Order'
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_items = order.orderitem_set.all()

    # Calculate order total
    total = sum(item.product.price * item.quantity for item in order_items)

    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'order_items': order_items,
        'total': total
    })


@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, prefix='items', instance=order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Order updated successfully!')
            return redirect('dashboard:order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(prefix='items', instance=order)

    return render(request, 'dashboard/order_form.html', {
        'form': form,
        'formset': formset,
        'order': order,
        'title': 'Update Order'
    })


@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('dashboard:order_list')

    return render(request, 'dashboard/order_confirm_delete.html', {'order': order})
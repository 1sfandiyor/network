from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from dashboard.models import Category, Product, Customer, Order, OrderItem
from decimal import Decimal
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Loads demo data for the Clothing CRM'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Loading demo data...'))

        # Create categories
        categories = [
            {'name': 'Ko\'ylaklar', 'description': 'Erkaklar va ayollar uchun ko\'ylaklar'},
            {'name': 'Shimlar', 'description': 'Erkaklar va ayollar uchun shimlar'},
            {'name': 'Oyoq kiyimlar', 'description': 'Barcha turdagi oyoq kiyimlar'},
            {'name': 'Aksessuarlar', 'description': 'Soatlar, sumkalar va boshqa aksessuarlar'},
            {'name': 'Sport kiyimlari', 'description': 'Sport va dam olish uchun kiyimlar'},
        ]

        for cat_data in categories:
            Category.objects.get_or_create(name=cat_data['name'], defaults={'description': cat_data['description']})

        self.stdout.write(self.style.SUCCESS('Categories created!'))

        # Create products
        products_data = [
            {'name': 'Klassik ko\'ylak', 'category': 'Ko\'ylaklar', 'price': Decimal('25.99'), 'stock': 50},
            {'name': 'Jinsi shim', 'category': 'Shimlar', 'price': Decimal('35.50'), 'stock': 30},
            {'name': 'Sport krossovka', 'category': 'Oyoq kiyimlar', 'price': Decimal('45.99'), 'stock': 25},
            {'name': 'Qo\'l soati', 'category': 'Aksessuarlar', 'price': Decimal('120.00'), 'stock': 15},
            {'name': 'Sport futbolka', 'category': 'Sport kiyimlari', 'price': Decimal('19.99'), 'stock': 40},
            {'name': 'Ayollar ko\'ylagi', 'category': 'Ko\'ylaklar', 'price': Decimal('29.99'), 'stock': 35},
            {'name': 'Erkaklar shimmi', 'category': 'Shimlar', 'price': Decimal('39.99'), 'stock': 28},
            {'name': 'Ayollar etigi', 'category': 'Oyoq kiyimlar', 'price': Decimal('59.99'), 'stock': 20},
            {'name': 'Qo\'l sumkasi', 'category': 'Aksessuarlar', 'price': Decimal('49.99'), 'stock': 18},
            {'name': 'Yoga kiyimi', 'category': 'Sport kiyimlari', 'price': Decimal('34.99'), 'stock': 22},
        ]

        for prod_data in products_data:
            category = Category.objects.get(name=prod_data['category'])
            Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'description': f"Bu {prod_data['name'].lower()} sifatli materialdan tayyorlangan.",
                    'price': prod_data['price'],
                    'stock': prod_data['stock'],
                    'category': category
                }
            )

        self.stdout.write(self.style.SUCCESS('Products created!'))

        # Create customers
        customers_data = [
            {'name': 'Alisher Karimov', 'phone': '+998901234567', 'email': 'alisher@example.com',
             'address': 'Toshkent sh., Chilonzor tumani, 7-mavze'},
            {'name': 'Malika Rahimova', 'phone': '+998907654321', 'email': 'malika@example.com',
             'address': 'Toshkent sh., Yunusobod tumani, 19-mavze'},
            {'name': 'Bobur Aliyev', 'phone': '+998901122334', 'email': 'bobur@example.com',
             'address': 'Toshkent sh., Mirzo Ulug\'bek tumani, 5-mavze'},
            {'name': 'Nilufar Azizova', 'phone': '+998909988776', 'email': 'nilufar@example.com',
             'address': 'Toshkent sh., Shayxontohur tumani, 10-mavze'},
            {'name': 'Jahongir Qodirov', 'phone': '+998901234567', 'email': 'jahongir@example.com',
             'address': 'Toshkent sh., Olmazor tumani, 3-mavze'},
        ]

        for cust_data in customers_data:
            Customer.objects.get_or_create(
                name=cust_data['name'],
                defaults={
                    'phone': cust_data['phone'],
                    'email': cust_data['email'],
                    'address': cust_data['address']
                }
            )

        self.stdout.write(self.style.SUCCESS('Customers created!'))

        # Create orders
        customers = Customer.objects.all()
        products = Product.objects.all()
        statuses = ['new', 'pending', 'paid', 'delivered', 'cancelled']

        # Delete existing orders to avoid duplication
        Order.objects.all().delete()

        # Create orders for the last 30 days
        for i in range(20):
            days_ago = random.randint(0, 30)
            order_date = timezone.now() - timedelta(days=days_ago)

            order = Order.objects.create(
                customer=random.choice(customers),
                date_ordered=order_date,
                status=random.choice(statuses),
                transaction_id=f'TRX{10000 + i}'
            )

            # Add 1-3 items to each order
            for _ in range(random.randint(1, 3)):
                product = random.choice(products)
                quantity = random.randint(1, 5)

                OrderItem.objects.create(
                    product=product,
                    order=order,
                    quantity=quantity,
                    date_added=order_date
                )

        self.stdout.write(self.style.SUCCESS('Orders created!'))

        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Admin user created! Username: admin, Password: admin'))

        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully!'))
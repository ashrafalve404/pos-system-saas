from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random

from accounts.models import User
from organizations.models import Organization
from stores.models import Store
from products.models import Product, Category
from customers.models import Customer
from sales.models import Sale, SaleItem
from payments.models import Payment


class Command(BaseCommand):
    help = 'Seed demo data for POS system'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...')

        # Create or get demo user first (owner)
        user, created = User.objects.get_or_create(
            email='demo@saaspos.com',
            defaults={
                'first_name': 'Demo',
                'last_name': 'User',
                'role': 'owner',
                'is_active': True
            }
        )
        if created:
            user.set_password('demo123456')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.email}'))
        else:
            self.stdout.write(f'Using existing user: {user.email}')

        # Create or get demo organization
        org, created = Organization.objects.get_or_create(
            name='Demo Coffee Shop',
            defaults={
                'owner': user,
                'slug': 'demo-coffee-shop',
                'subscription_plan': 'professional'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created organization: {org.name}'))
        else:
            self.stdout.write(f'Using existing organization: {org.name}')

        # Update user organization
        user.organization = org
        user.save()

        # Create or get demo store
        store, created = Store.objects.get_or_create(
            organization=org,
            name='Main Store',
            defaults={
                'address': '123 Main Street, City, Country',
                'phone': '+1 234 567 8900',
                'email': 'store@demo.com',
                'manager': user,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created store: {store.name}'))
        else:
            self.stdout.write(f'Using existing store: {store.name}')

        # Create categories
        categories_data = [
            {'name': 'Coffee', 'description': 'Hot and cold coffee drinks'},
            {'name': 'Tea', 'description': 'Various tea selections'},
            {'name': 'Bakery', 'description': 'Fresh baked goods'},
            {'name': 'Smoothies', 'description': 'Fruit smoothies and shakes'},
            {'name': 'Snacks', 'description': 'Light snacks and sides'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                organization=org,
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories[cat.name] = cat
            if created:
                self.stdout.write(f'Created category: {cat.name}')

        # Create products organized by category
        products_data = [
            # Coffee
            {'name': 'Espresso', 'category': 'Coffee', 'price': 3.50, 'stock': 100, 'sku': 'COF001', 'barcode': '123456789001'},
            {'name': 'Americano', 'category': 'Coffee', 'price': 4.00, 'stock': 100, 'sku': 'COF002', 'barcode': '123456789002'},
            {'name': 'Cappuccino', 'category': 'Coffee', 'price': 4.50, 'stock': 80, 'sku': 'COF003', 'barcode': '123456789003'},
            {'name': 'Latte', 'category': 'Coffee', 'price': 4.50, 'stock': 80, 'sku': 'COF004', 'barcode': '123456789004'},
            {'name': 'Mocha', 'category': 'Coffee', 'price': 5.00, 'stock': 60, 'sku': 'COF005', 'barcode': '123456789005'},
            {'name': 'Cold Brew', 'category': 'Coffee', 'price': 4.00, 'stock': 50, 'sku': 'COF006', 'barcode': '123456789006'},
            
            # Tea
            {'name': 'Green Tea', 'category': 'Tea', 'price': 3.00, 'stock': 100, 'sku': 'TEA001', 'barcode': '223456789001'},
            {'name': 'Black Tea', 'category': 'Tea', 'price': 3.00, 'stock': 100, 'sku': 'TEA002', 'barcode': '223456789002'},
            {'name': 'Chai Latte', 'category': 'Tea', 'price': 4.50, 'stock': 60, 'sku': 'TEA003', 'barcode': '223456789003'},
            {'name': 'Herbal Tea', 'category': 'Tea', 'price': 3.50, 'stock': 40, 'sku': 'TEA004', 'barcode': '223456789004'},
            
            # Bakery
            {'name': 'Croissant', 'category': 'Bakery', 'price': 3.50, 'stock': 25, 'sku': 'BAK001', 'barcode': '323456789001'},
            {'name': 'Blueberry Muffin', 'category': 'Bakery', 'price': 4.00, 'stock': 20, 'sku': 'BAK002', 'barcode': '323456789002'},
            {'name': 'Chocolate Chip Cookie', 'category': 'Bakery', 'price': 2.50, 'stock': 30, 'sku': 'BAK003', 'barcode': '323456789003'},
            {'name': 'Cinnamon Roll', 'category': 'Bakery', 'price': 4.50, 'stock': 15, 'sku': 'BAK004', 'barcode': '323456789004'},
            {'name': 'Banana Bread', 'category': 'Bakery', 'price': 5.00, 'stock': 10, 'sku': 'BAK005', 'barcode': '323456789005'},
            
            # Smoothies
            {'name': 'Strawberry Smoothie', 'category': 'Smoothies', 'price': 6.00, 'stock': 30, 'sku': 'SM001', 'barcode': '423456789001'},
            {'name': 'Mango Smoothie', 'category': 'Smoothies', 'price': 6.50, 'stock': 30, 'sku': 'SM002', 'barcode': '423456789002'},
            {'name': 'Berry Blast', 'category': 'Smoothies', 'price': 7.00, 'stock': 25, 'sku': 'SM003', 'barcode': '423456789003'},
            
            # Snacks
            {'name': 'Avocado Toast', 'category': 'Snacks', 'price': 8.00, 'stock': 15, 'sku': 'SNK001', 'barcode': '523456789001'},
            {'name': 'Granola Bowl', 'category': 'Snacks', 'price': 7.50, 'stock': 20, 'sku': 'SNK002', 'barcode': '523456789002'},
            {'name': 'Bagel with Cream Cheese', 'category': 'Snacks', 'price': 5.00, 'stock': 25, 'sku': 'SNK003', 'barcode': '523456789003'},
        ]

        products = []
        for prod_data in products_data:
            cat = categories[prod_data['category']]
            product, created = Product.objects.get_or_create(
                organization=org,
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'category': cat,
                    'store': store,
                    'price': Decimal(str(prod_data['price'])),
                    'stock_quantity': prod_data['stock'],
                    'low_stock_threshold': 10,
                    'barcode': prod_data['barcode'],
                    'is_active': True
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'Created product: {product.name}')

        # Create sample customers
        customers_data = [
            {'name': 'John Smith', 'email': 'john@example.com', 'phone': '+1 111 111 1111', 'points': 150},
            {'name': 'Sarah Johnson', 'email': 'sarah@example.com', 'phone': '+1 222 222 2222', 'points': 280},
            {'name': 'Mike Brown', 'email': 'mike@example.com', 'phone': '+1 333 333 3333', 'points': 75},
            {'name': 'Emily Davis', 'email': 'emily@example.com', 'phone': '+1 444 444 4444', 'points': 420},
            {'name': 'Chris Wilson', 'email': 'chris@example.com', 'phone': '+1 555 555 5555', 'points': 200},
        ]

        for cust_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                organization=org,
                email=cust_data['email'],
                defaults={
                    'name': cust_data['name'],
                    'phone': cust_data['phone'],
                    'loyalty_points': cust_data['points'],
                    'total_purchases': Decimal(str(cust_data['points'] * 2)),
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created customer: {customer.name}')

        # Create sample sales for the past 7 days
        today = timezone.now().date()
        
        for days_ago in range(7):
            sale_date = today - timezone.timedelta(days=days_ago)
            num_sales = random.randint(15, 35)
            
            for _ in range(num_sales):
                # Random customer (sometimes None for walk-in)
                customer = random.choice([None] + list(Customer.objects.filter(organization=org)[:5]))
                
                # Create sale
                sale = Sale.objects.create(
                    organization=org,
                    store=store,
                    cashier=user,
                    customer=customer,
                    discount_amount=Decimal('0.00'),
                    tax_amount=Decimal('0.00'),
                    payment_status='paid',
                )
                
                # Add random items (1-5 items per sale)
                num_items = random.randint(1, 5)
                sale_products = random.sample(products, num_items)
                subtotal = Decimal('0.00')
                
                for prod in sale_products:
                    qty = random.randint(1, 3)
                    item_subtotal = prod.price * qty
                    subtotal += item_subtotal
                    
                    SaleItem.objects.create(
                        sale=sale,
                        product=prod,
                        quantity=qty,
                        price=prod.price,
                        subtotal=item_subtotal
                    )
                    
                    # Update stock
                    prod.stock_quantity -= qty
                    prod.save()
                
                sale.subtotal = subtotal
                sale.total = subtotal
                sale.save()
                
                # Create payment
                Payment.objects.create(
                    sale=sale,
                    organization=org,
                    payment_method=random.choice(['cash', 'card']),
                    amount=sale.total,
                    status='completed',
                    paid_by=user
                )
                
                # Update customer points
                if customer:
                    customer.loyalty_points += int(sale.total)
                    customer.total_purchases += sale.total
                    customer.save()

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('  Email: demo@saaspos.com')
        self.stdout.write('  Password: demo123456')

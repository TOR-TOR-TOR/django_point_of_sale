"""
Management Command: seed_data
===============================
Populates the database with realistic synthetic (fake) data for SQL practice.

Usage:
    python manage.py seed_data              # seed with defaults
    python manage.py seed_data --flush      # wipe all data first, then seed

What gets created:
    - 10  Categories
    - 100 Products       (linked to categories via FK)
    - 150 Customers
    - 200 Sales          (linked to customers via FK)
    - ~500 SaleDetails   (linked to sales + products via FK)

Total record count: ~960 rows across all tables.

Author: <your name>
"""

import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

# ORM model imports — each import maps to a DB table
from products.models import Category, Product
from customers.models import Customer
from sales.models import Sale, SaleDetail

# Faker instance — generates realistic synthetic data
# 'en_US' is the locale, controls language/format of generated values
fake = Faker('en_US')


# ============================================================
# CONSTANTS — control the volume of seeded records
# ============================================================
NUM_CATEGORIES   = 10
NUM_PRODUCTS     = 100
NUM_CUSTOMERS    = 150
NUM_SALES        = 200
MAX_ITEMS_PER_SALE = 5   # max SaleDetail rows per Sale (randomised per sale)

# Realistic grocery product names grouped by category
# Used to generate believable product names instead of random strings
CATEGORY_PRODUCTS = {
    "Dairy":        ["Whole Milk", "Skimmed Milk", "Cheddar Cheese", "Mozzarella", "Butter", "Yoghurt", "Cream Cheese", "Sour Cream", "Heavy Cream", "Cottage Cheese"],
    "Bakery":       ["White Bread", "Brown Bread", "Sourdough Loaf", "Croissant", "Bagel", "Muffin", "Baguette", "Ciabatta", "Rye Bread", "Dinner Rolls"],
    "Beverages":    ["Orange Juice", "Apple Juice", "Sparkling Water", "Green Tea", "Black Coffee", "Energy Drink", "Lemonade", "Coconut Water", "Iced Tea", "Ginger Ale"],
    "Snacks":       ["Potato Chips", "Popcorn", "Pretzels", "Granola Bar", "Chocolate Bar", "Rice Cakes", "Trail Mix", "Crackers", "Cheese Puffs", "Dried Mango"],
    "Produce":      ["Bananas", "Apples", "Tomatoes", "Spinach", "Carrots", "Broccoli", "Avocado", "Strawberries", "Grapes", "Sweet Potatoes"],
    "Meat":         ["Chicken Breast", "Ground Beef", "Pork Chops", "Beef Steak", "Turkey Mince", "Lamb Chops", "Bacon Strips", "Beef Sausage", "Chicken Wings", "Salmon Fillet"],
    "Grains":       ["Basmati Rice", "Brown Rice", "Pasta", "Oatmeal", "Quinoa", "Cornmeal", "Barley", "Couscous", "Lentils", "Chickpeas"],
    "Frozen":       ["Frozen Pizza", "Ice Cream", "Frozen Fries", "Frozen Peas", "Fish Fingers", "Frozen Burger", "Frozen Waffles", "Frozen Burritos", "Sorbet", "Frozen Vegetables"],
    "Condiments":   ["Tomato Ketchup", "Mustard", "Mayonnaise", "Soy Sauce", "Hot Sauce", "Olive Oil", "Apple Cider Vinegar", "BBQ Sauce", "Salsa", "Ranch Dressing"],
    "Personal Care":["Shampoo", "Conditioner", "Body Wash", "Toothpaste", "Deodorant", "Face Wash", "Hand Lotion", "Lip Balm", "Sunscreen", "Razors"],
}

# Price ranges per category (min, max) in KES
# Reflects realistic grocery pricing
PRICE_RANGES = {
    "Dairy":         (50,  400),
    "Bakery":        (40,  300),
    "Beverages":     (30,  250),
    "Snacks":        (20,  200),
    "Produce":       (10,  150),
    "Meat":          (200, 1500),
    "Grains":        (50,  500),
    "Frozen":        (150, 800),
    "Condiments":    (80,  400),
    "Personal Care": (100, 600),
}

# Standard VAT/tax rate
TAX_PERCENTAGE = 16.0   # 16% VAT (Kenya standard rate)


class Command(BaseCommand):
    """
    BaseCommand — Django's base class for all management commands.
    Subclassing it registers this file as a valid manage.py command.
    The class name must always be 'Command'.
    """
    help = "Seeds the database with ~500 realistic records for SQL practice"

    def add_arguments(self, parser):
        """
        add_arguments — defines CLI flags for the command.
        --flush is an optional flag; store_true means it defaults to False
        and becomes True only when the flag is passed.
        """
        parser.add_argument(
            '--flush',
            action='store_true',
            help='Delete all existing data before seeding (clean slate)',
        )

    def handle(self, *args, **options):
        """
        handle() — the entry point Django calls when the command runs.
        All seeding logic is orchestrated from here.
        """
        if options['flush']:
            self.flush_data()

        # transaction.atomic() — wraps all DB writes in a single
        # database transaction. If anything fails midway, the entire
        # operation is rolled back, leaving the DB in a clean state.
        with transaction.atomic():
            categories = self.seed_categories()
            products   = self.seed_products(categories)
            customers  = self.seed_customers()
            self.seed_sales(customers, products)

        # stdout.write is the correct way to print in management commands
        # self.style.SUCCESS applies green terminal colouring
        self.stdout.write(self.style.SUCCESS(
            "\n✅ Seeding complete!"
            f"\n   Categories : {NUM_CATEGORIES}"
            f"\n   Products   : {NUM_PRODUCTS}"
            f"\n   Customers  : {NUM_CUSTOMERS}"
            f"\n   Sales      : {NUM_SALES}"
            f"\n   Sale Items : ~{NUM_SALES * 3} (avg 3 items/sale)"
            "\n\nYou are ready to start SQL practice. Happy querying! 🎯"
        ))

    # ============================================================
    # FLUSH — truncates all app tables before re-seeding
    # Truncating = deleting all rows but keeping the table structure
    # ============================================================
    def flush_data(self):
        self.stdout.write("🗑️  Flushing existing data...")
        # Delete in reverse FK dependency order to avoid constraint violations
        # FK constraint — a rule that a child row cannot exist without its parent
        SaleDetail.objects.all().delete()
        Sale.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write(self.style.WARNING("   All records deleted.\n"))

    # ============================================================
    # SEED CATEGORIES
    # ============================================================
    def seed_categories(self):
        self.stdout.write("📦 Seeding categories...")
        categories = []

        for name in list(CATEGORY_PRODUCTS.keys())[:NUM_CATEGORIES]:
            # get_or_create — a Django ORM method that either fetches an
            # existing record matching the lookup, or creates a new one.
            # Returns a tuple: (instance, created_boolean)
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    "description": fake.sentence(nb_words=8),
                    "status": random.choices(
                        ["ACTIVE", "INACTIVE"],
                        weights=[90, 10]   # 90% active, 10% inactive
                    )[0],
                }
            )
            categories.append(category)

        self.stdout.write(f"   ✔ {len(categories)} categories seeded.")
        return categories

    # ============================================================
    # SEED PRODUCTS
    # ============================================================
    def seed_products(self, categories):
        self.stdout.write("🛒 Seeding products...")
        products = []
        products_per_category = NUM_PRODUCTS // len(categories)

        for category in categories:
            price_min, price_max = PRICE_RANGES.get(category.name, (50, 500))
            product_names = CATEGORY_PRODUCTS.get(category.name, [])

            for i in range(products_per_category):
                # Cycle through the predefined names, then fall back to fake words
                name = product_names[i] if i < len(product_names) else fake.word().capitalize()

                product, created = Product.objects.get_or_create(
                    name=name,
                    category=category,
                    defaults={
                        "description": fake.sentence(nb_words=10),
                        "status": random.choices(
                            ["ACTIVE", "INACTIVE"],
                            weights=[85, 15]
                        )[0],
                        # round() ensures clean float values — avoids floating
                        # point precision issues common in price calculations
                        "price": round(random.uniform(price_min, price_max), 2),
                    }
                )
                products.append(product)

        self.stdout.write(f"   ✔ {len(products)} products seeded.")
        return products

    # ============================================================
    # SEED CUSTOMERS
    # ============================================================
    def seed_customers(self):
        self.stdout.write("👤 Seeding customers...")
        customers = []

        for _ in range(NUM_CUSTOMERS):
            # bulk insert pattern — build objects in memory, save once
            customer = Customer.objects.create(
                first_name = fake.first_name(),
                last_name  = fake.last_name(),
                address    = fake.address().replace('\n', ', '),
                email      = fake.unique.email(),
                phone      = fake.numerify(text="07########"),  # Kenyan mobile format
            )
            customers.append(customer)

        self.stdout.write(f"   ✔ {len(customers)} customers seeded.")
        return customers

    # ============================================================
    # SEED SALES + SALE DETAILS
    # A Sale is the parent record (the receipt header).
    # SaleDetail rows are the line items on that receipt.
    # This is a classic one-to-many (1:N) relationship.
    # ============================================================
    def seed_sales(self, customers, products):
        self.stdout.write("🧾 Seeding sales & sale details...")
        total_details = 0

        for _ in range(NUM_SALES):
            customer      = random.choice(customers)
            num_items     = random.randint(1, MAX_ITEMS_PER_SALE)
            # sample() picks unique products — avoids duplicate line items per sale
            sale_products = random.sample(products, min(num_items, len(products)))

            # --- Build SaleDetail data first to compute totals ---
            detail_data = []
            sub_total   = 0.0

            for product in sale_products:
                quantity     = random.randint(1, 10)
                total_detail = round(product.price * quantity, 2)
                sub_total   += total_detail
                detail_data.append({
                    "product"      : product,
                    "price"        : product.price,
                    "quantity"     : quantity,
                    "total_detail" : total_detail,
                })

            # --- Compute sale-level financial fields ---
            sub_total      = round(sub_total, 2)
            tax_amount     = round(sub_total * (TAX_PERCENTAGE / 100), 2)
            grand_total    = round(sub_total + tax_amount, 2)
            # amount_payed is always >= grand_total (customer pays with cash)
            amount_payed   = round(grand_total + random.choice([0, 50, 100, 200, 500]), 2)
            amount_change  = round(amount_payed - grand_total, 2)

            # --- Create the Sale header record ---
            sale = Sale.objects.create(
                customer       = customer,
                # date_added spread over the last 365 days for realistic temporal data
                date_added     = fake.date_time_between(start_date="-365d", end_date="now"),
                sub_total      = sub_total,
                grand_total    = grand_total,
                tax_amount     = tax_amount,
                tax_percentage = TAX_PERCENTAGE,
                amount_payed   = amount_payed,
                amount_change  = amount_change,
            )

            # --- Create SaleDetail line items for this sale ---
            # bulk_create() inserts all rows in a single SQL INSERT statement
            # instead of one INSERT per row — much more efficient at scale
            SaleDetail.objects.bulk_create([
                SaleDetail(
                    sale         = sale,
                    product      = d["product"],
                    price        = d["price"],
                    quantity     = d["quantity"],
                    total_detail = d["total_detail"],
                )
                for d in detail_data
            ])
            total_details += len(detail_data)

        self.stdout.write(f"   ✔ {NUM_SALES} sales seeded with {total_details} sale detail records.")
import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AutoPart",
            fields=[
                ("part_id", models.AutoField(primary_key=True, serialize=False)),
                ("sku", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("category", models.CharField(max_length=100)),
                (
                    "condition",
                    models.CharField(
                        choices=[
                            ("NEW", "New"),
                            ("REBUILT", "Rebuilt"),
                            ("USED", "Used"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "unit_price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                    ),
                ),
                (
                    "reorder_level",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(0)]
                    ),
                ),
            ],
            options={
                "db_table": "part",
                "indexes": [
                    models.Index(fields=["category"], name="part_categor_d46169_idx"),
                    models.Index(fields=["sku"], name="part_sku_2a579f_idx"),
                    models.Index(fields=["name"], name="part_name_880c73_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Customer",
            fields=[
                ("customer_id", models.AutoField(primary_key=True, serialize=False)),
                ("full_name", models.CharField(max_length=100)),
                ("customer_email", models.EmailField(max_length=254, unique=True)),
                ("customer_phone", models.CharField(max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("username", models.CharField(max_length=50, unique=True)),
                ("password", models.CharField(max_length=255)),
            ],
            options={
                "db_table": "customer",
                "indexes": [
                    models.Index(
                        fields=["username"], name="customer_usernam_db822e_idx"
                    ),
                    models.Index(
                        fields=["customer_email"], name="customer_custome_0813d5_idx"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="Store",
            fields=[
                ("store_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("phone", models.CharField(max_length=20)),
                ("address_line1", models.CharField(max_length=255)),
                (
                    "address_line2",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=50)),
                ("postal_code", models.CharField(max_length=20)),
            ],
            options={
                "db_table": "store",
                "indexes": [
                    models.Index(fields=["city", "state"], name="store_city_5edf17_idx")
                ],
            },
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("employee_id", models.AutoField(primary_key=True, serialize=False)),
                ("full_name", models.CharField(max_length=100)),
                ("role", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("username", models.CharField(max_length=50, unique=True)),
                ("password", models.CharField(max_length=255)),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="employees",
                        to="api.store",
                    ),
                ),
            ],
            options={
                "db_table": "employee",
            },
        ),
        migrations.CreateModel(
            name="CustomerOrder",
            fields=[
                ("order_id", models.AutoField(primary_key=True, serialize=False)),
                ("order_date", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("PROCESSING", "Processing"),
                            ("SHIPPED", "Shipped"),
                            ("DELIVERED", "Delivered"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to="api.customer",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.store"
                    ),
                ),
            ],
            options={
                "db_table": "customer_order",
            },
        ),
        migrations.CreateModel(
            name="Supplier",
            fields=[
                ("supplier_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("contact_email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=20)),
                ("address", models.TextField()),
            ],
            options={
                "db_table": "supplier",
                "indexes": [
                    models.Index(fields=["name"], name="supplier_name_b57b10_idx")
                ],
            },
        ),
        migrations.CreateModel(
            name="PurchaseOrder",
            fields=[
                ("po_id", models.AutoField(primary_key=True, serialize=False)),
                ("order_date", models.DateField(auto_now_add=True)),
                ("expected_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("APPROVED", "Approved"),
                            ("RECEIVED", "Received"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.store"
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.supplier"
                    ),
                ),
            ],
            options={
                "db_table": "purchase_order",
            },
        ),
        migrations.CreateModel(
            name="Delivery",
            fields=[
                ("delivery_id", models.AutoField(primary_key=True, serialize=False)),
                ("ship_date", models.DateField(blank=True, null=True)),
                ("delivery_date", models.DateField(blank=True, null=True)),
                ("tracking_number", models.CharField(max_length=100, unique=True)),
                (
                    "delivery_status",
                    models.CharField(
                        choices=[
                            ("PREPARING", "Preparing"),
                            ("SHIPPED", "Shipped"),
                            ("IN_TRANSIT", "In Transit"),
                            ("DELIVERED", "Delivered"),
                            ("FAILED", "Failed"),
                        ],
                        default="PREPARING",
                        max_length=20,
                    ),
                ),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="delivery",
                        to="api.customerorder",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.employee",
                    ),
                ),
            ],
            options={
                "db_table": "delivery",
                "indexes": [
                    models.Index(
                        fields=["tracking_number"], name="delivery_trackin_36d795_idx"
                    ),
                    models.Index(
                        fields=["delivery_status"], name="delivery_deliver_78d418_idx"
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "quantity",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "unit_price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="api.customerorder",
                    ),
                ),
                (
                    "part",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.autopart"
                    ),
                ),
            ],
            options={
                "db_table": "orderitem",
                "unique_together": {("order", "part")},
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("payment_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("CREDIT_CARD", "Credit Card"),
                            ("DEBIT_CARD", "Debit Card"),
                            ("PAYPAL", "PayPal"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                    ),
                ),
                ("paid_date", models.DateTimeField(auto_now_add=True)),
                (
                    "card_last_four_digit",
                    models.CharField(blank=True, max_length=4, null=True),
                ),
                ("authentication_code", models.CharField(max_length=100)),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment",
                        to="api.customerorder",
                    ),
                ),
            ],
            options={
                "db_table": "payment",
                "indexes": [
                    models.Index(
                        fields=["paid_date"], name="payment_paid_da_8007f2_idx"
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="POLineItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "quantity",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                (
                    "unit_cost",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                    ),
                ),
                (
                    "part",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.autopart"
                    ),
                ),
                (
                    "purchase_order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="line_items",
                        to="api.purchaseorder",
                    ),
                ),
            ],
            options={
                "db_table": "order_item",
                "unique_together": {("purchase_order", "part")},
            },
        ),
        migrations.CreateModel(
            name="ReturnItem",
            fields=[
                ("return_id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "quantity",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(1)]
                    ),
                ),
                ("reason", models.TextField()),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.customerorder",
                    ),
                ),
                (
                    "part",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.autopart"
                    ),
                ),
            ],
            options={
                "db_table": "returnitem",
                "indexes": [
                    models.Index(
                        fields=["created_date"], name="returnitem_created_4d7e80_idx"
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Inventory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "quantity_on_hand",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(0)]
                    ),
                ),
                (
                    "part",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.autopart"
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.store"
                    ),
                ),
            ],
            options={
                "db_table": "inventory",
                "indexes": [
                    models.Index(
                        fields=["store", "part"], name="inventory_store_i_4cee38_idx"
                    ),
                    models.Index(
                        fields=["quantity_on_hand"], name="inventory_quantit_c50ee4_idx"
                    ),
                ],
                "unique_together": {("store", "part")},
            },
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(fields=["username"], name="employee_usernam_f41457_idx"),
        ),
        migrations.AddIndex(
            model_name="employee",
            index=models.Index(
                fields=["store", "role"], name="employee_store_i_ad07a6_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="customerorder",
            index=models.Index(
                fields=["customer", "order_date"], name="customer_or_custome_2054ad_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="customerorder",
            index=models.Index(fields=["status"], name="customer_or_status_94fde1_idx"),
        ),
        migrations.AddIndex(
            model_name="purchaseorder",
            index=models.Index(
                fields=["status", "order_date"], name="purchase_or_status_bd86c3_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="purchaseorder",
            index=models.Index(
                fields=["store", "status"], name="purchase_or_store_i_b35582_idx"
            ),
        ),
    ]
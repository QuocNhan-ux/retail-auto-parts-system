from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinValueValidator
from decimal import Decimal

class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'store'
        indexes = [
            models.Index(fields=['city', 'state']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    customer_email = models.EmailField(unique=True)
    customer_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'customer'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['customer_email']),
        ]
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        # If password is not hashed yet (plain text), hash it
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} ({self.username})"


class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='employees')
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'employee'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['store', 'role']),
        ]
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        # if password is not hashed yet, hash it
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} - {self.role}"


class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    
    class Meta:
        db_table = 'supplier'
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class AutoPart(models.Model):
    CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('REBUILT', 'Rebuilt'),
        ('USED', 'Used'),
    ]
    
    part_id = models.AutoField(primary_key=True)
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    reorder_level = models.IntegerField(validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'part'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['sku']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return f"{self.sku} - {self.name}"


class Inventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    part = models.ForeignKey(AutoPart, on_delete=models.CASCADE)
    quantity_on_hand = models.IntegerField(validators=[MinValueValidator(0)])
    
    class Meta:
        db_table = 'inventory'
        unique_together = ('store', 'part')
        indexes = [
            models.Index(fields=['store', 'part']),
            models.Index(fields=['quantity_on_hand']),
        ]
    
    def __str__(self):
        return f"{self.store.name} - {self.part.name}: {self.quantity_on_hand}"


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    po_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    expected_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    class Meta:
        db_table = 'purchase_order'
        indexes = [
            models.Index(fields=['status', 'order_date']),
            models.Index(fields=['store', 'status']),
        ]
    
    def __str__(self):
        return f"PO-{self.po_id} - {self.supplier.name}"


class POLineItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='line_items')
    part = models.ForeignKey(AutoPart, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    class Meta:
        db_table = 'order_item'
        unique_together = ('purchase_order', 'part')
    
    def get_total_cost(self):
        return self.quantity * self.unit_cost
    
    def __str__(self):
        return f"PO-{self.purchase_order.po_id} - {self.part.name}"


class CustomerOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    class Meta:
        db_table = 'customer_order'
        indexes = [
            models.Index(fields=['customer', 'order_date']),
            models.Index(fields=['status']),
        ]
    
    def get_total_amount(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def __str__(self):
        return f"Order-{self.order_id} - {self.customer.full_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name='items')
    part = models.ForeignKey(AutoPart, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    class Meta:
        db_table = 'orderitem'
        unique_together = ('order', 'part')
    
    def get_total_price(self):
        return self.quantity * self.unit_price
    
    def __str__(self):
        return f"Order-{self.order.order_id} - {self.part.name}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('PAYPAL', 'PayPal'),
    ]
    
    payment_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(CustomerOrder, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    paid_date = models.DateTimeField(auto_now_add=True)
    card_last_four_digit = models.CharField(max_length=4, blank=True, null=True)
    authentication_code = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'payment'
        indexes = [
            models.Index(fields=['paid_date']),
        ]
    
    def __str__(self):
        return f"Payment-{self.payment_id} - Order-{self.order.order_id}"


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('PREPARING', 'Preparing'),
        ('SHIPPED', 'Shipped'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
    ]
    
    delivery_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(CustomerOrder, on_delete=models.CASCADE, related_name='delivery')
    ship_date = models.DateField(blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    tracking_number = models.CharField(max_length=100, unique=True)
    delivery_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PREPARING')
    
    class Meta:
        db_table = 'delivery'
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['delivery_status']),
        ]
    
    def __str__(self):
        return f"Delivery-{self.delivery_id} - Order-{self.order.order_id}"


class ReturnItem(models.Model):
    return_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE)
    part = models.ForeignKey(AutoPart, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    reason = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'returnitem'
        indexes = [
            models.Index(fields=['created_date']),
        ]
    
    def __str__(self):
        return f"Return-{self.return_id} - Order-{self.order.order_id}"
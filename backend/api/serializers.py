from rest_framework import serializers
from .models import (
    Store, Customer, Employee, Supplier, AutoPart, Inventory,
    PurchaseOrder, POLineItem, CustomerOrder, OrderItem,
    Payment, Delivery, ReturnItem
)

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'full_name', 'customer_email', 'customer_phone', 
                  'created_at', 'username', 'password']
        read_only_fields = ['customer_id', 'created_at']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()
        return customer


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class EmployeeSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Employee
        fields = ['employee_id', 'store', 'store_name', 'full_name', 'role', 
                  'email', 'username', 'password']
        read_only_fields = ['employee_id']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        employee = Employee(**validated_data)
        employee.set_password(password)
        employee.save()
        return employee
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class EmployeeLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class AutoPartSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoPart
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    part_name = serializers.CharField(source='part.name', read_only=True)
    part_sku = serializers.CharField(source='part.sku', read_only=True)
    part_price = serializers.DecimalField(source='part.unit_price', max_digits=10, 
                                          decimal_places=2, read_only=True)
    reorder_level = serializers.IntegerField(source='part.reorder_level', read_only=True)
    needs_reorder = serializers.SerializerMethodField()
    
    class Meta:
        model = Inventory
        fields = ['id', 'store', 'store_name', 'part', 'part_name', 'part_sku', 
                  'part_price', 'quantity_on_hand', 'reorder_level', 'needs_reorder']
    
    def get_needs_reorder(self, obj):
        return obj.quantity_on_hand <= obj.part.reorder_level


class POLineItemSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part.name', read_only=True)
    part_sku = serializers.CharField(source='part.sku', read_only=True)
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = POLineItem
        fields = ['id', 'part', 'part_name', 'part_sku', 'quantity', 'unit_cost', 'total_cost']
    
    def get_total_cost(self, obj):
        return obj.get_total_cost()


class PurchaseOrderSerializer(serializers.ModelSerializer):
    line_items = POLineItemSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = PurchaseOrder
        fields = ['po_id', 'store', 'store_name', 'supplier', 'supplier_name', 
                  'order_date', 'expected_date', 'status', 'line_items', 'total_amount']
        read_only_fields = ['po_id', 'order_date']
    
    def get_total_amount(self, obj):
        return sum(item.get_total_cost() for item in obj.line_items.all())


class OrderItemSerializer(serializers.ModelSerializer):
    part_name = serializers.CharField(source='part.name', read_only=True)
    part_sku = serializers.CharField(source='part.sku', read_only=True)
    part_condition = serializers.CharField(source='part.condition', read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'part', 'part_name', 'part_sku', 'part_condition', 
                  'quantity', 'unit_price', 'total_price']
    
    def get_total_price(self, obj):
        return obj.get_total_price()


class CustomerOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerOrder
        fields = ['order_id', 'customer', 'customer_name', 'store', 'store_name', 
                  'order_date', 'status', 'items', 'total_amount']
        read_only_fields = ['order_id', 'order_date']
    
    def get_total_amount(self, obj):
        return obj.get_total_amount()


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.order_id', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['payment_id', 'order', 'order_id', 'payment_method', 'amount', 
                  'paid_date', 'card_last_four_digit', 'authentication_code']
        read_only_fields = ['payment_id', 'paid_date']


class DeliverySerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.order_id', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    
    class Meta:
        model = Delivery
        fields = ['delivery_id', 'order', 'order_id', 'ship_date', 'delivery_date', 
                  'employee', 'employee_name', 'tracking_number', 'delivery_status']
        read_only_fields = ['delivery_id']


class ReturnItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.order_id', read_only=True)
    part_name = serializers.CharField(source='part.name', read_only=True)
    customer_name = serializers.CharField(source='order.customer.full_name', read_only=True)
    
    class Meta:
        model = ReturnItem
        fields = ['return_id', 'order', 'order_id', 'part', 'part_name', 
                  'customer_name', 'quantity', 'reason', 'created_date']
        read_only_fields = ['return_id', 'created_date']


class CartItemSerializer(serializers.Serializer):
    part_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    store_id = serializers.IntegerField()
    items = CartItemSerializer(many=True)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)
    card_last_four_digit = serializers.CharField(max_length=4, required=False, allow_blank=True)
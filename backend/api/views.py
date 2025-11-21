from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Sum, Count, F
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from .models import (
    Store, Customer, Employee, Supplier, AutoPart, Inventory,
    PurchaseOrder, POLineItem, CustomerOrder, OrderItem,
    Payment, Delivery, ReturnItem
)
from .serializers import (
    StoreSerializer, CustomerSerializer, CustomerLoginSerializer,
    EmployeeSerializer, EmployeeLoginSerializer, SupplierSerializer,
    AutoPartSerializer, InventorySerializer, PurchaseOrderSerializer,
    POLineItemSerializer, CustomerOrderSerializer, OrderItemSerializer,
    PaymentSerializer, DeliverySerializer, ReturnItemSerializer,
    CreateOrderSerializer
)


# Authentication Views
@api_view(['POST'])
def customer_login(request):
    """Customer authentication endpoint"""
    serializer = CustomerLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        try:
            customer = Customer.objects.get(username=username)
            if customer.check_password(password):
                 # store in session
                request.session['customer_id'] = customer.customer_id
                request.session['customer_name'] = customer.full_name

                return Response({
                    'success': True,
                    'customer_id': customer.customer_id,
                    'full_name': customer.full_name,
                    'email': customer.customer_email
                })
            else:
                return Response({'error': 'Invalid credentials'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def customer_logout(request):
    """Log out customer and clear session"""
    request.session.flush()  # clears all session data and cookie
    return Response({'success': True})

@api_view(['POST'])
def employee_login(request):
    """Employee authentication endpoint"""
    serializer = EmployeeLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        try:
            employee = Employee.objects.get(username=username)
            if employee.check_password(password):
                return Response({
                    'success': True,
                    'employee_id': employee.employee_id,
                    'full_name': employee.full_name,
                    'role': employee.role,
                    'store_id': employee.store_id
                })
            else:
                return Response({'error': 'Invalid credentials'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
        except Employee.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Customer ViewSet
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    @action(detail=True, methods=['get'])
    def order_history(self, request, pk=None):
        """Get customer's order history"""
        customer = self.get_object()
        orders = CustomerOrder.objects.filter(customer=customer).order_by('-order_date')
        serializer = CustomerOrderSerializer(orders, many=True)
        return Response(serializer.data)


# Employee ViewSet
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('store').all()
    serializer_class = EmployeeSerializer
    
    @action(detail=False, methods=['get'])
    def by_store(self, request):
        """Get employees by store"""
        store_id = request.query_params.get('store_id')
        if store_id:
            employees = self.queryset.filter(store_id=store_id)
            serializer = self.get_serializer(employees, many=True)
            return Response(serializer.data)
        return Response({'error': 'store_id parameter required'}, 
                       status=status.HTTP_400_BAD_REQUEST)


# AutoPart ViewSet
class AutoPartViewSet(viewsets.ModelViewSet):
    queryset = AutoPart.objects.all()
    serializer_class = AutoPartSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search parts by name, SKU, or category"""
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', '')
        condition = request.query_params.get('condition', '')
        
        parts = self.queryset
        
        if query:
            parts = parts.filter(
                Q(name__icontains=query) | 
                Q(sku__icontains=query) |
                Q(category__icontains=query)
            )
        
        if category:
            parts = parts.filter(category__iexact=category)
        
        if condition:
            parts = parts.filter(condition=condition)
        
        serializer = self.get_serializer(parts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all unique categories"""
        categories = AutoPart.objects.values_list('category', flat=True).distinct()
        return Response({'categories': list(categories)})


# Inventory ViewSet
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('store', 'part').all()
    serializer_class = InventorySerializer
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get parts that need reordering"""
        store_id = request.query_params.get('store_id')
        inventory = self.queryset.filter(
            quantity_on_hand__lte=F('part__reorder_level')
        )
        
        if store_id:
            inventory = inventory.filter(store_id=store_id)
        
        serializer = self.get_serializer(inventory, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_store(self, request):
        """Get inventory for specific store"""
        store_id = request.query_params.get('store_id')
        if store_id:
            inventory = self.queryset.filter(store_id=store_id)
            serializer = self.get_serializer(inventory, many=True)
            return Response(serializer.data)
        return Response({'error': 'store_id parameter required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_availability(self, request):
        """Check part availability at a store"""
        store_id = request.data.get('store_id')
        part_id = request.data.get('part_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            inventory = Inventory.objects.get(store_id=store_id, part_id=part_id)
            available = inventory.quantity_on_hand >= quantity
            return Response({
                'available': available,
                'quantity_on_hand': inventory.quantity_on_hand,
                'requested': quantity
            })
        except Inventory.DoesNotExist:
            return Response({'available': False, 'quantity_on_hand': 0})


# Purchase Order ViewSet
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.select_related('store', 'supplier').prefetch_related('line_items').all()
    serializer_class = PurchaseOrderSerializer
    
    @action(detail=True, methods=['post'])
    def add_line_item(self, request, pk=None):
        """Add line item to purchase order"""
        po = self.get_object()
        serializer = POLineItemSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(purchase_order=po)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def receive_order(self, request, pk=None):
        """Mark purchase order as received and update inventory"""
        po = self.get_object()
        
        if po.status == 'RECEIVED':
            return Response({'error': 'Order already received'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            po.status = 'RECEIVED'
            po.save()
            
            # Update inventory
            for line_item in po.line_items.all():
                inventory, created = Inventory.objects.get_or_create(
                    store=po.store,
                    part=line_item.part,
                    defaults={'quantity_on_hand': 0}
                )
                inventory.quantity_on_hand += line_item.quantity
                inventory.save()
        
        serializer = self.get_serializer(po)
        return Response(serializer.data)


# Customer Order ViewSet
class CustomerOrderViewSet(viewsets.ModelViewSet):
    queryset = CustomerOrder.objects.select_related('customer', 'store').prefetch_related('items').all()
    serializer_class = CustomerOrderSerializer
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create new customer order with items and payment"""
        serializer = CreateOrderSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        with transaction.atomic():
            # Create order
            order = CustomerOrder.objects.create(
                customer_id=data['customer_id'],
                store_id=data['store_id'],
                status='PENDING'
            )
            
            total_amount = 0
            
            # Create order items and update inventory
            for item_data in data['items']:
                part = AutoPart.objects.get(pk=item_data['part_id'])
                
                # Check and update inventory
                try:
                    inventory = Inventory.objects.get(
                        store_id=data['store_id'],
                        part=part
                    )
                    
                    if inventory.quantity_on_hand < item_data['quantity']:
                        return Response({
                            'error': f'Insufficient stock for {part.name}. Available: {inventory.quantity_on_hand}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    inventory.quantity_on_hand -= item_data['quantity']
                    inventory.save()
                    
                except Inventory.DoesNotExist:
                    return Response({
                        'error': f'Part {part.name} not available at this store'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    part=part,
                    quantity=item_data['quantity'],
                    unit_price=part.unit_price
                )
                total_amount += order_item.get_total_price()
            
            # Create payment
            payment = Payment.objects.create(
                order=order,
                payment_method=data['payment_method'],
                amount=total_amount,
                card_last_four_digit=data.get('card_last_four_digit', ''),
                authentication_code=str(uuid.uuid4())
            )
            
            # Create delivery record
            delivery = Delivery.objects.create(
                order=order,
                tracking_number=f"TRK{order.order_id}{timezone.now().strftime('%Y%m%d%H%M')}",
                delivery_status='PREPARING'
            )
            
            order.status = 'PROCESSING'
            order.save()
        
        order_serializer = CustomerOrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        """Get orders for specific customer"""
        customer_id = request.query_params.get('customer_id')
        if customer_id:
            orders = self.queryset.filter(customer_id=customer_id).order_by('-order_date')
            serializer = self.get_serializer(orders, many=True)
            return Response(serializer.data)
        return Response({'error': 'customer_id parameter required'}, 
                       status=status.HTTP_400_BAD_REQUEST)


# Reports API
@api_view(['GET'])
def daily_sales_report(request):
    """Generate daily sales report"""
    store_id = request.query_params.get('store_id')
    date = request.query_params.get('date', timezone.now().date())
    
    orders = CustomerOrder.objects.filter(
        order_date__date=date,
        status__in=['PROCESSING', 'SHIPPED', 'DELIVERED']
    )
    
    if store_id:
        orders = orders.filter(store_id=store_id)
    
    total_orders = orders.count()
    total_revenue = sum(order.get_total_amount() for order in orders)
    
    orders_by_status = orders.values('status').annotate(count=Count('status'))
    
    return Response({
        'date': date,
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'orders_by_status': list(orders_by_status)
    })


@api_view(['GET'])
def inventory_report(request):
    """Generate inventory status report"""
    store_id = request.query_params.get('store_id')
    
    inventory = Inventory.objects.select_related('part', 'store')
    
    if store_id:
        inventory = inventory.filter(store_id=store_id)
    
    low_stock = inventory.filter(quantity_on_hand__lte=F('part__reorder_level'))
    out_of_stock = inventory.filter(quantity_on_hand=0)
    
    total_value = sum(
        item.quantity_on_hand * item.part.unit_price 
        for item in inventory
    )
    
    return Response({
        'total_items': inventory.count(),
        'low_stock_items': low_stock.count(),
        'out_of_stock_items': out_of_stock.count(),
        'total_inventory_value': float(total_value),
        'low_stock_details': InventorySerializer(low_stock, many=True).data
    })


@api_view(['GET'])
def employee_performance_report(request):
    """Generate employee performance report"""
    store_id = request.query_params.get('store_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date', timezone.now().date())
    
    deliveries = Delivery.objects.select_related('employee', 'order')
    
    if store_id:
        deliveries = deliveries.filter(order__store_id=store_id)
    
    if start_date:
        deliveries = deliveries.filter(ship_date__gte=start_date)
    
    deliveries = deliveries.filter(ship_date__lte=end_date)
    
    performance = deliveries.values(
        'employee__full_name',
        'employee__role'
    ).annotate(
        total_deliveries=Count('delivery_id'),
        successful_deliveries=Count('delivery_id', filter=Q(delivery_status='DELIVERED'))
    )
    
    return Response({'performance': list(performance)})

def _get_cart(request):
    """Internal helper to get or init cart from session"""
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}
    request.session['cart'] = cart
    return cart


@api_view(['POST'])
def cart_add(request):
    """Add item to cart in session"""
    # make sure the user is logged in
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return Response({'error': 'Login required'}, status=status.HTTP_401_UNAUTHORIZED)

    part_id = str(request.data.get('part_id'))
    quantity = int(request.data.get('quantity', 1))

    if not part_id:
        return Response({'error': 'part_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    cart = _get_cart(request)
    cart[part_id] = cart.get(part_id, 0) + quantity
    request.session['cart'] = cart

    cart_count = sum(cart.values())
    return Response({'success': True, 'cart_count': cart_count})


@api_view(['GET'])
def cart_summary(request):
    """Return cart contents with details and total"""
    cart = _get_cart(request)
    items = []
    total_amount = Decimal(00.0)

    for part_id_str, qty in cart.items():
        try:
            part_id = int(part_id_str)
            part = AutoPart.objects.get(pk=part_id)
        except (ValueError, AutoPart.DoesNotExist):
            continue

        quantity = int(qty)
        subtotal = part.unit_price * quantity
        total_amount += subtotal

        items.append({
            'part_id': part.part_id,
            'name': part.name,
            'unit_price': str(part.unit_price),
            'quantity': quantity,
            'subtotal': str(subtotal),
        })

    cart_count = sum(i['quantity'] for i in items)


    return Response({
        'cart_count': cart_count,
        'items': items,
        'total_amount': str(total_amount),
    })


@api_view(['POST'])
def cart_clear(request):
    """Clear cart"""
    request.session['cart'] = {}
    return Response({'success': True})

def cart_page(request):
    if 'customer_id' not in request.session:
        return redirect('customer-login-page')
    return render(request, 'customer/cart.html')
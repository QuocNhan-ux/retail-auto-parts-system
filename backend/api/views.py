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

# Customer logout
@api_view(['POST'])
def customer_logout(request):
    """Log out customer and clear session"""
    request.session.flush()  # clears all session data and cookie
    return Response({'success': True})


# Employee login
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
                # ✅ store employee info in session
                request.session['employee_id'] = employee.employee_id
                request.session['employee_name'] = employee.full_name
                request.session['employee_role'] = employee.role
                request.session['store_id'] = employee.store_id

                return Response({
                    'success': True,
                    'employee_id': employee.employee_id,
                    'full_name': employee.full_name,
                    'role': employee.role,
                    'store_id': employee.store_id
                })
            else:
                return Response(
                    {'error': 'Invalid credentials'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Employee logout
@api_view(['POST'])
def employee_logout(request):
    """Log out employee and clear employee-related session data"""
    for key in ['employee_id', 'employee_name', 'employee_role', 'store_id']:
        request.session.pop(key, None)
    request.session.modified = True
    return Response({'success': True})


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
        # ... your existing create_order code ...
        # (leave this as-is)
        pass

    @action(detail=False, methods=['get'])
    def by_store(self, request):
        """
        Get orders for a specific store (for employees).
        Optional ?status= filter (e.g. PROCESSING, PENDING).
        """
        store_id = request.query_params.get('store_id')
        status_filter = request.query_params.get('status')

        if not store_id:
            return Response(
                {'error': 'store_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        orders = self.queryset.filter(store_id=store_id).order_by('-order_date')

        if status_filter:
            orders = orders.filter(status=status_filter)

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update order + delivery status (used by employees to process orders).
        Expects JSON like:
        {
            "status": "SHIPPED" or "DELIVERED",
            "delivery_status": "IN_TRANSIT" or "DELIVERED",
            "employee_id": 3
        }
        """
        order = self.get_object()
        new_status = request.data.get('status')
        delivery_status = request.data.get('delivery_status')
        employee_id = request.data.get('employee_id')

        # Validate order status
        valid_order_statuses = {code for code, _ in CustomerOrder.STATUS_CHOICES}
        if new_status and new_status not in valid_order_statuses:
            return Response(
                {'error': f'Invalid order status: {new_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate / get delivery object
        try:
            delivery = order.delivery
        except Delivery.DoesNotExist:
            delivery = Delivery(order=order)

        valid_delivery_statuses = {code for code, _ in Delivery.STATUS_CHOICES}
        if delivery_status and delivery_status not in valid_delivery_statuses:
            return Response(
                {'error': f'Invalid delivery status: {delivery_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Attach employee if provided
        if employee_id:
            try:
                employee = Employee.objects.get(pk=employee_id)
                delivery.employee = employee
            except Employee.DoesNotExist:
                return Response(
                    {'error': f'Employee {employee_id} not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Apply status changes + dates
        from django.utils import timezone

        if new_status:
            order.status = new_status

        if delivery_status:
            delivery.delivery_status = delivery_status

        # Auto set dates based on transitions
        today = timezone.now().date()
        if new_status == 'SHIPPED' and not delivery.ship_date:
            delivery.ship_date = today
        if new_status == 'DELIVERED' and not delivery.delivery_date:
            delivery.delivery_date = today

        order.save()
        delivery.save()

        serializer = CustomerOrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

# Cart helpers & API views
def _get_cart(request):
    """
    Internal helper to get or init cart from session.

    Cart shape in session:
    {
        "AP-100245": {
            "name": "Brake Pad Set",
            "unit_price": 49.99,
            "quantity": 2,
        },
        ...
    }
    """
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}

    normalised = {}

    for pid, item in cart.items():
        # Legacy scalar value (probably just a quantity)
        if not isinstance(item, dict):
            try:
                qty = int(item)
            except (TypeError, ValueError):
                qty = 1

            normalised[pid] = {
                "name": f"Item {pid}",
                "unit_price": 0.0,
                "quantity": max(1, qty),
            }
            continue

        # Proper dict – make sure required keys exist and are sane
        name = item.get("name") or f"Item {pid}"
        try:
            unit_price = float(item.get("unit_price", 0))
        except (TypeError, ValueError):
            unit_price = 0.0

        try:
            qty = int(item.get("quantity", 1))
        except (TypeError, ValueError):
            qty = 1

        normalised[pid] = {
            "name": name,
            "unit_price": unit_price,
            "quantity": max(1, qty),
        }

    request.session["cart"] = normalised
    request.session.modified = True
    return normalised


@api_view(["POST"])
def cart_add(request):
    """Add item to cart in session."""
    # require logged-in customer
    if not request.session.get("customer_id"):
        return Response({"error": "Login required"}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data
    part_id = str(data.get("part_id") or "").strip()
    if not part_id:
        return Response({"error": "part_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    # quantity
    try:
        quantity = int(data.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    # Try to read name/price from request first
    raw_name = (data.get("name") or "").strip()
    raw_price = data.get("unit_price")

    part_obj = None

    # If we don't have a good name/price from the request, look up the AutoPart
    if not raw_name or raw_price in (None, "", 0, "0", "0.0"):
        try:
            # numeric -> assume primary key
            pk = int(part_id)
            part_obj = AutoPart.objects.filter(pk=pk).first()
        except ValueError:
            # non-numeric -> assume SKU
            part_obj = AutoPart.objects.filter(sku=part_id).first()

        if part_obj:
            if not raw_name:
                raw_name = part_obj.name
            if raw_price in (None, "", 0, "0", "0.0"):
                raw_price = part_obj.unit_price  # Decimal is fine here

    # Finalize name
    name = raw_name or f"Item {part_id}"

    # Finalize price as float for JSON
    try:
        unit_price = float(raw_price or 0)
    except Exception:
        unit_price = float(part_obj.unit_price) if part_obj else 0.0

    cart = _get_cart(request)
    item = cart.get(part_id, {"name": name, "unit_price": unit_price, "quantity": 0})

    # Always keep latest name/price
    item["name"] = name
    item["unit_price"] = unit_price
    item["quantity"] = int(item.get("quantity", 0)) + quantity

    cart[part_id] = item
    request.session["cart"] = cart
    request.session.modified = True

    cart_count = sum(i["quantity"] for i in cart.values())
    return Response({"success": True, "cart_count": cart_count})


@api_view(["GET"])
def cart_summary(request):
    """Return cart items, totals, and count."""
    cart = _get_cart(request)

    items = []
    total = 0.0

    for part_id, item in cart.items():
        qty = int(item.get("quantity", 0))
        price = float(item.get("unit_price", 0))
        line_total = qty * price
        total += line_total

        items.append({
            "part_id": part_id,
            "name": item.get("name", f"Item {part_id}"),
            "unit_price": price,
            "quantity": qty,
            "line_total": line_total,
        })

    cart_count = sum(i["quantity"] for i in items)

    return Response({
        "cart_count": cart_count,
        "items": items,
        "total": total,
    })


@api_view(["POST"])
def cart_clear(request):
    """Clear the cart completely."""
    request.session["cart"] = {}
    request.session.modified = True
    return Response({"success": True, "cart_count": 0})


@api_view(["POST"])
def cart_remove(request):
    """Remove a single item from the cart."""
    part_id = str(request.data.get("part_id") or "").strip()
    cart = _get_cart(request)

    if part_id in cart:
        del cart[part_id]
        request.session["cart"] = cart
        request.session.modified = True

    cart_count = sum(i["quantity"] for i in cart.values())
    return Response({"success": True, "cart_count": cart_count})

def cart_page(request):
    if 'customer_id' not in request.session:
        return redirect('customer-login-page')
    return render(request, 'customer/cart.html')

@api_view(["POST"])
def cart_checkout(request):
    """
    Convert the current session cart into a CustomerOrder + Payment.
    Expects JSON body:
      {
        "payment_method": "CREDIT_CARD" | "DEBIT_CARD" | "PAYPAL",
        "card_last_four_digit": "1234"
      }
    """
    # Must be logged in as a customer
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return Response(
            {"error": "Login required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Get cart from session
    cart = _get_cart(request)
    if not cart:
        return Response(
            {"error": "Cart is empty."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # For this project we assume a single store
    store = Store.objects.first()
    if not store:
        return Response(
            {"error": "No store configured in the system."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    line_items = []
    total = Decimal("0.00")

    # Turn session cart entries into concrete AutoPart line items
    for part_key, item in cart.items():
        part = None
        key_str = str(part_key).strip()

        # 1) Try primary key (integer)
        try:
            pk = int(key_str)
            part = AutoPart.objects.filter(pk=pk).first()
        except (TypeError, ValueError):
            part = None

        # 2) Try SKU
        if not part:
            part = AutoPart.objects.filter(sku=key_str).first()

        # 3) As a last resort, try matching by name
        if not part:
            name = (item.get("name") or "").strip()
            if name:
                part = AutoPart.objects.filter(name__iexact=name).first()

        # If we still can't resolve the part, skip this entry
        if not part:
            continue

        # Quantity
        try:
            qty = int(item.get("quantity", 0))
        except (TypeError, ValueError):
            qty = 0

        if qty <= 0:
            continue

        # Unit price—prefer session value, fall back to DB value
        price_raw = item.get("unit_price", part.unit_price)
        try:
            price = Decimal(str(price_raw))
        except Exception:
            price = part.unit_price

        if price <= 0:
            price = part.unit_price

        line_total = price * qty
        total += line_total

        line_items.append((part, qty, price))

    # If nothing usable, bail out
    if not line_items:
        return Response(
            {"error": "No valid items in cart to place an order."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payment_method = request.data.get("payment_method", "CREDIT_CARD")
    card_last4 = (request.data.get("card_last_four_digit") or "")[-4:]

    with transaction.atomic():
        # Create the order
        order = CustomerOrder.objects.create(
            customer_id=customer_id,
            store=store,
            status="PENDING",
        )

        # Create order items
        for part, qty, price in line_items:
            OrderItem.objects.create(
                order=order,
                part=part,
                quantity=qty,
                unit_price=price,
            )

        # Payment record
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=total,
            card_last_four_digit=card_last4,
            authentication_code=str(uuid.uuid4())[:12],
        )

        # Delivery record
        Delivery.objects.create(
            order=order,
            tracking_number=f"TRK{order.order_id}{timezone.now().strftime('%Y%m%d%H%M')}",
            delivery_status="PREPARING",
        )

        # Move order to PROCESSING
        order.status = "PROCESSING"
        order.save()

    # Clear the session cart now that we've placed the order
    request.session["cart"] = {}
    request.session.modified = True

    return Response(
        {
            "success": True,
            "order_id": order.order_id,
            "total": float(total),
        },
        status=status.HTTP_201_CREATED,
    )
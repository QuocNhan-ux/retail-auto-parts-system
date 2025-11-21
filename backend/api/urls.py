from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet, basename='customer')
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'parts', views.AutoPartViewSet, basename='autopart')
router.register(r'inventory', views.InventoryViewSet, basename='inventory')
router.register(r'purchase-orders', views.PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'customer-orders', views.CustomerOrderViewSet, basename='customerorder')

urlpatterns = [
    
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/customer/login/', views.customer_login, name='customer-login'),
    path('auth/employee/login/', views.employee_login, name='employee-login'),
    
    # Report endpoints
    path('reports/daily-sales/', views.daily_sales_report, name='daily-sales-report'),
    path('reports/inventory/', views.inventory_report, name='inventory-report'),
    path('reports/employee-performance/', views.employee_performance_report, name='employee-performance-report'),

    path('auth/customer/login/', views.customer_login, name='customer-login-api'),
    path('auth/customer/logout/', views.customer_logout, name='customer-logout-api'),

    path('cart/add/', views.cart_add, name='cart-add-api'),
    path('cart/summary/', views.cart_summary, name='cart-summary-api'),
    path('cart/clear/', views.cart_clear, name='cart-clear-api'),
]
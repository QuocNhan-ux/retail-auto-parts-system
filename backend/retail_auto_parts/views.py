from django.shortcuts import render
from api.models import AutoPart

def home(request):
    # grab 6 random featured products from database
    featured_products = AutoPart.objects.all().order_by('?')[:6]
    return render(request, "home.html", {
        'featured_products': featured_products
    })

def customer_login_page(request):
    # Renders frontend/customer/login.html
    return render(request, "customer/login.html")

def employee_login_page(request):
    # Renders frontend/employee/login.html
    return render(request, "employee/login.html")

def catalog_view(request):
    # Get filter parameters from URL
    selected_category = request.GET.get('category', '')
    selected_condition = request.GET.get('condition', '')
    
    products = AutoPart.objects.all()
    
    # Filter by category if provided
    if selected_category:
        products = products.filter(category=selected_category)
        category_display = selected_category.replace('-', ' ').title()
    else:
        category_display = None
    
    # Filter by condition if provided
    if selected_condition:
        products = products.filter(condition=selected_condition)
    
    return render(request, 'catalog.html', {
        'products': products,
        'selected_category': selected_category,
        'selected_condition': selected_condition,
        'category_display': category_display,
    })
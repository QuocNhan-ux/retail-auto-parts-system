from django.shortcuts import render

def home(request):
    # Renders frontend/home.html
    return render(request, "home.html")

def customer_login_page(request):
    # Renders frontend/customer/login.html
    return render(request, "customer/login.html")

def employee_login_page(request):
    # Renders frontend/employee/login.html
    return render(request, "employee/login.html")
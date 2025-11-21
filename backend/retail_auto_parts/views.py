# backend/retail_auto_parts/views.py
from django.shortcuts import render, redirect
from api.models import AutoPart, Customer 
from django.db.models import Q

def home(request):
    # grab 6 random featured products from database
    featured_products = AutoPart.objects.all().order_by('?')[:6]
    return render(request, "home.html", {
        'featured_products': featured_products
    })

def customer_login_page(request):
    return render(request, "customer/login.html")

def employee_login_page(request):
    return render(request, "employee/login.html")

def customer_history_page(request):
    return render(request, "customer/history.html")

# CATALOG VIEW
def catalog_view(request):
    """
    Catalog page with optional filters, e.g.:
      /catalog/
      /catalog/?category=brakes
      /catalog/?category=engine-parts&condition=NEW
    """

    category_slug = (request.GET.get("category") or "").strip()
    condition = (request.GET.get("condition") or "").strip()

    # Slug -> text we search for in AutoPart.category
    CATEGORY_KEYWORDS = {
        "engine-parts": "Engine",
        "brakes": "Brake",
        "suspension": "Suspension",
        "electrical": "Electrical",
        "exhaust": "Exhaust",
        "body-parts": "Body",
    }

    # Slug -> nice display name for the page heading
    CATEGORY_LABELS = {
        "engine-parts": "Engine Parts",
        "brakes": "Brakes",
        "suspension": "Suspension",
        "electrical": "Electrical",
        "exhaust": "Exhaust",
        "body-parts": "Body Parts",
    }

    parts_qs = AutoPart.objects.all()

    selected_category = None
    category_display = "All Auto Parts"

    # Filter by category if selected
    if category_slug:
        selected_category = category_slug
        keyword = CATEGORY_KEYWORDS.get(category_slug)

        if keyword:
            # Use icontains so it matches things like "Brake Pad Set", "Brakes ",
            # "BRAKES", etc., even if the exact category text is different.
            parts_qs = parts_qs.filter(category__icontains=keyword)

        category_display = CATEGORY_LABELS.get(
            category_slug, category_slug.replace("-", " ").title()
        )

    selected_condition = None
    if condition:
        selected_condition = condition
        parts_qs = parts_qs.filter(condition=condition)

    context = {
        "products": parts_qs.order_by("name"),
        "selected_category": selected_category,
        "category_display": category_display,
        "selected_condition": selected_condition,
    }

    # Uses frontend/catalog.html
    return render(request, "catalog.html", context)

def customer_history_page(request):
    """
    Simple view that serves the customer order history template.
    The page itself will use JavaScript + API to load the current
    customer's past orders.
    """
    return render(request, "customer/history.html")

def search_parts(request):
    query = request.GET.get('q', '').strip()
    parts = AutoPart.objects.none()

    if query:
        parts = AutoPart.objects.filter(
            Q(name__icontains=query) | Q(sku__icontains=query)
        ).order_by('name')

    context = {
        'query': query,
        'parts': parts,
    }
    return render(request, "search_results.html", context)












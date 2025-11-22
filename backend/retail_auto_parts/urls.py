# URL configuration for retail_auto_parts project.

from django.contrib import admin
from django.urls import path, include
from . import views
from api import views as api_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # frontend  pages
    path("", views.home, name="home"),
    path("customer/login/", views.customer_login_page, name="customer-login-page"),
    path("employee/login/", views.employee_login_page, name="employee-login-page"),

    # catalog page for shopping
    path('catalog/', views.catalog_view, name='catalog'),
    path("catalog/<slug:category_slug>/", views.catalog_view, name="catalog-category"),

    path('search/', views.search_parts, name='search_parts'),

    # register cart page
    path('cart/', api_views.cart_page, name='cart-page'),

    # customer's history page
    path("customer/history/", views.customer_history_page, name="customer-history-page"),

    #API (DRF) endpoints
    path("api/", include("api.urls")),
]

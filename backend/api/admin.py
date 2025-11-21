from django.contrib import admin
from .models import (
    AutoPart,
    Customer,
    Store,
    Employee,
    CustomerOrder,
    Supplier,
    PurchaseOrder,
    Delivery,
    OrderItem,
    Payment,
    POLineItem,
    ReturnItem,
    Inventory,
)

admin.site.register(AutoPart)
admin.site.register(Customer)
admin.site.register(Store)
admin.site.register(Employee)
admin.site.register(CustomerOrder)
admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(Delivery)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(POLineItem)
admin.site.register(ReturnItem)
admin.site.register(Inventory)
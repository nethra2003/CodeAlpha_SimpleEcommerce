from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "category",
        "stock",
        "is_active",
    )
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
    list_editable = ("price", "stock", "is_active")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "user__username")
    inlines = [OrderItemInline]

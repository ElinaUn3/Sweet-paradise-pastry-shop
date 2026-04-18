from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Product, Order, OrderItem, DeliveryPoint


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['full_name', 'email', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['full_name', 'email']
    ordering = ['full_name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личные данные', {'fields': ('full_name', 'role')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['article', 'name', 'price', 'bakery', 'category', 'discount', 'stock', 'is_active']
    list_filter = ['bakery', 'category', 'cake_type', 'is_active']
    search_fields = ['name', 'article', 'description']
    ordering = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'customer_name', 'order_date', 'delivery_date', 'status']
    list_filter = ['status']
    search_fields = ['customer_name', 'number']
    inlines = [OrderItemInline]
    ordering = ['-order_date']


@admin.register(DeliveryPoint)
class DeliveryPointAdmin(admin.ModelAdmin):
    list_display = ['address']
    search_fields = ['address']

from django.contrib import admin
from store.models import Product, Category, Gallery, Specification, Size, Color, Cart, CartOrder, CartOrderItem

# Inline classes for related models
class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 0  # remove extra empty form

class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 0

class SizeInline(admin.TabularInline):
    model = Size
    extra = 0

class ColorInline(admin.TabularInline):
    model = Color
    extra = 0

class CartOrderItemsInlineAdmin(admin.TabularInline):
    model = CartOrderItem
    extra = 0

# Admin class for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'shipping_amount', 'stock_qty', 'in_stock', 'vendor', 'featured']
    list_editable = ['featured']
    list_filter = ['date']
    search_fields = ['title']
    inlines = [GalleryInline, SpecificationInline, SizeInline, ColorInline]

# Admin class for Cart
class CartAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart_id', 'qty', 'price', 'sub_total', 'shipping_amount', 'service_fee', 'tax_fee', 'total', 'country', 'size', 'color', 'date']

# Admin class for CartOrder
class CartOrderAdmin(admin.ModelAdmin):
    inlines = [CartOrderItemsInlineAdmin]
    list_display = ['oid', 'payment_status', 'order_status', 'sub_total', 'shipping_amount', 'tax_fee', 'service_fee', 'total', 'saved', 'date']
    search_fields = ['oid', 'full_name', 'email', 'mobile']
    list_editable = ['order_status', 'payment_status']
    list_filter = ['payment_status', 'order_status']

# Admin class for CartOrderItem
class CartOrderItemsAdmin(admin.ModelAdmin):
    list_display = ['order', 'vendor', 'product', 'qty', 'price', 'sub_total', 'shipping_amount', 'service_fee', 'tax_fee', 'total', 'date']
    search_fields = ['order__oid', 'product__title', 'vendor__name']
    list_filter = ['date']

# Registering the models with their admin classes
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartOrder, CartOrderAdmin)
admin.site.register(CartOrderItem, CartOrderItemsAdmin)

from django.contrib import admin
from .models.product import Product
from .models.sustainability import SustainabilityScore
from .models.shopping import ShoppingList, ShoppingListItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'weight', 'nutriscore', 'ecoscore']
    list_filter = ['category', 'nutriscore', 'ecoscore', 'is_organic']
    search_fields = ['name', 'brand', 'barcode']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SustainabilityScore)
class SustainabilityScoreAdmin(admin.ModelAdmin):
    list_display = ['product', 'total_score', 'economic_score', 'environmental_score', 'social_score']
    list_filter = ['total_score']
    search_fields = ['product__name']


class ShoppingListItemInline(admin.TabularInline):
    model = ShoppingListItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_price', 'total_items', 'average_score', 'is_optimized', 'created_at']
    list_filter = ['is_optimized', 'created_at']
    readonly_fields = ['total_price', 'total_items', 'average_score', 'created_at', 'updated_at']
    inlines = [ShoppingListItemInline]